"""Run summary artifact contracts."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from seo_content_pipeline.models.artifacts import ArtifactKey
from seo_content_pipeline.models.stage import WorkflowStage, WorkflowStatus


class RunSummaryArtifactEntry(BaseModel):
    """One generated artifact included in a job-level run summary."""

    key: ArtifactKey
    label: str
    path: str
    content_type: str
    exists: bool


class StageDurationSummary(BaseModel):
    """Derived elapsed time for a workflow stage."""

    stage: WorkflowStage
    elapsed_seconds: float
    transition_count: int


class RunSummaryArtifact(BaseModel):
    """Derived, exportable summary of one content job run."""

    job_id: str
    article_type: str | None = None
    status: WorkflowStatus
    current_stage: WorkflowStage
    decision_artifact: str | None = None
    decision_artifact_key: ArtifactKey | None = None
    generated_artifacts: list[RunSummaryArtifactEntry]
    generated_artifact_count: int
    artifact_counts: dict[str, int]
    stage_durations: list[StageDurationSummary] = Field(default_factory=list)
    total_duration_seconds: float = 0
    final_package_path: str | None = None
    final_qa_report_path: str | None = None
    manual_gate_required: bool
    revision_attempts: dict[WorkflowStage, int] = Field(default_factory=dict)
    revision_notes: dict[WorkflowStage, list[str]] = Field(default_factory=dict)
    qa_flags: dict[str, bool] = Field(default_factory=dict)
    uniqueness_score: float | None = None
    uniqueness_threshold: float | None = None
    uniqueness_source: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
