"""Brief validator tests."""

from seo_content_pipeline.validators.artifact_validators import validate_required_brief_fields


def _valid_brief() -> dict[str, object]:
    return {
        "topic": "AI workflow for SEO content",
        "goal": "Show how the portfolio project works.",
        "audience": "Technical hiring managers",
        "main_keyword": "multi-agent SEO content pipeline",
        "secondary_keywords": ["SEO automation"],
        "lsi_keywords": ["quality gates"],
        "outline": {
            "h1": "Multi-Agent SEO Content Pipeline",
            "sections": [
                {
                    "h2": "Brief generation",
                    "h3": ["Dry input", "Structured output"],
                }
            ],
        },
        "tone_of_voice": "Clear and technical",
        "constraints": ["Do not invent facts"],
    }


def test_validate_required_brief_fields_passes_complete_brief() -> None:
    checks = validate_required_brief_fields(_valid_brief())

    assert all(check.passed for check in checks)
    assert {check.metadata["field"] for check in checks} == {
        "main_keyword",
        "audience",
        "outline",
    }


def test_validate_required_brief_fields_fails_missing_main_keyword() -> None:
    brief = _valid_brief()
    brief["main_keyword"] = " "

    checks = validate_required_brief_fields(brief)

    failed = [check for check in checks if not check.passed]
    assert len(failed) == 1
    assert failed[0].metadata["field"] == "main_keyword"
    assert "Main keyword is missing" in failed[0].message


def test_validate_required_brief_fields_fails_unclear_audience() -> None:
    brief = _valid_brief()
    brief["audience"] = "everyone"

    checks = validate_required_brief_fields(brief)

    failed = [check for check in checks if not check.passed]
    assert len(failed) == 1
    assert failed[0].metadata["field"] == "audience"
    assert "Audience is unclear" in failed[0].message


def test_validate_required_brief_fields_fails_missing_outline() -> None:
    brief = _valid_brief()
    brief.pop("outline")

    checks = validate_required_brief_fields(brief)

    failed = [check for check in checks if not check.passed]
    assert len(failed) == 1
    assert failed[0].metadata["field"] == "outline"
    assert "Outline is missing" in failed[0].message


def test_validate_required_brief_fields_fails_incomplete_h3_outline() -> None:
    brief = _valid_brief()
    brief["outline"] = {
        "h1": "Multi-Agent SEO Content Pipeline",
        "sections": [{"h2": "Brief generation", "h3": []}],
    }

    checks = validate_required_brief_fields(brief)

    failed = [check for check in checks if not check.passed]
    assert len(failed) == 1
    assert failed[0].metadata["field"] == "outline"
    assert "without H3 items" in failed[0].message
