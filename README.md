# envlab - RL environment task pipeline (Harvey-LAB-style)

`envlab` is a small toolkit for **authoring, running, grading and researching** single-turn
document-workspace tasks in the format of Harvey's Legal Agent Benchmark: a partner-to-associate
instruction, a closed-universe set of matter files, one or more deliverable files, and an expert
rubric of atomic **binary** criteria graded by a **Jev** (judge-eval) verifier.

```
envlab/                 the package
  spec.py               TaskSpec / Criterion models, task-dir loader, format validation
  config.py             AgentConfig, EnvConfig, VerifierConfig (Jev), PackageConfig
  backends/             claude-cli (fresh `claude -p` session per run), anthropic SDK, openai, mock
  sandbox.py            fresh per-run sandbox: read-only workspace copy + deliverables dir
  jev/                  judge prompt + grader (batched / per-criterion, N samples, majority vote)
  runner.py             run one task -> runs/<stamp>-<task>-<agent>/ (prompt, transcript, grade.json, report.md)
  debug.py              interactive edit -> fresh re-run -> per-criterion feedback loop
  research.py           idea + edge case -> generate (model A) -> solve in sandbox (model B) -> grade -> QA -> revise
  cli.py                `envlab` command
configs/
  agents/               opus-5-5, fable-5-1, sonnet-5-5, opus-5-5-api, gpt-6-1-sol, mock
  envs/                 document-workspace
  verifiers/            jev-default, jev-strict, jev-fable, jev-mock
data/
  harvey/               data package: FORMAT.md, package.yaml (acceptance constraints), tasks/, candidates/
ideas/                  research ideas (task idea + edge case description)
runs/                   run artifacts (git-ignored)
```

## Install

```bash
pip install -e .            # click, pydantic, pyyaml, rich
pip install -e .[anthropic] # optional: Anthropic SDK backend (ANTHROPIC_API_KEY)
pip install -e .[openai]    # optional: OpenAI backend (OPENAI_API_KEY)
python -m pytest            # offline smoke tests (mock backend)
```

The default backend is **`claude-cli`**: every agent, judge and generator call spawns a brand-new
headless `claude -p` session (fresh session id, no persistence, session env scrubbed) with tools
limited to the sandbox (no Bash, no web). It works anywhere Claude Code is logged in, including
this cloud session, without an API key.

## Task format

See `data/harvey/FORMAT.md`. A task directory:

```
data/harvey/tasks/<task_id>/
  task.yaml         id, title, instruction (single turn), deliverables, workspace manifest, metadata.edge_case
  criteria.yaml     >= 10 atomic binary criteria (id, text, category, polarity, deliverable, grader_notes)
  workspace/        matter files the agent sees (read-only in the sandbox)
  grader_notes.md   hidden from the agent; shown to the Jev judge
```

## Commands

**Run and grade one task** with an agent config, env config and Jev verifier:

```bash
envlab run --task data/harvey/tasks/caa-gag-clause-deidentified-claims-access \
  --agent configs/agents/opus-5-5.yaml --env configs/envs/document-workspace.yaml \
  --verifier configs/verifiers/jev-fable.yaml --repeat 2
```

Each run gets a directory under `runs/` with `agent_prompt.md`, the sandbox (workspace copy +
`deliverables/`), `agent_result.json`, `grade.json` (per-criterion verdict, rationale, evidence)
and `report.md`.

**Re-grade** an existing run after editing `criteria.yaml` / `grader_notes.md` (no agent call):

```bash
envlab grade --run runs/<run-dir> --task data/harvey/tasks/<task_id> --verifier configs/verifiers/jev-default.yaml
```

**Debug / iterate on a task** (edit files in another window; every `r` is a fresh model session):

```bash
envlab debug --task data/harvey/tasks/<task_id> --agent configs/agents/opus-5-5.yaml --verifier configs/verifiers/jev-fable.yaml
envlab> r      # run in a fresh sandbox + fresh session, then grade; shows PASS/FAIL per criterion and what changed vs the last run
envlab> g      # re-grade the last deliverable only (cheap) after editing criteria
envlab> v      # validate the spec against the package format
envlab> d      # diff per-criterion verdicts between the last two runs
envlab> o      # print the last deliverable
envlab> w      # watch mode: auto re-run whenever a task file changes
```

**Validate / scaffold / list**:

```bash
envlab validate --task data/harvey/tasks/<task_id>
envlab new --package data/harvey --id my-new-task --title "..."
envlab list --package data/harvey
```

**Research pipeline** - turn an idea + edge-case description into a task that meets the
package's acceptance constraints. Model A (generator) authors the task directory; model B
(solver) attempts it in a fresh sandbox (N runs); the Jev verifier grades; a "lawyer QA"
reviewer checks realism and legal soundness; the generator revises with that feedback until the
task validates, the solver's mean criteria pass rate is below the target (0.75), and QA passes.

```bash
envlab research --idea ideas/nsa-gag-clause.md --package data/harvey \
  --generator configs/agents/fable-5-1.yaml --solver configs/agents/opus-5-5.yaml \
  --verifier configs/verifiers/jev-fable.yaml --iterations 3 --solver-runs 2
envlab promote --from data/harvey/candidates/<session>/best --package data/harvey
```

Artifacts land in `data/harvey/candidates/<idea>-<stamp>/iterN/` (generator prompt, task,
solver runs, `iteration.json`) plus `research_log.{json,md}` and `best/`.

## Jev grading configuration

`configs/verifiers/*.yaml`:

| field | meaning |
|---|---|
| `backend`, `model`, `effort` | judge model |
| `mode` | `batched` (one call, all criteria) or `per_criterion` |
| `samples`, `aggregate` | independent judge samples per criterion; `majority` / `all` / `any` |
| `include_grader_notes`, `include_workspace`, `max_workspace_chars` | what the judge sees |
| `all_pass_required`, `pass_threshold` | task-level scoring (Harvey LAB uses all-pass) |

Verdicts are binary per criterion; `negative` criteria pass when the deliverable avoids the error.

## Package acceptance (`data/harvey/package.yaml`)

- at least 10 criteria per task, each atomic and binary
- reference models (GPT 6.1 Sol, Opus 5.5) must average < 75% criteria pass rate
- >= 70% of tasks must pass a practicing lawyer's QA (realistic, legally sound)
