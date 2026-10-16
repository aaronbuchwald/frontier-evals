Revise the existing task in place in the directory `task/` of the current working directory, following the package format exactly.

## Package format specification
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


## Package acceptance constraints
- at least 10 criteria, each atomic and binary
- reference models (gpt-6.1-sol, claude-opus-5-5) should pass fewer than 75% of criteria on average: the task must contain genuine difficulty (ambiguity in the law, planted traps, multi-document synthesis), not obscurity or trick wording
- a practicing lawyer must agree the task is realistic and the law is stated correctly (QA pass rate target 70%)

## Task idea and edge case
# Task idea: gag clause prohibition vs. "how" de-identified claims data must be provided

**Practice area:** ERISA / health & welfare benefits; CAA 2021 transparency provisions
(commonly discussed together with the No Surprises Act).

**Idea.** A self-funded employer plan wants its claims data (per-claim allowed amounts,
provider identifiers, service codes) to benchmark its TPA and run a market check. The TPA's
administrative services agreement doesn't flatly forbid access, but makes the enumerated
per-claim fields available only as a paid, slow "custom extract", reserves a right to decline
extracts that reveal "proprietary" pricing, requires the TPA's consent before data goes to
any consultant or auditor (and defines consultants as "Competitors"), and caps audits at a
small annual sample. A savings clause says nothing in the contract restricts access in a
manner the law prohibits.

**Edge case / ambiguity.** ERISA § 724 (29 U.S.C. § 1185m) / PHSA § 2799A-9 / IRC § 9824
prohibit a plan from agreeing to terms that "directly or indirectly restrict" it from
electronically accessing de-identified claims data on a per-claim basis, but prescribe no
format, mechanism, turnaround, or price. Where do commercial terms (fees, lags, standard
formats, confidentiality of rates) end and "indirect restrictions" begin? The Departments'
FAQs (Part 57, Feb. 2023; Part 69, Jan. 2025) give examples (consent/discretion of the TPA,
"statistically significant" sample caps, frequency limits, premises-only access, "proprietary"
labels) but not a rule.

**Traps worth planting.** De-identification is about participants, not providers; a
general "compliance with law" savings clause does not remove the provisions; the plan - not
the TPA - is the regulated party and must attest; attestations already filed may be
inaccurate; the plan must still attest even if the TPA won't fix the contract (Additional
Information field); a "changes in law" clause doesn't apply to a 2020 statute; IRC § 4980D
excise tax exposure; downstream TPA/provider agreements.

**Expected difficulty.** Frontier models reliably spot the consent and participant-disclosure
clauses but tend to (i) over- or under-read the statute's silence on format and price,
(ii) miss the attestation mechanics in the FAQs, (iii) miss § 4980D, and (iv) fall for the
de-identification and changes-in-law traps.


## Feedback on the previous attempt


A strong solver model attempted the task in 2 fresh session(s); mean criteria pass rate = 98%.
Criteria the solver always passed (consider whether they test anything hard, or sharpen them): c01, c02, c03, c04, c06, c07, c08, c09, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22

