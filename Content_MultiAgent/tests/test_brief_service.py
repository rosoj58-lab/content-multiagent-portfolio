"""Brief service tests."""

import json

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.brief_service import BriefService
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.llm_runner import LLMRunner


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def _brief_json() -> str:
    return json.dumps(
        {
            "topic": "AI workflow for SEO content",
            "goal": "Show how a portfolio project replaces manual copywriting steps.",
            "audience": "Recruiters and engineering interviewers",
            "main_keyword": "multi-agent SEO content pipeline",
            "secondary_keywords": ["SEO brief automation", "AI content workflow"],
            "lsi_keywords": ["quality gates", "structured artifacts"],
            "outline": {
                "h1": "Multi-Agent SEO Content Pipeline",
                "sections": [
                    {
                        "h2": "From dry input to SEO brief",
                        "h3": ["Dry input intake", "Structured brief output"],
                    }
                ],
            },
            "tone_of_voice": "Confident, concrete and technical",
            "constraints": ["Do not invent facts", "Keep claims traceable to input"],
        }
    )


def _services(tmp_path, responses: list[str]) -> tuple[JobService, BriefService, ArtifactStore, FakeLLMClient]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    client = FakeLLMClient(responses)
    job_service = JobService(settings=settings, artifact_store=store)
    brief_service = BriefService(
        settings=settings,
        artifact_store=store,
        llm_runner=LLMRunner(client),
    )
    return job_service, brief_service, store, client


def test_brief_service_persists_generated_seo_brief(tmp_path) -> None:
    job_service, brief_service, store, client = _services(tmp_path, [_brief_json()])
    job = job_service.create_job("Build a portfolio case study for the SEO app.", ArticleType.BP)

    result = brief_service.generate_brief(job.metadata.job_id)

    assert result.status is WorkflowStatus.RUNNING
    assert result.brief is not None
    assert result.brief.brief.topic == "AI workflow for SEO content"
    assert len(client.prompts) == 1

    brief_artifact = store.read_json(job.metadata.job_id, ArtifactKey.BRIEF)
    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    metadata = store.read_json(job.metadata.job_id, ArtifactKey.METADATA)

    assert brief_artifact["job_id"] == job.metadata.job_id
    assert brief_artifact["article_type"] == "BP"
    assert brief_artifact["stage"] == "brief_drafted"
    assert brief_artifact["brief"]["main_keyword"] == "multi-agent SEO content pipeline"
    assert brief_artifact["brief"]["outline"]["h1"] == "Multi-Agent SEO Content Pipeline"
    assert state["current_stage"] == "brief_drafted"
    assert state["status"] == "running"
    assert state["artifact_paths"]["brief"].endswith("brief.json")
    assert metadata["current_stage"] == "brief_drafted"
    assert metadata["status_history"][-1]["stage"] == "brief_drafted"


def test_brief_service_repairs_invalid_first_output_once(tmp_path) -> None:
    job_service, brief_service, store, client = _services(tmp_path, ["not json", _brief_json()])
    job = job_service.create_job("Create content about SEO workflow automation.", ArticleType.LP)

    result = brief_service.generate_brief(job.metadata.job_id)

    assert result.status is WorkflowStatus.RUNNING
    assert len(client.prompts) == 2
    assert "Repair it and return only valid JSON" in client.prompts[1]
    assert store.read_json(job.metadata.job_id, ArtifactKey.BRIEF)["article_type"] == "LP"


def test_brief_service_routes_double_parse_failure_to_human_review(tmp_path) -> None:
    job_service, brief_service, store, client = _services(tmp_path, ["not json", "still not json"])
    job = job_service.create_job("Create content about SEO workflow automation.", ArticleType.GP)

    result = brief_service.generate_brief(job.metadata.job_id)

    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    metadata = store.read_json(job.metadata.job_id, ArtifactKey.METADATA)

    assert result.status is WorkflowStatus.NEEDS_HUMAN_REVIEW
    assert result.error is not None
    assert len(client.prompts) == 2
    assert state["current_stage"] == "brief_drafted"
    assert state["status"] == "needs_human_review"
    assert state["errors"][0]["code"] == "brief_parse_failed"
    assert state["errors"][0]["details"]["attempts"] == 2
    assert metadata["status"] == "needs_human_review"
    assert not store.artifact_path(job.metadata.job_id, ArtifactKey.BRIEF).exists()
