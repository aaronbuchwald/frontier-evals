# Grader notes (hidden from the solver)

## Governing law

ERISA § 724 (29 U.S.C. § 1185m), added by CAA 2021, Div. BB, Title II, § 201 (the
"transparency" title - not the No Surprises Act, which is Title I). Parallel: PHSA § 2799A-9,
IRC § 9824. Halvorsen's plan is a self-funded ERISA plan, so § 724 governs (and § 9824 for
excise-tax purposes). Meridian, a TPA, is the counterparty "third-party administrator or other
service provider offering access to a network"; the prohibition runs against the *plan*
entering into the agreement. There are no implementing regulations; the Departments have
proceeded through FAQs (Part 57, Feb. 2023; Part 69, Jan. 2025) and the HIOS GCPCA
instructions. ERISA § 502 has no gag-clause-specific civil penalty.

## The planted issues and intended answers

### 1. Clear violations in Article 9

- **§ 9.4** consent right over sharing with consultants/auditors (business associates):
  prohibited by § 724(a)(1)(C). The Departments treat access or sharing "at the discretion of"
  the TPA as the paradigm gag clause. The "Competitor" carve-out (§ 1.3 - every consultant,
  auditor and TPA in the country) makes it worse. The TPDUA that § 9.4 requires (doc 08) adds
  its own restrictions: approved-purpose-only (no benchmarking/repricing unless approved),
  "not a Competitor" rep, and § 3 "shall not disclose the Data to Client except in aggregated
  form approved by Meridian" - i.e., a restriction on the Plan's own access through its BA.
- **§ 9.5** bar on the Plan Sponsor disclosing provider-specific rates/allowed amounts/quality
  ratings to participants, network providers, referring providers: prohibited by (a)(1)(A).
  The "or the public" piece can survive under (a)(2) (reasonable restrictions on *public*
  disclosure), which applies only to (1)(A) information - not to (B)/(C) access or sharing.
- **§ 9.6** audit caps (once per year, 250-claim sample, Meridian's methodology,
  premises-only / view-only portal): the Departments have identified sample/number caps,
  frequency limits and premises-only access as prohibited restrictions on electronic access.
  Nuance a good memo may add: § 724 does not itself grant an audit right, but 9.6 operates by
  limiting what claims data the Plan's auditor (a BA) may access, which is what (B)/(C)
  protect. The intended conclusion is "prohibited", not "gray area".
- **§ 12.5 / § 9.8**: transition data only in standard format and "subject to 9.4 and 9.5",
  which survive three years - so a successor TPA (a "Competitor") cannot receive claim-level
  data without Meridian's consent. Must be fixed in the amendment.

### 2. The genuinely unsettled part - § 9.3

The statute requires that the plan not be restricted from "electronically accessing
de-identified claims and encounter information ... upon request ... including, on a per claim
basis" allowed amounts, provider name and clinical designation, service codes. It says nothing
about format, mechanism, timing or price. Meridian's "standard extract" omits exactly the
enumerated per-claim elements; getting them requires a "custom extract" at ~$140-160k with a
180-day lag from an acceptance that has no deadline, and Meridian may decline any extract that
would reveal "Proprietary Information" (defined in § 1.4 to include Allowed Amounts).

Intended answer: silence on price/format means a reasonable, cost-based charge or a standard
electronic format is not per se unlawful; but the combination here (statutory fields excluded
from standard access, six-figure fee, open-ended acceptance + 180 days, decline right keyed to
the statutory fields) functions as an indirect restriction and is likely prohibited. The
"proprietary" label is not a defense; the statute names allowed amounts and provider identity.

### 3. Upstream source of the restriction - Continental § 4.3 (doc 11)

Meridian Choice is Continental's network. Continental-Meridian § 4.3 bars Meridian from
disclosing, or *permitting any Client Plan to disclose*, Continental Rates or claim-level
allowed amounts to the plan's consultants, auditors or competing administrators without
Continental's sole-discretion consent, and requires Meridian to put equivalent terms in every
ASA. That is why §§ 9.4/9.5/1.4 look the way they do and why Delacroix "cannot" consent. The
Departments have said that a restriction in a TPA's agreement with another party can put the
plan out of compliance and expect plans to address this contractually. Consequences:
(i) the amendment needs Continental's consent/waiver or a Meridian rep and covenant that
Continental has waived § 4.3 for this Plan; (ii) the negotiation must reach Meridian legal and
Continental network management, not account management; (iii) Meridian's November 2024
confirmation spoke only to "Meridian's provider network agreements" and did not address the
intercompany agreement. § 4.2(b) ("to the extent required by applicable law") does not help
because § 4.3 separately bars sharing with the Plan's BAs. § 9.6 (no third-party
beneficiaries) means the Plan cannot enforce § 4.4/4.5 directly.

