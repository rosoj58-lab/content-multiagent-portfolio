"""Job debug snapshot artifact contract."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from seo_content_pipeline.models.artifacts import ArtifactKey
from seo_content_pipeline.models.errors import WorkflowError
from seo_content_pipeline.models.stage import WorkflowStage, WorkflowStatus


class DebugSnapshotArtifact(BaseModel):
    """Derived diagnostic snapshot for inspecting one local job."""

    job_id: str
    article_type: str | None = None
    status: WorkflowStatus
    current_stage: WorkflowStage
    manual_gate_required: bool
    workflow_error_count: int
    errors: list[WorkflowError] = Field(default_factory=list)
    revision_attempts: dict[WorkflowStage, int] = Field(default_factory=dict)
    revision_notes: dict[WorkflowStage, list[str]] = Field(default_factory=dict)
    artifact_counts: dict[str, int]
    present_artifacts: list[ArtifactKey]
    missing_artifacts: list[ArtifactKey]
    critical_missing_artifacts: list[ArtifactKey] = Field(default_factory=list)
    key_paths: dict[ArtifactKey, str] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
