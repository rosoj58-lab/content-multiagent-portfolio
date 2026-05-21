"""LLM client contracts."""

from typing import Protocol


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
