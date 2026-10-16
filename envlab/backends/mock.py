"""Deterministic offline backend for tests and dry runs.

* ``run_agent`` writes a canned deliverable (from ``extra.response`` / ``extra.response_file``
  or a generic stub) into the sandbox and returns it as the final text.
* ``complete`` answers judge / generator prompts heuristically so the whole pipeline can be
  exercised without credentials. Judge verdicts pass when enough distinctive words of the
  criterion appear in the deliverable; generator prompts return a small valid task bundle.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .base import AgentRun, Backend, Completion

_STOP = set("the a an of to and or in on for with that this is are be by as at from it its not must does do should".split())


def _words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9§]+", s.lower()) if w not in _STOP and len(w) > 2}


class MockBackend(Backend):
    name = "mock"

    def run_agent(self, *, prompt, cwd, model, effort, system_prompt, tools, max_turns,
                  max_budget_usd, timeout_s, extra) -> AgentRun:
        text = extra.get("response")
        if not text and extra.get("response_file"):
            text = Path(extra["response_file"]).read_text()
        if not text:
            text = "# Memorandum\n\nMock deliverable. (Configure `extra.response` on the mock agent to control content.)\n"
        m = re.search(r"Required deliverables: (.+?)\.\n", prompt)
        deliverables = [d.strip().strip("`") for d in m.group(1).split(",")] if m else ["memo.md"]
        m2 = re.search(r"as a file in `([^`]+)/`", prompt)
        out_dir = Path(cwd) / (m2.group(1) if m2 else "deliverables")
        out_dir.mkdir(parents=True, exist_ok=True)
        for d in deliverables:
            (out_dir / d).write_text(text)
        return AgentRun(final_text=text, model=model, session_id="mock", cost_usd=0.0, num_turns=1)

    def complete(self, *, prompt, model, effort, system_prompt, json_schema, timeout_s, extra) -> Completion:
        if json_schema and "verdicts" in json.dumps(json_schema):
            return self._judge(prompt)
        if json_schema and "qa_pass" in json.dumps(json_schema):
            return Completion(text="", structured={"qa_pass": True, "realism": 4, "legal_soundness": 4,
                                                   "criteria_quality": 4, "issues": [], "summary": "mock QA"}, model=model)
        if json_schema and "revision_plan" in json.dumps(json_schema):
            return Completion(text="", structured={"revision_plan": "mock: tighten criteria", "done": True}, model=model)
        return Completion(text="mock completion", structured=None, model=model)

    def _judge(self, prompt: str) -> Completion:
        crit_block = prompt.split("## Criteria", 1)[-1]
        deliv_block = prompt.split("## Deliverables", 1)[-1].split("## Criteria", 1)[0]
        dw = _words(deliv_block)
        verdicts = []
        for m in re.finditer(r"^- \[(?P<id>[^\]]+)\] (?P<text>.+)$", crit_block, flags=re.M):
            cw = _words(m.group("text"))
            overlap = len(cw & dw) / max(1, len(cw))
            passed = overlap >= 0.5
            verdicts.append({"id": m.group("id"), "verdict": "PASS" if passed else "FAIL",
                             "rationale": f"mock keyword overlap {overlap:.2f}", "evidence": ""})
        return Completion(text="", structured={"verdicts": verdicts}, model="mock")
