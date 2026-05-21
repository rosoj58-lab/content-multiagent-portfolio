"""Brief QA service tests."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, SEOBrief, SEOBriefArtifact, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.brief_qa_service import BriefQAService
from seo_content_pipeline.services.job_service import JobService


def _valid_brief_artifact(job_id: str, article_type: ArticleType) -> SEOBriefArtifact:
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
                        "h2": "Brief generation",
                        "h3": ["Dry input", "Structured output"],
                    }
                ],
            },
            tone_of_voice="Clear and technical",
            constraints=["Do not invent facts"],
        ),
    )


def _service_setup(tmp_path) -> tuple[JobService, BriefQAService, ArtifactStore]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    return (
        JobService(settings=settings, artifact_store=store),
        BriefQAService(settings=settings, artifact_store=store),
        store,
    )


def test_brief_qa_service_saves_report_and_opens_manual_gate_on_pass(tmp_path) -> None:
    job_service, qa_service, store = _service_setup(tmp_path)
    job = job_service.create_job("Create content about SEO automation.", ArticleType.LP)
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.BRIEF,
        _valid_brief_artifact(job.metadata.job_id, ArticleType.LP),
    )

    result = qa_service.validate_brief(job.metadata.job_id)

    report = store.read_json(job.metadata.job_id, ArtifactKey.BRIEF_QA)
    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    metadata = store.read_json(job.metadata.job_id, ArtifactKey.METADATA)

    assert result.status is WorkflowStatus.WAITING_FOR_HUMAN
    assert result.report.passed is True
    assert report["passed"] is True
    assert report["summary"] == "Brief QA passed. Brief is ready for manual approval."
    assert state["status"] == "waiting_for_human"
    assert state["manual_gate_required"] is True
    assert state["artifact_paths"]["brief_qa"].endswith("brief_qa.json")
    assert metadata["status"] == "waiting_for_human"


def test_brief_qa_service_saves_failed_report_with_actionable_fields(tmp_path) -> None:
    job_service, qa_service, store = _service_setup(tmp_path)
    job = job_service.create_job("Create content about SEO automation.", ArticleType.BP)
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.BRIEF,
        {
            "job_id": job.metadata.job_id,
            "stage": "brief_drafted",
            "article_type": "BP",
            "brief": {
                "topic": "AI workflow",
                "goal": "Show the workflow.",
                "audience": "everyone",
                "main_keyword": "",
                "secondary_keywords": ["SEO automation"],
                "lsi_keywords": ["quality gates"],
                "outline": {"h1": "", "sections": []},
                "tone_of_voice": "Clear",
                "constraints": ["Do not invent facts"],
            },
        },
    )

    result = qa_service.validate_brief(job.metadata.job_id)

    report = store.read_json(job.metadata.job_id, ArtifactKey.BRIEF_QA)
    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    failed_fields = {
        check["metadata"]["field"] for check in report["checks"] if check["passed"] is False
    }

    assert result.status is WorkflowStatus.NEEDS_REVISION
    assert report["passed"] is False
    assert failed_fields == {"main_keyword", "audience", "outline"}
    assert "main_keyword, audience, outline" in report["summary"]
    assert state["status"] == "needs_revision"
    assert state["manual_gate_required"] is False
    assert state["artifact_paths"]["brief_qa"].endswith("brief_qa.json")
