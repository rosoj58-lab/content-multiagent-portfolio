"""Workflow error contracts."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from seo_content_pipeline.models.stage import WorkflowStage


class WorkflowError(BaseModel):
    """Structured, persisted workflow error."""

    code: str
    message: str
    node: str
    stage: WorkflowStage
    recoverable: bool
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
