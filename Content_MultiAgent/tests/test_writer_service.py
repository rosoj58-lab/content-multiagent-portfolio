"""Writer service tests."""

import pytest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, SEOBrief, SEOBriefArtifact
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.brief_approval_service import BriefApprovalService
from seo_content_pipeline.services.brief_qa_service import BriefQAService
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.llm_runner import LLMRunner
from seo_content_pipeline.services.writer_service import WriterService


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


ARTICLE_MARKDOWN = """# Multi-Agent SEO Content Pipeline

## Brief Generation

### Dry Input

The system starts with source notes.
"""


def _brief_artifact(job_id: str, article_type: ArticleType) -> SEOBriefArtifact:
    return SEOBriefArtifact(
        job_id=job_id,
        article_type=article_type,
        brief=SEOBrief(
            topic="AI workflow for SEO content",
            goal="Show how the portfolio project works.",
            audience="Technical hiring managers",
            main_keyword="multi-agent SEO content pipeline",
            secondary_keywords=["SEO automation"],
            lsi_keywords=["quality gates"],
            outline={
                "h1": "Multi-Agent SEO Content Pipeline",
                "sections": [
                    {
                        "h2": "Brief Generation",
                        "h3": ["Dry Input", "Structured Output"],
                    }
                ],
            },
            tone_of_voice="Clear and technical",
            constraints=["Do not invent facts"],
        ),
    )


def _service_setup(
    tmp_path,
    responses: list[str],
) -> tuple[JobService, BriefQAService, BriefApprovalService, WriterService, ArtifactStore, FakeLLMClient]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    client = FakeLLMClient(responses)
    return (
        JobService(settings=settings, artifact_store=store),
        BriefQAService(settings=settings, artifact_store=store),
        BriefApprovalService(settings=settings, artifact_store=store),
        WriterService(settings=settings, artifact_store=store, llm_runner=LLMRunner(client)),
        store,
        client,
    )


def _create_approved_job(tmp_path, responses: list[str]) -> tuple[str, WriterService, ArtifactStore, FakeLLMClient]:
    job_service, qa_service, approval_service, writer_service, store, client = _service_setup(
        tmp_path,
        responses,
    )
    job = job_service.create_job("Create content about SEO automation.", ArticleType.LP)
    store.write_json(job.metadata.job_id, ArtifactKey.BRIEF, _brief_artifact(job.metadata.job_id, ArticleType.LP))
    qa_service.validate_brief(job.metadata.job_id)
    approval_service.approve_brief(job.metadata.job_id)
    return job.metadata.job_id, writer_service, store, client


def test_writer_service_generates_english_original_from_approved_brief(tmp_path) -> None:
    job_id, writer_service, store, client = _create_approved_job(tmp_path, [ARTICLE_MARKDOWN])

    result = writer_service.generate_english_original(job_id, mode="demo")

    article = store.read_text(job_id, ArtifactKey.ENGLISH_ORIGINAL)
    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.article_path.endswith("english_original.md")
    assert article.startswith("# Multi-Agent SEO Content Pipeline")
    assert state["current_stage"] == "writing"
    assert state["status"] == "running"
    assert state["artifact_paths"]["english_original"].endswith("english_original.md")
    assert state["qa_flags"]["english_original_generated"] is True
    assert metadata["status_history"][-1]["stage"] == "writing"
    assert "English US" in client.prompts[0]
    assert "# Multi-Agent SEO Content Pipeline" in client.prompts[0]
    assert "## Brief Generation" in client.prompts[0]
    assert "### Dry Input" in client.prompts[0]


def test_writer_service_rejects_unapproved_brief(tmp_path) -> None:
    job_service, _qa_service, _approval_service, writer_service, store, _client = _service_setup(
        tmp_path,
        [ARTICLE_MARKDOWN],
    )
    job = job_service.create_job("Create content about SEO automation.", ArticleType.LP)
    store.write_json(job.metadata.job_id, ArtifactKey.BRIEF, _brief_artifact(job.metadata.job_id, ArticleType.LP))

    with pytest.raises(ValueError, match="approved brief"):
        writer_service.generate_english_original(job.metadata.job_id)


def test_writer_service_demo_mode_uses_shorter_target_length(tmp_path) -> None:
    job_id, writer_service, _store, client = _create_approved_job(tmp_path, [ARTICLE_MARKDOWN])

    writer_service.generate_english_original(job_id, mode="demo")

    assert "500-700 words" in client.prompts[0]


def test_writer_service_full_mode_targets_1500_to_1600_words(tmp_path) -> None:
    job_id, writer_service, _store, client = _create_approved_job(tmp_path, [ARTICLE_MARKDOWN])

    writer_service.generate_english_original(job_id, mode="full")

    assert "1500-1600 words" in client.prompts[0]