### 4. Traps

- **De-identification** is about participants/beneficiaries (45 C.F.R. § 164.514); it is
  not a basis to strip provider NPIs/names or allowed amounts (BAA § 2.4 is a hint).
- **§ 9.7 savings clause**: Meridian's "no gag clause by definition" fails. The second
  sentence is triggered only on a court/agency determination; the provisions remain operative
  and are being applied; the Departments expect removal or reporting.
- **§ 12.4 Changes in Law** does not apply: § 724 was enacted December 27, 2020, before the
  January 1, 2024 Effective Date. Amendment is by § 12.3 (mutual agreement) under negotiating
  pressure, or § 12.2 (material breach - arguable, aggressive).
- **Non-renewal notice** (October 2, 2026) has passed; the ASA renews for 2027. A
  termination threat has no teeth for 2027; leverage is the attestation disclosure, DOL
  exposure, fiduciary posture, the 2028 market check, and Continental's own § 4.4/4.5 and
  § 9.3 compliance language.
- **Meridian is not "in violation"**: it is the counterparty; the Plan is the regulated party
  and attests.
- **Cordell period**: Northgate asks for October 1, 2023 - September 30, 2026. Meridian's
  records start January 1, 2024; Q4 2023 (and run-out through March 2024) is in the Cordell
  final claims file already on the shared drive (with allowed amounts and NPIs, outside the
  Meridian ASA). Meridian's extract should be scoped to January 2024 onward.

### 5. HIPAA structure of the data flow (docs 04, 09, 10)

