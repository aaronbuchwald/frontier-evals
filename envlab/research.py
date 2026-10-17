"""Research pipeline: task idea + edge case -> generated task -> sandboxed solve with a different
model -> Jev grade -> QA review -> revise until the package's acceptance criteria are met.

    envlab research --idea ideas/nsa-gag-clause.md --package data/harvey \
        --generator configs/agents/fable-5-1.yaml --solver configs/agents/opus-5-5.yaml \
        --verifier configs/verifiers/jev-default.yaml --iterations 3

Acceptance (from package.yaml, overridable on the CLI):
  * spec validates (>= min_criteria, atomic binary criteria, deliverables, non-empty workspace)
  * mean solver criteria pass rate over N fresh runs < target_max_pass_rate (e.g. 0.75)
  * QA reviewer (a "lawyer" role) rates the task realistic & legally sound (qa_pass)
"""
from __future__ import annotations

import json
import shutil
import statistics
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .backends import get_backend
from .config import AgentConfig, EnvConfig, PackageConfig, VerifierConfig
from .runner import RunResult, run_task
from .spec import TaskSpec

GENERATOR_SYSTEM = """You are a former BigLaw partner who now authors evaluation tasks for AI legal agents.
You write realistic, closed-universe client matters with planted legal issues and an expert rubric of
atomic, binary pass/fail criteria. You care about legal accuracy above all: never invent statutes,
regulations, cases or agency guidance; where the law is genuinely unsettled, build the task around the
ambiguity and make the criteria reward calibrated analysis rather than false certainty."""

QA_SYSTEM = """You are a practicing lawyer doing quality assurance on an evaluation task before it is paid for.
Assess whether the task is realistic (a partner would plausibly assign it), the facts in the workspace
are internally consistent, the legal analysis implied by the criteria is sound and current, every
criterion is atomic, binary and verifiable from the deliverable, and the grader notes do not contain
errors. Be strict: a task fails QA if any criterion rests on a legal misstatement."""

QA_SCHEMA = {
    "type": "object",
    "properties": {
        "qa_pass": {"type": "boolean"},
        "realism": {"type": "integer", "minimum": 1, "maximum": 5},
        "legal_soundness": {"type": "integer", "minimum": 1, "maximum": 5},
        "criteria_quality": {"type": "integer", "minimum": 1, "maximum": 5},
        "issues": {"type": "array", "items": {"type": "object", "properties": {
            "where": {"type": "string"}, "severity": {"type": "string", "enum": ["blocker", "major", "minor"]},
            "issue": {"type": "string"}, "fix": {"type": "string"}}, "required": ["where", "severity", "issue", "fix"]}},
        "summary": {"type": "string"},
    },
    "required": ["qa_pass", "realism", "legal_soundness", "criteria_quality", "issues", "summary"],
}


@dataclass
class IterationRecord:
    iteration: int
    task_dir: str
    validation_problems: list[str]
    solver_runs: list[dict[str, Any]]
    mean_pass_rate: float | None
    per_criterion_pass: dict[str, float]
    qa: dict[str, Any] | None
    accepted: bool
    reasons: list[str]
    generator_cost_usd: float
    solver_cost_usd: float
    judge_cost_usd: float
    qa_cost_usd: float


@dataclass
class ResearchLog:
    idea_file: str
    package: str
    generator: str
    solver: str
    verifier: str
    started_at: str
    iterations: list[IterationRecord] = field(default_factory=list)
    best_task_dir: str | None = None
    accepted: bool = False

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(asdict(self), indent=2, default=str))


def _read_idea(path: Path) -> str:
    return path.read_text()


