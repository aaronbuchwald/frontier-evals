"""Offline smoke tests for the envlab pipeline using the mock backend."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envlab.config import AgentConfig, EnvConfig, VerifierConfig
from envlab.runner import regrade, run_task
from envlab.spec import TaskSpec

ROOT = Path(__file__).resolve().parent.parent
TASK = ROOT / "data" / "harvey" / "tasks" / "caa-gag-clause-deidentified-claims-access"


def test_seed_task_validates():
    task = TaskSpec.load(TASK)
    assert task.validate_spec() == []
    assert len(task.criteria) >= 10
    assert len(task.workspace_files()) == 10


def test_mock_run_and_grade(tmp_path):
    task = TaskSpec.load(TASK)
    # A deliverable that restates several criteria verbatim should pass those with the mock judge.
    response = "# MEMORANDUM\nTo: Dana Okafor\n\n## Executive summary\n" + "\n".join(c.text for c in task.criteria[:5])
    agent = AgentConfig(name="mock", backend="mock", model="mock", effort=None, extra={"response": response})
    env = EnvConfig(runs_root=tmp_path)
    ver = VerifierConfig(name="jev-mock", backend="mock", model="mock", effort=None)
    rr = run_task(TASK, agent, env, ver, runs_root=tmp_path)
    assert rr.grade is not None
    assert rr.grade.n_criteria == len(task.criteria)
    assert sum(r.passed for r in rr.grade.results[:5]) >= 4
    assert (rr.run_dir / "sandbox" / "deliverables" / "memo.md").exists()
    assert (rr.run_dir / "grade.json").exists() and (rr.run_dir / "report.md").exists()
    # workspace copy is read-only
    ws = rr.run_dir / "sandbox" / "workspace"
    assert not (ws / "02_meridian_asa_excerpts.md").stat().st_mode & 0o200
    # regrade without re-running the agent
    g2 = regrade(rr.run_dir, ver, task_dir=TASK)
    assert g2.n_criteria == rr.grade.n_criteria
    meta = json.loads((rr.run_dir / "run.json").read_text())
    assert meta["pass_rate"] == pytest.approx(g2.pass_rate, abs=1e-3)


def test_research_pipeline_mock(tmp_path):
    from envlab.research import run_research
    pkg = ROOT / "data" / "harvey"
    gen = AgentConfig(name="gen", backend="mock", model="mock", effort=None,
                      extra={"response": "stub"})
    solver = AgentConfig(name="solver", backend="mock", model="mock", effort=None, extra={"response": "x"})
    ver = VerifierConfig(name="jev-mock", backend="mock", model="mock", effort=None)
    # The mock generator does not author files, so the iteration is rejected for format reasons
    # and the loop must terminate cleanly with a log.
    rlog = run_research(idea_file=ROOT / "ideas" / "nsa-gag-clause.md", package_dir=pkg, generator=gen,
                        solver=solver, verifier=ver, env=EnvConfig(runs_root=tmp_path), iterations=2,
                        out_root=tmp_path / "cand", runs_root=tmp_path / "runs", log=lambda m: None)
    assert len(rlog.iterations) == 2
    assert rlog.accepted is False
    assert all(any("could not load" in p for p in it.validation_problems) for it in rlog.iterations)
    assert (tmp_path / "cand").exists()
