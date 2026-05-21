"""Prompts for QA stages."""

from seo_content_pipeline.models import QAReport, SEOBrief


def build_editorial_qa_prompt(
    *,
    brief: SEOBrief,
    english_original: str,
    article_validation_summary: str,
) -> str:
    """Build the prompt for editorial QA of the English Original."""
    schema = QAReport.model_json_schema()
    return (
        "You are the Editorial QA agent in a multi-agent SEO content pipeline.\n"
        "Review the English Original against the approved SEO brief and deterministic checks.\n"
        "Return only valid JSON matching this QAReport schema:\n"
        f"{schema}\n\n"
        "Evaluate these areas:\n"
        "- brief compliance and intent fit\n"
        "- logical structure and readability\n"
        "- filler, repetition and vague claims\n"
        "- factual discipline\n\n"
        "Unsupported factual claims must be flagged unless they are generic and low-risk. "
        "Examples of claims that need support: statistics, market leadership, medical/legal/"
        "financial outcomes, precise performance numbers, named comparisons and guarantees. "
        "Generic low-risk claims may pass if they do not imply a specific unverifiable fact.\n\n"
        "If the article fails, include actionable recommendations and set routing_target to "
        '"writing" so targeted revision can happen without regenerating the whole workflow.\n\n'
        f"Brief topic: {brief.topic}\n"
        f"Brief goal: {brief.goal}\n"
        f"Brief audience: {brief.audience}\n"
        f"Main keyword: {brief.main_keyword}\n"
        f"Tone of voice: {brief.tone_of_voice}\n"
        f"Constraints: {'; '.join(brief.constraints)}\n\n"
        f"Deterministic validation summary:\n{article_validation_summary}\n\n"
        f"English Original Markdown:\n{english_original}"
    )