def _feedback_block(rec: IterationRecord | None, task: "TaskSpec | None") -> str:
    if rec is None:
        return ""
    lines = ["## Feedback on the previous attempt", ""]
    if rec.validation_problems:
        lines += ["Format validation problems (must fix):"] + [f"- {p}" for p in rec.validation_problems]
    if rec.mean_pass_rate is not None:
        lines.append(f"\nA strong solver model attempted the task in {len(rec.solver_runs)} fresh session(s); mean criteria pass rate = {rec.mean_pass_rate:.0%}.")
        easy = [cid for cid, r in rec.per_criterion_pass.items() if r >= 0.99]
        hard = [cid for cid, r in rec.per_criterion_pass.items() if r <= 0.01]
        crit_text = {c.id: c.text for c in task.criteria} if task else {}
        if easy:
            lines.append(f"Criteria the solver always passed ({len(easy)}/{len(rec.per_criterion_pass)}): {', '.join(easy)}")
        if hard:
            lines.append(f"Criteria the solver always failed (check they are fair and verifiable): {', '.join(hard)}")
            lines += [f"  - [{cid}] {crit_text.get(cid, '')[:300]}" for cid in hard]
        lines += ["",
                  "IMPORTANT: the acceptance metric is the solver's MEAN criteria pass rate. Adding more criteria that the",
                  "solver will also pass does not lower it; the previous revision grew the rubric without moving the",
                  "number. To lower the mean you must raise the share of criteria the solver gets wrong. Do that by:",
                  "(1) reading the solver's deliverable below and identifying its actual errors, omissions, hedges and",
                  "    unsupported assertions, then writing criteria (positive or negative) that a careful lawyer would",
                  "    agree are required and that this deliverable fails;",
                  "(2) replacing criteria that any competent associate passes with criteria that require a specific",
                  "    conclusion, number, date, or cross-document synthesis the solver missed;",
                  "(3) changing the fact pattern so the correct answer is counter-intuitive or depends on a document",
                  "    the solver ignored, rather than adding more issues of the same kind;",
                  "(4) keeping the rubric compact (prefer 12-25 criteria) and every criterion fair and lawyer-defensible.",
                  "Never lower the pass rate by making criteria obscure, ambiguous, or trick questions."]
        for run in rec.solver_runs[:1]:
            if run.get("deliverable_excerpt"):
                lines += ["", "Excerpt of the solver's deliverable (so you can see what it got right and where it was shallow):",
                          "```", run["deliverable_excerpt"][:6000], "```"]
    if rec.qa:
        lines.append(f"\nLawyer QA review: pass={rec.qa.get('qa_pass')} realism={rec.qa.get('realism')}/5 "
                     f"legal_soundness={rec.qa.get('legal_soundness')}/5 criteria_quality={rec.qa.get('criteria_quality')}/5")
        for iss in rec.qa.get("issues", []):
            lines.append(f"- [{iss.get('severity')}] {iss.get('where')}: {iss.get('issue')} -> {iss.get('fix')}")
    lines += ["", "Reasons the attempt was not accepted:"] + [f"- {r}" for r in rec.reasons]
    return "\n".join(lines)


def generator_prompt(idea: str, format_doc: str, pkg: PackageConfig, task_id: str, out_dir: str,
                     feedback: str, existing_task_dir: Path | None) -> str:
    mode = ("Revise the existing task in place" if existing_task_dir else "Create a new task")
    return f"""{mode} in the directory `{out_dir}/` of the current working directory, following the package format exactly.

## Package format specification
{format_doc}

## Package acceptance constraints
- at least {pkg.min_criteria} criteria, each atomic and binary
- reference models ({', '.join(pkg.reference_models) or 'frontier models'}) should pass fewer than {pkg.target_max_pass_rate:.0%} of criteria on average: the task must contain genuine difficulty (ambiguity in the law, planted traps, multi-document synthesis), not obscurity or trick wording
- a practicing lawyer must agree the task is realistic and the law is stated correctly (QA pass rate target {pkg.qa_pass_threshold:.0%})

## Task idea and edge case
{idea}

{feedback}

## What to write
Task id: `{task_id}`. {"The existing task files are already in `" + out_dir + "/`; read them all first, keep what works, and revise in place (edit files, add documents or criteria, sharpen criteria that the solver passed trivially, add fair criteria for issues a careful lawyer would address but the solver missed, add negative criteria for errors the solver actually made). Keep the task realistic: never add obscure trivia or trick wording just to lower the pass rate." if existing_task_dir else "Write these files under `" + out_dir + "/`:"}
- `task.yaml` (id, title, package, instruction, deliverables, workspace manifest with roles and descriptions, metadata incl. edge_case)
- `criteria.yaml`
- `workspace/...` the matter documents (emails, contract excerpts, memos, statutory excerpts, peripheral files). Make them realistic, dated, internally consistent, and long enough to require real reading. Use fictional parties.
- `grader_notes.md` (hidden from the solver): the intended answer, why each criterion is right, and common wrong answers.
Do not write anything outside `{out_dir}/`. When finished, reply with a one-paragraph summary of the planted issues."""


