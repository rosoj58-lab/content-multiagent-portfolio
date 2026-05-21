"""StageView builder tests."""

from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    QAReport,
    StageView,
    ValidationCheck,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.stage_view_builder import (
    build_brief_qa_stage_view,
    build_initial_stage_views,
)


def test_build_initial_stage_views_returns_stage_view_data() -> None:
    metadata = JobMetadata(
        job_id="job-123",
        current_stage=WorkflowStage.INPUT_RECEIVED,
        status=WorkflowStatus.RUNNING,
    )

    views = build_initial_stage_views(metadata)

    assert views
    assert all(isinstance(view, StageView) for view in views)
    assert views[0].stage is WorkflowStage.INPUT_RECEIVED
    assert views[0].status is WorkflowStatus.RUNNING
    assert views[0].label == "Input received"
    assert set(views[0].artifact_links) == {
        ArtifactKey.METADATA,
        ArtifactKey.INPUT,
        ArtifactKey.STATE,
    }
    assert views[0].available_actions == ["Create SEO brief"]


def test_build_initial_stage_views_marks_non_current_future_steps_waiting() -> None:
    metadata = JobMetadata(
        job_id="job-123",
        current_stage=WorkflowStage.INPUT_RECEIVED,
        status=WorkflowStatus.RUNNING,
    )

    views = build_initial_stage_views(metadata)

    assert [view.stage for view in views] == [
        WorkflowStage.INPUT_RECEIVED,
        WorkflowStage.BRIEF_DRAFTED,
    ]
    assert views[1].status is WorkflowStatus.WAITING_FOR_HUMAN
    assert views[1].artifact_links == []


def test_build_brief_qa_stage_view_exposes_actionable_failed_fields() -> None:
    report = QAReport(
        job_id="job-123",
        stage=WorkflowStage.BRIEF_DRAFTED,
        passed=False,
        checks=[
            ValidationCheck(
                name="brief_main_keyword",
                passed=False,
                severity="error",
                message="Main keyword is missing.",
                metadata={"field": "main_keyword"},
            ),
            ValidationCheck(
                name="brief_audience",
                passed=False,
                severity="error",
                message="Audience is unclear.",
                metadata={"field": "audience"},
            ),
        ],
        summary="Brief QA failed.",
    )

    view = build_brief_qa_stage_view(report)

    assert view.status is WorkflowStatus.NEEDS_REVISION
    assert view.artifact_links == [ArtifactKey.BRIEF, ArtifactKey.BRIEF_QA]
    assert view.available_actions == ["Regenerate SEO brief"]
    assert view.blocking_reason == "Fix these fields before writing: main_keyword, audience."


def test_build_brief_qa_stage_view_exposes_manual_gate_actions_on_pass() -> None:
    report = QAReport(
        job_id="job-123",
        stage=WorkflowStage.BRIEF_DRAFTED,
        passed=True,
        checks=[
            ValidationCheck(
                name="brief_main_keyword",
                passed=True,
                severity="info",
                message="Main keyword is present.",
                metadata={"field": "main_keyword"},
            )
        ],
        summary="Brief QA passed.",
    )

    view = build_brief_qa_stage_view(report)

    assert view.status is WorkflowStatus.WAITING_FOR_HUMAN
    assert view.artifact_links == [ArtifactKey.BRIEF, ArtifactKey.BRIEF_QA]
    assert view.available_actions == ["Approve brief", "Request revision"]
    assert view.blocking_reason is None
