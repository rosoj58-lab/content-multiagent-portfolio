"""Deterministic end-to-end demo runner for the local portfolio app."""

from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import ArtifactKey, ArticleType, PipelineState, WorkflowStatus
from seo_content_pipeline.services.article_validation_service import ArticleValidationService
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.brief_approval_service import BriefApprovalService
from seo_content_pipeline.services.brief_qa_service import BriefQAService
from seo_content_pipeline.services.brief_service import BriefService
from seo_content_pipeline.services.editorial_qa_service import EditorialQAService
from seo_content_pipeline.services.exporters import FinalPackageExporter
from seo_content_pipeline.services.final_qa_service import FinalQAService
from seo_content_pipeline.services.llm_runner import LLMRunner
from seo_content_pipeline.services.localization_service import LocalizationService
from seo_content_pipeline.services.seo_qa_service import SEOQAService
from seo_content_pipeline.services.uniqueness_gate_service import UniquenessGateService
from seo_content_pipeline.services.uniqueness_provider_service import UniquenessProviderService
from seo_content_pipeline.services.uniqueness_score_service import UniquenessScoreService
from seo_content_pipeline.services.writer_service import WriterService


DemoRunMode = Literal["demo", "full"]


class DemoPipelineResult(BaseModel):
    """Summary returned after an offline demo pipeline run."""

    job_id: str
    status: WorkflowStatus
    final_package_path: str
    final_qa_report_path: str


class _DeterministicDemoClient:
    """Small LLM client stand-in used only for the local demo runner."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = responses

    def generate(self, prompt: str) -> str:
        if not self._responses:
            raise ValueError("demo pipeline response queue is empty")
        return self._responses.pop(0)


class DemoPipelineService:
    """Run a complete offline portfolio demo using the normal stage services."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def run_full_demo(self, job_id: str, *, mode: DemoRunMode = "demo") -> DemoPipelineResult:
        """Generate all required artifacts for an existing job without external services."""
        state = PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))
        article_type = state.article_type or ArticleType.BP
        responses = [
            json.dumps(_brief_payload(article_type)),
            _article_markdown(article_type, mode),
            json.dumps(_editorial_qa_payload(job_id)),
            _localized_markdown("Spanish", article_type),
            _localized_markdown("Italian", article_type),
            _localized_markdown("French", article_type),
        ]
        llm_runner = LLMRunner(_DeterministicDemoClient(responses))

        BriefService(
            settings=self.settings,
            artifact_store=self.artifact_store,
            llm_runner=llm_runner,
        ).generate_brief(job_id)
        BriefQAService(settings=self.settings, artifact_store=self.artifact_store).validate_brief(job_id)
        BriefApprovalService(settings=self.settings, artifact_store=self.artifact_store).approve_brief(job_id)
        WriterService(
            settings=self.settings,
            artifact_store=self.artifact_store,
            llm_runner=llm_runner,
        ).generate_english_original(job_id, mode=mode)
        ArticleValidationService(
            settings=self.settings,
            artifact_store=self.artifact_store,
        ).validate_english_original(job_id, mode=mode)
        EditorialQAService(
            settings=self.settings,
            artifact_store=self.artifact_store,
            llm_runner=llm_runner,
        ).run_editorial_qa(job_id)
        SEOQAService(settings=self.settings, artifact_store=self.artifact_store).run_seo_qa(job_id)
        UniquenessProviderService(
            settings=self.settings,
            artifact_store=self.artifact_store,
        ).select_provider(job_id, "manual")
        UniquenessScoreService(
            settings=self.settings,
            artifact_store=self.artifact_store,
        ).record_manual_score(job_id, 94.0)
        UniquenessGateService(
            settings=self.settings,
            artifact_store=self.artifact_store,
        ).apply_threshold_gate(job_id)
        LocalizationService(
            settings=self.settings,
            artifact_store=self.artifact_store,
            llm_runner=llm_runner,
        ).generate_spanish_localization(job_id)
        LocalizationService(
            settings=self.settings,
            artifact_store=self.artifact_store,
            llm_runner=llm_runner,
        ).generate_italian_and_french_localizations(job_id)
        package = FinalPackageExporter(
            settings=self.settings,
            artifact_store=self.artifact_store,
        ).assemble_final_package(job_id)
        final_qa = FinalQAService(
            settings=self.settings,
            artifact_store=self.artifact_store,
        ).run_final_qa(job_id)

        return DemoPipelineResult(
            job_id=job_id,
            status=final_qa.status,
            final_package_path=package.markdown_path,
            final_qa_report_path=str(self.artifact_store.artifact_path(job_id, ArtifactKey.FINAL_QA_REPORT)),
        )