def _qa_prompt(task: TaskSpec) -> str:
    ws = []
    for p in task.workspace_files():
        ws.append(f"### workspace/{p.relative_to(task.workspace_dir)}\n```\n{p.read_text(errors='replace')[:20000]}\n```")
    crit = "\n".join(f"- [{c.id}] ({c.category}{', negative' if c.polarity == 'negative' else ''}) {c.text}"
                     + (f"\n    grader note: {c.grader_notes}" if c.grader_notes else "") for c in task.criteria)
    return (f"## Task\n**{task.title}**\n\nInstruction:\n{task.instruction}\n\nDeliverables: {task.deliverables}\n\n"
            f"Edge case the author intends to test: {task.metadata.edge_case}\n\n## Workspace\n" + "\n".join(ws) +
            f"\n\n## Criteria\n{crit}\n\n## Grader notes\n{task.grader_notes}\n\n"
            "Review the task as described in your instructions and return the structured assessment.")


def _baseline_record(seed_dir: Path, baseline_runs: list[Path], solver: AgentConfig, env: EnvConfig,
                     verifier: VerifierConfig, pkg: PackageConfig, solver_runs: int, runs_root: Path,
                     log) -> IterationRecord:
    task = TaskSpec.load(seed_dir)
    task.metadata.min_criteria = pkg.min_criteria
    problems = task.validate_spec()
    solver_results: list[dict[str, Any]] = []
    per_crit: dict[str, list[bool]] = {}
    solver_cost = judge_cost = 0.0
    if baseline_runs:
        from .jev import GradeReport
        for rd in baseline_runs:
            rd = Path(rd)
            meta = json.loads((rd / "run.json").read_text())
            g = GradeReport.from_dict(json.loads((rd / "grade.json").read_text()))
            deliv = rd / "sandbox" / meta["env"]["deliverable_dir"]
            excerpt = ""
            for name in task.deliverables:
                if (deliv / name).exists():
                    excerpt = (deliv / name).read_text(errors="replace")
                    break
            solver_results.append({**meta, "deliverable_excerpt": excerpt[:8000]})
            for r in g.results:
                per_crit.setdefault(r.id, []).append(r.passed)
    else:
        for n in range(solver_runs):
            log(f"[research]   baseline solver run {n + 1}/{solver_runs} on seed task")
            rr = run_task(seed_dir, solver, env, verifier, runs_root=runs_root, label=f"seed{n + 1}")
            solver_cost += rr.agent_cost_usd
            judge_cost += rr.grade.cost_usd if rr.grade else 0.0
            excerpt = next(iter(rr.deliverables.values()), "") if rr.deliverables else ""
            solver_results.append({**rr.summary(), "deliverable_excerpt": excerpt[:8000]})
            if rr.grade:
                for r in rr.grade.results:
                    per_crit.setdefault(r.id, []).append(r.passed)
    prs = [s["pass_rate"] for s in solver_results if s.get("pass_rate") is not None]
    mean_pr = statistics.fmean(prs) if prs else None
    reasons = [f"format: {p}" for p in problems]
    if mean_pr is None:
        reasons.append("no baseline grade available")
    elif mean_pr >= pkg.target_max_pass_rate:
        reasons.append(f"too easy: solver mean pass rate {mean_pr:.0%} >= target max {pkg.target_max_pass_rate:.0%}")
    return IterationRecord(iteration=0, task_dir=str(seed_dir), validation_problems=problems,
                           solver_runs=solver_results, mean_pass_rate=mean_pr,
                           per_criterion_pass={k: sum(v) / len(v) for k, v in per_crit.items()},
                           qa=None, accepted=not reasons, reasons=reasons, generator_cost_usd=0.0,
                           solver_cost_usd=solver_cost, judge_cost_usd=judge_cost, qa_cost_usd=0.0)


