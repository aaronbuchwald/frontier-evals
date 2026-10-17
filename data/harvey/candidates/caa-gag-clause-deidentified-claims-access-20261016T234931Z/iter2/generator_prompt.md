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


A strong solver model attempted the task in 1 fresh session(s); mean criteria pass rate = 94%.
Criteria the solver always passed (consider whether they test anything hard, or sharpen them): c01, c02, c03, c06, c07, c08, c09, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22, c23, c24, c25, c26, c27, c28, c29, c30, c31, c32
Criteria the solver always failed (make sure they are fair, verifiable and not trick questions): c04, c05

Excerpt of the solver's deliverable (so you can see what it got right and where it was shallow):
```
# MEMORANDUM

**PRIVILEGED AND CONFIDENTIAL — ATTORNEY-CLIENT COMMUNICATION / ATTORNEY WORK PRODUCT**

| | |
|---|---|
| **To** | Dana Okafor, General Counsel, Halvorsen Industrial Group, Inc. |
| **From** | Lindqvist Vale (prepared for M. Lindqvist's review) |
| **Date** | October 17, 2026 |
| **Re** | Meridian ASA — CAA gag clause analysis, Northgate data request and Claimsight audit, GCPCA attestations, exposure, and recommended amendment and negotiation strategy (for the October 28, 2026 Benefits Committee meeting) |

> **A note on privilege before you circulate this.** Courts applying ERISA generally recognize a "fiduciary exception" to attorney-client privilege. Advice to plan fiduciaries about how to administer the plan can be discoverable by participants. Advice about the Company's own liability generally stays privileged. Parts I–V and VIII of this memo are mostly plan-administration advice. Part VI (excise tax exposure) concerns a tax that falls on the **Company as employer** (IRC §4980D(e)). We recommend presenting Part VI to the Committee orally or in a separate Company-addressed memo, and not attaching it to the Committee minutes.

---

## I. EXECUTIVE SUMMARY

**Bottom line.** In our view the Meridian ASA contains provisions prohibited by ERISA §724 (29 U.S.C. §1185m; parallel IRC §9824). Three are clear: the "Meridian Proprietary Information" veto in §9.3, the consent and "Competitor" bar in §9.4, and the participant and referring-provider restrictions in §9.5. Section 9.7's compliance-with-law clause does not cure them. Meridian is relying on those provisions right now to refuse access, which shows the restriction is real. The ASA has already auto-renewed through December 31, 2027. So the Plan's leverage is legal and compliance-based rather than commercial, and the next step is to go to Meridian's legal department with a proposed amendment. **The Plan should not file another unqualified "in compliance" attestation on December 31, 2026 under any scenario.** The 2026 attestation period began December 20, 2025, and the gag clauses were in force for at least most of that period whether or not Meridian amends.

**1. Does Article 9 contain prohibited gag clauses?** Yes. Our confidence varies by provision:

| Provision | Our view | Confidence |
|---|---|---|
| §9.3: Meridian may *decline* any custom extract that would disclose "Meridian Proprietary Information." That term is defined to include Allowed Amounts and provider rates, which are exactly the per-claim fields §724(a)(1)(B)(i)–(ii) guarantees. | Prohibited. It leaves access to statutorily protected data to the TPA's discretion. The Departments' FAQ guidance gives TPA discretion over access as its example of a gag clause. | **High** |
| §9.4: the Plan may not disclose Claims Data, or *direct Meridian to disclose* it, to any consultant, auditor, broker or successor TPA without Meridian's consent. Consent is unavailable for any "Competitor," and every benefits consultant and claims auditor is one. | Prohibited as applied to the Plan's business associates. It is close to a mirror image of §724(a)(1)(C), which protects "sharing ... or directing that such data be shared, with a business associate." | **High** |
| §9.5: the Plan may not disclose provider-specific rates, Allowed Amounts or quality ratings to **Participants** or **referring providers**. | Prohibited. §724(a)(1)(A) names both groups. The bar on disclosure **to the public** is permissible under §724(a)(2). | **High** (participants and referring providers); permissible (public) |
| §9.8 survival and §12.5 transition, which keep §§9.4–9.5 alive for 3 years and make delivery of data to a successor TPA "subject to" them | Prohibited to the same extent as §§9.4 and 9.5. Practically, this is the most dangerous provision for a 2028 transition. | **High** |
| §9.3: 180-day delivery that runs from Meridian's "written acceptance," with **no deadline to accept** | Likely an indirect restriction, because access becomes open-ended at Meridian's option. | **Moderate–High** |
| §9.3: custom-extract fee ($18,500 + $0.11/line, about $140–160K for this request), charged only for the statutory fields | Unsettled. The statute is silent on fees. A reasonable, cost-based fee is probably permissible. A fee at "then-current" rates, aimed precisely at the statutory fields and equal to about 7% of annual admin fees, is vulnerable as an indirect restriction. | **Moderate / unclear** |
| §9.6: audit capped at 250 claims, Meridian's sampling, on-site or view-only | Audit-cooperation limits standing alone are probably commercial terms. The non-Competitor condition and the Third-Party Data Use Agreement (TPDUA) condition are problematic. §9.6 also cannot be read to stop the Plan from giving its auditor data the Plan is entitled to under §724. | **Low–Moderate** (cap itself); **High** (conditions) |
| §9.7: compliance-with-law savings clause | Does not cure. The clause covers only "access," not disclosure or sharing. Its modification mechanism requires a court or agency ruling first. And Meridian is enforcing the restrictive text. No guidance addresses savings clauses directly. | **Moderate–High** |
| Meridian's TPDUA (incorporated by §§9.4 and 9.6) | Indirect restriction. Among other things, it bars the recipient from giving the Data to the Plan except "in aggregated form approved by Meridian." | **High** |

The upstream Continental–Meridian network access agreement (§4.3) obligates Meridian to bar client plans from giving claim-level allowed amounts to "any consultant, broker, actuary, auditor" without Continental's sole-discretion consent. That is the source of §9.4. It also means Meridian's November 2024 written assurance that its agreements "do not contain gag clauses" was, at best, incomplete.

**2. Northgate and Claimsight.** Meridian cannot lawfully use the "Competitor" label to stop the Plan from sharing its claims data with a consultant or auditor acting as the Plan's business associate.
```

