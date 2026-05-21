"""Manual uniqueness provider metadata."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import UniquenessProviderOption


class ManualUniquenessProvider:
    """Manual provider is always available and waits for operator input."""

    name = "manual"

    def get_option(self, settings: AppSettings) -> UniquenessProviderOption:
        """Return manual provider availability."""
        return UniquenessProviderOption(
            name=self.name,
            label="Manual score",
            available=True,
            configured=True,
            reason="Enter a score from an external plagiarism checker.",
            requires_manual_score=True,
        )
