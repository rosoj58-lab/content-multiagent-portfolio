"""SEO validator tests."""

from seo_content_pipeline.models import ArticleType, QAReport, SEOBrief, SEOBriefArtifact
from seo_content_pipeline.validators.artifact_validators import validate_word_count
from seo_content_pipeline.validators.seo_validators import validate_seo_article


def _brief_artifact() -> SEOBriefArtifact:
    return SEOBriefArtifact(
        job_id="job-123",
        article_type=ArticleType.LP,
        brief=SEOBrief(
            topic="AI workflow for SEO content",
            goal="Show how a portfolio project automates content workflow.",
            audience="Technical hiring managers",
            main_keyword="multi-agent SEO content pipeline",
            secondary_keywords=["SEO automation"],
            lsi_keywords=["quality gates"],
            outline={
                "h1": "Multi-Agent SEO Content Pipeline",
                "sections": [{"h2": "SEO Automation Workflow", "h3": ["Quality Gates"]}],
            },
            tone_of_voice="Clear and technical",
            constraints=["Do not invent facts"],
        ),
    )


def _article() -> str:
    return (
        "# Multi-Agent SEO Content Pipeline\n\n"
        "## SEO Automation Workflow\n\n"
        "### Quality Gates\n\n"
        "A multi-agent SEO content pipeline helps technical hiring managers inspect "
        "SEO automation, quality gates, and content workflow decisions."
    )


def _article_validation_report() -> QAReport:
    return QAReport(
        job_id="job-123",
        stage="writing",
        passed=True,
        checks=validate_word_count(_article(), min_words=1, max_words=100),
        summary="Deterministic article validation passed.",
    )


def test_validate_seo_article_returns_required_checks_for_passing_article() -> None:
    checks = validate_seo_article(
        article=_article(),
        brief_artifact=_brief_artifact(),
        article_validation_report=_article_validation_report(),
    )

    assert {check.name for check in checks} == {
        "seo_main_keyword_usage",
        "seo_secondary_keyword_usage",
        "seo_lsi_keyword_coverage",
        "seo_heading_alignment",
        "seo_word_count_signal",
        "seo_intent_match",
        "seo_article_type_fit",
        "seo_keyword_stuffing_risk",
    }
    assert all(check.passed for check in checks)


def test_validate_seo_article_flags_keyword_lsi_and_heading_failures() -> None:
    checks = validate_seo_article(
        article="# Unrelated Title\n\n## Overview\n\n### Details\n\nNothing relevant here.",
        brief_artifact=_brief_artifact(),
        article_validation_report=_article_validation_report(),
    )
    failed = {check.name for check in checks if not check.passed}

    assert "seo_main_keyword_usage" in failed
    assert "seo_secondary_keyword_usage" in failed
    assert "seo_lsi_keyword_coverage" in failed
    assert "seo_heading_alignment" in failed
    assert "seo_intent_match" in failed


def test_validate_seo_article_flags_keyword_stuffing_risk() -> None:
    article = "# Multi-Agent SEO Content Pipeline\n\n## SEO Automation\n\n### Quality Gates\n\n"
    article += "multi-agent SEO content pipeline " * 15

    checks = validate_seo_article(
        article=article,
        brief_artifact=_brief_artifact(),
        article_validation_report=_article_validation_report(),
    )
    stuffing = next(check for check in checks if check.name == "seo_keyword_stuffing_risk")

    assert stuffing.passed is False
    assert stuffing.severity == "error"
