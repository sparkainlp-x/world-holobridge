# Pilot protocol: holographic display fan versus ordinary signage for heat-risk communication

**Status: draft protocol. Not registered. No pilot has been run, scheduled or agreed with any partner.** No municipal partner, site, evaluator, funder, ethics board or participant exists for this protocol. It contains no results, and every number it needs is left to be fixed, with a recorded reason, before data collection (see section 9).

Author: Jean-François Brisson (Spark AI NLP), sole author of this draft. Protocol version: 0.1-draft. It was written against World-HoloBridge `main` after v0.2.0 and the use case in [heat-resilience-use-case.md](heat-resilience-use-case.md). It is not legal advice and not an ethics approval. AI tools assisted with drafting; the author is responsible for the content.

**Conflict of interest.** The author created World-HoloBridge and operates Spark AI NLP / FrederictonHolograms.com, which could benefit from favourable results for holographic displays. This is the reason for the independent evaluator (section 7) and the negative-result commitment (section 13).

## 1. Background and purpose

The use-case document finds no evidence that a holographic display fan lowers temperatures or heat-related illness, and treats the device only as a possible **communication layer** for heat-risk information. Evidence that comprehensive heat-health action plans are associated with lower mortality is evidence for the plan, not for the display. This protocol is the design for testing whether the display adds anything to the *message*, compared with simpler media. It does not test physical cooling, and it does not test the World-HoloBridge software, which has no heat, display or hardware functionality.

## 2. Research question and hypotheses

**Question.** At sites that already carry an accurate heat-health message, does showing the same message on an enclosed holographic fan display change how well passers-by understand it and act on it, compared with a conventional digital screen and with an existing sign?

Hypotheses are stated in terms of a smallest effect worth acting on, δ, which the registrants must set (section 9).

- **H1 (primary, superiority of medium over medium).** The proportion of intercepted passers-by who can state, unprompted, the current heat-risk level *and* one protective action is higher with the holographic fan (arm C) than with a conventional digital screen (arm B) by at least δ.
- **H0 for H1.** The difference C − B is smaller than δ. Under H0, the simpler technology is chosen (the decision gate in the use-case document).
- **H2 (secondary).** Arm C differs from arm A (existing sign) on the same outcome.
- **H3 (secondary).** Arm C differs from arm B on resource use (short-link or QR scans per counted passer-by, and aggregate service use at the linked facility).
- **H4 (secondary, equity).** The C − B difference does not differ materially across age band, language and disability subgroups. This is exploratory because the subgroup sizes are not powered.
- **H5 (safety, descriptive).** No arm is associated with an excess of safety events, stale or wrong alerts, or accessibility failures. No test of H5 is planned; events are counted and reported (section 8).

No directional claim about heat illness, mortality or air temperature is made or tested.

## 3. Design

A prospective, multi-site comparison with three arms and a pre-specified analysis. The unit of assignment is the **site-time block** (a site on a set of days), not the individual passer-by, because the display is a property of the place.

| Arm | Condition | Message |
|---|---|---|
| **A** | Existing sign | The site's existing heat-health sign, unchanged. |
| **B** | Conventional digital screen | The pilot message, identical wording, timing and accessibility alternatives to arm C. |
| **C** | Enclosed holographic fan | The same pilot message as arm B. |

Rules that apply to every arm:

- All arms carry accurate minimum guidance. No one is denied essential safety information; access to it is never randomised.
- The message content comes from one authoritative public-health or emergency-management source, is identical between B and C, and is not edited by the author or evaluator during the trial. Content approval and the photosensitivity rule (no flashing at all; see the use-case document) are recorded before the first block.
- Sites are indoor or weather-protected and supervised. The enclosure certification status is to be confirmed by the operator before any block.
- **Allocation:** the order of arms across site-time blocks is set by the independent evaluator, by a documented random process with a recorded seed, balanced so that each site meets each arm where the sites allow it (a crossover or Latin-square layout). If balance is impossible, the registered fallback is a stratified allocation with the strata named before the baseline. The allocation list is held by the evaluator and written to the registry entry before the first block.
- **Baseline:** a baseline period at each site with arm A only, before any allocation, to estimate the variance and the intra-site correlation used in section 6, and to describe the existing heat plan. Seasonal changes are never attributed to the display without the concurrent comparison.
- **Washout and carry-over:** blocks are separated by a gap whose length is set at registration with a stated reason, and block order is included in the analysis.

**Limits stated in advance.** Staff and interviewers cannot be blind to the arm because the device is visible. Novelty may raise attention early and fade, so outcomes are also reported by week. A small number of sites limits generalisation and makes cluster-level inference fragile. Passers-by are not a random sample of the population most at risk.

## 4. Participants and sampling

Passers-by aged at least the age set by the ethics board (to be fixed), intercepted at the site according to a fixed rule written before the baseline (for example every k-th person passing a marked point, with k and the point recorded; no one chosen by appearance). Anyone may decline. No identifying information is collected (section 10). Inclusion of people using assistive technology or a non-headset alternative is sought deliberately, and the accessibility sessions in section 5 recruit them separately.

## 5. Outcomes and instruments

