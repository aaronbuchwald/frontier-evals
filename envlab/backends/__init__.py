from __future__ import annotations

from .base import AgentRun, Backend, Completion


def get_backend(name: str) -> Backend:
    if name == "claude-cli":
        from .claude_cli import ClaudeCliBackend
        return ClaudeCliBackend()
    if name == "anthropic":
        from .anthropic_api import AnthropicBackend
        return AnthropicBackend()
    if name == "openai":
        from .openai_api import OpenAIBackend
        return OpenAIBackend()
    if name == "mock":
        from .mock import MockBackend
        return MockBackend()
    raise ValueError(f"unknown backend {name!r}")


__all__ = ["AgentRun", "Backend", "Completion", "get_backend"]
