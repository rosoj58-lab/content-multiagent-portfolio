"""Mock uniqueness provider metadata."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import UniquenessProviderOption


class MockUniquenessProvider:
    """Mock provider is available for deterministic demos and tests."""

    name = "mock"

    def get_option(self, settings: AppSettings) -> UniquenessProviderOption:
        """Return mock provider availability."""
        return UniquenessProviderOption(
            name=self.name,
            label="Mock demo score",
            available=True,
            configured=True,
            reason="Use deterministic demo behavior without external credentials.",
            requires_manual_score=False,
        )
