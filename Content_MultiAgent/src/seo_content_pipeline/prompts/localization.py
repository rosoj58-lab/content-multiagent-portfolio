"""Prompts for localization generation."""

from seo_content_pipeline.models import SEOBrief


DEFAULT_SPANISH_GEO = "es-US"
DEFAULT_ITALIAN_GEO = "it-IT"
DEFAULT_FRENCH_GEO = "fr-FR"


def build_localization_prompt(
    *,
    brief: SEOBrief,
    english_original: str,
    language: str,
    geo: str = DEFAULT_SPANISH_GEO,
) -> str:
    """Build a prompt for a localized Markdown article."""
    return (
        f"You are the {language} localizer agent in an SEO content pipeline.\n"
        f"Localize the English Original into {language}.\n"
        f"{language} geo: {geo}.\n"
        "Return Markdown only. Do not include commentary outside the localized article.\n"
        "Preserve the Markdown heading hierarchy and the meaning of every section.\n"
        f"Preserve SEO intent, adapting wording naturally for the selected {language} geo.\n\n"
        f"Topic: {brief.topic}\n"
        f"Goal: {brief.goal}\n"
        f"Audience: {brief.audience}\n"
        f"Main keyword: {brief.main_keyword}\n"
        f"Secondary keywords: {', '.join(brief.secondary_keywords)}\n"
        f"LSI keywords: {', '.join(brief.lsi_keywords)}\n\n"
        "English Original:\n"
        f"{english_original}"
    )


def build_spanish_localization_prompt(
    *,
    brief: SEOBrief,
    english_original: str,
    geo: str = DEFAULT_SPANISH_GEO,
) -> str:
    """Build a prompt for Spanish localization."""
    return build_localization_prompt(
        brief=brief,
        english_original=english_original,
        language="Spanish",
        geo=geo,
    )


def build_italian_localization_prompt(
    *,
    brief: SEOBrief,
    english_original: str,
    geo: str = DEFAULT_ITALIAN_GEO,
) -> str:
    """Build a prompt for Italian localization."""
    return build_localization_prompt(
        brief=brief,
        english_original=english_original,
        language="Italian",
        geo=geo,
    )


def build_french_localization_prompt(
    *,
    brief: SEOBrief,
    english_original: str,
    geo: str = DEFAULT_FRENCH_GEO,
) -> str:
    """Build a prompt for French localization."""
    return build_localization_prompt(
        brief=brief,
        english_original=english_original,
        language="French",
        geo=geo,
    )
