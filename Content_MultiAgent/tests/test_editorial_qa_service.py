"""Editorial QA service tests."""

import json

import pytest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, QAReport, SEOBrief, SEOBriefArtifact
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.editorial_qa_service import EditorialQAService
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.llm_runner import LLMRunner


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def _brief_artifact(job_id: str) -> SEOBriefArtifact:
    return SEOBriefArtifact(
        job_id=job_id,
        article_type=ArticleType.LP,
        brief=SEOBrief(
            topic="AI workflow for SEO content",
            goal="Show how the portfolio project works.",
            audience="Technical hiring managers",
            main_keyword="multi-agent SEO content pipeline",
            secondary_keywords=["SEO automation"],
            lsi_keywords=["quality gates"],
            outline={
                "h1": "Multi-Agent SEO Content Pipeline",
                "sections": [{"h2": "Brief generation", "h3": ["Dry input"]}],
            },
            tone_of_voice="Clear and technical",
            constraints=["Do not invent facts"],
        ),
    )


def _qa_report_json(*, passed: bool, requires_human_review: bool = False) -> str:
    return json.dumps(
        {
            "job_id": "placeholder",
            "stage": "editorial_review",
            "passed": passed,
            "checks": [
                {
                    "name": "unsupported_factual_claims",
                    "passed": passed,
                    "severity": "info" if passed else "error",
                    "message": (
                        "No unsupported factual claims found."
                        if passed
                        else "Unsupported factual claims need evidence or removal."
                    ),
                    "metadata": {"area": "factual_discipline"},
                }
            ],
            "summary": "Editorial QA passed." if passed else "Editorial QA failed.",
            "score": 1.0 if passed else 0.0,
            "recommendations": [] if passed else ["Remove unsupported performance claims."],
            "routing_target": None,
            "requires_human_review": requires_human_review,
        }
    )


def _service_setup(tmp_path, responses: list[str]) -> tuple[JobService, EditorialQAService, ArtifactStore, FakeLLMClient]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    client = FakeLLMClient(responses)
    return (
        JobService(settings=settings, artifact_store=store),
        EditorialQAService(
            settings=settings,
            artifact_store=store,
            llm_runner=LLMRunner(client),
        ),
        store,
        client,
    )


def _create_job_with_editorial_inputs(
    tmp_path,
    responses: list[str],
) -> tuple[str, EditorialQAService, ArtifactStore, FakeLLMClient]:
    job_service, service, store, client = _service_setup(tmp_path, responses)
    job = job_service.create_job("Create content about SEO automation.")
    store.write_json(job.metadata.job_id, ArtifactKey.BRIEF, _brief_artifact(job.metadata.job_id))
    store.write_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL, "# Article\n\nBody.")
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.ARTICLE_VALIDATION,
        QAReport(
            job_id=job.metadata.job_id,
            stage="writing",
            passed=True,
            checks=[],
            summary="Deterministic article validation passed.",
        ),
    )
    return job.metadata.job_id, service, store, client


def test_editorial_qa_service_persists_passing_report(tmp_path) -> None:
    job_id, service, store, client = _create_job_with_editorial_inputs(
        tmp_path,
        [_qa_report_json(passed=True)],
    )

    result = service.run_editorial_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.EDITORIAL_QA)
    state = store.read_json(job_id, ArtifactKey.STATE)

    assert result.report.passed is True
    assert report["job_id"] == job_id
    assert report["stage"] == "editorial_review"
    assert state["current_stage"] == "editorial_review"
    assert state["status"] == "running"
    assert state["artifact_paths"]["editorial_qa"].endswith("editorial_qa.json")
    assert state["qa_flags"]["editorial_qa_passed"] is True
    assert "Unsupported factual claims must be flagged" in client.prompts[0]


def test_editorial_qa_service_routes_failed_report_to_writing_revision(tmp_path) -> None:
    job_id, service, store, _client = _create_job_with_editorial_inputs(
        tmp_path,
        [_qa_report_json(passed=False)],
    )

    result = service.run_editorial_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.EDITORIAL_QA)
    state = store.read_json(job_id, ArtifactKey.STATE)

    assert result.status.value == "needs_revision"
    assert report["passed"] is False
    assert report["routing_target"] == "writing"
    assert report["recommendations"] == ["Remove unsupported performance claims."]
    assert state["status"] == "needs_revision"
    assert state["qa_flags"]["editorial_qa_passed"] is False
    assert state["revision_notes"]["editorial_review"] == [
        "Remove unsupported performance claims."
    ]


def test_editorial_qa_service_routes_sensitive_review_to_human(tmp_path) -> None:
    job_id, service, store, _client = _create_job_with_editorial_inputs(
        tmp_path,
        [_qa_report_json(passed=False, requires_human_review=True)],
    )

    result = service.run_editorial_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.EDITORIAL_QA)
    state = store.read_json(job_id, ArtifactKey.STATE)

    assert result.status.value == "needs_human_review"
    assert report["requires_human_review"] is True
    assert report["routing_target"] is None
    assert state["status"] == "needs_human_review"
    assert state["errors"][0]["code"] == "editorial_human_review_required"
    assert state["revision_notes"]["editorial_review"] == [
        "Remove unsupported performance claims."
    ]


def test_editorial_qa_service_requires_article_validation_report(tmp_path) -> None:
    job_service, service, store, _client = _service_setup(tmp_path, [_qa_report_json(passed=True)])
    job = job_service.create_job("Create content about SEO automation.")
    store.write_json(job.metadata.job_id, ArtifactKey.BRIEF, _brief_artifact(job.metadata.job_id))
    store.write_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL, "# Article\n\nBody.")

    with pytest.raises(FileNotFoundError):
        service.run_editorial_qa(job.metadata.job_id)
