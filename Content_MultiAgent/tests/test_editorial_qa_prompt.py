"""Editorial QA prompt tests."""

from seo_content_pipeline.models import SEOBrief
from seo_content_pipeline.prompts.qa_prompt import build_editorial_qa_prompt


def _brief() -> SEOBrief:
    return SEOBrief(
        topic="AI workflow for SEO content",
        goal="Show how the portfolio project works.",
        audience="Technical hiring managers",
        main_keyword="multi-agent SEO content pipeline",
        secondary_keywords=["SEO automation"],
        lsi_keywords=["quality gates"],
        outline={
            "h1": "Multi-Agent SEO Content Pipeline",
            "sections": [{"h2": "Brief generation", "h3": ["Dry input"]}],
        },
        tone_of_voice="Clear and technical",
        constraints=["Do not invent facts"],
    )


def test_editorial_qa_prompt_requires_factual_discipline_and_schema() -> None:
    prompt = build_editorial_qa_prompt(
        brief=_brief(),
        english_original="# Article\n\nBody.",
        article_validation_summary="Deterministic article validation passed.",
    )

    assert "QAReport schema" in prompt
    assert "Unsupported factual claims must be flagged" in prompt
    assert "generic and low-risk" in prompt
    assert '"writing"' in prompt
    assert "requires_human_review true" in prompt
    assert "sensitive native link placement" in prompt
    assert "Deterministic validation summary" in prompt
