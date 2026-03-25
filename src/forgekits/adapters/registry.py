"""ForgeKits — adapter registry.

Central place to register and resolve LLM providers.
Community contributors: add your adapter here after creating the class.
"""

from __future__ import annotations

from typing import Any

from forgekits.adapters.base import LLMAdapter

# Registry of provider name -> adapter class
_ADAPTERS: dict[str, type[LLMAdapter]] = {}


def register_adapter(name: str, adapter_cls: type[LLMAdapter]) -> None:
    """Register a new LLM provider adapter."""
    _ADAPTERS[name] = adapter_cls


def get_adapter(provider: str, model: str, **kwargs: Any) -> LLMAdapter:
    """Resolve and instantiate an adapter by provider name."""
    if provider not in _ADAPTERS:
        available = ", ".join(_ADAPTERS.keys()) or "(none registered)"
        raise ValueError(
            f"Unknown provider '{provider}'. Available: {available}"
        )
    return _ADAPTERS[provider](model=model, **kwargs)


def resolve_provider(requested: str | None) -> str:
    """Return the provider to use, auto-detecting when not specified.

    Priority:
    1. Explicitly requested provider (--provider flag)
    2. ANTHROPIC_API_KEY in env → 'anthropic'
    3. Fallback → 'claudecode' (uses local claude CLI)
    """
    # Explicit provider always wins
    if requested is not None:
        return requested

    import os

    # Auto-detect: prefer anthropic if key is available, else use claudecode
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"

    return "claudecode"


def _register_defaults() -> None:
    """Register built-in adapters. Called at import time."""
    from forgekits.adapters.anthropic import AnthropicAdapter
    from forgekits.adapters.claudecode import ClaudeCodeAdapter

    register_adapter("anthropic", AnthropicAdapter)
    register_adapter("claudecode", ClaudeCodeAdapter)


# Auto-register defaults on import
_register_defaults()
