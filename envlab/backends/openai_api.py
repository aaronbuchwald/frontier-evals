"""Backend for OpenAI models (e.g. the GPT reference models named in a package spec).

Uses the Responses API with function tools for the sandbox. Needs OPENAI_API_KEY and
`pip install openai`. Untested in environments without that key; kept minimal on purpose.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .anthropic_api import _TOOLS, _exec_tool
from .base import AgentRun, Backend, Completion


def _client():
    try:
        from openai import OpenAI  # noqa: WPS433
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("pip install openai  (or `pip install envlab[openai]`)") from e
    return OpenAI()


def _oa_tools() -> list[dict[str, Any]]:
    return [{"type": "function", "name": t["name"], "description": t["description"],
             "parameters": t["input_schema"], "strict": True} for t in _TOOLS]


class OpenAIBackend(Backend):
    name = "openai"

    def run_agent(self, *, prompt, cwd, model, effort, system_prompt, tools, max_turns,
                  max_budget_usd, timeout_s, extra) -> AgentRun:
        client = _client()
        inputs: list[Any] = [{"role": "user", "content": prompt}]
        kw: dict[str, Any] = {"model": model, "tools": _oa_tools(), "instructions": system_prompt or None}
        if effort:
            kw["reasoning"] = {"effort": effort if effort in ("low", "medium", "high") else "high"}
        final_text = ""
        read_only = "workspace/" if extra.get("workspace_read_only", True) else None
        transcript: list[dict[str, Any]] = []
        for turn in range(max_turns):
            resp = client.responses.create(input=inputs, timeout=timeout_s, **kw)
            inputs += resp.output
            calls = [o for o in resp.output if getattr(o, "type", "") == "function_call"]
            if getattr(resp, "output_text", ""):
                final_text = resp.output_text
            transcript.append({"turn": turn, "tools": [c.name for c in calls]})
            if not calls:
                break
            for c in calls:
                out = _exec_tool(Path(cwd), c.name, json.loads(c.arguments), read_only)
                inputs.append({"type": "function_call_output", "call_id": c.call_id, "output": out})
        return AgentRun(final_text=final_text, model=model, num_turns=turn + 1, transcript=transcript)

    def complete(self, *, prompt, model, effort, system_prompt, json_schema, timeout_s, extra) -> Completion:
        client = _client()
        kw: dict[str, Any] = {"model": model, "instructions": system_prompt or None}
        if json_schema:
            kw["text"] = {"format": {"type": "json_schema", "name": "out", "schema": json_schema, "strict": False}}
        resp = client.responses.create(input=prompt, timeout=timeout_s, **kw)
        text = resp.output_text
        structured = json.loads(text) if json_schema else None
        return Completion(text=text, structured=structured, model=model, raw=resp)
