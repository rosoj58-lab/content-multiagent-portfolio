"""StageView builder tests."""

from datetime import UTC, datetime, timedelta

from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    PipelineState,
    QAReport,
    StageView,
    StatusHistoryEntry,
    ValidationCheck,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.stage_view_builder import (
    build_brief_manual_gate_stage_view,
    build_brief_qa_stage_view,
    build_initial_stage_views,
    build_pipeline_stage_views,
    build_uniqueness_gate_stage_view,
    build_uniqueness_provider_stage_view,
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


def test_build_brief_manual_gate_stage_view_exposes_gate_details() -> None:
    view = build_brief_manual_gate_stage_view(
        revision_attempt=1,
        max_revision_attempts=2,
    )

    assert view.status is WorkflowStatus.WAITING_FOR_HUMAN
    assert view.artifact_links == [ArtifactKey.BRIEF, ArtifactKey.BRIEF_QA]
    assert view.available_actions == ["Approve brief", "Request revision"]
    assert view.blocking_reason == "Brief QA passed. Human approval is required before writing."
    assert view.revision_attempt == 1
    assert view.max_revision_attempts == 2
    assert "enable writing" in view.description


def test_build_uniqueness_provider_stage_view_exposes_available_provider_actions() -> None:
    view = build_uniqueness_provider_stage_view(
        available_provider_names=["manual", "mock"],
        has_copyleaks_config=False,
    )

    assert view.stage is WorkflowStage.UNIQUENESS_CHECK
    assert view.status is WorkflowStatus.WAITING_FOR_HUMAN
    assert ArtifactKey.SEO_QA in view.artifact_links
    assert view.available_actions == ["Select manual provider", "Select mock provider"]
    assert view.blocking_reason == "Select a uniqueness provider before entering a score."


def test_build_uniqueness_gate_stage_view_shows_pass_details() -> None:
    view = build_uniqueness_gate_stage_view(
        score=90,
        source="manual",
        threshold=90,
        passed=True,
        routing_reason="Uniqueness score meets the 90 percent threshold.",
    )

    assert view.stage is WorkflowStage.UNIQUENESS_CHECK
    assert view.status is WorkflowStatus.RUNNING
    assert ArtifactKey.UNIQUENESS in view.artifact_links
    assert view.available_actions == ["Continue to localization"]
    assert "90" in view.description
    assert "manual" in view.description
    assert view.blocking_reason is None


def test_build_uniqueness_gate_stage_view_shows_revision_details() -> None:
    view = build_uniqueness_gate_stage_view(
        score=72.5,
        source="manual",
        threshold=90,
        passed=False,
        routing_reason="Uniqueness score is below 90; revise the English Original.",
    )

    assert view.status is WorkflowStatus.NEEDS_REVISION
    assert view.available_actions == ["Revise English Original"]
    assert view.blocking_reason == "Uniqueness score is below 90; revise the English Original."


def test_build_pipeline_stage_views_exposes_stage_duration_labels() -> None:
    base = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
    state = PipelineState(
        job_id="job-123",
        current_stage=WorkflowStage.WRITING,
        status=WorkflowStatus.RUNNING,
        artifact_paths={
            ArtifactKey.METADATA: "metadata.json",
            ArtifactKey.INPUT: "input.json",
            ArtifactKey.STATE: "state.json",
            ArtifactKey.BRIEF: "brief.json",
        },
        status_history=[
            StatusHistoryEntry(
                stage=WorkflowStage.INPUT_RECEIVED,
                status=WorkflowStatus.RUNNING,
                message="Input saved.",
                created_at=base,
            ),
            StatusHistoryEntry(
                stage=WorkflowStage.BRIEF_DRAFTED,
                status=WorkflowStatus.RUNNING,
                message="Brief started.",
                created_at=base + timedelta(seconds=3),
            ),
            StatusHistoryEntry(
                stage=WorkflowStage.WRITING,
                status=WorkflowStatus.RUNNING,
                message="Writing started.",
                created_at=base + timedelta(seconds=65),
            ),
        ],
    )

    views = build_pipeline_stage_views(state)

    durations = {view.stage: view.duration_label for view in views}
    assert durations[WorkflowStage.INPUT_RECEIVED] == "3s"
    assert durations[WorkflowStage.BRIEF_DRAFTED] == "1m 2s"
    assert durations[WorkflowStage.WRITING] is None
