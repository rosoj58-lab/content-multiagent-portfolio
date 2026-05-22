"""Localization graph nodes."""

from seo_content_pipeline.prompts.localization import (
    DEFAULT_FRENCH_GEO,
    DEFAULT_ITALIAN_GEO,
    DEFAULT_SPANISH_GEO,
)
from seo_content_pipeline.services.localization_service import (
    LocalizationResult,
    LocalizationService,
    MultilingualLocalizationResult,
)


def generate_spanish_localization_node(
    job_id: str,
    localization_service: LocalizationService,
    *,
    geo: str = DEFAULT_SPANISH_GEO,
) -> LocalizationResult:
    """Generate Spanish localization for a job."""
    return localization_service.generate_spanish_localization(job_id, geo=geo)


def generate_italian_and_french_localizations_node(
    job_id: str,
    localization_service: LocalizationService,
    *,
    italian_geo: str = DEFAULT_ITALIAN_GEO,
    french_geo: str = DEFAULT_FRENCH_GEO,
) -> MultilingualLocalizationResult:
    """Generate Italian and French localizations for a job."""
    return localization_service.generate_italian_and_french_localizations(
        job_id,
        italian_geo=italian_geo,
        french_geo=french_geo,
    )
