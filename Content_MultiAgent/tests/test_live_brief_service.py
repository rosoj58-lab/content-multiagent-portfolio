"""Optional live SEO brief orchestration tests using only fake model output."""

import json

import pytest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.live_brief_service import LiveBriefService


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
            "topic": "Live AI workflow for SEO content",
            "goal": "Demonstrate one explicit model-backed SEO brief action.",
            "audience": "Technical interviewers",
            "main_keyword": "live SEO brief generation",
            "secondary_keywords": ["OpenAI content workflow"],
            "lsi_keywords": ["quality gate"],
            "outline": {
                "h1": "Live SEO Brief Generation",
                "sections": [{"h2": "Controlled live step", "h3": ["Brief QA"]}],
            },
            "tone_of_voice": "Clear and technical",
            "constraints": ["Do not invent facts"],
        }
    )


def _new_job(tmp_path, *, api_key: str | None = "test-key"):
    settings = AppSettings(artifact_root=tmp_path, openai_api_key=api_key)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Create an SEO brief from provided product notes.",
        ArticleType.BP,
    )
    return settings, store, job.metadata.job_id


def test_live_brief_generation_persists_brief_qa_and_stops_for_human_approval(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path)
    client = FakeLLMClient([_brief_json()])

    result = LiveBriefService(
        settings=settings,
        artifact_store=store,
        llm_client=client,
    ).generate_live_brief(job_id)

    state = store.read_json(job_id, ArtifactKey.STATE)
    assert result.status is WorkflowStatus.WAITING_FOR_HUMAN
    assert result.brief_path.endswith("brief.json")
    assert result.brief_qa_path.endswith("brief_qa.json")
    assert store.artifact_path(job_id, ArtifactKey.RUN_SUMMARY).exists()
    assert state["status"] == "waiting_for_human"
    assert state["manual_gate_required"] is True
    assert store.read_json(job_id, ArtifactKey.BRIEF)["brief"]["main_keyword"] == (
        "live SEO brief generation"
    )
    assert store.read_json(job_id, ArtifactKey.BRIEF_QA)["passed"] is True
    run_summary = store.read_json(job_id, ArtifactKey.RUN_SUMMARY)
    assert run_summary["status"] == "waiting_for_human"
    assert run_summary["manual_gate_required"] is True
    assert run_summary["decision_artifact"].endswith("brief_qa.json")
    assert run_summary["final_package_path"] is None
    assert len(client.prompts) == 1


@pytest.mark.parametrize("api_key", [None, " "])
def test_live_brief_generation_requires_local_api_key_without_writing_brief(
    tmp_path, api_key: str | None
) -> None:
    settings, store, job_id = _new_job(tmp_path, api_key=api_key)
    service = LiveBriefService(settings=settings, artifact_store=store)

    with pytest.raises(ValueError, match="requires OPENAI_API_KEY"):
        service.generate_live_brief(job_id)

    assert service.is_configured is False
    assert not store.artifact_path(job_id, ArtifactKey.BRIEF).exists()
    assert not store.artifact_path(job_id, ArtifactKey.BRIEF_QA).exists()


def test_live_brief_generation_routes_unparseable_model_output_to_human_review(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path)

    result = LiveBriefService(
        settings=settings,
        artifact_store=store,
        llm_client=FakeLLMClient(["not json", "still not json"]),
    ).generate_live_brief(job_id)

    assert result.status is WorkflowStatus.NEEDS_HUMAN_REVIEW
    assert store.read_json(job_id, ArtifactKey.STATE)["status"] == "needs_human_review"
    assert not store.artifact_path(job_id, ArtifactKey.BRIEF).exists()
    assert store.artifact_path(job_id, ArtifactKey.RUN_SUMMARY).exists()


def test_live_brief_generation_rejects_second_path_on_started_job(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path)
    service = LiveBriefService(
        settings=settings,
        artifact_store=store,
        llm_client=FakeLLMClient([_brief_json()]),
    )
    service.generate_live_brief(job_id)

    with pytest.raises(ValueError, match="newly created job"):
        service.generate_live_brief(job_id)
