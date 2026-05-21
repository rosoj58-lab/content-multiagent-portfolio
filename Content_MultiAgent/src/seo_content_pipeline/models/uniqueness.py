"""Uniqueness provider and result contracts."""

from pydantic import BaseModel

from seo_content_pipeline.config import UniquenessProviderName


class UniquenessProviderOption(BaseModel):
    """UI and service-visible uniqueness provider availability."""

    name: UniquenessProviderName
    label: str
    available: bool
    configured: bool
    reason: str | None = None
    requires_manual_score: bool = False
