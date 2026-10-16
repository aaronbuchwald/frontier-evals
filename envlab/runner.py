"""Run one task end to end: fresh sandbox -> agent -> Jev grade -> run directory with artifacts."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .backends import get_backend
from .config import AgentConfig, EnvConfig, VerifierConfig
from .jev import GradeReport, grade
from .sandbox import Sandbox, build_agent_prompt, create_sandbox
from .spec import TaskSpec


@dataclass
class RunResult:
    run_dir: Path
    task_id: str
    agent: str
    agent_model: str
    agent_cost_usd: float
    agent_error: str | None
    deliverables: dict[str, str]
    grade: GradeReport | None

    def summary(self) -> dict[str, Any]:
        g = self.grade
        return {
            "run_dir": str(self.run_dir), "task_id": self.task_id, "agent": self.agent,
            "agent_model": self.agent_model, "agent_cost_usd": round(self.agent_cost_usd, 4),
            "agent_error": self.agent_error,
            "pass_rate": None if g is None else round(g.pass_rate, 4),
            "n_passed": None if g is None else g.n_passed, "n_criteria": None if g is None else g.n_criteria,
            "all_pass": None if g is None else g.all_pass, "task_passed": None if g is None else g.task_passed,
            "judge_model": None if g is None else g.judge_model,
            "judge_cost_usd": None if g is None else round(g.cost_usd, 4),
        }


def run_agent_in_sandbox(task: TaskSpec, agent: AgentConfig, env: EnvConfig, sb: Sandbox) -> tuple[dict[str, str], dict[str, str], Any]:
    backend = get_backend(agent.backend)
    prompt = build_agent_prompt(task, env)
    (sb.root / "agent_prompt.md").write_text(prompt)
    extra = {"workspace_read_only": env.workspace_read_only, "allow_network": env.allow_network, **agent.extra}
    result = backend.run_agent(
        prompt=prompt, cwd=sb.cwd, model=agent.model, effort=agent.effort, system_prompt=agent.system_prompt,
        tools=agent.tools, max_turns=agent.max_turns, max_budget_usd=agent.max_budget_usd,
        timeout_s=agent.timeout_s, extra=extra,
    )
    (sb.root / "agent_result.json").write_text(json.dumps({
        "model": result.model, "session_id": result.session_id, "cost_usd": result.cost_usd,
        "num_turns": result.num_turns, "usage": result.usage, "error": result.error, "raw": result.raw,
        "transcript": result.transcript,
    }, indent=2, default=str))
    (sb.root / "agent_final_text.md").write_text(result.final_text or "")
    deliverables: dict[str, str] = {}
    sources: dict[str, str] = {}
    for name in task.deliverables:
        text, from_file = sb.deliverable_text(name, result.final_text if env.inline_fallback else None)
        deliverables[name] = text
        sources[name] = "file" if from_file else ("inline_fallback" if text else "missing")
    return deliverables, sources, result


def run_task(task_dir: str | Path, agent: AgentConfig, env: EnvConfig, verifier: VerifierConfig | None,
             runs_root: Path | None = None, label: str | None = None) -> RunResult:
    task = TaskSpec.load(task_dir)
    sb = create_sandbox(task, env, agent.name, runs_root=runs_root, label=label)
    deliverables, sources, agent_res = run_agent_in_sandbox(task, agent, env, sb)
    report = None
    if verifier is not None and any(t.strip() for t in deliverables.values()):
        report = grade(task, deliverables, verifier, deliverable_sources=sources)
        report.save(sb.root / "grade.json")
    rr = RunResult(run_dir=sb.root, task_id=task.id, agent=agent.name, agent_model=agent.model,
                   agent_cost_usd=agent_res.cost_usd, agent_error=agent_res.error,
                   deliverables=deliverables, grade=report)
    (sb.root / "run.json").write_text(json.dumps({
        **rr.summary(), "env": env.model_dump(mode="json"), "agent_config": agent.model_dump(mode="json"),
        "verifier": None if verifier is None else verifier.model_dump(mode="json"),
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2, default=str))
    (sb.root / "report.md").write_text(render_report(rr))
    return rr


def regrade(run_dir: str | Path, verifier: VerifierConfig, task_dir: str | Path | None = None) -> GradeReport:
    """Re-grade an existing run's deliverables (e.g. after editing criteria) without re-running the agent."""
    run_dir = Path(run_dir)
    meta = json.loads((run_dir / "run.json").read_text())
    snap = json.loads((run_dir / "task_snapshot.json").read_text())
    task = TaskSpec.load(task_dir) if task_dir else TaskSpec.model_validate(snap)
    if not task_dir:
        task.path = None
    env = EnvConfig.model_validate(meta["env"])
    sb_deliv = run_dir / "sandbox" / env.deliverable_dir
    final_text = (run_dir / "agent_final_text.md").read_text() if (run_dir / "agent_final_text.md").exists() else ""
    deliverables, sources = {}, {}
    for name in task.deliverables:
        p = sb_deliv / name
        if p.exists():
            deliverables[name], sources[name] = p.read_text(errors="replace"), "file"
        else:
            deliverables[name], sources[name] = final_text, "inline_fallback"
    report = grade(task, deliverables, verifier, deliverable_sources=sources)
    report.save(run_dir / "grade.json")
    meta.update({k: v for k, v in RunResult(run_dir, task.id, meta["agent"], meta["agent_model"],
                                             meta["agent_cost_usd"], meta.get("agent_error"),
                                             deliverables, report).summary().items()})
    (run_dir / "run.json").write_text(json.dumps(meta, indent=2, default=str))
    return report


def render_report(rr: RunResult) -> str:
    lines = [f"# Run report: {rr.task_id}", "",
             f"- agent: {rr.agent} ({rr.agent_model})", f"- run dir: {rr.run_dir}",
             f"- agent cost: ${rr.agent_cost_usd:.4f}"]
    if rr.agent_error:
        lines.append(f"- agent error: {rr.agent_error}")
    g = rr.grade
    if g is None:
        lines += ["", "(not graded)"]
        return "\n".join(lines)
    lines += [f"- judge: {g.judge_model} via {g.verifier}",
              f"- criteria passed: {g.n_passed}/{g.n_criteria} ({g.pass_rate:.0%})  all-pass: {g.all_pass}  task passed: {g.task_passed}",
              "", "| id | verdict | criterion | rationale |", "|---|---|---|---|"]
    for r in g.results:
        mark = "PASS" if r.passed else "FAIL"
        lines.append(f"| {r.id} | {mark} | {r.text.replace('|', '/')} | {r.rationale.replace('|', '/')[:300]} |")
    if g.error:
        lines += ["", f"grader error: {g.error}"]
    return "\n".join(lines)
