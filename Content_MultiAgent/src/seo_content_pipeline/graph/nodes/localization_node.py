"""Localization graph nodes."""

from seo_content_pipeline.services.localization_service import LocalizationResult, LocalizationService


def generate_spanish_localization_node(
    job_id: str,
    localization_service: LocalizationService,
    *,
    geo: str = "es-US",
) -> LocalizationResult:
    """Generate Spanish localization for a job."""
    return localization_service.generate_spanish_localization(job_id, geo=geo)
