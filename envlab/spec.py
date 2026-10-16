"""Task specification (Harvey Legal Agent Benchmark style).

A task directory looks like::

    <task_id>/
      task.yaml          # id, title, instruction, deliverables, workspace manifest, metadata
      criteria.yaml      # list of atomic, binary pass/fail criteria (the Jev verifier input)
      workspace/         # closed-universe matter files the agent sees
      grader_notes.md    # optional, hidden from the agent, shown to the judge

The format mirrors the public description of Harvey's Legal Agent Benchmark:
a short partner-to-associate instruction, a closed-universe document workspace
mixing key and peripheral files, one or more deliverable files, and an expert
rubric of atomic binary criteria each tied to a deliverable.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator


class Criterion(BaseModel):
    id: str
    text: str = Field(description="Atomic, binary statement the deliverable must satisfy.")
    category: Literal[
        "issue_spotting", "legal_analysis", "fact_use", "citation",
        "recommendation", "format", "negative",
    ] = "legal_analysis"
    polarity: Literal["positive", "negative"] = "positive"
    deliverable: str | None = Field(default=None, description="Deliverable file this criterion is tied to.")
    weight: float = 1.0
    grader_notes: str | None = Field(default=None, description="Hidden guidance for the judge only.")
    tags: list[str] = Field(default_factory=list)

    @field_validator("text")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("criterion text must be non-empty")
        return v.strip()


class WorkspaceFile(BaseModel):
    path: str
    role: Literal["key", "peripheral", "reference"] = "key"
    description: str = ""


class TaskMetadata(BaseModel):
    practice_area: str = ""
    task_type: Literal["advisory", "transactional", "regulatory", "litigation", "other"] = "advisory"
    difficulty: Literal["easy", "medium", "hard", "expert"] = "hard"
    edge_case: str = Field(default="", description="The legal ambiguity / trap the task is built around.")
    author: str = ""
    source_idea: str = ""
    target_max_pass_rate: float = 0.75
    min_criteria: int = 10
    notes: str = ""


class TaskSpec(BaseModel):
    id: str
    title: str
    package: str = "harvey"
    instruction: str = Field(description="Single-turn partner-to-associate request.")
    deliverables: list[str] = Field(default_factory=lambda: ["memo.md"])
    workspace: list[WorkspaceFile] = Field(default_factory=list)
    criteria: list[Criterion] = Field(default_factory=list)
    metadata: TaskMetadata = Field(default_factory=TaskMetadata)
    grader_notes: str = ""
    path: Path | None = Field(default=None, exclude=True)

    # ---- loading -----------------------------------------------------------------
    @classmethod
    def load(cls, task_dir: str | Path) -> "TaskSpec":
        task_dir = Path(task_dir)
        task_file = task_dir / "task.yaml"
        if not task_file.exists():
            raise FileNotFoundError(f"no task.yaml in {task_dir}")
        data = yaml.safe_load(task_file.read_text()) or {}
        crit_file = task_dir / "criteria.yaml"
        if crit_file.exists():
            crit = yaml.safe_load(crit_file.read_text()) or {}
            data["criteria"] = crit.get("criteria", crit if isinstance(crit, list) else [])
        notes = task_dir / "grader_notes.md"
        if notes.exists():
            data["grader_notes"] = notes.read_text()
        ws_dir = task_dir / "workspace"
        if not data.get("workspace") and ws_dir.exists():
            data["workspace"] = [
                {"path": str(p.relative_to(ws_dir)), "role": "key"}
                for p in sorted(ws_dir.rglob("*")) if p.is_file()
            ]
        spec = cls.model_validate(data)
        spec.path = task_dir
        return spec

    def save(self, task_dir: str | Path) -> Path:
        task_dir = Path(task_dir)
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "workspace").mkdir(exist_ok=True)
        body = self.model_dump(mode="json", exclude={"criteria", "grader_notes"})
        (task_dir / "task.yaml").write_text(yaml.safe_dump(body, sort_keys=False, allow_unicode=True, width=100))
        crit = {"criteria": [c.model_dump(mode="json", exclude_none=True) for c in self.criteria]}
        (task_dir / "criteria.yaml").write_text(yaml.safe_dump(crit, sort_keys=False, allow_unicode=True, width=100))
        if self.grader_notes:
            (task_dir / "grader_notes.md").write_text(self.grader_notes)
        return task_dir

    # ---- helpers -----------------------------------------------------------------
    @property
    def workspace_dir(self) -> Path:
        assert self.path is not None
        return self.path / "workspace"

    def workspace_files(self) -> list[Path]:
        if not self.path:
            return []
        return [p for p in sorted(self.workspace_dir.rglob("*")) if p.is_file()]

    def validate_spec(self) -> list[str]:
        """Return a list of human-readable problems (empty list == valid)."""
        problems: list[str] = []
        if len(self.instruction.split()) < 8:
            problems.append("instruction is too short to be a realistic partner request")
        if len(self.instruction.split()) > 250:
            problems.append("instruction is longer than a single-turn request should be (>250 words)")
        if not self.deliverables:
            problems.append("at least one deliverable file is required")
        n = len(self.criteria)
        if n < self.metadata.min_criteria:
            problems.append(f"only {n} criteria; package requires at least {self.metadata.min_criteria}")
        ids = [c.id for c in self.criteria]
        if len(ids) != len(set(ids)):
            problems.append("criterion ids are not unique")
        for c in self.criteria:
            if c.deliverable and c.deliverable not in self.deliverables:
                problems.append(f"criterion {c.id} references unknown deliverable {c.deliverable!r}")
            if len(c.text.split()) < 5:
                problems.append(f"criterion {c.id} is too vague to be binary: {c.text!r}")
        if self.path:
            ws = self.workspace_files()
            if not ws:
                problems.append("workspace/ is empty; a closed-universe document set is required")
            declared = {w.path for w in self.workspace}
            actual = {str(p.relative_to(self.workspace_dir)) for p in ws}
            for missing in sorted(declared - actual):
                problems.append(f"task.yaml lists workspace file {missing!r} that does not exist")
        return problems

    def lint(self) -> list[str]:
        """Soft warnings (style / atomicity heuristics) that do not fail validation."""
        warnings: list[str] = []
        for c in self.criteria:
            if c.text.count(" and ") >= 4:
                warnings.append(f"criterion {c.id} may bundle several checks; consider splitting")
            if len(c.text.split()) > 90:
                warnings.append(f"criterion {c.id} is long ({len(c.text.split())} words); judges grade short criteria more reliably")
        return warnings


def load_task(task_dir: str | Path) -> TaskSpec:
    return TaskSpec.load(task_dir)
