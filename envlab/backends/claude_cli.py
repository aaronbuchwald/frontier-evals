"""Backend that drives the local `claude` CLI in headless (`-p`) mode.

Every call starts a brand-new session (fresh UUID, no persistence, scrubbed
session environment) so that re-runs after an edit are genuinely fresh.
Tools are restricted to the sandbox: no Bash, no web access, unless the agent
config asks for them explicitly.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from .base import AgentRun, Backend, Completion

# Env vars that would tie a child run to *this* session or alter its behaviour.
_SCRUB_ENV = (
    "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_AFTER_LAST_COMPACT",
    "CLAUDE_EFFORT", "MAX_THINKING_TOKENS", "CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD",
)
_NETWORK_TOOLS = ["WebSearch", "WebFetch"]
_SHELL_TOOLS = ["Bash", "PowerShell", "Agent", "Task"]


def _clean_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in _SCRUB_ENV}
    env["CLAUDECODE"] = ""  # allow nesting from inside an interactive claude session
    return env


def _binary() -> str:
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError("`claude` CLI not found on PATH; install Claude Code or pick another backend")
    return exe


def _parse_json_output(stdout: str) -> dict[str, Any]:
    stdout = stdout.strip()
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        # The CLI may print non-JSON warnings first; take the last JSON object.
        start = stdout.rfind("\n{")
        if start >= 0:
            return json.loads(stdout[start + 1:])
        raise


class ClaudeCliBackend(Backend):
    name = "claude-cli"

    def _base_cmd(self, model: str, effort: str | None, system_prompt: str | None,
                  max_budget_usd: float | None) -> list[str]:
        cmd = [_binary(), "-p", "--output-format", "json", "--no-session-persistence",
               "--session-id", str(uuid.uuid4()), "--model", model]
        if effort:
            cmd += ["--effort", effort]
        if system_prompt:
            cmd += ["--system-prompt", system_prompt]
        if max_budget_usd:
            cmd += ["--max-budget-usd", str(max_budget_usd)]
        return cmd

    def run_agent(self, *, prompt, cwd, model, effort, system_prompt, tools, max_turns,
                  max_budget_usd, timeout_s, extra) -> AgentRun:
        cmd = self._base_cmd(model, effort, system_prompt, max_budget_usd)
        cmd += ["--permission-mode", extra.get("permission_mode", "acceptEdits")]
        if tools:
            cmd += ["--tools", *tools]
        disallowed = list(extra.get("disallowed_tools", []))
        if not extra.get("allow_network"):
            disallowed += _NETWORK_TOOLS
        if not extra.get("allow_shell"):
            disallowed += _SHELL_TOOLS
        if disallowed:
            cmd += ["--disallowedTools", *sorted(set(disallowed))]
        # Prompt goes over stdin: the variadic --tools/--disallowedTools flags would swallow a trailing argument.
        try:
            proc = subprocess.run(cmd, cwd=str(cwd), env=_clean_env(), capture_output=True,
                                  text=True, timeout=timeout_s, input=prompt)
        except subprocess.TimeoutExpired as e:
            return AgentRun(final_text="", model=model, error=f"timeout after {timeout_s}s", raw=str(e))
        if proc.returncode != 0 and not proc.stdout.strip():
            return AgentRun(final_text="", model=model, error=f"claude exited {proc.returncode}: {proc.stderr[-2000:]}")
        try:
            data = _parse_json_output(proc.stdout)
        except Exception as e:  # noqa: BLE001
            return AgentRun(final_text=proc.stdout, model=model, error=f"unparseable CLI output: {e}; stderr={proc.stderr[-1000:]}")
        err = None
        if data.get("is_error") or data.get("subtype") not in (None, "success"):
            err = f"subtype={data.get('subtype')} result={str(data.get('result'))[:500]}"
        return AgentRun(
            final_text=str(data.get("result") or ""),
            model=model,
            session_id=data.get("session_id", ""),
            cost_usd=float(data.get("total_cost_usd") or 0.0),
            num_turns=int(data.get("num_turns") or 0),
            usage=data.get("usage") or {},
            error=err,
            raw={k: v for k, v in data.items() if k not in ("result",)},
        )

    def complete(self, *, prompt, model, effort, system_prompt, json_schema, timeout_s, extra) -> Completion:
        cmd = self._base_cmd(model, effort, system_prompt, extra.get("max_budget_usd"))
        cmd += ["--tools", "", "--permission-mode", "dontAsk"]
        if json_schema:
            cmd += ["--json-schema", json.dumps(json_schema)]
        proc = subprocess.run(cmd, env=_clean_env(), capture_output=True, text=True, timeout=timeout_s,
                              cwd=extra.get("cwd") or None, input=prompt)
        if not proc.stdout.strip():
            raise RuntimeError(f"claude CLI produced no output (rc={proc.returncode}): {proc.stderr[-2000:]}")
        data = _parse_json_output(proc.stdout)
        if data.get("is_error"):
            raise RuntimeError(f"claude CLI error: {str(data.get('result'))[:1000]}")
        structured = data.get("structured_output")
        text = str(data.get("result") or "")
        if json_schema and structured is None:
            try:
                structured = json.loads(text)
            except json.JSONDecodeError:
                structured = None
        return Completion(text=text, structured=structured, model=model,
                          cost_usd=float(data.get("total_cost_usd") or 0.0),
                          usage=data.get("usage") or {}, raw=data)
