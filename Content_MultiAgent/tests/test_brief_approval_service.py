"""Brief approval service tests."""

import pytest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, SEOBrief, SEOBriefArtifact, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.brief_approval_service import BriefApprovalService
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


def _service_setup(
    tmp_path,
    *,
    max_revision_attempts: int = 2,
) -> tuple[JobService, BriefQAService, BriefApprovalService, ArtifactStore]:
    settings = AppSettings(artifact_root=tmp_path, max_revision_attempts=max_revision_attempts)
    store = ArtifactStore(settings.artifact_root)
    return (
        JobService(settings=settings, artifact_store=store),
        BriefQAService(settings=settings, artifact_store=store),
        BriefApprovalService(settings=settings, artifact_store=store),
        store,
    )


def _create_job_waiting_for_brief_approval(
    tmp_path,
    *,
    max_revision_attempts: int = 2,
) -> tuple[str, BriefApprovalService, ArtifactStore]:
    job_service, qa_service, approval_service, store = _service_setup(
        tmp_path,
        max_revision_attempts=max_revision_attempts,
    )
    job = job_service.create_job("Create content about SEO automation.", ArticleType.LP)
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.BRIEF,
        _valid_brief_artifact(job.metadata.job_id, ArticleType.LP),
    )
    qa_service.validate_brief(job.metadata.job_id)
    return job.metadata.job_id, approval_service, store


def test_approve_brief_records_brief_approved_and_closes_manual_gate(tmp_path) -> None:
    job_id, approval_service, store = _create_job_waiting_for_brief_approval(tmp_path)

    result = approval_service.approve_brief(job_id)

    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.status is WorkflowStatus.APPROVED
    assert result.current_stage.value == "brief_approved"
    assert state["current_stage"] == "brief_approved"
    assert state["status"] == "approved"
    assert state["manual_gate_required"] is False
    assert state["qa_flags"]["brief_approved"] is True
    assert metadata["status_history"][-1]["stage"] == "brief_approved"


def test_request_revision_persists_notes_and_increments_attempts(tmp_path) -> None:
    job_id, approval_service, store = _create_job_waiting_for_brief_approval(tmp_path)

    result = approval_service.request_revision(job_id, "Make the audience more specific.")

    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.status is WorkflowStatus.NEEDS_REVISION
    assert result.revision_attempt == 1
    assert state["current_stage"] == "brief_drafted"
    assert state["status"] == "needs_revision"
    assert state["manual_gate_required"] is False
    assert state["revision_attempts"]["brief_drafted"] == 1
    assert state["revision_notes"]["brief_drafted"] == ["Make the audience more specific."]
    assert metadata["status_history"][-1]["status"] == "needs_revision"


def test_request_revision_rejects_empty_notes(tmp_path) -> None:
    job_id, approval_service, _store = _create_job_waiting_for_brief_approval(tmp_path)

    with pytest.raises(ValueError, match="revision notes"):
        approval_service.request_revision(job_id, "   ")


def test_request_revision_routes_to_human_review_when_revision_limit_is_reached(tmp_path) -> None:
    job_id, approval_service, store = _create_job_waiting_for_brief_approval(
        tmp_path,
        max_revision_attempts=1,
    )
    approval_service.request_revision(job_id, "First revision.")

    result = approval_service.request_revision(job_id, "Second revision.")

    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.status is WorkflowStatus.NEEDS_HUMAN_REVIEW
    assert result.revision_attempt == 1
    assert state["status"] == "needs_human_review"
    assert state["errors"][0]["code"] == "brief_revision_limit_reached"
    assert state["errors"][0]["details"]["latest_notes"] == "Second revision."
    assert metadata["status"] == "needs_human_review"


def test_approve_brief_rejects_failed_qa_report(tmp_path) -> None:
    job_service, _qa_service, approval_service, store = _service_setup(tmp_path)
    job = job_service.create_job("Create content about SEO automation.", ArticleType.BP)
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.BRIEF,
        _valid_brief_artifact(job.metadata.job_id, ArticleType.BP),
    )
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.BRIEF_QA,
        {
            "job_id": job.metadata.job_id,
            "stage": "brief_drafted",
            "passed": False,
            "checks": [],
            "summary": "Brief QA failed.",
        },
    )

    with pytest.raises(ValueError, match="passed brief QA"):
        approval_service.approve_brief(job.metadata.job_id)
