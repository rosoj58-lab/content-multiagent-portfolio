"""Uniqueness provider interface."""

from typing import Protocol

from seo_content_pipeline.config import AppSettings, UniquenessProviderName
from seo_content_pipeline.models import UniquenessProviderOption


class UniquenessProvider(Protocol):
    """Provider metadata interface used before uniqueness score collection."""

    name: UniquenessProviderName

    def get_option(self, settings: AppSettings) -> UniquenessProviderOption:
        """Return current availability for this provider."""
        ...
