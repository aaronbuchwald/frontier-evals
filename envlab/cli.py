"""envlab command line interface."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import click
import yaml
from rich.console import Console

from .config import AgentConfig, EnvConfig, VerifierConfig
from .spec import Criterion, TaskMetadata, TaskSpec, WorkspaceFile

console = Console()
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV = ROOT / "configs" / "envs" / "document-workspace.yaml"
DEFAULT_VERIFIER = ROOT / "configs" / "verifiers" / "jev-default.yaml"
DEFAULT_AGENT = ROOT / "configs" / "agents" / "opus-5-5.yaml"


def _agent(p: str | None) -> AgentConfig:
    return AgentConfig.load(p or DEFAULT_AGENT)


def _env(p: str | None) -> EnvConfig:
    return EnvConfig.load(p or DEFAULT_ENV)


def _verifier(p: str | None) -> VerifierConfig:
    return VerifierConfig.load(p or DEFAULT_VERIFIER)


@click.group()
def main() -> None:
    """Author, run, grade and research RL environment tasks (Harvey-LAB-style)."""


@main.command()
@click.option("--task", "task_dir", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--agent", "agent_path", type=click.Path(exists=True), help="Agent config YAML (default: Opus 5.5 via claude CLI).")
@click.option("--env", "env_path", type=click.Path(exists=True), help="Env config YAML.")
@click.option("--verifier", "verifier_path", type=click.Path(exists=True), help="Jev verifier config YAML.")
@click.option("--no-grade", is_flag=True, help="Run the agent only.")
@click.option("--runs-root", type=click.Path(file_okay=False), default=None)
@click.option("--repeat", default=1, show_default=True, help="Number of fresh-session runs.")
@click.option("--json", "as_json", is_flag=True, help="Print machine-readable summary.")
def run(task_dir, agent_path, env_path, verifier_path, no_grade, runs_root, repeat, as_json):
    """Run ONE task in a fresh sandbox with an agent config and grade it with a Jev verifier."""
    from .runner import run_task
    agent, env = _agent(agent_path), _env(env_path)
    verifier = None if no_grade else _verifier(verifier_path)
    summaries = []
    for i in range(repeat):
        rr = run_task(task_dir, agent, env, verifier, runs_root=Path(runs_root) if runs_root else None,
                      label=f"r{i + 1}" if repeat > 1 else None)
        summaries.append(rr.summary())
        if not as_json:
            console.print((rr.run_dir / "report.md").read_text())
    if as_json:
        click.echo(json.dumps(summaries if repeat > 1 else summaries[0], indent=2))
    elif repeat > 1:
        prs = [s["pass_rate"] for s in summaries if s["pass_rate"] is not None]
        if prs:
            console.print(f"\n[bold]mean pass rate over {len(prs)} runs: {sum(prs) / len(prs):.0%}[/]")


@main.command()
@click.option("--run", "run_dir", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--task", "task_dir", type=click.Path(exists=True, file_okay=False), help="Re-load criteria from this task dir (after edits).")
@click.option("--verifier", "verifier_path", type=click.Path(exists=True))
def grade(run_dir, task_dir, verifier_path):
    """Re-grade an existing run's deliverables (no agent call)."""
    from .runner import RunResult, regrade, render_report
    g = regrade(run_dir, _verifier(verifier_path), task_dir=task_dir)
    meta = json.loads((Path(run_dir) / "run.json").read_text())
    rr = RunResult(Path(run_dir), g.task_id, meta["agent"], meta["agent_model"], meta["agent_cost_usd"],
                   meta.get("agent_error"), {}, g)
    console.print(render_report(rr))


