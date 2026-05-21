"""LLM runner tests."""

import json

import pytest

from seo_content_pipeline.models import SEOBrief
from seo_content_pipeline.services.llm_runner import LLMOutputParsingError, LLMRunner


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def _brief_json() -> str:
    return json.dumps(
        {
            "topic": "AI content pipeline",
            "goal": "Explain how the portfolio system creates SEO content.",
            "audience": "Hiring managers and technical interviewers",
            "main_keyword": "multi-agent SEO content system",
            "secondary_keywords": ["SEO automation", "content workflow"],
            "lsi_keywords": ["brief generation", "quality gates"],
            "outline": {
                "h1": "Multi-Agent SEO Content System",
                "sections": [
                    {
                        "h2": "How the system works",
                        "h3": ["Input intake", "Brief generation"],
                    }
                ],
            },
            "tone_of_voice": "Clear, practical and technical",
            "constraints": ["Avoid unsupported claims", "Keep examples concrete"],
        }
    )


def _repair_prompt(original_prompt: str, invalid_output: str, error_message: str) -> str:
    return f"{original_prompt}\nRepair this output: {invalid_output}\nError: {error_message}"


def test_llm_runner_parses_valid_json_without_repair() -> None:
    client = FakeLLMClient([_brief_json()])
    runner = LLMRunner(client)

    brief = runner.generate_structured(
        prompt="Create a brief.",
        model_type=SEOBrief,
        repair_prompt_builder=_repair_prompt,
    )

    assert brief.topic == "AI content pipeline"
    assert len(client.prompts) == 1


def test_llm_runner_repairs_once_after_parse_failure() -> None:
    client = FakeLLMClient(["not json", _brief_json()])
    runner = LLMRunner(client)

    brief = runner.generate_structured(
        prompt="Create a brief.",
        model_type=SEOBrief,
        repair_prompt_builder=_repair_prompt,
    )

    assert brief.main_keyword == "multi-agent SEO content system"
    assert len(client.prompts) == 2
    assert "Repair this output: not json" in client.prompts[1]


def test_llm_runner_raises_after_one_failed_repair_attempt() -> None:
    client = FakeLLMClient(["not json", "still not json"])
    runner = LLMRunner(client)

    with pytest.raises(LLMOutputParsingError) as exc_info:
        runner.generate_structured(
            prompt="Create a brief.",
            model_type=SEOBrief,
            repair_prompt_builder=_repair_prompt,
        )

    assert exc_info.value.attempts == 2
    assert len(client.prompts) == 2
