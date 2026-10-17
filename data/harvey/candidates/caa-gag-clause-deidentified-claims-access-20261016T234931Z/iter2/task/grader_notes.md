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

Timeline the memo must work with: ASA signed December 2023, effective January 1, 2024;
Northgate letter September 22, 2026; Raman request September 23; Delacroix refusal
September 25; Delacroix non-renewal reminder September 28; Committee meeting September 30
(Committee elects not to give non-renewal notice); non-renewal deadline October 2 passes;
Meridian proposed amendment October 9 (fee waiver if signed by October 30); GC request
October 14; memo on or about October 17; Committee October 28; attestation due December 31.

## The planted issues and intended answers

### 1. Clear violations in the original Article 9

- **§ 9.4** consent right over sharing with consultants/auditors (business associates):
  prohibited by § 724(a)(1)(C). The Departments treat access or sharing "at the discretion of"
  the TPA as the paradigm gag clause. The "Competitor" carve-out (§ 1.3 - every consultant,
  auditor and TPA in the country) makes it worse. The TPDUA that § 9.4 requires (doc 08) adds
  its own restrictions: approved-purpose-only (no benchmarking/repricing unless approved),
  "not a Competitor" rep, and § 3 "shall not disclose the Data to Client except in aggregated
  form approved by Meridian" - i.e., a restriction on the Plan's own access through its BA -
  and "shall not disclose ... to Client's other vendors", which blocks Northgate passing the
  data set to Claimsight (SOW § 1.3).
- **§ 9.5** bar on the Plan Sponsor disclosing provider-specific rates/allowed amounts/quality
  ratings to participants, network providers, referring providers: prohibited by (a)(1)(A).
  The "or the public" piece can survive under (a)(2) (reasonable restrictions on *public*
  disclosure), which applies only to (1)(A) information - not to (B)/(C) access or sharing.
- **§ 9.6** audit caps (once per year, 250-claim sample, Meridian's methodology,
  premises-only / view-only portal). Statutory grounding: (B) protects per-claim electronic
  access "upon request"; (C) protects sharing with a BA; a clause limiting the auditor-BA to
  a 250-claim sample, once a year, on premises or view-only restricts quantity, frequency and
  mode of per-claim electronic access. The Departments' FAQs Part 69 address terms of this
  kind (sample / number-of-claims limits, frequency limits, premises-only access) as
  restrictions. Nuance a good memo may add: § 724 covers *de-identified* data and does not
  itself grant an audit right over identified PHI (eligibility, COB) - that rests on the BAA
  § 3.2 and the fiduciary's right to plan records (Plan § 8.6) - but as applied to the
  auditor's access to de-identified claim-level data, 9.6(a)/(c) are prohibited. The
  intended conclusion is "prohibited", not "gray area".
- **§ 12.5 / § 9.8**: transition data only in standard format and "subject to 9.4 and 9.5",
  which survive three years - so a successor TPA (a "Competitor") cannot receive claim-level
  data without Meridian's consent. The proposed amendment (§ 9) expressly leaves 9.8 and 12.5
  unchanged. Must be fixed.

### 2. The genuinely unsettled part - original § 9.3

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
the statutory fields) functions as an indirect restriction and is more likely than not
prohibited. "Unsettled / moderate confidence, but on balance an indirect restriction" is the
right register and passes c07. The "proprietary" label is not a defense; the statute names
allowed amounts and provider identity.

### 3. Meridian's proposed amendment (doc 13) - what it fixes and what it does not

Meridian's form cures the three things a plan is most likely to complain about (consent,
180 days, per-line pricing) and then re-creates the restrictions in subtler forms. The memo
must not sign it as drafted (c44) and must not reject it wholesale (c43).