One primary outcome; everything else is labelled secondary or exploratory.

**Primary outcome (H1).** *Unprompted message recall.* A passer-by is intercepted after leaving the display area and asked, without showing the sign, two open questions: what is the heat risk today, and what is one thing a person could do. Two blinded coders score each answer against a coding sheet fixed before the baseline (risk level correct; protective action correct); the outcome is "both correct". Instrument: the intercept form and coding sheet, to be pilot-tested for clarity with accessibility reviewers and kept unchanged afterwards. No validated instrument is claimed. Inter-coder agreement is reported with the method named before the trial (for example Cohen's kappa).

**Secondary outcomes**

| Outcome | Instrument | Hypothesis |
|---|---|---|
| Resource use | A distinct short link or QR code per arm; aggregate scan counts per block; counted passers-by (observer tally); aggregate visits at the linked facility if the operator reports them | H3 |
| Perceived relevance and trust | Two short Likert items on the intercept form, wording fixed before baseline | H2 |
| Equity | Recall outcome by self-reported age band, language of response and whether the respondent uses an accessibility aid, each optional | H4 |
| Accessibility performance | Task-success sessions with disabled residents using the non-headset alternative, captions and plain-language summary, observed by the evaluator against a fixed checklist | H5 |
| Alert accuracy and freshness | Automatic log of the displayed alert's timestamp against the authoritative source; counts of stale or mismatched displays | H5 |
| Safety events | Incident log: injuries, near misses, equipment faults, reports of discomfort including reports linked to visual effects | H5 |
| Energy | Metered kWh and operating hours per arm | Descriptive |
| Cost | Procurement, installation, maintenance and staff time per arm, with sources | Descriptive |

Physical heat outcomes (temperature, heat illness) are **not** outcomes of this pilot. They may be reported only for linked cooling interventions, never attributed to the display.

## 6. Sample size: method, not numbers

No figure is given here because the inputs do not exist yet and none is invented. The registrants fix the following, each with a written reason, **before the baseline ends**:

1. δ, the smallest difference in the recall proportion (C − B) that would change the decision, set with the municipal decision-makers and the accessibility advisers by comparing it with the extra cost of arm C.
2. The significance level and the power.
3. The baseline recall proportion in arm A (from the baseline period) as the starting estimate for the reference proportion.
4. The intra-site (or intra-block) correlation ρ, estimated from the baseline data, and the average number of respondents per block, m.

Method: compute the individual-level sample per arm for comparing two proportions with the normal approximation, then multiply by the design effect 1 + (m − 1)ρ to allow for clustering by block. State the resulting number of respondents and number of blocks. If the number of blocks that can be run is too small for the cluster-level analysis in section 11 to have any power at the chosen level, the registered options are: increase blocks or sites, relax δ with a stated reason, or downgrade the pilot to a feasibility study that reports estimates and intervals without a decision rule. Nothing may be changed after data are seen except through the deviations log (section 12).

## 7. Independent evaluator

The evaluation is run by a party that has no financial or reporting interest in the result: not an employee, contractor or relation of Spark AI NLP / FrederictonHolograms.com, not paid in a way that depends on the outcome, and not a vendor of display hardware. The evaluator:

- holds the allocation list and the raw data;
- supervises coding by two coders who do not see the arm label (they see the answer sheet only);
- runs the frozen analysis script from section 11 and writes the results section;
- may publish the results without the author's approval; the author may append a response.

The author may not access individual-level data, change content during the trial, or alter the analysis. The evaluator's identity, affiliation and any conflicts are written into the registry entry. **No evaluator has been identified.**

## 8. Safety monitoring and stopping rules

Safety stopping rules are set in advance and do not depend on any outcome result. The pilot does not use interim analysis of efficacy, so no stopping for apparent benefit is allowed and no alpha is spent on interim looks.

Stop the affected arm at the affected site immediately and notify the evaluator and the operator when any of these happens:

- an injury or credible near-miss involving the rotating blades, the mounting or the enclosure;
- an electrical, thermal or fire hazard, or an equipment fault that exposes the rotating parts;
- a report of a photosensitive reaction, or any content that flashes;
- a stale, expired or incorrect alert shown for longer than a limit set by the emergency-management partner before the trial;
- a privacy event (any identifying data collected or shared outside this protocol);
- an open `high` or `critical` incident in the project's incident log. This mirrors the World-HoloBridge publication gate in `publish_project`: such an incident blocks publication of the project until it is resolved and reviewed.

A stopped arm resumes only after the evaluator and the operator record a corrective action. The pilot as a whole stops if the ethics board or the municipal partner withdraws approval, or if the safety events show a pattern the evaluator judges unacceptable (the evaluator writes the judgement and its reasons). Stopping for safety is reported in the final report with counts, never omitted.

Participants may leave or withdraw their response at any time; withdrawal removes their record from the dataset if it can be identified, and since no identifiers are collected, the protocol tells respondents when this is not possible.

## 9. Pre-registration and the values left open

Before the first block, the protocol, the coding sheet, the allocation seed and list, the analysis script, and the values from section 6 are committed together to a version-controlled repository and entered in a public registry (for example OSF Registries, or the registry the ethics board or funder requires). The date and the commit hash are recorded in the registry entry. Research-ethics-board review is required before any contact with participants; in Canada the board applies the Tri-Council Policy Statement (TCPS 2). The board's approval number is added here when it exists.

Values still to be fixed and recorded: δ; significance level; power; ρ; m; age limit; interception rule; display-area marker; block length and gap; stale-alert time limit; coder training; cell-suppression threshold (section 10); site list; evaluator identity.

## 10. Data minimisation, retention and sharing

- **Collect the minimum.** No facial recognition, no passive device tracking, no audio or video recording of passers-by, no names, contact details or health information. Intercept forms hold the two recall answers, the Likert items, and optional age band, language and accessibility-aid response. Observer tallies are counts. Short-link and QR scans are aggregate counts per arm and block; individual device data is not stored.
- **Purpose limitation.** Data are used only for this evaluation. Consent for storytelling or public display recorded in World-HoloBridge is separate and does not authorise research reuse.
- **Storage.** Raw forms are held by the evaluator on access-controlled storage, retention period set by the ethics board; identifiable fields do not exist to delete.
- **Small cells.** Subgroup counts below a threshold set by the evaluator and the privacy officer are suppressed or merged before sharing.
- **Sharing.** The public release contains: this protocol and its registry entry; the allocation list; aggregate, non-identifiable tables by arm, block and week; the coding sheet; the frozen analysis script and the outputs it produced; the deviations log; the safety-event counts; cost and energy tables. Individual-level records are not released.
- **Cultural material.** Any Indigenous material shown is governed by the rights-holders identified locally; nothing in this protocol authorises research use of such material.

## 11. Analysis plan (fixed in advance)

Written as a script and committed before the baseline ends; the evaluator runs it unchanged.

1. **Primary analysis (H1).** Difference in recall proportions, C − B, with a 95% confidence interval (Newcombe–Wilson for the unadjusted difference; a stratified estimate by site as the main analysis). Because the assigned unit is the block, the registered inference method accounts for clustering: a permutation test over the allocation scheme with block as the unit, and a cluster-robust or mixed-model estimate as a sensitivity analysis. The method actually used must be the one named in the registry entry.
2. **Decision rule.** Arm C is considered better than arm B for the purposes of the decision gate only if the lower bound of the interval is at least δ. If the interval includes values below δ, the simpler technology (B, or A if B does no better than A) is retained, and World-HoloBridge remains the governance layer.
3. **Secondary outcomes.** Reported with intervals and labelled exploratory. If any secondary outcome is used to claim an effect, the Holm correction over the registered secondary outcomes applies.
4. **Population.** Analysed as allocated (all intercepted respondents in the block's arm). A per-protocol analysis excluding blocks with documented display downtime is a sensitivity analysis only.
5. **Missing data.** Refusals are counted, not imputed. If refusal rates differ by arm by more than a threshold set at registration, that difference is reported prominently as a threat to validity.
6. **Time and novelty.** Outcomes by week and by block order are plotted and tested for a trend; the main estimate is also reported for the later weeks.
7. **Reporting.** All pre-registered analyses are reported, whatever the result. Any analysis not in the registry is labelled post hoc.
8. **Reproducibility.** The evaluator records the Python or R version, package versions, random seeds and a hash of the data file used for each reported number.

## 12. Deviations log

Every departure from this protocol is recorded when it happens, before the next block, in an append-only log kept by the evaluator and published with the results. A deviation is never made by editing the registered protocol; a dated amendment is added instead.

| # | Date | Section changed | What changed | Why | Decided by | Data seen before the change? (yes/no) | Effect on the analysis |
|---|---|---|---|---|---|---|---|
| (none recorded; no pilot has run) | | | | | | | |

## 13. Negative-result commitment

The author and the evaluator commit, before the baseline, to publish the full results whether the holographic display performs better, equal to or worse than simpler media, whether the pilot is stopped early, and whether the result is inconclusive. A null or negative result is reported with the same prominence as a positive one, under the same title, in the same venue, within a period set at registration. If the result favours a simpler technology, the author will say so in the repository README and in the use-case document.

## 14. Limitations of this protocol

- It has not been reviewed by a statistician, an ethics board, a public-health authority or a disabled-resident advisory group. Their changes override this text.
- The recall instrument has not been validated. A different primary outcome may be preferable after the instrument is piloted; that change is allowed only before the baseline ends and must be recorded.
- It assumes sites exist where three arms can be run in turn. If they do not, the design degrades to the feasibility study described in section 6.
- It evaluates communication only. A positive result does not show that the display saves lives or cools anyone.
- It depends on identical message content in arms B and C, which is a judgement that the evaluator must check and record.

## 15. How this protocol relates to the code

World-HoloBridge can record contributor consent, payment before publication, accessibility declarations with optional evidence references, incidents and an audit log for the *content* shown in the pilot. It does not run the pilot, store respondent data, collect the outcomes above, control a display, or ingest an alert feed. The claims in this document about the repository's behaviour are listed with their evidence in [evidence-register.md](evidence-register.md).
