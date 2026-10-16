# Harvey-style task format

Each task is a directory under `tasks/` (or `candidates/` while under research):

```
<task_id>/
  task.yaml         # metadata + instruction + deliverables + workspace manifest
  criteria.yaml     # the rubric (Jev verifier input)
  workspace/        # closed-universe matter files the agent can read
  grader_notes.md   # hidden from the agent; shown to the judge
```

## task.yaml
- `id`, `title`, `package: harvey`
- `instruction`: ONE partner-to-associate request (40-120 words). An affirmative statement of
  what to review and what to produce, for whom, by when. No hints about the planted issues.
- `deliverables`: file names the agent must write (e.g. `memo.md`, `redline_notes.md`).
- `workspace`: manifest of files with `role` (`key` | `peripheral` | `reference`) and a one-line
  `description`. Key files contain the planted issues; peripheral files are realistic noise;
  reference files are statutes/regulations/firm templates.
- `metadata`: `practice_area`, `task_type`, `difficulty`, `edge_case` (the ambiguity the task
  turns on), `author`, `target_max_pass_rate`, `min_criteria`.

## workspace/
Realistic, dated, internally consistent documents: client emails, contract excerpts with
section numbers, correspondence with counterparties, minutes, prior filings, statutory text.
Use fictional parties. Issues should span several documents so the agent must synthesise.
Do not include the answer or the agency guidance the agent is expected to know.

## criteria.yaml
A list of **atomic, binary** criteria (minimum 10). Each has:
- `id` (`c01`...), `text` (one verifiable statement about the deliverable),
- `category`: `issue_spotting | legal_analysis | fact_use | citation | recommendation | format | negative`,
- `polarity`: `positive` (deliverable must do this) or `negative` (must NOT do this),
- `deliverable`: which file it is checked against, optional `grader_notes`, `tags`, `weight`.

Rules of thumb:
- One check per criterion. "Identifies X and explains Y and recommends Z" is three criteria.
- Reward calibrated analysis where the law is unsettled; penalise false certainty with
  negative criteria.
- Mix: a few criteria a competent associate always hits (format, obvious issue), several that
  need real synthesis across documents, and several that need current knowledge of agency
  guidance or practice. Target: strong frontier models pass < 75% on average.
- Every criterion must be defensible to a practicing lawyer as realistic and legally correct.

## grader_notes.md
The intended answer: the planted issues, why each criterion is right (with authority), and
the common wrong answers the judge should not accept.
