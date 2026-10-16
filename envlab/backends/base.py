"""Backend interface: anything that can (a) act as an agent inside a sandbox and (b) answer a one-shot prompt."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Completion:
    """Result of a single-shot (no tools) call: judges, generators, QA reviewers."""
    text: str
    structured: dict[str, Any] | None = None
    model: str = ""
    cost_usd: float = 0.0
    usage: dict[str, Any] = field(default_factory=dict)
    raw: Any = None


@dataclass
class AgentRun:
    """Result of an agentic run inside a sandbox directory."""
    final_text: str
    model: str = ""
    session_id: str = ""
    cost_usd: float = 0.0
    num_turns: int = 0
    usage: dict[str, Any] = field(default_factory=dict)
    transcript: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    raw: Any = None


class Backend:
    name = "base"

    def run_agent(
        self,
        *,
        prompt: str,
        cwd: Path,
        model: str,
        effort: str | None,
        system_prompt: str | None,
        tools: list[str],
        max_turns: int,
        max_budget_usd: float | None,
        timeout_s: int,
        extra: dict[str, Any],
    ) -> AgentRun:
        raise NotImplementedError

    def complete(
        self,
        *,
        prompt: str,
        model: str,
        effort: str | None,
        system_prompt: str | None,
        json_schema: dict[str, Any] | None,
        timeout_s: int,
        extra: dict[str, Any],
    ) -> Completion:
        raise NotImplementedError
