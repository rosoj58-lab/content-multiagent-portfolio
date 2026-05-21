"""Prompts for localization generation."""

from seo_content_pipeline.models import SEOBrief


DEFAULT_SPANISH_GEO = "es-US"


def build_spanish_localization_prompt(
    *,
    brief: SEOBrief,
    english_original: str,
    geo: str = DEFAULT_SPANISH_GEO,
) -> str:
    """Build a prompt for Spanish localization."""
    return (
        "You are the Spanish localizer agent in an SEO content pipeline.\n"
        "Localize the English Original into Spanish.\n"
        f"Spanish geo: {geo}.\n"
        "Return Markdown only. Do not include commentary outside the localized article.\n"
        "Preserve the Markdown heading hierarchy and the meaning of every section.\n"
        "Preserve SEO intent, adapting wording naturally for the selected Spanish geo.\n\n"
        f"Topic: {brief.topic}\n"
        f"Goal: {brief.goal}\n"
        f"Audience: {brief.audience}\n"
        f"Main keyword: {brief.main_keyword}\n"
        f"Secondary keywords: {', '.join(brief.secondary_keywords)}\n"
        f"LSI keywords: {', '.join(brief.lsi_keywords)}\n\n"
        "English Original:\n"
        f"{english_original}"
    )