def run_research(*, idea_file: Path, package_dir: Path, generator: AgentConfig, solver: AgentConfig,
                 verifier: VerifierConfig, env: EnvConfig, qa_agent: AgentConfig | None = None,
                 iterations: int = 3, solver_runs: int = 1, task_id: str | None = None,
                 target_max_pass_rate: float | None = None, min_criteria: int | None = None,
                 skip_qa: bool = False, runs_root: Path | None = None, out_root: Path | None = None,
                 seed_task: Path | None = None, baseline_runs: list[Path] | None = None,
                 log=print) -> ResearchLog:
    """Run the research loop.

    ``seed_task``: start from an existing task directory and have the generator *revise* it
    (harden it) instead of authoring from scratch. ``baseline_runs``: existing run directories
    for the seed task (from ``envlab run``) whose grades are used as iteration-0 feedback so the
    solver is not re-run on the seed; if omitted, the solver is run on the seed first.
    """
    pkg = PackageConfig.load(package_dir / "package.yaml")
    if target_max_pass_rate is not None:
        pkg.target_max_pass_rate = target_max_pass_rate
    if min_criteria is not None:
        pkg.min_criteria = min_criteria
    format_doc = (package_dir / pkg.format_doc).read_text() if (package_dir / pkg.format_doc).exists() else ""
    idea = _read_idea(idea_file)
    task_id = task_id or idea_file.stem
    out_root = out_root or (package_dir / "candidates")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_dir = out_root / f"{task_id}-{stamp}"
    session_dir.mkdir(parents=True, exist_ok=True)
    rlog = ResearchLog(idea_file=str(idea_file), package=pkg.name, generator=f"{generator.name}/{generator.model}",
                       solver=f"{solver.name}/{solver.model}", verifier=f"{verifier.name}/{verifier.model}",
                       started_at=stamp)
    gen_backend = get_backend(generator.backend)
    qa_cfg = qa_agent or verifier
    qa_backend = get_backend(qa_cfg.backend)

    prev: IterationRecord | None = None
    best: tuple[float, Path] | None = None
    if seed_task is not None:
        seed_dir = session_dir / "iter0" / "task"
        shutil.copytree(seed_task, seed_dir, ignore=shutil.ignore_patterns(".envlab_debug.json"))
        prev = _baseline_record(seed_dir, baseline_runs or [], solver, env, verifier, pkg, solver_runs,
                                runs_root or (session_dir / "iter0" / "runs"), log)
        rlog.iterations.append(prev)
        (session_dir / "iter0" / "iteration.json").write_text(json.dumps(asdict(prev), indent=2, default=str))
        mp = prev.mean_pass_rate
        best = ((0.0 if mp is None else 1.0 - mp) - 0.1 * len(prev.validation_problems), seed_dir)
        log(f"[research]   baseline on seed task: mean_pass_rate={mp} reasons={prev.reasons}")
        if prev.accepted:
            rlog.accepted = True
            iterations = 0
    for it in range(1, iterations + 1):
        it_dir = session_dir / f"iter{it}"
        it_dir.mkdir(exist_ok=True)
        task_out = it_dir / "task"
        if prev is not None and Path(prev.task_dir).exists():
            shutil.copytree(prev.task_dir, task_out)
        log(f"[research] iteration {it}/{iterations}: generating with {generator.name} ({generator.model})")
        prev_task = None
        if prev is not None and Path(prev.task_dir).exists():
            try:
                prev_task = TaskSpec.load(prev.task_dir)
            except Exception:  # noqa: BLE001
                prev_task = None
        prompt = generator_prompt(idea, format_doc, pkg, task_id, "task", _feedback_block(prev, prev_task),
                                  task_out if prev else None)
        (it_dir / "generator_prompt.md").write_text(prompt)
        t0 = time.time()
        gen = gen_backend.run_agent(prompt=prompt, cwd=it_dir, model=generator.model, effort=generator.effort,
                                    system_prompt=generator.system_prompt or GENERATOR_SYSTEM, tools=generator.tools,
                                    max_turns=generator.max_turns, max_budget_usd=generator.max_budget_usd,
                                    timeout_s=generator.timeout_s, extra={**generator.extra, "workspace_read_only": False})
        (it_dir / "generator_result.json").write_text(json.dumps({"final_text": gen.final_text, "error": gen.error,
                                                                   "cost_usd": gen.cost_usd, "num_turns": gen.num_turns,
                                                                   "seconds": round(time.time() - t0)}, indent=2))
        reasons: list[str] = []
        problems: list[str] = []
        task: TaskSpec | None = None
        try:
            task = TaskSpec.load(task_out)
            task.metadata.min_criteria = pkg.min_criteria
            problems = task.validate_spec()
        except Exception as e:  # noqa: BLE001
            problems = [f"could not load generated task: {e}"]
        if gen.error:
            reasons.append(f"generator error: {gen.error}")
        if problems:
            reasons += [f"format: {p}" for p in problems]
        solver_results: list[dict[str, Any]] = []
        per_crit: dict[str, list[bool]] = {}
        mean_pr: float | None = None
        solver_cost = judge_cost = 0.0
        qa: dict[str, Any] | None = None
        qa_cost = 0.0
        if task is not None and not any(p.startswith("could not load") for p in problems):
            for n in range(solver_runs):
                log(f"[research]   solver run {n + 1}/{solver_runs} with {solver.name} ({solver.model})")
                rr: RunResult = run_task(task_out, solver, env, verifier, runs_root=runs_root or (it_dir / "runs"),
                                         label=f"solve{n + 1}")
                solver_cost += rr.agent_cost_usd
                g = rr.grade
                judge_cost += g.cost_usd if g else 0.0
                excerpt = next(iter(rr.deliverables.values()), "") if rr.deliverables else ""
                solver_results.append({**rr.summary(), "deliverable_excerpt": excerpt[:8000]})
                if g:
                    for r in g.results:
                        per_crit.setdefault(r.id, []).append(r.passed)
            prs = [s["pass_rate"] for s in solver_results if s.get("pass_rate") is not None]
            mean_pr = statistics.fmean(prs) if prs else None
            if mean_pr is None:
                reasons.append("solver produced no gradable output")
            elif mean_pr >= pkg.target_max_pass_rate:
                reasons.append(f"too easy: solver mean pass rate {mean_pr:.0%} >= target max {pkg.target_max_pass_rate:.0%}")
            if not skip_qa:
                log(f"[research]   lawyer QA review with {qa_cfg.model}")
                try:
                    comp = qa_backend.complete(prompt=_qa_prompt(task), model=qa_cfg.model, effort=qa_cfg.effort,
                                               system_prompt=QA_SYSTEM, json_schema=QA_SCHEMA,
                                               timeout_s=getattr(qa_cfg, "timeout_s", 900), extra=qa_cfg.extra)
                    qa = comp.structured or {"qa_pass": False, "summary": comp.text[:2000], "issues": []}
                    qa_cost = comp.cost_usd
                except Exception as e:  # noqa: BLE001
                    qa = {"qa_pass": False, "summary": f"QA call failed: {e}", "issues": []}
                if not qa.get("qa_pass"):
                    reasons.append("lawyer QA did not pass: " + str(qa.get("summary", ""))[:300])
        accepted = not reasons
        rec = IterationRecord(
            iteration=it, task_dir=str(task_out), validation_problems=problems, solver_runs=solver_results,
            mean_pass_rate=mean_pr, per_criterion_pass={k: sum(v) / len(v) for k, v in per_crit.items()},
            qa=qa, accepted=accepted, reasons=reasons, generator_cost_usd=gen.cost_usd,
            solver_cost_usd=solver_cost, judge_cost_usd=judge_cost, qa_cost_usd=qa_cost,
        )
        rlog.iterations.append(rec)
        (it_dir / "iteration.json").write_text(json.dumps(asdict(rec), indent=2, default=str))
        rlog.save(session_dir / "research_log.json")
        score = (0.0 if mean_pr is None else (1.0 - mean_pr)) + (0.5 if qa and qa.get("qa_pass") else 0.0) - 0.1 * len(problems)
        if task is not None and (best is None or score > best[0]):
            best = (score, task_out)
        log(f"[research]   iteration {it}: accepted={accepted} mean_pass_rate={mean_pr} reasons={reasons}")
        if accepted:
            rlog.accepted = True
            break
        prev = rec
    if best is not None:
        final = session_dir / "best"
        if final.exists():
            shutil.rmtree(final)
        shutil.copytree(best[1], final)
        rlog.best_task_dir = str(final)
    rlog.save(session_dir / "research_log.json")
    (session_dir / "research_log.md").write_text(render_research_log(rlog))
    return rlog


