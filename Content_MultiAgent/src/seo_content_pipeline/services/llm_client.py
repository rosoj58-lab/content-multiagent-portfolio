"""LLM client contracts."""

from typing import Any, Protocol

from openai import OpenAI


class LLMClientProtocol(Protocol):
    """Minimal interface used by LLMRunner."""

    def generate(self, prompt: str) -> str:
        """Return raw model output for a prompt."""
        ...


class UnconfiguredLLMClient:
    """Default client that makes missing provider configuration explicit."""

    def generate(self, prompt: str) -> str:
        """Raise until a real provider adapter is configured."""
        raise RuntimeError("No LLM client is configured for this environment.")


class OpenAILLMClient:
    """Generate text through the OpenAI Responses API for explicit live actions."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        client: Any | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenAI live generation requires OPENAI_API_KEY.")
        if not model.strip():
            raise ValueError("OpenAI live generation requires a model name.")
        self.model = model
        self.client = client or OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        """Return model text without storing the response at the provider."""
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=1600,
                store=False,
            )
        except Exception as error:
            raise RuntimeError("OpenAI live generation failed.") from error
        output_text = getattr(response, "output_text", "")
        if not isinstance(output_text, str) or not output_text.strip():
            raise ValueError("OpenAI response did not include text output.")
        return output_text
