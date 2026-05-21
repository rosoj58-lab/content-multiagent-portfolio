"""Article validator tests."""

from seo_content_pipeline.validators.artifact_validators import (
    validate_heading_structure,
    validate_required_artifacts,
    validate_word_count,
)


def _words(count: int) -> str:
    return " ".join(f"word{i}" for i in range(count))


def test_validate_word_count_returns_info_for_pass() -> None:
    checks = validate_word_count(_words(600), min_words=500, max_words=700)

    assert len(checks) == 1
    assert checks[0].passed is True
    assert checks[0].severity == "info"
    assert checks[0].metadata["word_count"] == 600


def test_validate_word_count_returns_warning_for_near_range() -> None:
    checks = validate_word_count(_words(450), min_words=500, max_words=700, warning_tolerance=75)

    assert len(checks) == 1
    assert checks[0].passed is True
    assert checks[0].severity == "warning"


def test_validate_word_count_returns_error_for_far_out_of_range() -> None:
    checks = validate_word_count(_words(300), min_words=500, max_words=700, warning_tolerance=75)

    assert len(checks) == 1
    assert checks[0].passed is False
    assert checks[0].severity == "error"


def test_validate_heading_structure_passes_required_markdown_headings() -> None:
    checks = validate_heading_structure("# H1\n\n## H2\n\n### H3\n\nBody.")

    assert checks[0].passed is True
    assert checks[0].severity == "info"
    assert checks[0].metadata == {"h1_count": 1, "h2_count": 1, "h3_count": 1}


def test_validate_heading_structure_errors_on_missing_h3() -> None:
    checks = validate_heading_structure("# H1\n\n## H2\n\nBody.")

    assert checks[0].passed is False
    assert checks[0].severity == "error"
    assert checks[0].metadata["h3_count"] == 0


def test_validate_required_artifacts_returns_list_of_validation_checks() -> None:
    checks = validate_required_artifacts({"english_original": False, "brief": True})

    assert [check.name for check in checks] == [
        "required_artifact_english_original",
        "required_artifact_brief",
    ]
    assert checks[0].passed is False
    assert checks[0].severity == "error"
    assert checks[1].passed is True
    assert checks[1].severity == "info"
