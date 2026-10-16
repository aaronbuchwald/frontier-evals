"""Fresh, isolated sandbox per run: a copy of the task workspace plus a deliverables dir."""
from __future__ import annotations

import json
import os
import shutil
import stat
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import EnvConfig
from .spec import TaskSpec


@dataclass
class Sandbox:
    root: Path          # run directory
    cwd: Path           # directory the agent works in
    workspace: Path     # cwd/workspace (read-only copy of the task workspace)
    deliverables: Path  # cwd/<deliverable_dir>

    def deliverable_text(self, name: str, fallback: str | None = None) -> tuple[str, bool]:
        """Return (text, from_file). If the file is missing and a fallback is given, use it."""
        p = self.deliverables / name
        if p.exists():
            return p.read_text(errors="replace"), True
        if fallback is not None:
            return fallback, False
        return "", False


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_sandbox(task: TaskSpec, env: EnvConfig, agent_name: str, runs_root: Path | None = None,
                   label: str | None = None) -> Sandbox:
    root = (runs_root or env.runs_root) / f"{_stamp()}-{task.id}-{agent_name}{('-' + label) if label else ''}"
    cwd = root / "sandbox"
    ws = cwd / "workspace"
    shutil.copytree(task.workspace_dir, ws)
    if env.workspace_read_only:
        for p in ws.rglob("*"):
            if p.is_file():
                p.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    deliv = cwd / env.deliverable_dir
    deliv.mkdir(parents=True, exist_ok=True)
    (root / "task_snapshot.json").write_text(json.dumps(task.model_dump(mode="json"), indent=2))
    return Sandbox(root=root, cwd=cwd, workspace=ws, deliverables=deliv)


def build_agent_prompt(task: TaskSpec, env: EnvConfig) -> str:
    manifest = ""
    if env.include_file_manifest:
        lines = []
        for f in task.workspace:
            desc = f" - {f.description}" if f.description else ""
            lines.append(f"- workspace/{f.path}{desc}")
        if lines:
            manifest = "Matter files:\n" + "\n".join(lines)
    return env.prompt_template.format(
        instruction=task.instruction.strip(),
        deliverables=", ".join(f"`{d}`" for d in task.deliverables),
        deliverable_dir=env.deliverable_dir,
        manifest=manifest,
    )


def unlock(sandbox: Sandbox) -> None:
    for p in sandbox.workspace.rglob("*"):
        if p.is_file():
            p.chmod(p.stat().st_mode | stat.S_IWUSR)