def _brief_payload(article_type: ArticleType) -> dict:
    article_labels = {
        ArticleType.BP: "Blog Post",
        ArticleType.LP: "Landing Page",
        ArticleType.GP: "Guest Post",
    }
    return {
        "topic": "AI workflow for SEO content",
        "goal": f"Show how the {article_labels[article_type]} demo moves from source notes to approved content.",
        "audience": "Technical hiring managers and product-minded interviewers",
        "main_keyword": "multi-agent SEO content pipeline",
        "secondary_keywords": ["SEO automation", "AI content workflow"],
        "lsi_keywords": ["quality gates", "structured artifacts"],
        "outline": {
            "h1": "Multi-Agent SEO Content Pipeline",
            "sections": [
                {
                    "h2": "From Dry Input To Approved Content",
                    "h3": ["Brief Control", "QA Gates"],
                },
                {
                    "h2": "Why The Workflow Is Interview Ready",
                    "h3": ["Revision Routing", "Inspectable Artifacts"],
                },
            ],
        },
        "tone_of_voice": "Clear, concrete and technical",
        "constraints": ["Do not invent facts", "Keep claims traceable to the source input"],
    }


def _article_markdown(article_type: ArticleType, mode: DemoRunMode) -> str:
    context = {
        ArticleType.BP: "The blog post path shows a clean informational workflow.",
        ArticleType.LP: "The landing page path shows how commercial claims stay controlled.",
        ArticleType.GP: "The guest post path shows where human review protects link placement.",
    }[article_type]
    paragraphs = [
        (
            "The multi-agent SEO content pipeline turns dry source notes into a structured "
            "content package that can be inspected at every stage. It starts with a brief, "
            "moves through English drafting, validates quality gates, checks uniqueness, "
            "creates localizations, and finishes with a final QA report. "
            f"{context}"
        ),
        (
            "The system is designed around SEO automation without hiding the workflow inside "
            "one opaque prompt. Each stage writes structured artifacts, so an interviewer can "
            "open the job folder and see what happened. The brief explains the topic, audience, "
            "keyword intent, outline, tone, and constraints before writing begins."
        ),
        (
            "That structure is what makes the demo stronger than a simple chat transcript. "
            "The operator can compare the source input, generated brief, article draft, QA "
            "reports, uniqueness result, and final package side by side. This gives the project "
            "a clear audit trail and makes implementation choices visible during a technical "
            "conversation."
        ),
        (
            "It also makes the user experience predictable. A reviewer does not need to guess "
            "which invisible agent made a decision, because the timeline and artifacts show the "
            "stage, status, and next action in one place."
        ),
        (
            "Quality gates keep the workflow practical. Deterministic validators check article "
            "shape and length. Editorial QA checks whether the article respects source material "
            "and keeps claims disciplined. SEO QA checks keyword coverage, heading alignment, "
            "search intent, and article type fit. These checks make the project easier to defend "
            "because every decision has a visible report."
        ),
        (
            "When a check fails, revision routing gives the next action instead of a vague error. "
            "Brief problems go back to brief generation. Writing and editorial problems go back "
            "to the English article. SEO problems route to targeted writing revision. Uniqueness "
            "problems stop localization until the source article is fixed."
        ),
        (
            "The demo uses a manual uniqueness score so it can run offline without Copyleaks "
            "credentials. A real provider can be added behind the same provider boundary later. "
            "For portfolio purposes, the important point is that the uniqueness gate is explicit: "
            "the score must meet the threshold before localized content is produced."
        ),
        (
            "Localization happens only after English quality gates pass. Spanish, Italian, and "
            "French versions are stored as separate Markdown artifacts, which keeps review simple. "
            "The final package then combines the approved English article, localizations, artifact "
            "references, workflow status, and QA evidence into Markdown and JSON outputs."
        ),
        (
            "This AI content workflow is interview ready because it is repeatable, observable, "
            "and honest about human control. It does not pretend that automation removes editorial "
            "judgment. Instead, it shows where automation helps, where quality gates protect the "
            "content, and where a person should review sensitive decisions."
        ),
        (
            "The result is a working local product rather than a static prompt collection. The "
            "operator can create a job, run the demo pipeline, inspect structured artifacts, and "
            "download the final content package. That makes the project suitable for a technical "
            "portfolio conversation about architecture, product judgment, and delivery quality."
        ),
    ]
    sections = [
        "# Multi-Agent SEO Content Pipeline",
        "## From Dry Input To Approved Content",
        "### Brief Control",
        *paragraphs[:4],
        "## Why The Workflow Is Interview Ready",
        "### Inspectable Artifacts",
        *paragraphs[4:],
    ]
    if mode == "full":
        expansions = [
            (
                "A full-length portfolio article can spend more time on operational detail. "
                "The intake step captures source notes, audience signals, article type, and "
                "keyword intent before any draft exists. That early structure gives later "
                "validators something concrete to inspect instead of relying on taste alone."
            ),
            (
                "The brief stage is also useful as a product boundary. It separates planning "
                "from writing, stores the outline as JSON, and creates a manual approval point. "
                "That manual gate is important because a project owner can reject weak strategy "
                "before the system spends effort on article generation."
            ),
            (
                "The writing stage then produces the English source article from an approved "
                "brief. In a real production setup, this is where a configured LLM provider "
                "would be connected. In the local demo, deterministic content keeps the example "
                "repeatable and removes external API risk during interviews."
            ),
            (
                "The validation stage checks structural facts that do not need an LLM. Word "
                "count, heading structure, required artifacts, and SEO signals are deterministic "
                "enough to test reliably. This makes the pipeline easier to maintain because "
                "basic quality does not depend on a model judge."
            ),
            (
                "The editorial QA stage represents higher-level review. It evaluates whether "
                "claims stay disciplined, whether the structure is useful, and whether the "
                "article needs revision. The output is still a structured report, so the UI can "
                "show a checklist instead of a vague paragraph of feedback."
            ),
            (
                "The SEO QA stage focuses on intent alignment. It checks whether the main "
                "keyword, secondary keywords, related terms, headings, article type, and word "
                "count signal are present. If the article misses the mark, the workflow records "
                "routing notes for targeted writing revision."
            ),
            (
                "The uniqueness gate is deliberately explicit. The system records the provider, "
                "score, threshold, and routing reason before localization starts. That keeps "
                "plagiarism control visible and gives a clean place to replace the manual score "
                "with a real provider integration later."
            ),
            (
                "Localization runs after the English source is accepted. Separate Spanish, "
                "Italian, and French Markdown artifacts make it easy to inspect each output. "
                "The final package references those artifacts instead of flattening every "
                "decision into one unreadable blob."
            ),
            (
                "Final QA closes the loop. It verifies that mandatory artifacts exist, QA "
                "reports passed, uniqueness passed, localization exists, and package assembly "
                "completed. If something is missing, the report records a failed check and a "
                "routing target rather than pretending the job succeeded."
            ),
            (
                "For an interview, this architecture gives several strong talking points: "
                "typed models, file-based persistence, provider boundaries, deterministic "
                "validators, human-in-the-loop gates, revision routing, and Streamlit "
                "observability. Each part is small enough to explain and real enough to run."
            ),
        ]
        index = 0
        while _word_count("\n\n".join(sections)) < 1500:
            sections.append(expansions[index % len(expansions)])
            index += 1

    return "\n\n".join(
        sections
    )


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _editorial_qa_payload(job_id: str) -> dict:
    return {
        "job_id": job_id,
        "stage": "editorial_review",
        "passed": True,
        "checks": [
            {
                "name": "source_discipline",
                "passed": True,
                "severity": "info",
                "message": "Article keeps claims tied to the supplied demo context.",
                "metadata": {},
            },
            {
                "name": "structure_clarity",
                "passed": True,
                "severity": "info",
                "message": "Article has clear sections and interview-ready framing.",
                "metadata": {},
            },
        ],
        "summary": "Editorial QA passed for the deterministic demo article.",
        "score": 1.0,
        "recommendations": [],
        "routing_target": None,
    }


def _localized_markdown(language: str, article_type: ArticleType) -> str:
    return (
        f"# {language} Localization: Multi-Agent SEO Content Pipeline\n\n"
        "## Localized Demo Summary\n\n"
        f"This {article_type.value} localization is generated by the offline demo runner. "
        "It preserves the core message: structured artifacts, QA gates, uniqueness control, "
        "revision routing, and final package assembly make the portfolio project inspectable."
    )
