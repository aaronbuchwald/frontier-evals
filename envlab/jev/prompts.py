"""Prompt templates for the Jev judge."""
from __future__ import annotations

JUDGE_SYSTEM = """You are a meticulous senior lawyer acting as a rubric grader for legal work product.
You grade atomic, binary criteria. For each criterion decide PASS or FAIL strictly on what the
deliverable actually says. Do not reward hedging, vague gestures, or correct ideas that are
stated too generally to satisfy the criterion. Do not penalise a deliverable for omitting
things the criterion does not ask for. Quote the specific sentence(s) from the deliverable
that support each verdict, or state that nothing in the deliverable addresses it.
For criteria marked NEGATIVE (things the deliverable must NOT do), PASS means the deliverable
avoided the error."""

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
                    "rationale": {"type": "string"},
                    "evidence": {"type": "string"},
                },
                "required": ["id", "verdict", "rationale", "evidence"],
            },
        }
    },
    "required": ["verdicts"],
}


def judge_prompt(*, instruction: str, workspace_docs: str | None, deliverables: str, criteria_lines: str,
                 grader_notes: str | None) -> str:
    parts = ["## Partner request\n", instruction.strip(), "\n"]
    if workspace_docs:
        parts += ["## Matter workspace (what the associate had access to)\n", workspace_docs, "\n"]
    parts += ["## Deliverables (the work product being graded)\n", deliverables, "\n"]
    if grader_notes:
        parts += ["## Grader notes (hidden from the associate; use to inform your judgment)\n", grader_notes.strip(), "\n"]
    parts += [
        "## Criteria\n",
        "Grade each criterion below as PASS or FAIL. Criteria are listed as `- [id] text`.\n",
        criteria_lines,
        "\nReturn one verdict per criterion id, in the same order.",
    ]
    return "\n".join(parts)