@main.command()
@click.option("--task", "task_dir", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--agent", "agent_path", type=click.Path(exists=True))
@click.option("--env", "env_path", type=click.Path(exists=True))
@click.option("--verifier", "verifier_path", type=click.Path(exists=True))
@click.option("--runs-root", type=click.Path(file_okay=False), default=None)
@click.option("--run-first", is_flag=True, help="Run immediately on start.")
@click.option("--watch", is_flag=True, help="Auto re-run (fresh session) whenever a task file changes.")
def debug(task_dir, agent_path, env_path, verifier_path, runs_root, run_first, watch):
    """Interactive edit -> fresh re-run -> feedback loop for one task."""
    from .debug import debug_loop
    debug_loop(Path(task_dir), _agent(agent_path), _env(env_path), _verifier(verifier_path),
               runs_root=Path(runs_root) if runs_root else None, run_first=run_first, watch=watch)


@main.command()
@click.option("--task", "task_dir", required=True, type=click.Path(exists=True, file_okay=False))
def validate(task_dir):
    """Check a task directory against the package format rules."""
    task = TaskSpec.load(task_dir)
    problems = task.validate_spec()
    console.print(f"{task.id}: {len(task.criteria)} criteria, {len(task.workspace_files())} workspace files, deliverables={task.deliverables}")
    for w in task.lint():
        console.print(f"[yellow]warn[/] {w}")
    if problems:
        for p in problems:
            console.print(f"[red]![/] {p}")
        raise SystemExit(1)
    console.print("[green]valid[/]")


@main.command()
@click.option("--package", "package_dir", default="data/harvey", type=click.Path(exists=True, file_okay=False))
def list(package_dir):  # noqa: A001
    """List tasks in a data package."""
    tasks_dir = Path(package_dir) / "tasks"
    for d in sorted(p for p in tasks_dir.iterdir() if (p / "task.yaml").exists()):
        t = TaskSpec.load(d)
        console.print(f"{t.id:50s} criteria={len(t.criteria):3d} files={len(t.workspace_files()):3d}  {t.title}")


@main.command()
@click.option("--package", "package_dir", default="data/harvey", type=click.Path(exists=True, file_okay=False))
@click.option("--id", "task_id", required=True)
@click.option("--title", default="Untitled task")
def new(package_dir, task_id, title):
    """Scaffold a new task directory."""
    d = Path(package_dir) / "tasks" / task_id
    if d.exists():
        raise click.ClickException(f"{d} already exists")
    spec = TaskSpec(id=task_id, title=title, package=Path(package_dir).name,
                    instruction="<partner-to-associate request: what to review, what to produce, for whom>",
                    deliverables=["memo.md"],
                    workspace=[WorkspaceFile(path="01_request_email.md", role="key", description="Client request")],
                    criteria=[Criterion(id=f"c{i:02d}", text=f"<atomic binary criterion {i}>") for i in range(1, 11)],
                    metadata=TaskMetadata(edge_case="<the ambiguity the task is built around>"))
    spec.save(d)
    (d / "workspace" / "01_request_email.md").write_text("From: ...\nTo: ...\nSubject: ...\n\n<client email>\n")
    (d / "grader_notes.md").write_text("# Grader notes (hidden from the solver)\n\n<intended answer and common errors>\n")
    console.print(f"scaffolded {d}")


@main.command()
@click.option("--idea", "idea_file", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--package", "package_dir", default="data/harvey", type=click.Path(exists=True, file_okay=False))
@click.option("--generator", "generator_path", required=True, type=click.Path(exists=True), help="Agent config that authors the task.")
@click.option("--solver", "solver_path", required=True, type=click.Path(exists=True), help="Agent config that attempts the task in a sandbox (different model/config).")
@click.option("--verifier", "verifier_path", type=click.Path(exists=True))
@click.option("--qa", "qa_path", type=click.Path(exists=True), help="Agent config for the lawyer-QA reviewer (default: verifier model).")
@click.option("--env", "env_path", type=click.Path(exists=True))
@click.option("--iterations", default=3, show_default=True)
@click.option("--solver-runs", default=1, show_default=True, help="Fresh solver runs per iteration.")
@click.option("--task-id", default=None)
@click.option("--target-max-pass-rate", type=float, default=None, help="Override package target (e.g. 0.75).")
@click.option("--min-criteria", type=int, default=None)
@click.option("--skip-qa", is_flag=True)
@click.option("--runs-root", type=click.Path(file_okay=False), default=None)
@click.option("--out-root", type=click.Path(file_okay=False), default=None, help="Where candidate tasks go (default <package>/candidates).")
@click.option("--seed-task", type=click.Path(exists=True, file_okay=False), default=None, help="Revise/harden an existing task dir instead of authoring from scratch.")
@click.option("--baseline-run", "baseline_runs", multiple=True, type=click.Path(exists=True, file_okay=False), help="Existing graded run dir(s) of the seed task to use as iteration-0 feedback (repeatable).")
def research(idea_file, package_dir, generator_path, solver_path, verifier_path, qa_path, env_path, iterations,
             solver_runs, task_id, target_max_pass_rate, min_criteria, skip_qa, runs_root, out_root, seed_task, baseline_runs):
    """Idea + edge case -> generate task (model A) -> solve in sandbox (model B) -> Jev grade -> QA -> revise."""
    from .research import run_research
    rlog = run_research(
        idea_file=Path(idea_file), package_dir=Path(package_dir), generator=AgentConfig.load(generator_path),
        solver=AgentConfig.load(solver_path), verifier=_verifier(verifier_path), env=_env(env_path),
        qa_agent=AgentConfig.load(qa_path) if qa_path else None, iterations=iterations, solver_runs=solver_runs,
        task_id=task_id, target_max_pass_rate=target_max_pass_rate, min_criteria=min_criteria, skip_qa=skip_qa,
        runs_root=Path(runs_root) if runs_root else None, out_root=Path(out_root) if out_root else None,
        seed_task=Path(seed_task) if seed_task else None, baseline_runs=[Path(b) for b in baseline_runs],
        log=lambda m: console.print(f"[dim]{m}[/]"),
    )
    console.print(f"\n[bold]accepted={rlog.accepted}[/]  best task: {rlog.best_task_dir}")
    if rlog.best_task_dir:
        console.print((Path(rlog.best_task_dir).parent / "research_log.md").read_text())


@main.command()
@click.option("--ideas", "idea_files", required=True, multiple=True, type=click.Path(exists=True, dir_okay=False), help="Idea files (repeatable / glob).")
@click.option("--package", "package_dir", default="data/harvey", type=click.Path(exists=True, file_okay=False))
@click.option("--generator", "generator_path", required=True, type=click.Path(exists=True))
@click.option("--solver", "solver_path", required=True, type=click.Path(exists=True))
@click.option("--verifier", "verifier_path", type=click.Path(exists=True))
@click.option("--qa", "qa_path", type=click.Path(exists=True))
@click.option("--env", "env_path", type=click.Path(exists=True))
@click.option("--iterations", default=3, show_default=True)
@click.option("--solver-runs", default=1, show_default=True)
@click.option("--skip-qa", is_flag=True)
@click.option("--runs-root", type=click.Path(file_okay=False), default="runs/research")
@click.option("--promote", "do_promote", is_flag=True, help="Copy accepted tasks into <package>/tasks/.")
def batch(idea_files, package_dir, generator_path, solver_path, verifier_path, qa_path, env_path, iterations,
          solver_runs, skip_qa, runs_root, do_promote):
    """Run the research loop over a queue of ideas and print a summary table."""
    from .research import run_research
    rows = []
    for idea in idea_files:
        console.rule(f"[bold]{idea}[/]")
        try:
            rlog = run_research(
                idea_file=Path(idea), package_dir=Path(package_dir), generator=AgentConfig.load(generator_path),
                solver=AgentConfig.load(solver_path), verifier=_verifier(verifier_path), env=_env(env_path),
                qa_agent=AgentConfig.load(qa_path) if qa_path else None, iterations=iterations,
                solver_runs=solver_runs, skip_qa=skip_qa, runs_root=Path(runs_root),
                log=lambda m: console.print(f"[dim]{m}[/]"),
            )
        except Exception as e:  # noqa: BLE001
            rows.append((idea, "ERROR", None, str(e)[:120]))
            continue
        last = rlog.iterations[-1] if rlog.iterations else None
        rows.append((idea, "accepted" if rlog.accepted else "not accepted",
                     None if last is None else last.mean_pass_rate, rlog.best_task_dir or ""))
        if do_promote and rlog.accepted and rlog.best_task_dir:
            t = TaskSpec.load(rlog.best_task_dir)
            dest = Path(package_dir) / "tasks" / t.id
            if not dest.exists():
                shutil.copytree(rlog.best_task_dir, dest)
                console.print(f"promoted {t.id} -> {dest}")
    console.rule("[bold]batch summary[/]")
    for idea, status, pr, where in rows:
        console.print(f"{Path(idea).stem:45s} {status:14s} pass_rate={'-' if pr is None else f'{pr:.0%}':6s} {where}")


@main.command()
@click.option("--from", "src", required=True, type=click.Path(exists=True, file_okay=False), help="Candidate task dir (e.g. .../best).")
@click.option("--package", "package_dir", default="data/harvey", type=click.Path(exists=True, file_okay=False))
@click.option("--id", "task_id", default=None)
def promote(src, package_dir, task_id):
    """Copy an accepted research candidate into the package's tasks/ directory."""
    t = TaskSpec.load(src)
    dest = Path(package_dir) / "tasks" / (task_id or t.id)
    if dest.exists():
        raise click.ClickException(f"{dest} exists")
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".envlab_debug.json"))
    if task_id and task_id != t.id:
        data = yaml.safe_load((dest / "task.yaml").read_text())
        data["id"] = task_id
        (dest / "task.yaml").write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    console.print(f"promoted to {dest}")


if __name__ == "__main__":
    main()
