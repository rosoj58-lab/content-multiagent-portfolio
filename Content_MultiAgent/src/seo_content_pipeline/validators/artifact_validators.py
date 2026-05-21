"""Deterministic artifact validators."""

from collections.abc import Mapping
from typing import Any

from seo_content_pipeline.models import SEOBrief, ValidationCheck


GENERIC_AUDIENCES = {
    "all",
    "anyone",
    "everyone",
    "general",
    "general audience",
    "people",
    "users",
}


def validate_required_brief_fields(brief: SEOBrief | Mapping[str, Any]) -> list[ValidationCheck]:
    """Validate that a brief has enough structure for article generation."""
    brief_data = _brief_to_mapping(brief)
    return [
        _validate_main_keyword(brief_data.get("main_keyword")),
        _validate_audience(brief_data.get("audience")),
        _validate_outline(brief_data.get("outline")),
    ]


def _validate_main_keyword(value: object) -> ValidationCheck:
    if _blank(value):
        return _failed_check(
            name="brief_main_keyword",
            field="main_keyword",
            message="Main keyword is missing. Add one primary SEO keyword before writing.",
        )
    return ValidationCheck(
        name="brief_main_keyword",
        passed=True,
        severity="info",
        message="Main keyword is present.",
        metadata={"field": "main_keyword"},
    )


def _validate_audience(value: object) -> ValidationCheck:
    if _blank(value):
        return _failed_check(
            name="brief_audience",
            field="audience",
            message="Audience is missing. Define the reader segment before writing.",
        )

    audience = str(value).strip()
    if audience.lower() in GENERIC_AUDIENCES or len(audience.split()) < 2:
        return _failed_check(
            name="brief_audience",
            field="audience",
            message="Audience is unclear. Replace it with a specific reader segment.",
        )

    return ValidationCheck(
        name="brief_audience",
        passed=True,
        severity="info",
        message="Audience is specific enough for article generation.",
        metadata={"field": "audience"},
    )


def _validate_outline(value: object) -> ValidationCheck:
    outline = _as_mapping(value)
    if outline is None:
        return _failed_check(
            name="brief_outline",
            field="outline",
            message="Outline is missing. Add H1 plus H2 sections with H3 subsections.",
        )

    sections = outline.get("sections")
    has_valid_sections = isinstance(sections, list) and bool(sections)
    if _blank(outline.get("h1")) or not has_valid_sections:
        return _failed_check(
            name="brief_outline",
            field="outline",
            message="Outline is incomplete. Add H1 plus at least one H2 section with H3 items.",
        )

    for section in sections:
        section_data = _as_mapping(section)
        if section_data is None or _blank(section_data.get("h2")):
            return _failed_check(
                name="brief_outline",
                field="outline",
                message="Outline has an incomplete H2 section. Add clear H2 headings.",
            )
        h3_items = section_data.get("h3")
        has_h3 = isinstance(h3_items, list) and any(not _blank(item) for item in h3_items)
        if not has_h3:
            return _failed_check(
                name="brief_outline",
                field="outline",
                message="Outline has an H2 section without H3 items. Add supporting H3s.",
            )

    return ValidationCheck(
        name="brief_outline",
        passed=True,
        severity="info",
        message="Outline includes H1, H2 and H3 structure.",
        metadata={"field": "outline"},
    )


def _failed_check(*, name: str, field: str, message: str) -> ValidationCheck:
    return ValidationCheck(
        name=name,
        passed=False,
        severity="error",
        message=message,
        metadata={"field": field, "actionable": True},
    )


def _brief_to_mapping(brief: SEOBrief | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(brief, SEOBrief):
        return brief.model_dump(mode="python")
    return brief


def _as_mapping(value: object) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    return None


def _blank(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()
