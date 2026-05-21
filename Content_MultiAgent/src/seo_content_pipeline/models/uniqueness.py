"""Uniqueness provider and result contracts."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from seo_content_pipeline.config import UniquenessProviderName
from seo_content_pipeline.models.stage import WorkflowStage


class UniquenessProviderOption(BaseModel):
    """UI and service-visible uniqueness provider availability."""

    name: UniquenessProviderName
    label: str
    available: bool
    configured: bool
    reason: str | None = None
    requires_manual_score: bool = False


class UniquenessResult(BaseModel):
    """Persisted uniqueness-check result."""

    job_id: str
    stage: WorkflowStage = WorkflowStage.UNIQUENESS_CHECK
    score: float = Field(ge=0, le=100)
    source: UniquenessProviderName
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
