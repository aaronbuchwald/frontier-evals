# Grader notes (hidden from the solver)

## The planted issues and intended answers

**Governing law.** ERISA § 724 (29 U.S.C. § 1185m), added by CAA 2021, Div. BB, Title II,
§ 201 (the "transparency" title, not the No Surprises Act surprise-billing provisions in
Title I). Parallel: PHSA § 2799A-9, IRC § 9824. Halvorsen's plan is a self-funded ERISA
plan, so § 724 (and § 9824 for excise tax purposes) governs. Meridian, a TPA, is the
counterparty "third-party administrator or other service provider offering access to a
network"; the prohibition runs against the *plan* entering into the agreement.

**Clear violations in Article 9.**
- § 9.4 consent right over sharing with consultants/auditors (business associates): prohibited
  by § 724(a)(1)(C). FAQs Part 57 Q2 and Part 69 Q7: sharing or access "at the discretion of"
  the TPA is the paradigm gag clause. The "Competitor" carve-out makes it worse, not better.
- § 9.5 bar on the Plan Sponsor disclosing provider-specific rates/allowed amounts/quality
  ratings to participants, network providers, referring providers: prohibited by (a)(1)(A).
  The "or the public" piece could survive under the (a)(2) exception (reasonable restrictions
  on *public* disclosure), which applies only to (1)(A) information.
- § 9.6 audit caps (once per year, 250-claim sample, Meridian's methodology, on-premises /
  view-only): FAQs Part 69 Q8 lists exactly these ("statistically significant"/minimum sample
  limits, frequency limits, purpose limits, premises-only access) as prohibited restrictions
  on electronic access.

**The genuinely unsettled part - § 9.3.** The statute requires that the plan not be
restricted from "electronically accessing de-identified claims and encounter information ...
upon request ... including, on a per claim basis" allowed amounts, provider name and clinical
designation, service codes, and any other data element. It says nothing about format,
mechanism, timing or price. Meridian's "standard extract" omits exactly the enumerated
per-claim elements; getting them requires a "custom extract" at ~$140-160k with a 180-day
lag from an acceptance that has no deadline, and Meridian reserves the right to decline any
extract that would reveal "Proprietary Information" (defined to include allowed amounts).
Intended answer: the statute's silence on price/format means a reasonable, cost-based
charge or a standard electronic format is not per se unlawful; but the combination here
functions as an indirect restriction on the enumerated per-claim elements and is likely
prohibited. FAQs Part 69 Q8 ("unreasonable limits" on scope, scale, frequency; restricting
data elements) supports this, and Part 57 Q2 rejects "proprietary" as a justification.

**Traps.**
- De-identification is about participants/beneficiaries (HIPAA 45 C.F.R. § 164.514 safe
  harbor or expert determination); it is not a basis to strip provider NPIs/names or allowed
  amounts. The BAA § 2.4 excerpt is a hint.
- § 9.7 savings clause: Meridian's "no gag clause by definition" argument fails. The clause
  is triggered only on a determination by a court/agency, the provisions remain operative and
  are being applied, and the Departments expect removal or reporting (Part 69 Q9).
- § 12.4 "Changes in Law" does not apply: § 724 was enacted December 27, 2020 (and applied
  to agreements from that date), before the ASA's January 1, 2024 effective date. Amendment
  must come through § 12.3 (mutual agreement) under negotiating pressure, or § 12.2
  (material breach - arguable but aggressive).
- The non-renewal notice date (90 days before December 31, 2026 = October 2, 2026) has
  passed; the ASA renews for 2027. A termination threat has no teeth for 2027.

**Attestations.** The plan must attest annually by December 31 (HIOS GCPCA). Meridian may
decline to attest for self-funded clients; the obligation stays with the plan (Part 57 Q9).
The 2024 and 2025 attestations were unqualified while Article 9 was in force - an inaccurate
attestation is an exposure (and the CFO has flagged discomfort). There is no formal
"amended attestation" procedure in the guidance; sensible advice is to document the
reliance on Meridian's November 2024 confirmation, correct the record (voluntary
supplement/disclosure, and/or describe the history in the 2026 Additional Information
field), and build a remediation file. For 2026: must still submit (Part 69 Q9); if
unremediated, identify the provisions, Meridian's refusal, and steps taken in the
"Additional Information" text box; the Departments will consider good-faith self-reporting
in any enforcement.

**Exposure.** ERISA fiduciary exposure (duty to monitor Meridian, reasonableness of the
~$2.1M fees and $71M claims spend, documentation); DOL enforcement of § 724; IRC § 4980D
excise tax ($100/day/affected individual) for a Chapter 100 failure (§ 9824), self-reported
on Form 8928 - theoretical but real for the sponsor.

**Northgate / Claimsight.** Both should sign BAAs with the Plan (Northgate already offered).
§ 724(a)(1)(C) protects sharing with, or directing that data be shared with, business
associates; the Competitor carve-out cannot be used to refuse. Meridian may legitimately ask
for reasonable confidentiality protections for its rates (a BAA-level undertaking, no public
disclosure), but not a purpose restriction that blocks benchmarking or the market check, and
not a Meridian-approved-aggregates-only limitation like TPDUA § 3.

**Amendment ask.** Delete 9.4 consent right (replace with BAA + reasonable confidentiality);
specify per-claim elements including allowed amount, provider name/NPI/clinical designation,
service codes; standard electronic delivery (SFTP/flat file) within a defined period (e.g.,
30 days) at no charge or cost-based fee; delete the 9.3 "decline" right; conform 9.5 to
(a)(2) (public disclosure only); delete 9.6 caps (audits "upon request", full population,
remote electronic access); downstream-agreement representation and covenant (Part 69 Q6);
Meridian cooperation with attestation; Meridian attestation support/indemnity.

## Common wrong answers
- Treating portal access to aggregated reports as satisfying (a)(1)(B).
- Asserting any fee or any delay is per se illegal (over-reading), or the reverse: that
  because the statute is silent on price the fee/lag terms are fine.
- Advising Halvorsen to withhold the 2026 attestation until the contract is fixed.
- Saying Meridian is "in violation of § 724" (it is the counterparty, not the regulated plan).
- Invoking § 12.4 changes-in-law.
- Suggesting provider identifiers can be redacted as part of de-identification.
