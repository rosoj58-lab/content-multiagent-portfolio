"""StageView builder tests."""

from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    StageView,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.stage_view_builder import build_initial_stage_views


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
