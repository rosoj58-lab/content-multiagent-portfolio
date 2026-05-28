"""Workflow stage, status and UI-facing stage view contracts."""

from enum import Enum

from pydantic import BaseModel, Field

from seo_content_pipeline.models.artifacts import ArtifactKey


class WorkflowStage(str, Enum):
    """Pipeline locations a job can occupy."""

    INPUT_RECEIVED = "input_received"
    BRIEF_DRAFTED = "brief_drafted"
    BRIEF_APPROVED = "brief_approved"
    WRITING = "writing"
    EDITORIAL_REVIEW = "editorial_review"
    SEO_QA = "seo_qa"
    UNIQUENESS_CHECK = "uniqueness_check"
    LOCALIZATION = "localization"
    FINAL_QA = "final_qa"


class WorkflowStatus(str, Enum):
    """Execution and control outcomes for workflow stages."""

    RUNNING = "running"
    WAITING_FOR_HUMAN = "waiting_for_human"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    FAILED = "failed"


class StageView(BaseModel):
    """UI-ready status object for timelines, manual gates and failures."""

    stage: WorkflowStage
    status: WorkflowStatus
    label: str
    description: str
    artifact_links: list[ArtifactKey] = Field(default_factory=list)
    available_actions: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None
    recoverable: bool = True
    revision_attempt: int | None = None
    max_revision_attempts: int | None = None
    duration_label: str | None = None
