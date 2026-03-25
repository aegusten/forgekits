"""ForgeKits — Claude Code adapter.

Calls the local `claude` CLI as a subprocess, reusing the user's existing
Claude Code authentication. No API key required.

Limitations:
  - Cannot be used while a Claude Code session is already running
    (Claude Code blocks nested sessions via the CLAUDECODE env var).
  - Run forgekits from a regular terminal, not from inside Claude Code.
"""

from __future__ import annotations

import asyncio
import os
import shutil
from typing import Any

from forgekits.adapters.base import LLMAdapter, LLMMessage, LLMResponse

MODEL_MAP: dict[str, str] = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
}

MODEL_TIERS: dict[str, str] = {
    "haiku": "fast",
    "sonnet": "standard",
    "opus": "premium",
}


class ClaudeCodeAdapter(LLMAdapter):
    """Adapter that delegates to the local `claude` CLI.

    Uses the existing Claude Code OAuth session — no ANTHROPIC_API_KEY needed.
    Must be run from a terminal outside an active Claude Code session.
    """

    def __init__(self, model: str = "sonnet", **kwargs: Any) -> None:
        if not shutil.which("claude"):
            raise RuntimeError(
                "claude CLI not found on PATH. "
                "Install Claude Code: https://claude.ai/code"
            )

        if os.environ.get("CLAUDECODE"):
            raise RuntimeError(
                "Cannot run forgekits with the claudecode provider inside an active "
                "Claude Code session.\n"
                "Run forgekits from a regular terminal (PowerShell, cmd, bash)."
            )

        self._model_short = model
        self._model_id = MODEL_MAP.get(model, model)

    async def generate(
        self,
        messages: list[LLMMessage],
        system: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Build the prompt: system prefix + conversation
        parts: list[str] = []

        if system:
            parts.append(f"<system>\n{system}\n</system>\n")

        for msg in messages:
            if msg.role == "user":
                parts.append(msg.content)
            elif msg.role == "assistant":
                # Inject prior assistant turn as context
                parts.append(f"[assistant previously said]: {msg.content}")

        prompt = "\n\n".join(parts)

        cmd = [
            "claude",
            "--model", self._model_id,
            "--max-tokens", str(max_tokens),
            "-p", prompt,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                f"claude CLI exited with code {proc.returncode}: {error_msg}"
            )

        content = stdout.decode("utf-8", errors="replace").strip()

        return LLMResponse(
            content=content,
            model=self._model_id,
            # Token counts not available from CLI output
            input_tokens=0,
            output_tokens=0,
            raw={"returncode": proc.returncode},
        )

    def model_tier(self) -> str:
        return MODEL_TIERS.get(self._model_short, "standard")

    @property
    def provider_name(self) -> str:
        return "claudecode"
