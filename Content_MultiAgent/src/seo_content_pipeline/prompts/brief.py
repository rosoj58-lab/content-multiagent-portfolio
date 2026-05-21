"""Prompts for SEO brief generation."""

from seo_content_pipeline.models import ArticleType, SEOBrief


def build_brief_prompt(*, dry_input: str, article_type: ArticleType) -> str:
    """Build the prompt for generating a structured SEO brief."""
    schema = SEOBrief.model_json_schema()
    return (
        "You are an SEO brief agent for a content production pipeline.\n"
        "Create a complete SEO brief from the dry input and article type.\n"
        "Return only valid JSON that matches this schema:\n"
        f"{schema}\n\n"
        f"Article type: {article_type.value}\n"
        f"Dry input:\n{dry_input}\n\n"
        "The brief must include topic, goal, audience, main_keyword, "
        "secondary_keywords, lsi_keywords, an H1/H2/H3 outline, tone_of_voice, "
        "and constraints."
    )


def build_brief_repair_prompt(
    original_prompt: str,
    invalid_output: str,
    error_message: str,
) -> str:
    """Build one repair prompt for invalid structured brief output."""
    return (
        "The previous response did not parse as the required SEOBrief JSON.\n"
        "Repair it and return only valid JSON. Do not add markdown or commentary.\n\n"
        f"Parse error:\n{error_message}\n\n"
        f"Invalid output:\n{invalid_output}\n\n"
        f"Original task:\n{original_prompt}"
    )
