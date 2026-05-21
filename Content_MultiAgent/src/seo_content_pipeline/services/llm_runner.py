"""Structured LLM execution helpers."""

from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from seo_content_pipeline.services.llm_client import LLMClientProtocol, UnconfiguredLLMClient


ModelT = TypeVar("ModelT", bound=BaseModel)
RepairPromptBuilder = Callable[[str, str, str], str]


class LLMOutputParsingError(Exception):
    """Raised when raw LLM output cannot be parsed after one repair attempt."""

    def __init__(self, message: str, *, attempts: int, last_error: str) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


class LLMRunner:
    """Runs LLM calls and parses raw responses into Pydantic contracts."""

    def __init__(self, client: LLMClientProtocol | None = None) -> None:
        self.client = client or UnconfiguredLLMClient()

    def generate_structured(
        self,
        *,
        prompt: str,
        model_type: type[ModelT],
        repair_prompt_builder: RepairPromptBuilder,
    ) -> ModelT:
        """Generate and parse a structured model, with exactly one repair attempt."""
        raw_output = self.client.generate(prompt)
        try:
            return self._parse(raw_output, model_type)
        except ValidationError as first_error:
            repair_prompt = repair_prompt_builder(prompt, raw_output, str(first_error))

        repaired_output = self.client.generate(repair_prompt)
        try:
            return self._parse(repaired_output, model_type)
        except ValidationError as second_error:
            raise LLMOutputParsingError(
                "LLM output could not be parsed after one repair attempt.",
                attempts=2,
                last_error=str(second_error),
            ) from second_error

    @staticmethod
    def _parse(raw_output: str, model_type: type[ModelT]) -> ModelT:
        return model_type.model_validate_json(raw_output)
