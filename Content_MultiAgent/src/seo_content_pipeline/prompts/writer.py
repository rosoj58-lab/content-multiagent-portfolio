"""Prompts for English original article generation."""

from typing import Literal

from seo_content_pipeline.models import SEOBrief


WritingMode = Literal["demo", "full"]


def build_writer_prompt(*, brief: SEOBrief, mode: WritingMode) -> str:
    """Build a prompt for generating the English Original article."""
    target_length = _target_length_instruction(mode)
    outline = _format_outline(brief)
    return (
        "You are the copywriter agent in an SEO content pipeline.\n"
        "Generate the English Original article in English US.\n"
        "Return Markdown only. Do not include commentary outside the article.\n"
        f"Target length: {target_length}\n\n"
        f"Topic: {brief.topic}\n"
        f"Goal: {brief.goal}\n"
        f"Audience: {brief.audience}\n"
        f"Main keyword: {brief.main_keyword}\n"
        f"Secondary keywords: {', '.join(brief.secondary_keywords)}\n"
        f"LSI keywords: {', '.join(brief.lsi_keywords)}\n"
        f"Tone of voice: {brief.tone_of_voice}\n"
        f"Constraints: {'; '.join(brief.constraints)}\n\n"
        "Use this exact H1/H2/H3 structure:\n"
        f"{outline}\n\n"
        "Use one H1 at the top, H2 sections for main parts, and H3 subsections where provided."
    )


def _target_length_instruction(mode: WritingMode) -> str:
    if mode == "full":
        return "1500-1600 words"
    return "500-700 words for a concise demo article"


def _format_outline(brief: SEOBrief) -> str:
    lines = [f"# {brief.outline.h1}"]
    for section in brief.outline.sections:
        lines.append(f"## {section.h2}")
        lines.extend(f"### {heading}" for heading in section.h3)
    return "\n".join(lines)