Lawyer QA review: pass=True realism=5/5 legal_soundness=5/5 criteria_quality=4/5
- [minor] workspace/04_northgate_data_request_2026-09-22.md vs. workspace/03_email_chain_raman_delacroix_2026-09.md: Date inconsistency: the Northgate request letter is dated September 22, 2026, but Raman's September 15 email says the 'formal data request is attached' and Delacroix's September 18 reply says he has reviewed 'the Northgate letter.' A careful solver will notice the letter post-dates the emails that discuss it. -> Re-date the Northgate letter to on or before September 14, 2026 (and rename the file accordingly), or move the Raman/Delacroix exchange to after September 22.
- [minor] Criterion c22: Compound criterion: it bundles (i) memo format addressed to Okafor, (ii) executive summary first, and (iii) explicit confidence language for each of 9.3, 9.4, 9.5 and 9.6. A memo could satisfy two of three and the grader has no guidance on partial credit. -> Split into two criteria: one for memo format + executive-summary-first, one for per-provision confidence/calibration language covering at least 9.3, 9.4, 9.5 and 9.6.
- [minor] Criterion c07 / edge-case description: The task description calls the 9.3 fee/lag/format terms 'genuinely unsettled,' while c07 requires the conclusion 'likely prohibited.' A well-calibrated memo that says 'unsettled, but on these facts the combination probably operates as an indirect restriction (moderate confidence)' should pass, but a literal grader could read 'unsettled/moderate' as failing c07. -> Add to the c07 grader note: a memo that characterises 9.3 as unsettled or moderate-confidence passes so long as it concludes the terms in combination more likely than not operate as an indirect restriction; only 'probably fine' or 'portal access satisfies (B)' fails.
- [minor] Criterion c23 grader note: The note says 'the $500,000 limb applies' but does not address that the § 4980D(c)(3) cap is per taxable year of the employer, so a memo that correctly aggregates 2024, 2025 and 2026 (up to $1.5M before any (c)(4) waiver) is giving the realistic ceiling and should not be marked down for exceeding $500,000. -> Add: 'The cap applies per taxable year; a memo that states $500,000 per year (e.g., up to ~$1.5M across 2024-2026, subject to (c)(4) waiver) passes.'
- [minor] Criterion c24 grader note: The scenario is dated October 17, 2026 and the note computes the (c)(2) 30-day window from September 18 as expiring 'about October 18.' A solver writing on the task date may reasonably say the window is still open for one day and advise immediate action; the note already says 'probably unavailable or nearly expired' but should make explicit that this is a pass. -> Add: 'A memo that notes the September 18 trigger and advises that the window closes on or about October 18 (i.e., is effectively unavailable because the contract cannot be amended in time) passes.'
- [minor] Criterion c01 grader note: Failing an otherwise correct memo solely because it uses the common shorthand 'No Surprises Act' for all of Division BB is strict. The line drawn ('the CAA includes the NSA' passes; 'the NSA's gag clause prohibition' fails) is defensible for a citation criterion, but graders should be told the ERISA § 724 / § 201 citation is the operative element. -> Keep the criterion but note that a memo correctly citing ERISA § 724 / Div. BB Title II § 201 passes even if it elsewhere loosely refers to Division BB as the 'No Surprises Act' package; fail only where the memo affirmatively places the prohibition within Title I.
- [minor] Criterion c05 grader note: The note attributes to the Departments a specific identification of claim-sample caps, audit-frequency limits and premises-only/view-only access as prohibited restrictions. That is consistent with my understanding of FAQ Part 69, but because the criterion does not require the solver to cite the FAQ, the pass/fail turns on the statutory 'directly or indirectly restrict ... electronically accessing ... per claim' standard, which independently supports the conclusion. Author should confirm the FAQ paraphrase before relying on it in grader training. -> Add a parenthetical cite to the specific FAQ Part 69 question relied on, or rephrase the note to ground the conclusion in the statutory text (a cap on claims the Plan's BA auditor may access, view-only, is a restriction on per-claim electronic access under (a)(1)(B)/(C)).

Reasons the attempt was not accepted:
- too easy: solver mean pass rate 94% >= target max 75%

## What to write
Task id: `caa-gag-clause-deidentified-claims-access`. The existing task files are already in `task/`; read them all first, keep what works, and revise in place (edit files, add documents or criteria, sharpen criteria that the solver passed trivially, add fair criteria for issues a careful lawyer would address but the solver missed, add negative criteria for errors the solver actually made). Keep the task realistic: never add obscure trivia or trick wording just to lower the pass rate.
- `task.yaml` (id, title, package, instruction, deliverables, workspace manifest with roles and descriptions, metadata incl. edge_case)
- `criteria.yaml`
- `workspace/...` the matter documents (emails, contract excerpts, memos, statutory excerpts, peripheral files). Make them realistic, dated, internally consistent, and long enough to require real reading. Use fictional parties.
- `grader_notes.md` (hidden from the solver): the intended answer, why each criterion is right, and common wrong answers.
Do not write anything outside `task/`. When finished, reply with a one-paragraph summary of the planted issues.