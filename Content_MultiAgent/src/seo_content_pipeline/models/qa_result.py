"""QA report contracts."""

from pydantic import BaseModel, Field

from seo_content_pipeline.models.stage import WorkflowStage
from seo_content_pipeline.models.validation import ValidationCheck


class QAReport(BaseModel):
    """Structured report produced by QA and validation stages."""

    job_id: str
    stage: WorkflowStage
    passed: bool
    checks: list[ValidationCheck]
    summary: str
    score: float | None = None
    recommendations: list[str] = Field(default_factory=list)
    routing_target: WorkflowStage | None = None