**Acceptable / commercially reasonable (credit these):** SFTP delivery; 90-day delivery
commitment from receipt (vs. 180 days from an open-ended acceptance); allowed amounts in the
standard extract; a flat $7,500 fee for subsequent extracts (a reasonable cost-based charge is
not a restriction on the statute's silence); remote audit access; TPDUA term extended to
18 months; deletion of the Competitor representation; a defined Data Access Request form.

**Defects (each is a planted criterion):**

1. **Provider-key masking (§ 1.2, Sched. A-1 row 11, § 9.3(d)) - c35.** Provider name, NPI,
   TIN and address are replaced with a Meridian Provider Key "in furtherance of
   de-identification". HIPAA de-identification (§ 164.514(b)(2)) concerns identifiers of the
   individual, not the treating provider; § 724(a)(1)(B)(ii) expressly guarantees "provider
   information, including name and clinical designation" per claim. Named-provider data is
   relegated to a "custom extract" under new § 9.3(d), which restates the original 180-day /
   then-current-rates / decline-for-Proprietary-Information terms. Net effect: the amendment
   still does not deliver (B)(ii) data, and Northgate cannot benchmark against Transparency in
   Coverage machine-readable files (SOW § 1.1) without provider identity.
2. **Notice-and-objection (§ 9.4(b)) - c36.** Meridian may object within 30 days that a
   Recipient is a Competitor and "shall not be required to deliver ... until the parties have
   resolved Meridian's objection". Delivery to a BA is again at Meridian's satisfaction -
   consent by another name. A misuse covenant binding the Recipient is a reasonable
   protection; a right to withhold delivery is not.
3. **Frequency cap (§ 9.3(b)) - c37.** Two Data Access Requests per Plan Year. The statute
   says "upon request"; the Departments treat frequency limits as restrictions. Must go.
4. **24-month lookback (§ 9.3(b)) - c38.** Each extract covers claims *paid* in the 24 months
   before the request. A request in November 2026 reaches back to November 2024, excluding
   claims paid January-October 2024 - most of the first Meridian year - and defeats the
   36-month benchmark. It would also limit what a successor could receive in 2028.
   Recommend full history for the term (plus run-out), no lookback.
5. **Partial TPDUA fix (Sched. A-2) - c39.** Only TPDUA § 2 (Competitor rep) is deleted.
   § 1 (Meridian-approved purpose; "any benchmarking or repricing analysis not expressly
   included in the Approved Purpose" prohibited) and § 3 (no disclosure to Client except in
   Meridian-approved aggregated form; no disclosure to Client's other vendors) survive. § 3
   restricts the Plan's own access through its BA and blocks the Northgate-to-Claimsight flow
   in SOW § 1.3. Replace the TPDUA with a BAA-plus-confidentiality undertaking.
6. **§ 9.5 savings-clause qualifier (§ 4) - c40.** The participant / referring-provider bar
   stays; "except as required by applicable law, including ERISA Section 724" is the same
   approach as § 9.7. Rewrite 9.5 to a reasonable restriction on *public* disclosure (a)(2).
7. **§ 6.1 acknowledgment - c41.** The Plan "acknowledges" that the Standard CAA Extract
   satisfies (B) and that the amended Agreement contains no prohibited provision. A plan
   cannot contract around § 724 or bind the Departments; the acknowledgment is false on the
   amendment's own terms (provider masking, frequency cap, 9.4(b)); and it inverts the
   proper allocation - the representation should run from Meridian. § 6.2 (Plan solely
   responsible for its attestation; Meridian makes no representation about Continental's
   provider agreements) is legally accurate as to responsibility but the disclaimer is
   exactly why the Plan needs a Meridian rep covering the Continental agreements. The § 6.3
   comfort letter is not a basis to attest "without additional information".
8. **§ 7 release - c42.** Releases Meridian and affiliates from all claims, known or unknown,
   relating to data access, Article 9 or the attestations for the pre-amendment period,
   including Article 7 indemnification. The Committee is an ERISA fiduciary; releasing Plan
   claims (including indemnity for the very exposure the memo describes) in exchange for a
   waiver of a fee on an extract the Plan was arguably entitled to anyway is not a prudent
   exchange. Strike, or at minimum carve out indemnification, unknown claims and the
   attestation period. ERISA § 410 is not squarely on point (Meridian is not a fiduciary for
   data functions); the prudence / adequacy-of-consideration point is the right one.
9. **Conditional effectiveness (§ 8.1) - c18.** Effective only upon Continental's § 4.3
   consent, with a 120-day mutual withdrawal right that reinstates the unamended Article 9.
   The Plan could sign on October 30, attest on December 31 on the strength of an amendment
   that is not effective, and see it withdrawn in February. Require Continental's consent in
   hand before signing, or make Meridian's obligations unconditional (Meridian bears the
   Continental risk), with a fallback remedy.
10. **9.8 / 12.5 untouched (§ 9) - c34.**
11. **Year-only dates and no member linkage key (Sched. A-1 rows 3, 4, 7) - c45.** The extract
    is safe-harbor de-identified, which is fine for (B) but useless for Claimsight's 100%
    audit of the 2025 plan year (needs dates of service and paid dates, member linkage for
    duplicates, eligibility, timely filing, COB) and weak for trending. The Plan's right to
    fuller data for its auditor does not come from § 724 (which covers de-identified data);
    it comes from the BAA § 3.2 (PHI to "a person designated by Covered Entity" for health
    care operations including evaluating the BA), 45 C.F.R. § 164.504(e)/(f), the limited data
    set route (§ 164.514(e)), and the fiduciary's right to plan records (Plan § 8.6) - all
    preserved by § 724(a)(4). The amendment needs a second channel for PHI / limited data set
    to the Plan's BAs.
12. **The October 30 fee-waiver deadline** is a pressure tactic; the fee can be re-negotiated.

### 4. Upstream source of the restriction - Continental § 4.3 (doc 11)

Meridian Choice is Continental's network. Continental-Meridian § 4.3 bars Meridian from
disclosing, or *permitting any Client Plan to disclose*, Continental Rates or claim-level
allowed amounts to the plan's consultants, auditors or competing administrators without
Continental's sole-discretion consent, and requires Meridian to put equivalent terms in every
ASA. That is why §§ 9.4/9.5/1.4 look the way they do, why Delacroix "cannot" consent, and why
Amendment § 8.1 is conditioned on Continental. The Departments have said that a restriction in
a TPA's agreement with another party can put the plan out of compliance and expect plans to
address this contractually. Consequences: (i) the amendment needs Continental's consent/waiver
or a Meridian rep and covenant that Continental has waived § 4.3 for this Plan; (ii) the
negotiation must reach Meridian legal and Continental network management, not account
management; (iii) Meridian's November 2024 confirmation spoke only to "Meridian's provider
network agreements" and did not address the intercompany agreement; (iv) Amendment § 6.2
disclaims any representation about Continental's provider agreements - the opposite of what
the Plan needs. § 4.2(b) ("to the extent required by applicable law") does not help because
§ 4.3 separately bars sharing with the Plan's BAs. § 9.6 (no third-party beneficiaries) means
the Plan cannot enforce § 4.4/4.5 directly, though Continental § 4.5 and § 9.3 give Meridian
arguments to take to Continental.

### 5. Traps

- **De-identification** is about participants/beneficiaries (45 C.F.R. § 164.514); it is
  not a basis to strip provider NPIs/names or allowed amounts (BAA § 2.4 is a hint; the
  amendment's § 1.2 and § 9.3(e) assert the opposite).
- **§ 9.7 savings clause**: Meridian's "no gag clause by definition" fails. The second
  sentence is triggered only on a court/agency determination; the first sentence covers
  "access" only (not sharing with BAs or participant disclosure); the provisions remain
  operative and are being applied; the Departments expect removal or reporting. Amendment
  § 4 repeats the same technique for 9.5.
- **§ 12.4 Changes in Law** does not apply: § 724 was enacted December 27, 2020, before the
  January 1, 2024 Effective Date. Amendment is by § 12.3 (mutual agreement) under negotiating
  pressure, or § 12.2 (material breach - arguable, aggressive).
- **Non-renewal notice** (October 2, 2026) has passed - and the Committee consciously let it
  pass on September 30 while the dispute was live. The ASA renews for 2027. A termination
  threat has no teeth for 2027; leverage is the attestation disclosure, DOL exposure,
  fiduciary posture, the 2028 market check, and Continental's own § 4.4/4.5 and § 9.3
  compliance language.
- **Meridian is not "in violation"**: it is the counterparty; the Plan is the regulated party
  and attests. (Amendment § 6.2 is accurate on this.)
- **Cordell period**: Northgate asks for October 1, 2023 - September 30, 2026. Meridian's
  records start January 1, 2024; Q4 2023 (and run-out through March 2024) is in the Cordell
  final claims file already on the shared drive (with allowed amounts and NPIs, outside the
  Meridian ASA). Meridian's extract should be scoped to January 2024 onward.
- **Fee-waiver pressure**: signing by October 30 "to lock in the waiver" is not a reason to
  accept the release, the acknowledgment or the masking.

### 6. HIPAA structure of the data flow (docs 04, 09, 10, 13)

- Northgate's field list includes full dates of service and received/paid dates. Under the
  safe harbor (§ 164.514(b)(2)(i)(C)) all elements of dates except year directly related to
  an individual must be removed; service dates are such dates. So the data set as drafted is
  not de-identified. Compliant routes: (a) limited data set (§ 164.514(e): dates permitted,
  direct identifiers removed) under a data use agreement for health care operations;
  (b) PHI disclosed to Northgate/Claimsight as the Plan's business associates for the Plan's
  health care operations (BAA § 3.2); (c) expert determination. § 724(a)(1)(B) is itself
  "consistent with" HIPAA, and (a)(4) preserves HIPAA-permitted access, so this structure is
  not a work-around; it is the intended design.
- Plan § 8.7 / § 164.504(f): PHI may go to the plan sponsor for plan administration functions
  only to Appendix B personnel (Director Benefits, Benefits Analyst, Payroll Benefits
  Specialist, GC for limited purposes). The CFO's request to circulate the full claim-level
  file to Committee members is not permissible unless the file is HIPAA de-identified
  (year-only dates, etc.) or is summary health information. Correct advice: BAs hold the
  PHI/limited data set; the Committee gets Northgate's analysis and, if it wants row-level
  data, a de-identified version (ironically, something like Schedule A-1 - but with provider
  identity).
- A persistent pseudonymous member key is permitted in de-identified data under
  § 164.514(c) (re-identification code not derived from PHI, mechanism not disclosed); the
  amendment's refusal to include one is not required by HIPAA. Plus, not a criterion.

### 7. Attestations

The plan must attest annually by December 31 (HIOS GCPCA). Meridian may decline to attest for
self-funded clients; the obligation stays with the plan. The 2024 and 2025 attestations were
unqualified while Article 9 was in force - an inaccurate attestation is an exposure (and the
CFO has flagged discomfort). There is no formal "amended attestation" procedure in the
guidance; sensible advice is to document the reliance on Meridian's November 2024
confirmation, correct the record (voluntary supplement/disclosure and/or describe the history
in the 2026 Additional Information field), and build a remediation file.

For 2026: must still submit; if unremediated, identify the provisions, Meridian's refusal, and
steps taken in the Additional Information text box. **Attestation-period point (c13):** the
2026 attestation covers December 20, 2025 through submission; Article 9 was operative and
applied for most of that period. Even if a compliant amendment is signed in December, the
honest attestation describes the provisions and their removal in Additional Information.
Meridian's promise that the Plan can attest "without any additional information" on the
strength of a § 6.3 comfort letter should be rejected.

### 8. Exposure - the realistic number (CFO's question)

- ERISA: fiduciary exposure (duty to monitor Meridian; reasonableness of ~$2.1M fees and
  ~$71M claims spend; documentation); DOL enforcement of § 724 under its general civil
  enforcement authority. No ERISA per-day penalty for § 724.
- IRC § 4980D: $100/day per individual to whom the failure relates for a Chapter 100
  (§ 9824) failure; the employer is liable (§ 4980D(e)) and self-reports on Form 8928 (due
  with the employer's income tax return). $100 x ~14,790 lives is ~$1.48M/day - a
  meaningless headline figure (and "individual to whom the failure relates" is itself
  unclear for a gag clause). For failures due to reasonable cause and not willful neglect,
  § 4980D(c)(3) caps the tax for the taxable year at the lesser of 10% of the employer's
  prior-year group health plan payments or $500,000 - here $500,000 per taxable year
  (so up to ~$1.5M across 2024-2026 before any waiver). § 4980D(c)(4) allows the Secretary
  to waive part or all where the tax would be excessive relative to the failure.
  § 4980D(c)(1) (no tax where the failure was unknown and undiscoverable with reasonable
  diligence) is weak because Article 9 was on the face of a contract the Plan signed in
  December 2023 and Ms. Raman did not compare it to the statute; § 4980D(c)(2) (no tax if
  corrected within 30 days of actual/constructive knowledge) likely ran from December 2023
  or, at the latest, from Meridian's September 25, 2026 application of the restrictions
  (expiring about October 25, 2026 - before the Committee meets) - so it is probably
  unavailable, which is why prompt correction, the cap, the waiver and a documented
  reasonable-cause record (Meridian's confirmation) matter. **§ 4980D(b)(3) (c22):** if the
  failure is not corrected before the IRS sends a notice of examination, a minimum tax of
  $2,500 per individual ($15,000 if more than de minimis) applies notwithstanding the
  (c)(1)-(2) exceptions - the reason to correct and paper the file now. The tax is the
  employer's; it cannot be paid from plan assets.

### 9. Northgate engagement (docs 05, 12)

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

### 10. The Plan's counter-amendment

Delete 9.4 consent right and the 9.4(b) objection/withholding mechanism (replace with BAA +
reasonable confidentiality / misuse undertaking, no Competitor test, no Meridian-approved
purpose, no aggregated-only limit); specify per-claim elements including allowed amount,
provider name / NPI / clinical designation, service codes, full dates where delivered to a BA
under HIPAA; standard electronic delivery (SFTP) within a defined period (30-90 days) at no
charge or a cost-based fee; access upon request with no frequency cap or lookback; delete the
9.3(d) "decline" right and the § 1.4 Allowed-Amount carve-out; conform 9.5 to (a)(2) (public
disclosure only); delete 9.6 caps (audits "upon request", full population, remote electronic
access); fix 12.5/9.8; strike §§ 6.1 and 7; Meridian rep, warranty and covenant that no
Meridian agreement (including the Continental network access agreement and Continental
provider agreements) restricts the Plan's § 724 rights, with Continental's written waiver of
§ 4.3 for this Plan delivered before signing; Meridian cooperation with and support for the
attestation; indemnity; Committee approval documented in minutes.

## Common wrong answers

- Treating portal access to aggregated reports as satisfying (a)(1)(B).
- Asserting any fee or any delay is per se illegal, or the reverse (silence on price means
  the fee/lag terms are fine).
- Recommending the Plan sign Meridian's amendment as drafted to lock in the fee waiver, or
  rejecting it wholesale without crediting the 90-day / SFTP / allowed-amount / flat-fee
  elements.
- Accepting the Standard CAA Extract as (B)-compliant because it contains allowed amounts,
  while missing the provider-key masking and the surviving 9.3(d) decline right.
- Describing 9.4(b) as a "notice, not consent" improvement.
- Treating the deletion of the TPDUA Competitor representation as fixing the TPDUA.
- Advising Halvorsen to withhold the 2026 attestation until the contract is fixed; or
  advising that once the amendment is signed the Plan can attest with no additional
  information.
- Saying Meridian is "in violation of § 724".
- Invoking § 12.4 changes-in-law.
- Suggesting provider identifiers can be redacted as part of de-identification.
- Asserting that § 724 entitles the Plan to identified / full-date PHI for the audit.
- Calling the Northgate request "de-identified" without noticing the dates of service.
- Endorsing circulation of the raw claim-level file to the Committee/CFO.
- Quoting $100/day x covered lives as the exposure without the § 4980D(c)(3) cap, or
  assuming a fresh 30-day correction window starts now; omitting § 4980D(b)(3).
- Asking Meridian for all 36 months when the first three are Cordell's.
- A generic "downstream provider contracts" representation that never engages with
  Continental § 4.3, or accepting Amendment § 8.1's Continental condition.
- Citing a nonexistent 29 C.F.R. § 2590.724 regulation or an ERISA per-day penalty.
- Treating Northgate as unconflicted / ignoring § 408(b)(2)(B).
- Accepting the § 7 release because "the fee waiver is consideration".
