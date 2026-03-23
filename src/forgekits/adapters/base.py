"""ForgeKits — abstract LLM adapter.

Every provider (Anthropic, OpenAI, Ollama, etc.) implements this interface.
The orchestrator never talks to a provider directly — only through this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMMessage:
    """A single message in a conversation."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Standardized response from any provider."""

    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    raw: dict[str, Any] = field(default_factory=dict)


class LLMAdapter(ABC):
    """Abstract interface for LLM providers.

    To add a new provider:
    1. Create a new file in adapters/ (e.g. openai.py)
    2. Subclass LLMAdapter
    3. Register it in adapters/registry.py
    """

    @abstractmethod
    def __init__(self, model: str, **kwargs: Any) -> None:
        """Initialize with a model name and provider-specific config."""
        ...

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        system: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Send messages to the LLM and get a response."""
        ...

    @abstractmethod
    def model_tier(self) -> str:
        """Return the tier of the current model: 'fast', 'standard', 'premium'.

        Used by the router to decide if a model switch is needed.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier (e.g. 'anthropic', 'openai')."""
        ...
