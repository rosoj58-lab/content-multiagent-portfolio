"""Deterministic SEO validators."""

import re

from seo_content_pipeline.models import QAReport, SEOBriefArtifact, ValidationCheck


def validate_seo_article(
    *,
    article: str,
    brief_artifact: SEOBriefArtifact,
    article_validation_report: QAReport,
) -> list[ValidationCheck]:
    """Validate SEO signals in the English Original."""
    brief = brief_artifact.brief
    return [
        _validate_main_keyword(article, brief.main_keyword),
        _validate_secondary_keywords(article, brief.secondary_keywords),
        _validate_lsi_keywords(article, brief.lsi_keywords),
        _validate_heading_alignment(article, brief.main_keyword, brief.topic),
        _validate_word_count_signal(article_validation_report),
        _validate_intent_match(article, brief.topic, brief.goal, brief.main_keyword),
        _validate_article_type_fit(brief_artifact),
        _validate_keyword_stuffing(article, brief.main_keyword),
    ]


def _validate_main_keyword(article: str, main_keyword: str) -> ValidationCheck:
    count = _phrase_count(article, main_keyword)
    passed = count > 0
    return ValidationCheck(
        name="seo_main_keyword_usage",
        passed=passed,
        severity="info" if passed else "error",
        message=(
            f"Main keyword appears {count} time(s)."
            if passed
            else "Main keyword is missing from the article."
        ),
        metadata={"keyword": main_keyword, "count": count},
    )


def _validate_secondary_keywords(article: str, keywords: list[str]) -> ValidationCheck:
    matched = [keyword for keyword in keywords if _phrase_count(article, keyword) > 0]
    passed = bool(matched)
    return ValidationCheck(
        name="seo_secondary_keyword_usage",
        passed=passed,
        severity="info" if passed else "error",
        message=(
            f"Secondary keyword coverage found: {', '.join(matched)}."
            if passed
            else "No secondary keywords are present in the article."
        ),
        metadata={"matched": matched, "expected": keywords},
    )


def _validate_lsi_keywords(article: str, keywords: list[str]) -> ValidationCheck:
    matched = [keyword for keyword in keywords if _phrase_count(article, keyword) > 0]
    passed = bool(matched)
    return ValidationCheck(
        name="seo_lsi_keyword_coverage",
        passed=passed,
        severity="info" if passed else "error",
        message=(
            f"LSI keyword coverage found: {', '.join(matched)}."
            if passed
            else "No LSI keywords are present in the article."
        ),
        metadata={"matched": matched, "expected": keywords},
    )


def _validate_heading_alignment(article: str, main_keyword: str, topic: str) -> ValidationCheck:
    headings = "\n".join(re.findall(r"^#{1,3}\s+(.+)$", article, flags=re.MULTILINE))
    aligned = _phrase_count(headings, main_keyword) > 0 or _any_topic_word_present(headings, topic)
    return ValidationCheck(
        name="seo_heading_alignment",
        passed=aligned,
        severity="info" if aligned else "error",
        message=(
            "Headings align with the main keyword or topic."
            if aligned
            else "Headings do not include the main keyword or topic language."
        ),
        metadata={"main_keyword": main_keyword, "topic": topic},
    )


def _validate_word_count_signal(article_validation_report: QAReport) -> ValidationCheck:
    word_count_check = next(
        (check for check in article_validation_report.checks if check.name == "article_word_count"),
        None,
    )
    if word_count_check is None:
        return ValidationCheck(
            name="seo_word_count_signal",
            passed=False,
            severity="error",
            message="Article word count validation is missing.",
            metadata={},
        )
    return ValidationCheck(
        name="seo_word_count_signal",
        passed=word_count_check.passed,
        severity=word_count_check.severity,
        message=f"SEO QA reused word-count signal: {word_count_check.message}",
        metadata=word_count_check.metadata,
    )


def _validate_intent_match(article: str, topic: str, goal: str, main_keyword: str) -> ValidationCheck:
    topic_hit = _any_topic_word_present(article, topic)
    goal_hit = _any_topic_word_present(article, goal)
    keyword_hit = _phrase_count(article, main_keyword) > 0
    passed = keyword_hit and (topic_hit or goal_hit)
    return ValidationCheck(
        name="seo_intent_match",
        passed=passed,
        severity="info" if passed else "error",
        message=(
            "Article appears aligned with keyword and brief intent."
            if passed
            else "Article does not clearly match keyword and brief intent."
        ),
        metadata={"topic_hit": topic_hit, "goal_hit": goal_hit, "keyword_hit": keyword_hit},
    )


def _validate_article_type_fit(brief_artifact: SEOBriefArtifact) -> ValidationCheck:
    return ValidationCheck(
        name="seo_article_type_fit",
        passed=True,
        severity="info",
        message=f"Article type context is available: {brief_artifact.article_type.value}.",
        metadata={"article_type": brief_artifact.article_type.value},
    )


def _validate_keyword_stuffing(article: str, main_keyword: str) -> ValidationCheck:
    word_count = len(_words(article))
    count = _phrase_count(article, main_keyword)
    density = count / word_count if word_count else 0.0
    if count >= 3 and density > 0.05:
        return ValidationCheck(
            name="seo_keyword_stuffing_risk",
            passed=False,
            severity="error",
            message="Main keyword density is too high and may look over-optimized.",
            metadata={"count": count, "word_count": word_count, "density": density},
        )
    if count >= 2 and density > 0.03:
        return ValidationCheck(
            name="seo_keyword_stuffing_risk",
            passed=True,
            severity="warning",
            message="Main keyword density is elevated; keep usage natural.",
            metadata={"count": count, "word_count": word_count, "density": density},
        )
    return ValidationCheck(
        name="seo_keyword_stuffing_risk",
        passed=True,
        severity="info",
        message="Main keyword density is within a natural range.",
        metadata={"count": count, "word_count": word_count, "density": density},
    )


def _phrase_count(text: str, phrase: str) -> int:
    normalized_phrase = phrase.strip()
    if not normalized_phrase:
        return 0
    return len(re.findall(rf"\b{re.escape(normalized_phrase)}\b", text, flags=re.IGNORECASE))


def _any_topic_word_present(text: str, value: str) -> bool:
    words = [word for word in _words(value) if len(word) >= 4]
    text_words = set(_words(text))
    return any(word in text_words for word in words)


def _words(text: str) -> list[str]:
    return [word.lower() for word in re.findall(r"\b[\w'-]+\b", text)]
