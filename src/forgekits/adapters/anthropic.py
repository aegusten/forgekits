"""ForgeKits — Anthropic (Claude) adapter."""

from __future__ import annotations

import os
from typing import Any

from anthropic import AsyncAnthropic

from forgekits.adapters.base import LLMAdapter, LLMMessage, LLMResponse

# Model ID mapping — short names to full IDs
MODEL_MAP: dict[str, str] = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
}

# Tier classification for the router
MODEL_TIERS: dict[str, str] = {
    "haiku": "fast",
    "sonnet": "standard",
    "opus": "premium",
}


class AnthropicAdapter(LLMAdapter):
    """Anthropic Claude adapter — ships as the default provider."""

    def __init__(self, model: str = "sonnet", **kwargs: Any) -> None:
        api_key = kwargs.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Set it as an environment variable or pass api_key= to the adapter."
            )

        self._model_short = model
        self._model_id = MODEL_MAP.get(model, model)  # allow full model IDs too
        self._client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        messages: list[LLMMessage],
        system: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Convert to Anthropic's message format
        api_messages = [{"role": m.role, "content": m.content} for m in messages]

        kwargs: dict[str, Any] = {
            "model": self._model_id,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["system"] = system

        response = await self._client.messages.create(**kwargs)

        return LLMResponse(
            content=response.content[0].text,
            model=self._model_id,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            raw={"id": response.id, "stop_reason": response.stop_reason},
        )

    def model_tier(self) -> str:
        return MODEL_TIERS.get(self._model_short, "standard")

    @property
    def provider_name(self) -> str:
        return "anthropic"
