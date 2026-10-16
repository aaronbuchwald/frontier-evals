"""Backend using the Anthropic Python SDK directly (needs ANTHROPIC_API_KEY or an `ant auth login` profile).

The agent loop is a small manual tool loop with three sandbox tools (list_files, read_file,
write_file) so that document-workspace tasks can be attempted without the Claude Code harness.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import AgentRun, Backend, Completion

_TOOLS = [
    {"name": "list_files", "description": "List all files in the workspace (relative paths).",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}, "strict": True},
    {"name": "read_file", "description": "Read a file from the current working directory tree.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"],
                      "additionalProperties": False}, "strict": True},
    {"name": "write_file", "description": "Write (create or overwrite) a file relative to the current working directory.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                      "required": ["path", "content"], "additionalProperties": False}, "strict": True},
]


def _client():
    try:
        import anthropic  # noqa: WPS433
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("pip install anthropic  (or `pip install envlab[anthropic]`)") from e
    return anthropic.Anthropic()


def _safe(cwd: Path, rel: str) -> Path:
    p = (cwd / rel).resolve()
    if cwd.resolve() not in p.parents and p != cwd.resolve():
        raise ValueError("path escapes sandbox")
    return p


def _exec_tool(cwd: Path, name: str, inp: dict[str, Any], read_only_prefix: str | None) -> str:
    if name == "list_files":
        return "\n".join(str(p.relative_to(cwd)) for p in sorted(cwd.rglob("*")) if p.is_file())
    if name == "read_file":
        return _safe(cwd, inp["path"]).read_text(errors="replace")
    if name == "write_file":
        if read_only_prefix and inp["path"].startswith(read_only_prefix):
            return f"error: {read_only_prefix} is read-only"
        p = _safe(cwd, inp["path"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(inp["content"])
        return f"wrote {inp['path']} ({len(inp['content'])} chars)"
    return f"error: unknown tool {name}"


class AnthropicBackend(Backend):
    name = "anthropic"

    def _kwargs(self, model: str, effort: str | None) -> dict[str, Any]:
        kw: dict[str, Any] = {}
        if effort:
            kw["output_config"] = {"effort": effort}
        return kw

    def run_agent(self, *, prompt, cwd, model, effort, system_prompt, tools, max_turns,
                  max_budget_usd, timeout_s, extra) -> AgentRun:
        client = _client().with_options(timeout=float(timeout_s))
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        transcript: list[dict[str, Any]] = []
        usage_total = {"input_tokens": 0, "output_tokens": 0}
        final_text = ""
        read_only = "workspace/" if extra.get("workspace_read_only", True) else None
        for turn in range(max_turns):
            with client.messages.stream(model=model, max_tokens=64000, system=system_prompt or "",
                                        tools=_TOOLS, messages=messages, **self._kwargs(model, effort)) as stream:
                resp = stream.get_final_message()
            usage_total["input_tokens"] += resp.usage.input_tokens
            usage_total["output_tokens"] += resp.usage.output_tokens
            messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason == "refusal":
                return AgentRun(final_text="", model=model, error="refusal", transcript=transcript, usage=usage_total)
            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            texts = [b.text for b in resp.content if b.type == "text"]
            if texts:
                final_text = "\n".join(texts)
            transcript.append({"turn": turn, "text": final_text, "tools": [t.name for t in tool_uses]})
            if not tool_uses:
                break
            results = []
            for tu in tool_uses:
                try:
                    out = _exec_tool(cwd, tu.name, dict(tu.input), read_only)
                    results.append({"type": "tool_result", "tool_use_id": tu.id, "content": out})
                except Exception as e:  # noqa: BLE001
                    results.append({"type": "tool_result", "tool_use_id": tu.id, "content": str(e), "is_error": True})
            messages.append({"role": "user", "content": results})
        return AgentRun(final_text=final_text, model=model, num_turns=turn + 1, usage=usage_total, transcript=transcript)

    def complete(self, *, prompt, model, effort, system_prompt, json_schema, timeout_s, extra) -> Completion:
        client = _client().with_options(timeout=float(timeout_s))
        kw = self._kwargs(model, effort)
        if json_schema:
            kw["output_config"] = {**kw.get("output_config", {}), "format": {"type": "json_schema", "schema": json_schema}}
        with client.messages.stream(model=model, max_tokens=32000, system=system_prompt or "",
                                    messages=[{"role": "user", "content": prompt}], **kw) as stream:
            resp = stream.get_final_message()
        text = "\n".join(b.text for b in resp.content if b.type == "text")
        structured = None
        if json_schema:
            try:
                structured = json.loads(text)
            except json.JSONDecodeError:
                structured = None
        return Completion(text=text, structured=structured, model=model,
                          usage={"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}, raw=resp)
