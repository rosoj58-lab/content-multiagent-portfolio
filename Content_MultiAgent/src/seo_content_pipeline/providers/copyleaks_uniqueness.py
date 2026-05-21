"""Optional Copyleaks provider metadata.

This module intentionally does not import a Copyleaks SDK or make network calls.
"""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import UniquenessProviderOption


class CopyleaksUniquenessProvider:
    """Copyleaks provider is selectable only when credentials are configured."""

    name = "copyleaks"

    def get_option(self, settings: AppSettings) -> UniquenessProviderOption:
        """Return Copyleaks provider availability without contacting Copyleaks."""
        configured = bool(settings.copyleaks_email and settings.copyleaks_api_key)
        return UniquenessProviderOption(
            name=self.name,
            label="Copyleaks",
            available=configured,
            configured=configured,
            reason=(
                "Copyleaks credentials are configured."
                if configured
                else "Copyleaks credentials are missing; manual and mock providers remain available."
            ),
            requires_manual_score=False,
        )