Excerpt of the solver's deliverable (so you can see what it got right and where it was shallow):
```
**PRIVILEGED AND CONFIDENTIAL — ATTORNEY-CLIENT COMMUNICATION — ATTORNEY WORK PRODUCT**

# MEMORANDUM

**To:** Dana Okafor, General Counsel, Halvorsen Industrial Group, Inc.
**From:** Lindqvist Vale (M. Lindqvist; prepared by associate)
**Date:** October 16, 2026
**Re:** Meridian Administrative Services Agreement: CAA gag clause analysis, Northgate/Claimsight data request, GCPCA attestations, and amendment strategy (for the October 28, 2026 Benefits Committee meeting)

---

## I. EXECUTIVE SUMMARY

**Bottom line.** In our view, Article 9 of the Meridian ASA contains several provisions that the gag clause rule in ERISA § 724 (29 U.S.C. § 1185m; parallel PHSA § 2799A-9 and IRC § 9824) prohibits. The savings clause in Section 9.7 does not cure them. The Plan's two unqualified "in compliance" attestations for 2024 and 2025 were therefore very likely inaccurate. They were made in good faith, though, and the realistic exposure is manageable if the Plan acts promptly now. The Plan should not file another unqualified attestation on December 31 unless Meridian has signed an amendment, and even then the filing will need an explanation. The ASA has already renewed automatically for 2027 (the October 2, 2026 non-renewal date has passed). The Plan's leverage therefore comes from the law, from Meridian's own written positions, and from the 2028 market check, not from a threat to leave at year-end.

**1. Does Article 9 contain prohibited gag clauses?** Yes. In order of confidence:

| Provision | What it does | Prohibited? | Confidence |
|---|---|---|---|
| **§ 9.4** (with § 1.3 "Competitor") | Plan cannot share Claims Data with any consultant, auditor, actuary, broker or successor administrator without Meridian's consent. Consent may be withheld from any "Competitor", a term broad enough to cover every benefits consultant, claims auditor and TPA in the U.S. Consent also requires Meridian's form TPDUA and a Meridian-approved purpose. | Yes, as applied to Claims Data shared with the Plan's business associates (§ 724(a)(1)(C)) | **High** |
| **§ 9.5** | Plan may not disclose provider-specific rates, Allowed Amounts or provider quality ratings to Participants, Network Providers or referring providers. | Yes as to Participants and referring providers (§ 724(a)(1)(A)). The "public" restriction is likely permissible under § 724(a)(2) if reasonable. | **High** (public prong: permissible) |
| **§ 9.3, last sentence** | Meridian may decline any custom extract that would disclose "Meridian Proprietary Information". Under § 1.4 that term *includes Allowed Amounts* and any compilation of Claims Data that would reveal them. | Yes. It gives Meridian a veto over exactly the data elements § 724(a)(1)(B)(i)–(ii) names. | **High** |
| **§ 9.3, fee/timing/acceptance mechanics** | Statutory fields (allowed amount, provider name/NPI) are excluded from "standard" access. They cost $18,500 + $0.11/line (about $140–160k here) and arrive 180 days after a "written acceptance" that has no deadline. | Likely an indirect restriction when the terms are taken together. The law is unsettled on whether a reasonable fee or delivery period standing alone is a gag clause. | **Moderate** (combined); **Low/unsettled** (fee or timing standing alone) |
| **TPDUA (Form TPDUA-2023.2)**, required by §§ 9.4 and 9.6 | Recipient may not give the Plan anything except aggregated data that Meridian approves (§ 3). It also bars benchmarking/repricing outside a Meridian-approved purpose (§ 1) and requires a "not a Competitor" representation (§ 2). | Yes. It restricts the Plan's own access through its business associate and its use of its own data. | **High** |
| **§ 12.5** (transition) and **§ 9.8** (survival) | Transition data comes only in Meridian's standard format and "subject to Sections 9.4 and 9.5". Those sections survive termination by 3 years, which reaches the successor TPA, itself a "Competitor". | Yes, to the extent it imports § 9.4/9.5 restrictions on sharing with a successor administrator (a business associate). | **High** (as to § 9.4 linkage) |
| **§ 9.6** (audits) | Audits are limited to 250 claims chosen by Meridian's methodology, once a year, by a non-Competitor auditor that signs the TPDUA, through a view-only portal. | The Competitor and TPDUA conditions likely are prohibited. The sample cap and view-only limits are a gray area. They are vulnerable if Meridian uses them to cap the auditor's access to claims data, but the statute does not itself grant audit rights. | **Moderate** ((b)); **Low–moderate** ((a), (c)) |
| **§§ 1.4, 9.1** | Allowed Amounts are defined as Meridian's property "notwithstanding that [they] may be embedded in" Plan-owned Claims Data. | Not a standalone gag clause, but this is the definitional hook for the restrictions above. Must be fixed. | n/a |
| **§ 9.2** | Standard Reports are aggregated. | Not a gag clause (it describes a deliverable). | **High** that it is permissible |

Section 9.7 does not change the result. It applies only on a court's or agency's "determination". It speaks only to "access", not to sharing (§ 9.4) or disclosure (§ 9.5). And Meridian is invoking the restrictive provisions right now to deny access. We know of no regulatory guidance treating a generic savings clause as curing a specific restriction, and we think the better reading is that it does not.

**2. Northgate and Claimsight.** Contractually, § 9.4 lets Meridian refuse consent for Northgate as a "Competitor". Legally, we believe that veto is a prohibited gag clause as applied to a Plan business associate, and Meridian cannot lawfully use it to keep Northgate from receiving the Plan's data. **Meridian's legitimate interest in its rates can be protected by confidentiality terms. It does not support a veto.** We recommend restructuring the request before pressing it:

- **(a)** Northgate's field list, as written, is probably *not* HIPAA de-identified under the safe harbor because it includes full dates of service, received dates and
```

Reasons the attempt was not accepted:
- too easy: solver mean pass rate 98% >= target max 75%

## What to write
Task id: `caa-gag-clause-deidentified-claims-access`. The existing task files are already in `task/`; read them all first, keep what works, and revise in place (edit files, add documents or criteria, sharpen criteria that the solver passed trivially, add fair criteria for issues a careful lawyer would address but the solver missed, add negative criteria for errors the solver actually made). Keep the task realistic: never add obscure trivia or trick wording just to lower the pass rate.
- `task.yaml` (id, title, package, instruction, deliverables, workspace manifest with roles and descriptions, metadata incl. edge_case)
- `criteria.yaml`
- `workspace/...` the matter documents (emails, contract excerpts, memos, statutory excerpts, peripheral files). Make them realistic, dated, internally consistent, and long enough to require real reading. Use fictional parties.
- `grader_notes.md` (hidden from the solver): the intended answer, why each criterion is right, and common wrong answers.
Do not write anything outside `task/`. When finished, reply with a one-paragraph summary of the planted issues.