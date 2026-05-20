"""Job metadata and lightweight state contracts."""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field

from seo_content_pipeline.models.artifacts import ArtifactKey
from seo_content_pipeline.models.errors import WorkflowError
from seo_content_pipeline.models.stage import WorkflowStage, WorkflowStatus


class ArticleType(str, Enum):
    """Supported article type shortcuts from the product workflow."""

    BP = "BP"
    LP = "LP"
    GP = "GP"


class StatusHistoryEntry(BaseModel):
    """One status transition for job observability."""

    stage: WorkflowStage
    status: WorkflowStatus
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class JobMetadata(BaseModel):
    """Persisted metadata for a content job."""

    job_id: str
    current_stage: WorkflowStage
    status: WorkflowStatus = WorkflowStatus.RUNNING
    article_type: ArticleType | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status_history: list[StatusHistoryEntry] = Field(default_factory=list)


class PipelineState(BaseModel):
    """Lightweight persisted workflow state; full content stays in artifacts."""

    job_id: str
    current_stage: WorkflowStage
    status: WorkflowStatus
    article_type: ArticleType | None = None
    artifact_paths: dict[ArtifactKey, str] = Field(default_factory=dict)
    status_history: list[StatusHistoryEntry] = Field(default_factory=list)
    revision_attempts: dict[WorkflowStage, int] = Field(default_factory=dict)
    qa_flags: dict[str, bool] = Field(default_factory=dict)
    errors: list[WorkflowError] = Field(default_factory=list)
    manual_gate_required: bool = False
