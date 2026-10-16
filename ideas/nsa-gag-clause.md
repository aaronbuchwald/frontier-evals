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
