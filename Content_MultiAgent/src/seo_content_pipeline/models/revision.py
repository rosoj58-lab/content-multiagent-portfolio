"""Targeted revision audit trail contracts."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from seo_content_pipeline.models.qa_result import QAReport
from seo_content_pipeline.models.stage import WorkflowStage, WorkflowStatus


class RevisionHistoryEntry(BaseModel):
    """One routed issue and its eventual resolution outcome."""

    attempt: int = Field(ge=1)
    source_stage: WorkflowStage
    initial_status: WorkflowStatus
    failed_report: QAReport
    action: str
    resolved_status: WorkflowStatus | None = None
    resolution_summary: str | None = None
    resolved_at: datetime | None = None


class RevisionHistoryArtifact(BaseModel):
    """Persisted audit trail for targeted revisions within one job."""

    job_id: str
    revisions: list[RevisionHistoryEntry] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
