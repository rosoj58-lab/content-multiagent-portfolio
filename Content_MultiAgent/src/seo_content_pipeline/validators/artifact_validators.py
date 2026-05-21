"""Deterministic artifact validators."""

from collections.abc import Mapping
import re
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


def validate_word_count(
    text: str,
    *,
    min_words: int,
    max_words: int,
    warning_tolerance: int = 100,
) -> list[ValidationCheck]:
    """Validate article word count against target and warning bands."""
    word_count = len(re.findall(r"\b[\w'-]+\b", text))
    metadata = {
        "word_count": word_count,
        "min_words": min_words,
        "max_words": max_words,
        "warning_tolerance": warning_tolerance,
    }
    if min_words <= word_count <= max_words:
        return [
            ValidationCheck(
                name="article_word_count",
                passed=True,
                severity="info",
                message=f"Word count is within target range: {word_count}.",
                metadata=metadata,
            )
        ]

    warning_min = max(0, min_words - warning_tolerance)
    warning_max = max_words + warning_tolerance
    if warning_min <= word_count <= warning_max:
        return [
            ValidationCheck(
                name="article_word_count",
                passed=True,
                severity="warning",
                message=f"Word count is near target range: {word_count}.",
                metadata=metadata,
            )
        ]

    return [
        ValidationCheck(
            name="article_word_count",
            passed=False,
            severity="error",
            message=f"Word count is outside target range: {word_count}.",
            metadata=metadata,
        )
    ]


def validate_heading_structure(text: str) -> list[ValidationCheck]:
    """Validate basic Markdown H1/H2/H3 structure."""
    h1_count = len(re.findall(r"^# (?!#).+", text, flags=re.MULTILINE))
    h2_count = len(re.findall(r"^## (?!#).+", text, flags=re.MULTILINE))
    h3_count = len(re.findall(r"^### (?!#).+", text, flags=re.MULTILINE))
    metadata = {"h1_count": h1_count, "h2_count": h2_count, "h3_count": h3_count}
    if h1_count == 1 and h2_count >= 1 and h3_count >= 1:
        return [
            ValidationCheck(
                name="article_heading_structure",
                passed=True,
                severity="info",
                message="Article includes one H1 plus H2 and H3 headings.",
                metadata=metadata,
            )
        ]

    return [
        ValidationCheck(
            name="article_heading_structure",
            passed=False,
            severity="error",
            message="Article must include exactly one H1, at least one H2 and at least one H3.",
            metadata=metadata,
        )
    ]


def validate_required_artifacts(artifact_availability: Mapping[str, bool]) -> list[ValidationCheck]:
    """Validate that required artifacts are available."""
    checks: list[ValidationCheck] = []
    for artifact_name, exists in artifact_availability.items():
        checks.append(
            ValidationCheck(
                name=f"required_artifact_{artifact_name}",
                passed=exists,
                severity="info" if exists else "error",
                message=(
                    f"Required artifact is available: {artifact_name}."
                    if exists
                    else f"Required artifact is missing: {artifact_name}."
                ),
                metadata={"artifact": artifact_name},
            )
        )
    return checks


def validate_uniqueness_score(score: object) -> list[ValidationCheck]:
    """Validate a manually entered uniqueness score."""
    valid_number = isinstance(score, int | float) and not isinstance(score, bool)
    valid_range = valid_number and 0 <= float(score) <= 100
    return [
        ValidationCheck(
            name="uniqueness_score_range",
            passed=valid_range,
            severity="info" if valid_range else "error",
            message=(
                f"Uniqueness score is within range: {float(score)}."
                if valid_range
                else "Uniqueness score must be a numeric value from 0 to 100."
            ),
            metadata={"score": float(score) if valid_number else None, "min": 0, "max": 100},
        )
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
