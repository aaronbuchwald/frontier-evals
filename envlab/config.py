"""Agent, environment and verifier (Jev) configuration models."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

BackendName = Literal["claude-cli", "anthropic", "openai", "mock"]


class AgentConfig(BaseModel):
    """How a model is invoked to attempt (or generate) a task."""
    name: str
    backend: BackendName = "claude-cli"
    model: str = "claude-opus-5-5"
    effort: Literal["low", "medium", "high", "xhigh", "max"] | None = "high"
    system_prompt: str | None = None
    tools: list[str] = Field(default_factory=lambda: ["Read", "Glob", "Grep", "Write", "Edit"])
    max_turns: int = 60
    max_budget_usd: float | None = 5.0
    timeout_s: int = 1800
    extra: dict[str, Any] = Field(default_factory=dict, description="Backend-specific options.")

    @classmethod
    def load(cls, path: str | Path) -> "AgentConfig":
        return cls.model_validate(yaml.safe_load(Path(path).read_text()))


class EnvConfig(BaseModel):
    """How the sandbox around a task is constructed."""
    name: str = "document-workspace"
    runs_root: Path = Path("runs")
    deliverable_dir: str = Field(default="deliverables", description="Dir (inside the sandbox) the agent writes outputs to.")
    workspace_read_only: bool = True
    allow_network: bool = False
    include_file_manifest: bool = True
    prompt_template: str = Field(
        default=(
            "You are an associate at a law firm. A partner has sent you the request below. "
            "The matter files are in the `workspace/` directory of the current working directory; this is a "
            "closed universe - rely only on those files and your own legal knowledge, and do not assume facts "
            "that are not in them.\n\n"
            "Write each deliverable as a file in `{deliverable_dir}/` (create the directory if needed). "
            "Required deliverables: {deliverables}.\n\n"
            "Partner request:\n\n{instruction}\n\n{manifest}"
        ),
        description="Python format string with {instruction}, {deliverables}, {deliverable_dir}, {manifest}.",
    )
    inline_fallback: bool = Field(default=True, description="If a deliverable file is missing, use the agent's final text response in its place.")

    @classmethod
    def load(cls, path: str | Path) -> "EnvConfig":
        return cls.model_validate(yaml.safe_load(Path(path).read_text()))


class VerifierConfig(BaseModel):
    """Jev (judge-eval) grading configuration: binary per-criterion verdicts from an LLM judge."""
    name: str = "jev-default"
    backend: BackendName = "claude-cli"
    model: str = "claude-opus-5-5"
    effort: Literal["low", "medium", "high", "xhigh", "max"] | None = "high"
    mode: Literal["batched", "per_criterion"] = Field(default="batched", description="One judge call for all criteria, or one call per criterion.")
    samples: int = Field(default=1, ge=1, description="Independent judge samples per criterion.")
    aggregate: Literal["majority", "all", "any"] = "majority"
    include_grader_notes: bool = True
    include_workspace: bool = Field(default=True, description="Show the judge the workspace documents (truncated).")
    max_workspace_chars: int = 120_000
    all_pass_required: bool = Field(default=False, description="Harvey-LAB style: task passes only if every criterion passes.")
    pass_threshold: float = Field(default=1.0, description="Task-level pass threshold on weighted criteria pass rate.")
    timeout_s: int = 900
    extra: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> "VerifierConfig":
        return cls.model_validate(yaml.safe_load(Path(path).read_text()))


class PackageConfig(BaseModel):
    """Package-level acceptance constraints (e.g. data/harvey/package.yaml)."""
    name: str
    description: str = ""
    min_criteria: int = 10
    target_max_pass_rate: float = 0.75
    reference_models: list[str] = Field(default_factory=list)
    qa_pass_threshold: float = 0.70
    format_doc: str = "FORMAT.md"

    @classmethod
    def load(cls, path: str | Path) -> "PackageConfig":
        return cls.model_validate(yaml.safe_load(Path(path).read_text()))
