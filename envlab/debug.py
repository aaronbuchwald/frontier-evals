"""Interactive debug loop for editing a task and getting fresh-session feedback.

    envlab debug --task data/harvey/tasks/<id> --agent configs/agents/opus-5-5.yaml

Commands inside the loop:
  r  run the task again in a brand-new sandbox + fresh model session, then grade
  g  re-grade the last run only (cheap: after editing criteria.yaml / grader_notes.md)
  v  validate the task spec (format rules, criteria count, workspace manifest)
  s  show task summary and criteria
  d  show per-criterion diff between the last two runs
  o  print the last deliverable
  w  toggle watch mode (auto re-run when a task file changes)
  q  quit
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .config import AgentConfig, EnvConfig, VerifierConfig
from .jev import GradeReport
from .runner import RunResult, regrade, run_task
from .spec import TaskSpec

console = Console()


def _mtimes(task_dir: Path) -> dict[str, float]:
    return {str(p): p.stat().st_mtime for p in task_dir.rglob("*") if p.is_file()}


def print_grade(g: GradeReport, prev: GradeReport | None = None) -> None:
    t = Table(title=f"{g.task_id}: {g.n_passed}/{g.n_criteria} passed ({g.pass_rate:.0%}) judge={g.judge_model}")
    t.add_column("id"); t.add_column("verdict"); t.add_column("criterion", max_width=60); t.add_column("rationale", max_width=70)
    prev_map = {r.id: r.passed for r in prev.results} if prev else {}
    for r in g.results:
        mark = "[green]PASS[/]" if r.passed else "[red]FAIL[/]"
        if r.id in prev_map and prev_map[r.id] != r.passed:
            mark += " [yellow](changed)[/]"
        t.add_row(r.id, mark, r.text, r.rationale[:200])
    console.print(t)
    if g.error:
        console.print(f"[red]grader error:[/] {g.error}")


def print_task(task: TaskSpec) -> None:
    console.rule(f"[bold]{task.title}[/] ({task.id})")
    console.print(task.instruction.strip())
    console.print(f"\n[dim]deliverables:[/] {', '.join(task.deliverables)}   [dim]workspace files:[/] {len(task.workspace_files())}   [dim]criteria:[/] {len(task.criteria)}")
    for c in task.criteria:
        console.print(f"  - [{c.id}] ({c.category}{', negative' if c.polarity == 'negative' else ''}) {c.text}")
    problems = task.validate_spec()
    if problems:
        console.print("[yellow]validation problems:[/]")
        for p in problems:
            console.print(f"  ! {p}")
    else:
        console.print("[green]spec valid[/]")


def debug_loop(task_dir: Path, agent: AgentConfig, env: EnvConfig, verifier: VerifierConfig,
               runs_root: Path | None = None, run_first: bool = False, watch: bool = False) -> None:
    history: list[RunResult] = []
    state_file = task_dir / ".envlab_debug.json"
    if state_file.exists():
        try:
            for rd in json.loads(state_file.read_text()).get("runs", []):
                p = Path(rd)
                if (p / "grade.json").exists():
                    g = GradeReport.from_dict(json.loads((p / "grade.json").read_text()))
                    meta = json.loads((p / "run.json").read_text())
                    history.append(RunResult(p, g.task_id, meta["agent"], meta["agent_model"], meta["agent_cost_usd"],
                                             meta.get("agent_error"), {}, g))
        except Exception:  # noqa: BLE001
            history = []

    def persist() -> None:
        state_file.write_text(json.dumps({"runs": [str(h.run_dir) for h in history[-10:]]}))

    def do_run() -> None:
        task = TaskSpec.load(task_dir)
        problems = task.validate_spec()
        for p in problems:
            console.print(f"[yellow]![/] {p}")
        console.print(f"[cyan]running[/] {task.id} with {agent.name} ({agent.model}) in a fresh session...")
        t0 = time.time()
        rr = run_task(task_dir, agent, env, verifier, runs_root=runs_root, label="debug")
        console.print(f"[dim]done in {time.time() - t0:.0f}s, run dir {rr.run_dir}[/]")
        if rr.agent_error:
            console.print(f"[red]agent error:[/] {rr.agent_error}")
        prev = history[-1].grade if history else None
        history.append(rr)
        persist()
        if rr.grade:
            print_grade(rr.grade, prev)

    print_task(TaskSpec.load(task_dir))
    if run_first:
        do_run()
    last_m = _mtimes(task_dir)
    console.print("[bold]commands:[/] r=run fresh  g=regrade last  v=validate  s=show  d=diff  o=output  w=watch  q=quit")
    while True:
        if watch:
            console.print("[dim]watching for edits... (ctrl-c to stop watching)[/]")
            try:
                while _mtimes(task_dir) == last_m:
                    time.sleep(1.0)
            except KeyboardInterrupt:
                watch = False
                continue
            last_m = _mtimes(task_dir)
            console.print("[cyan]change detected[/]")
            do_run()
            continue
        try:
            cmd = input("envlab> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if cmd in ("q", "quit", "exit"):
            break
        elif cmd == "r":
            do_run(); last_m = _mtimes(task_dir)
        elif cmd == "g":
            if not history:
                console.print("no run yet"); continue
            prev = history[-1].grade
            g = regrade(history[-1].run_dir, verifier, task_dir=task_dir)
            history[-1].grade = g
            print_grade(g, prev)
        elif cmd == "v":
            probs = TaskSpec.load(task_dir).validate_spec()
            console.print("[green]valid[/]" if not probs else "\n".join(f"! {p}" for p in probs))
        elif cmd == "s":
            print_task(TaskSpec.load(task_dir))
        elif cmd == "d":
            if len(history) < 2 or not history[-1].grade or not history[-2].grade:
                console.print("need two graded runs"); continue
            a = {r.id: r.passed for r in history[-2].grade.results}
            b = {r.id: r.passed for r in history[-1].grade.results}
            for cid in b:
                if a.get(cid) != b[cid]:
                    console.print(f"  {cid}: {a.get(cid)} -> {b[cid]}")
            console.print(f"pass rate {history[-2].grade.pass_rate:.0%} -> {history[-1].grade.pass_rate:.0%}")
        elif cmd == "o":
            if not history:
                console.print("no run yet"); continue
            env_cfg = env
            for name in TaskSpec.load(task_dir).deliverables:
                p = history[-1].run_dir / "sandbox" / env_cfg.deliverable_dir / name
                console.rule(name)
                console.print(p.read_text() if p.exists() else (history[-1].run_dir / "agent_final_text.md").read_text())
        elif cmd == "w":
            watch = True; last_m = _mtimes(task_dir)
        elif cmd:
            console.print("unknown command")
    sys.stdout.flush()
