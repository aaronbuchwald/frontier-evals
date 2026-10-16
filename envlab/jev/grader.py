"""Jev grader: turns a deliverable + rubric into per-criterion binary verdicts.

Supports batched (all criteria in one judge call) or per-criterion calls, N samples per
criterion with majority / all / any aggregation, weighted pass rate and all-pass scoring.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..backends import get_backend
from ..config import VerifierConfig
from ..spec import Criterion, TaskSpec
from .prompts import JUDGE_SCHEMA, JUDGE_SYSTEM, judge_prompt


@dataclass
class CriterionResult:
    id: str
    text: str
    passed: bool
    votes: list[bool]
    rationale: str
    evidence: str
    category: str
    polarity: str
    weight: float = 1.0


@dataclass
class GradeReport:
    task_id: str
    verifier: str
    judge_model: str
    results: list[CriterionResult]
    pass_rate: float
    weighted_pass_rate: float
    all_pass: bool
    task_passed: bool
    n_criteria: int
    n_passed: int
    cost_usd: float = 0.0
    judge_calls: int = 0
    deliverable_sources: dict[str, str] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GradeReport":
        d = dict(d)
        d["results"] = [CriterionResult(**r) for r in d["results"]]
        return cls(**d)


def _criteria_lines(criteria: list[Criterion], include_notes: bool) -> str:
    out = []
    for c in criteria:
        tag = " (NEGATIVE: the deliverable must NOT do this)" if c.polarity == "negative" else ""
        line = f"- [{c.id}] {c.text}{tag}"
        if c.deliverable:
            line += f"  [deliverable: {c.deliverable}]"
        if include_notes and c.grader_notes:
            line += f"\n    grader note: {c.grader_notes.strip()}"
        out.append(line)
    return "\n".join(out)


def _workspace_blob(task: TaskSpec, max_chars: int) -> str:
    chunks, used = [], 0
    for p in task.workspace_files():
        rel = p.relative_to(task.workspace_dir)
        body = p.read_text(errors="replace")
        budget = max_chars - used
        if budget <= 0:
            chunks.append(f"### workspace/{rel}\n[omitted: workspace excerpt budget exhausted]\n")
            continue
        if len(body) > budget:
            body = body[:budget] + "\n[truncated]"
        used += len(body)
        chunks.append(f"### workspace/{rel}\n```\n{body}\n```\n")
    return "\n".join(chunks)


def _aggregate(votes: list[bool], how: str) -> bool:
    if not votes:
        return False
    if how == "all":
        return all(votes)
    if how == "any":
        return any(votes)
    c = Counter(votes)
    return c[True] > c[False]


def grade(task: TaskSpec, deliverables: dict[str, str], cfg: VerifierConfig,
          deliverable_sources: dict[str, str] | None = None) -> GradeReport:
    """Grade ``deliverables`` ({filename: text}) for ``task`` using the Jev config."""
    backend = get_backend(cfg.backend)
    workspace_docs = _workspace_blob(task, cfg.max_workspace_chars) if cfg.include_workspace else None
    deliv_text = "\n".join(f"### {name}\n```\n{text}\n```\n" for name, text in deliverables.items())
    groups: list[list[Criterion]] = [task.criteria] if cfg.mode == "batched" else [[c] for c in task.criteria]

    votes: dict[str, list[bool]] = {c.id: [] for c in task.criteria}
    rationale: dict[str, list[str]] = {c.id: [] for c in task.criteria}
    evidence: dict[str, str] = {c.id: "" for c in task.criteria}
    cost, calls, err = 0.0, 0, None

    for group in groups:
        prompt = judge_prompt(
            instruction=task.instruction,
            workspace_docs=workspace_docs,
            deliverables=deliv_text,
            criteria_lines=_criteria_lines(group, cfg.include_grader_notes),
            grader_notes=task.grader_notes if cfg.include_grader_notes else None,
        )
        for _ in range(cfg.samples):
            try:
                comp = backend.complete(prompt=prompt, model=cfg.model, effort=cfg.effort,
                                        system_prompt=JUDGE_SYSTEM, json_schema=JUDGE_SCHEMA,
                                        timeout_s=cfg.timeout_s, extra=cfg.extra)
            except Exception as e:  # noqa: BLE001
                err = f"judge call failed: {e}"
                continue
            calls += 1
            cost += comp.cost_usd
            data = comp.structured or {}
            for v in data.get("verdicts", []):
                cid = str(v.get("id", "")).strip()
                if cid not in votes:
                    continue
                votes[cid].append(str(v.get("verdict", "")).upper() == "PASS")
                rationale[cid].append(str(v.get("rationale", "")))
                if v.get("evidence") and not evidence[cid]:
                    evidence[cid] = str(v["evidence"])

    results: list[CriterionResult] = []
    for c in task.criteria:
        passed = _aggregate(votes[c.id], cfg.aggregate)
        results.append(CriterionResult(
            id=c.id, text=c.text, passed=passed, votes=votes[c.id],
            rationale=" | ".join(r for r in rationale[c.id] if r) or ("no verdict returned" if not votes[c.id] else ""),
            evidence=evidence[c.id], category=c.category, polarity=c.polarity, weight=c.weight,
        ))
    n = len(results)
    n_pass = sum(r.passed for r in results)
    wsum = sum(r.weight for r in results) or 1.0
    wpass = sum(r.weight for r in results if r.passed) / wsum
    all_pass = n > 0 and n_pass == n
    task_passed = all_pass if cfg.all_pass_required else wpass >= cfg.pass_threshold
    return GradeReport(
        task_id=task.id, verifier=cfg.name, judge_model=cfg.model, results=results,
        pass_rate=(n_pass / n) if n else 0.0, weighted_pass_rate=wpass, all_pass=all_pass,
        task_passed=task_passed, n_criteria=n, n_passed=n_pass, cost_usd=cost, judge_calls=calls,
        deliverable_sources=deliverable_sources or {}, error=err,
    )