def render_research_log(rlog: ResearchLog) -> str:
    lines = [f"# Research log: {Path(rlog.idea_file).stem}", "",
             f"- generator: {rlog.generator}", f"- solver: {rlog.solver}", f"- verifier: {rlog.verifier}",
             f"- accepted: {rlog.accepted}", f"- best task dir: {rlog.best_task_dir}", ""]
    for rec in rlog.iterations:
        lines += [f"## Iteration {rec.iteration} - {'ACCEPTED' if rec.accepted else 'rejected'}",
                  f"- task dir: {rec.task_dir}",
                  f"- mean solver pass rate: {rec.mean_pass_rate}",
                  f"- QA: {None if not rec.qa else rec.qa.get('qa_pass')} ({'' if not rec.qa else rec.qa.get('summary', '')[:300]})",
                  f"- costs: gen ${rec.generator_cost_usd:.2f} solver ${rec.solver_cost_usd:.2f} judge ${rec.judge_cost_usd:.2f} qa ${rec.qa_cost_usd:.2f}",
                  "- reasons: " + ("; ".join(rec.reasons) or "none"), ""]
        if rec.per_criterion_pass:
            all_pass = [bool(r.get("all_pass")) for r in rec.solver_runs if r.get("all_pass") is not None]
            if all_pass:
                lines.append(f"- all-pass (Harvey LAB scoring) rate: {sum(all_pass)}/{len(all_pass)}")
            lines.append("| criterion | solver pass rate |\n|---|---|")
            lines += [f"| {k} | {v:.0%} |" for k, v in rec.per_criterion_pass.items()]
            lines.append("")
    return "\n".join(lines)
