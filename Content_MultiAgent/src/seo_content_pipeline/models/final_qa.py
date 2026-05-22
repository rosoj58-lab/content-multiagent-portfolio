"""Final QA report contracts."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from seo_content_pipeline.models.artifacts import ArtifactKey
from seo_content_pipeline.models.stage import WorkflowStage, WorkflowStatus


class FinalQAFailedCheck(BaseModel):
    """One final QA finding that prevents approval."""

    name: str
    message: str
    routing_target: WorkflowStage


class FinalQAUniquenessResult(BaseModel):
    """Uniqueness status included in final QA."""

    score: float | None = None
    source: str | None = None
    threshold: float
    passed: bool


class FinalQALocalizationStatus(BaseModel):
    """Localization readiness for one language."""

    language: str
    artifact_key: ArtifactKey
    present: bool
    geo: str | None = None


class FinalQAReport(BaseModel):
    """Final QA report persisted before the workflow exits."""

    job_id: str
    status: WorkflowStatus
    completed_stages: list[WorkflowStage]
    failed_checks: list[FinalQAFailedCheck] = Field(default_factory=list)
    uniqueness_result: FinalQAUniquenessResult
    localization_status: dict[str, FinalQALocalizationStatus]
    routing_target: WorkflowStage | None = None
    routing_guidance: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