- Northgate's field list includes full dates of service and received/paid dates. Under the
  safe harbor (§ 164.514(b)(2)(i)(C)) all elements of dates except year directly related to
  an individual must be removed; service dates are such dates. So the data set as drafted is
  not de-identified. Compliant routes: (a) limited data set (§ 164.514(e): dates permitted,
  direct identifiers removed) under a data use agreement for health care operations;
  (b) PHI disclosed to Northgate/Claimsight as the Plan's business associates for the Plan's
  health care operations (BAA § 3.2 already requires Meridian to make PHI available to "a
  person designated by Covered Entity" for evaluating Meridian's performance); (c) expert
  determination. Note § 724(a)(1)(B) is itself "consistent with" HIPAA, and (a)(4) preserves
  HIPAA-permitted access, so this structure is not a work-around; it is the intended design.
- Plan § 8.7 / § 164.504(f): PHI may go to the plan sponsor for plan administration functions
  only to Appendix B personnel (Director Benefits, Benefits Analyst, Payroll Benefits
  Specialist, GC for limited purposes). The CFO's request to circulate the full claim-level
  file to Committee members is not permissible unless the file is HIPAA de-identified
  (year-only dates, etc.) or is summary health information. Correct advice: BAs hold the
  PHI/limited data set; the Committee gets Northgate's analysis and, if it wants row-level
  data, a de-identified version.

### 6. Attestations

The plan must attest annually by December 31 (HIOS GCPCA). Meridian may decline to attest for
self-funded clients; the obligation stays with the plan. The 2024 and 2025 attestations were
unqualified while Article 9 was in force - an inaccurate attestation is an exposure (and the
CFO has flagged discomfort). There is no formal "amended attestation" procedure in the
guidance; sensible advice is to document the reliance on Meridian's November 2024
confirmation, correct the record (voluntary supplement/disclosure and/or describe the history
in the 2026 Additional Information field), and build a remediation file. For 2026: must still
submit; if unremediated, identify the provisions, Meridian's refusal, and steps taken in the
Additional Information text box.

### 7. Exposure - the realistic number (CFO's question)

- ERISA: fiduciary exposure (duty to monitor Meridian; reasonableness of ~$2.1M fees and
  ~$71M claims spend; documentation); DOL enforcement of § 724 under its general civil
  enforcement authority. No ERISA per-day penalty for § 724.
- IRC § 4980D: $100/day per individual to whom the failure relates for a Chapter 100
  (§ 9824) failure, self-reported by the employer on Form 8928. $100 x ~14,800 lives is
  ~$1.48M/day - a meaningless headline figure. For failures due to reasonable cause and not
  willful neglect, § 4980D(c)(3) caps the tax for the taxable year at the lesser of 10% of
  the employer's prior-year group health plan payments or $500,000 - here $500,000 per
  taxable year. § 4980D(c)(4) allows the Secretary to waive part or all where the tax would
  be excessive relative to the failure. § 4980D(c)(1) (no tax where the failure was unknown
  and undiscoverable with reasonable diligence) is weak because Article 9 was on the face of
  a contract the Plan signed in December 2023 and Ms. Raman did not compare it to the
  statute; § 4980D(c)(2) (no tax if corrected within 30 days of actual/constructive
  knowledge) likely ran from December 2023 or, at the latest, from Meridian's September 18,
  2026 application of the restrictions (expiring about October 18, 2026) - so it is probably
  unavailable, which is why prompt correction, the cap, the waiver and a documented
  reasonable-cause record (Meridian's confirmation) matter. If uncorrected, Form 8928 is due
  with the employer's income tax return.

### 8. Northgate engagement (docs 05, 12)

- **Conflict**: $150,000 transition fee payable only if the Plan leaves Meridian gives
  Northgate a stake in the market-check outcome. The Committee should recognize, document and
  manage it (renegotiate to a flat implementation fee, require independent validation of the
  benchmarking, or discount accordingly). It also feeds Meridian's "Competitor" narrative.
- **ERISA § 408(b)(2)(B)** (CAA 2021 § 202): consultants to group health plans expecting
  $1,000+ must disclose in writing, reasonably in advance of contracting, services, fiduciary
  status, direct and indirect compensation (including arrangement and payer), related-party
  compensation and termination compensation. SOW § 7 is in the contract itself, not in
  advance, and describes the Marketplace fees only generically although Marketplace
  participants may respond to the RFP. The Committee should obtain a compliant disclosure in
  writing; the responsible-fiduciary relief requires a written request and DOL notice if not
  provided within 90 days.
- **Meridian Advisory Services' free report**: the monitored vendor's affiliate evaluating
  its own affiliate's network cannot discharge the monitoring duty; at most a supplement.

### 9. Amendment ask

Delete 9.4 consent right (replace with BAA + reasonable confidentiality undertaking, no
Competitor test, no Meridian-approved purpose, no aggregated-only limit); specify per-claim
elements including allowed amount, provider name/NPI/clinical designation, service codes;
standard electronic delivery (SFTP/flat file) within a defined period (e.g., 30 days) at no
charge or a cost-based fee; delete the 9.3 "decline" right and the § 1.4 Allowed-Amount
carve-out; conform 9.5 to (a)(2) (public disclosure only); delete 9.6 caps (audits "upon
request", full population, remote electronic access); fix 12.5/9.8; Meridian rep and covenant
that no Meridian agreement (including the Continental network access agreement and Continental
provider agreements) restricts the Plan's § 724 rights, with Continental's written waiver of
§ 4.3 for this Plan; Meridian cooperation with and support for the attestation; indemnity.

## Common wrong answers

- Treating portal access to aggregated reports as satisfying (a)(1)(B).
- Asserting any fee or any delay is per se illegal, or the reverse (silence on price means
  the fee/lag terms are fine).
- Advising Halvorsen to withhold the 2026 attestation until the contract is fixed.
- Saying Meridian is "in violation of § 724".
- Invoking § 12.4 changes-in-law.
- Suggesting provider identifiers can be redacted as part of de-identification.
- Calling the Northgate request "de-identified" without noticing the dates of service.
- Endorsing circulation of the raw claim-level file to the Committee/CFO.
- Quoting $100/day x covered lives as the exposure without the § 4980D(c)(3) cap, or
  assuming a fresh 30-day correction window starts now.
- Asking Meridian for all 36 months when the first three are Cordell's.
- A generic "downstream provider contracts" representation that never engages with
  Continental § 4.3.
- Citing a nonexistent 29 C.F.R. § 2590.724 regulation or an ERISA per-day penalty.
- Treating Northgate as unconflicted / ignoring § 408(b)(2)(B).
