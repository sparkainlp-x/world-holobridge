# Holographic Display Fans for Urban Heat Resilience and Social Benefit

**A documented use case for World-HoloBridge.** Author: Jean-François Brisson (Spark AI NLP). Written against World-HoloBridge v0.2.0 (DOI [10.5281/zenodo.23423942](https://doi.org/10.5281/zenodo.23423942)); the repository's version was not changed by adding this document. Last checked: 2026-10-27.

> **What this is not.**
> - It is **not legal advice** and **not a production system**. World-HoloBridge is a reference prototype.
> - **No municipal partner, deployment or pilot is claimed.** No city, agency or organisation named here has reviewed or endorses this document.
> - The repository's code contains **no heat-alert, display or hardware functionality**. The pilot design and the municipal extensions below are proposals, and **none of them is implemented in the repository**.
> - **No evidence was found** that holographic display fans reduce temperatures or heat-related deaths. A holographic fan does not cool air. The proposal is a communication and mobilization layer only, to be compared against ordinary signage in a pilot.

## Evidence tags

Statements in this document carry one of these tags, in italics, where it matters. An untagged statement is explained by the source cited next to it.

| Tag | Meaning |
|---|---|
| **measured** | The author measured it. (Nothing in this document is.) |
| **reported** | A cited source states it. The source was read, or only a search extract of it was seen; the reference list says which. |
| **vendor claim** | A manufacturer or seller states it on a product page or manual. Not independently verified. |
| **design rationale** | The author's reasoning about how something should work. Not tested. |
| **unverified** | Could not be checked. |

## Executive finding

A holographic display fan cannot meaningfully cool outdoor air. It is a persistence-of-vision LED display, not an air-circulation fan, and the electricity it uses ends up as heat. (This is physical reasoning, tagged *design rationale*; I did not measure any device, and I found no source that measures airflow or temperature effects of these units.) Its defensible role is **heat-risk communication and community mobilization**: attracting attention, directing residents to cooling resources, explaining protective actions, visualizing neighborhood heat data, and inviting participation in real cooling projects.

This distinction matters. Physical urban cooling comes from interventions such as trees, vegetation, shade, green or reflective roofs, and cool or permeable pavements; governments also use warning systems and cooling centres to reduce acute health risk.[1][2][3] A display should therefore be treated as the **visible communication layer** of a broader heat-health action plan, not advertised as cooling infrastructure.

Several of World-HoloBridge's gates map onto this use: consent, Indigenous authority, accessibility, payment, incident reporting, audit logging and publication checks. The section "World-HoloBridge fit" describes each one as the code in this repository actually implements it, including where a control is narrower than the name suggests. World-HoloBridge is a reference prototype, not legal advice and not a production system. It contains nothing specific to heat alerts, displays or hardware, and it would need security, privacy, municipal-operations and emergency-management extensions before any deployment.[4]

## What the device can do

“Holographic fans” use rapidly rotating LED blades and persistence of vision to create an apparently floating image. They do not project a volumetric hologram, and the blades are not designed or sold to move useful quantities of air for people. Product specifications vary widely. Two vendor pages list electrical draws of roughly 36 W to 150 W depending on model (one states 20–150 W; the other lists individual models at 36, 50, 60, 65, 130 and 150 W). These are **vendor claims**, not measurements.[5][6]

Their urban value comes from high-salience animated communication:

- **Dynamic heat status:** Show a simple local heat-risk level, current temperature/humidity context, and the time at which information was updated.
- **Wayfinding:** Animate arrows, walking distance, opening hours, accessibility, transit options, and QR/NFC handoff to nearby cooling centres, libraries, pools, splash pads, drinking-water points, and shaded routes.
- **Protective action:** Present short loops such as “drink water,” “check on neighbours,” “move to a cool place,” and signs requiring urgent medical attention. EPA guidance explicitly identifies early warning, public communication, awareness of symptoms, and cooling centres as short-term protections.[2]
- **Cooling-project visualization:** Show before/after concepts for shade trees, cool roofs, green roofs, reflective pavement, bus-stop canopies, or water access. This connects attention to measures that actually lower heat exposure.[1][7]
- **Community feedback:** Offer a QR/NFC route for reporting hot spots, missing shade, broken fountains, inaccessible cooling facilities, or desired tree locations. Community-science projects show that residents can reveal neighborhood-scale heat variation missed by coarser operational products.[8]
- **Public recognition:** Credit community data collectors, artists, accessibility reviewers, local organizations, and paid contributors—with explicit permission.

## Causal pathways

| Intended outcome | Display-mediated pathway | Necessary companion action | Evidence strength |
|---|---|---|---|
| Lower heat illness | Attention → understandable warning → protective action | Reliable alert protocol, cool places, water, outreach and healthcare guidance | *Reported:* comprehensive heat-health action plans are associated with lower mortality in pre–post studies; evidence for warnings alone is inconsistent.[9][10] This is evidence for the plan, not for the display. |
| Better cooling-centre use | Animated local wayfinding → QR/map handoff → arrival | Open, accessible, culturally safe facilities with accurate hours and capacity | *Reported* policy guidance for cooling centres;[2][11] *unverified* for any display: no direct holographic-fan evidence found. |
| Physical heat reduction | Public visualization/support → funded trees, shade, roofs or pavements | Capital works, maintenance and equitable siting | *Reported* (EPA) for the physical measures;[1][3] nothing for the display itself. |
| Civic participation | Hyperlocal content → conversation → feedback and co-design | Moderation, response commitments and transparent decision-making | *Reported* (research on public screens and situated displays);[12][13] not specific to heat or to holographic fans. |
| Social connection | Shared local stories and prompts → gathering and interaction | Community programming, consent and inclusive facilitation | *Reported* but thin: an opinion questionnaire[14] and one in-the-wild neighbourhood display study;[15] context-dependent. |
| Trust and legitimacy | Visible provenance, update times and contributor governance | Accountable municipal owner and documented content approvals | *Design rationale*, consistent with situated-display research.[13] |

The key limitation is evidence specificity: in the sources I checked, I found no study showing that holographic display fans themselves reduce city temperatures or heat-related mortality, and none comparing them with ordinary signage. Absence of a search hit is not proof that no such study exists. Research supports the surrounding mechanisms—heat-health action plans, cooling resources, locally relevant warnings, community science and participatory public displays—but a city pilot would still be an evaluation of a new communication medium.

## Heat-risk communication

Warning availability alone is insufficient. A 2013 systematic review of 15 articles found six studies asserting fewer deaths after a heat warning system was introduced, and eight studies showing that merely having a warning system did not change behaviour; perceived personal threat and barriers such as the cost of running air conditioning affected response. The authors concluded that research in the area is limited.[9] A 2026 systematic review (reference 10; the conference abstract and the full preprint are both listed, and the preprint has not been peer reviewed) concluded that comprehensive heat-health action plans appear to reduce heat-related mortality, while evidence for warning systems alone and for other intervention types is limited or inconsistent.[10]

Accordingly, holographic content should always combine four elements:

1. **Risk:** “Extreme heat today,” localized to the site rather than vague regional messaging.
2. **Action:** One or two immediate, feasible steps rather than a long instruction list.
3. **Resource:** A nearby place or service that makes the action possible.
4. **Handoff:** QR, NFC, short URL, transit information, or a staffed human contact.

A 2024 NOAA/National Weather Service social-science report, based on focus groups, mentions practical measures such as putting cooling centres on Google Maps, text-based alerts, video public-service announcements and bus-stop signs.[16] A 2025 Canadian stocktake of heat alert and response systems describes three components (an alert protocol, a community response plan and a communication plan) and reports that most systems it reviewed focused on alert protocols and communication, that some included pre-season engagement and community response, and that few included an evaluation plan.[17]

## Social benefits

### Placemaking and belonging

A book chapter on urban screens argues that participatory displays can connect people to place and to one another and create opportunities for civic participation.[12] A paper on situated public displays names hyperlocal relevance, community trust and enriched experiences of the environment as design considerations, and an in-the-wild study of neighbourhood displays reports some residents describing personal reflection.[13][15] These sources concern public displays in general, not heat messaging and not holographic fans.

For a heat-resilience deployment, this means the display should feature locally commissioned animation, community-defined languages and narratives, neighborhood cooling priorities, public art, and visible feedback loops showing what changed after residents contributed. It should not default to commercial advertising during an emergency or treat community stories as decoration.

### Participation and climate literacy

Community heat mapping can turn abstract climate risk into visible neighborhood evidence. A Los Angeles community-science pilot involved about 1,000 participants (about 750 of them K–12 students) and found large neighbourhood-scale variation in air temperature and ozone that was not exhibited in the daily satellite observations or operational model predictions it was compared with.[8] Showing community-approved measurements on a public display *could* encourage data literacy and support decisions about trees, shade and cooling services, provided sensor uncertainty and update times are shown. That use is a *design rationale*; the study did not involve a display.

### Inclusion and access

World-HoloBridge's accessibility requirement (captions, a transcript, a plain-language summary and a non-headset alternative) is a useful minimum.[4] In the code it is a check that a project declares those four feature names; it does not verify that the captions, transcript or summary exist or are accurate, so human review is still needed. For heat emergencies, the city should add large high-contrast text, multilingual messages selected with local communities, pictograms, audio available by user choice, screen-reader-compatible mobile pages, tactile or conventional signs, and a no-smartphone route to the same information.

A holographic effect must never be the only channel. Bright animation may be unreadable in sunlight, inaccessible to people with low vision, and hard to interpret quickly; flashing content can also be unsafe for people with photosensitive epilepsy (see "Photosensitivity" below). Redundant conventional signage and staff or telephone support are essential.

## World-HoloBridge fit

World-HoloBridge v0.2.0 (the current release when this document was written) is a Python/SQLite reference workflow for community-led cultural and spatial-media projects. Its browser plan generator runs in the browser: it loads its own `plan_template.json` from the same site, the city, region and country you type are not sent anywhere, and it uses no storage or analytics (the page has a strict Content-Security-Policy and the repository's README makes the same statement). It produces English or French starting plans.[4]

The table below states what each control does in the code on the `main` branch and what that means for this use. Where `main` behaves differently from release 0.2.0 (the hardening changes listed under "Unreleased" in the changelog), the row says so; the right-hand column was written against v0.2.0 and the limits it names still hold unless the left-hand column says otherwise. The tests that check each behaviour are listed in [evidence-register.md](evidence-register.md). Everything in the right-hand column is a *design rationale* for a hypothetical heat-communication deployment. Nothing in the repository is specific to heat.

| Existing control | What the code does | Heat-resilience application and limits |
|---|---|---|
| Consent | A contributor needs an active (not withdrawn, not expired) consent record that permits the use `community_storytelling` before they can be added to a project and again before the project is published. A use prohibited in any active record is refused. Consent is per contributor. | Helps keep resident stories, portraits or voices out of a project without current consent. It does not track where individual items go afterwards, and it checks only the `community_storytelling` use, so it would not by itself prevent reuse of heat-map contributions beyond agreed purposes.[4] |
| Indigenous-authority gate | Indigenous material can only be registered by a contributor flagged as an Indigenous governance authority. The material is stored with external AI training set to "no"; on `main` SQLite triggers reject any attempt to set it to "yes", and `ai_training_allowed()` reads it. | Requires a registered authority for Indigenous material. In release 0.2.0 the AI-training flag was a stored value that nothing read. On `main` it is protected by triggers and exposed through `ai_training_allowed()`, but nothing in the repository trains a model, so only a downstream tool that calls it can honour it. The tool does not identify nations or territory.[4] |
| Public-display permission | Registered material without public-display permission cannot be attached to a project. On `main` the permission is checked again at publication, and `withdraw_public_display()` revokes it. | The code models only Indigenous material; there is no generic material type. Other material, such as non-public interviews or health experiences from non-Indigenous contributors, is not represented and so has no public-display check, so a municipal deployment would need its own rule for those.[4] |
| Accessibility gate | A project cannot be created unless it declares captions, transcript, plain-language summary and non-headset alternative. On `main` the declaration is re-checked at publication, and optional evidence references (a non-empty file, a URL checked for syntax only, or a text description) are verified when given and again at publication. | Without evidence references this is a declared checklist. Even with them, the code cannot tell whether captions are accurate, a summary is plain, or an alternative is usable; that needs review by disabled residents and accessibility staff.[4] |
| Payment gate | Publishing is refused while any of the project's contracts is unpaid; contract amounts must be greater than zero. On `main`, a project can declare paid contributors and publication is refused while any of them has no contract; a project with no contracts gets a `no_contracts_recorded` warning, and `strict=True` refuses it. | Blocks publication while contributor contracts are unpaid. By default a project with no contracts and no declared paid contributors can still be published (with the warning in the audit entry), so the gate still depends on contracts having been created or declared.[4] |
| Incident process | Incidents (low, medium, high, critical) can be reported, linked to a project, and resolved with a corrective action. On `main`, an open high or critical incident linked to a project blocks that project's publication; lower severities and unlinked incidents are warnings (blockers in strict mode). | A place to record misinformation, inaccessible content, cultural harm, privacy events or unsafe hardware. In release 0.2.0 an open incident never blocked publishing. The incident type is free text, and nothing checks that a high-severity incident was linked to the right project.[4] |
| Append-only audit log | Each action writes an audit entry in the same transaction, and SQLite triggers reject `UPDATE` and `DELETE` on `audit_log`. | Records approvals and actions. It blocks edits through SQL only, and the database file is not tamper-proof.[4] |
| AI-use assessment | `assess_ai_use()` returns and logs an assessment. Sensitive-data or Indigenous-material requests get the status `blocked_pending_governance`. | An advisory record. Nothing else in the code refuses to proceed on that status.[4] |

### Required municipal extensions (NOT implemented in this repository)

None of the items below exist in World-HoloBridge. They are requirements a city or operator would have to build or procure. This list is a design rationale, not a feature list.

- **Authoritative data connector:** Pull heat alerts only from approved emergency/public-health sources; cache the last verified message and display its timestamp.
- **Two-person publishing control:** Require an emergency-management or public-health approver plus a communications/accessibility approver for alert content.
- **Automatic expiry:** Remove or downgrade alerts when the source expires; never leave stale emergency guidance visible.
- **Fail-safe state:** On connectivity or data-validation failure, show a neutral “information temporarily unavailable” state plus permanent emergency contacts—not an old alert.
- **Privacy minimization:** Do not use facial recognition, passive device tracking or identifiable health data. Aggregate feedback unless follow-up is explicitly requested.
- **Security:** Signed content packages, device authentication, encrypted administration, role-based access, patching, monitoring, rollback and an incident-response process.
- **Records policy:** Define retention and deletion rules for submissions, contracts and incidents; append-only logging alone does not establish legal compliance.
- **Operational ownership:** Name who updates facility hours, verifies translations, tests links, cleans the enclosure, responds to reports and turns equipment off during unsafe conditions.
- **Indigenous governance:** Identify rights-holders locally and confirm protocols directly. The tool intentionally does not identify nations or territory and cannot substitute for consultation.[4]

## Deployment model

### Recommended sites

A first pilot should use indoor or weather-protected, supervised sites where people already seek trusted information: library entrances, community centres, transit terminals, municipal service counters, malls acting as cooling spaces, or the interior window of a cooling centre. Health Canada guidance lists shopping malls, libraries, community centres, swimming pools, beaches, splash pads and similar public spaces as cooling facilities (the page, "Extreme heat and COVID-19", was published in 2021 and says some of its information may be outdated).[11]

Outdoor, unattended installation is a poor starting point. Direct sunlight weakens the floating-image effect, and many units are not waterproof. Vendor and product-manual guidance (vendor claims) commonly calls for protection from moisture, secure mounting, ventilation, placement out of reach and a protective cover around the rotating blades.[18][19][20]

### Content loop

Keep the emergency loop short enough to understand in one pass:

- **0–4 seconds:** Heat-risk color and plain-language status.
- **4–9 seconds:** Primary action, such as “Cool down now—library open until 9 PM.”
- **9–15 seconds:** Animated direction or distance, accessibility symbol and transit cue.
- **15–20 seconds:** QR/NFC/short URL plus “No phone? Ask staff or call [local number].” (311 is not available everywhere; use the real local line.)
- **20–30 seconds:** Community-approved cooling project, public-art segment or feedback invitation.

During a severe alert, emergency content should displace nonessential programming. Motion should be limited, text should remain stable long enough to read, and flashing is prohibited (see "Photosensitivity" below). This loop is a *design rationale*, untested.

## Physical cooling linkage

The display becomes strategically useful when every campaign leads to measurable physical or service interventions:

| Display campaign | Real-world action | City metric |
|---|---|---|
| “Map your hottest walk” | Install shade, trees, benches or drinking-water access on priority routes | Projects completed; canopy/shade added; resident-reported comfort |
| “Cool-roof demonstration” | Retrofit a municipal or community building | Roof surface temperature and cooling-energy use before/after |
| “Find your cool space” | Expand hours, access and transit links to cooling facilities | Visits, denied entries, accessible hours, neighborhood coverage |
| “Adopt a block” | Community planting and stewardship with paid local roles | Tree survival, maintenance response and equitable distribution |
| “Heat-watch neighbours” | Organized check-ins led by trained community partners | Reach, opt-in participation, referrals and response time |
| “Community heat map” | Sensor campaign and participatory planning | Validated observations, hot spots addressed and public decisions influenced |

Trees and vegetation cool through shade and evapotranspiration; green roofs, reflective roofs and cool pavements reduce heat absorption or increase cooling.[1][3] These are the interventions against which physical temperature outcomes should be claimed—not the holographic display.

## Photosensitivity

Content for this use should not flash at all. This is a kit default stricter than the standard. WCAG 2.2 Success Criterion 2.3.1 (Three Flashes or Below Threshold) requires that content not flash more than three times in any one-second period unless the flashes stay below the general-flash and red-flash thresholds.[21][22] A rule of "no flashing, no strobing, only static output and slow fades" is simpler to check than the thresholds. That line concerns the *content* shown. I have not assessed the refresh behaviour of any particular display unit, and that needs its own check before a deployment.

## Risks and mitigations

| Risk | Consequence | Minimum mitigation |
|---|---|---|
| Misleading “cooling technology” claim | Greenwashing and procurement mistrust | State explicitly that the unit communicates and mobilizes; it does not cool the city. |
| Rotating-blade contact or falling equipment | Serious injury | Fully enclosed unit (certification status to be confirmed by the operator), tamper-resistant mounting, out-of-reach placement, inspection and emergency shutoff.[19] |
| Rain, dust, heat or glare | Failure, unreadable messages or electrical hazard | Indoor/sheltered siting, rated enclosure, thermal limits, ventilation and conventional backup signs.[18][20] |
| Stale or wrong alerts | Harmful public-health decisions | Authoritative feed, timestamps, expiry, two-person approval and fail-safe content. |
| Digital exclusion | Highest-risk residents miss information | Plain signs, staff, telephone line, audio, multilingual and no-phone access. |
| Surveillance or data misuse | Chilling effect and loss of trust | No biometric analytics; minimum data; consent and purpose limits; public privacy notice. |
| Cultural appropriation | Harm to rights-holders | Community-defined protocols, authorized governance, withdrawal rights, fair payment and prohibited-use enforcement.[4] |
| Accessibility failure | Unequal access during emergency | Human review plus World-HoloBridge gates; test with disabled residents.[4] |
| Energy/rebound impact | Extra electricity and waste heat | Occupancy/alert scheduling, efficient model, repairable equipment, renewable supply where available and energy metering. |
| Novelty decay | Falling attention after launch | Rotate useful local content, evaluate comprehension, and discontinue if it does not outperform simpler signage. |

## Pilot design

A credible pilot should compare the holographic display with ordinary digital signage or printed signs rather than assuming novelty equals impact.

The phases below are an outline. [pilot-protocol.md](pilot-protocol.md) is a pre-registration-style protocol for the controlled trial (hypotheses, outcomes and instruments, sample-size method, safety stopping rules, independent evaluator, analysis plan, deviations log). Neither document reports a result: no pilot has been run.

### Phase 1: Co-design

Create a paid advisory circle including public health, emergency management, accessibility advocates, community organizations, youth, older adults, housing and homelessness services, cultural contributors, and locally identified Indigenous rights-holders where relevant. Define prohibited uses, languages, decision rights, compensation, withdrawal, moderation and incident response through the World-HoloBridge plan workflow.[4]

### Phase 2: Baseline

For two to four weeks, measure current cooling-centre awareness, route-finding success, QR/short-link use, service uptake, message comprehension and accessibility barriers. Document the existing heat plan and do not attribute seasonal changes to the display without a comparison.

### Phase 3: Controlled trial

Use matched sites or alternating time blocks:

- **A:** Existing sign.
- **B:** Conventional digital screen with identical message.
- **C:** Enclosed holographic fan with identical message.

This isolates the medium from the message. Do not randomize access to essential safety information; all groups must receive accurate minimum guidance.

### Phase 4: Outcomes

Prioritize outcomes in this order:

1. **Safety and accuracy:** injuries, near misses, stale alerts, uptime and data discrepancies.
2. **Equity and accessibility:** comprehension and resource use by age, language, disability and neighborhood, collected only with ethical and privacy safeguards.
3. **Behavior:** cooling-centre visits, route completion, QR/NFC/short-link engagement, calls and protective-action recall.
4. **Social value:** participation, contributor diversity, trust, perceived relevance and hot-spot reports resolved.
5. **Environmental performance:** metered kWh, operating hours, lifecycle and electronic-waste plan.
6. **Physical heat outcomes:** only for linked interventions such as trees, roofs or shade—not for the display itself.

### Phase 5: Decision gate

Scale only if the enclosed fan is safe, accessible, more effective or cost-effective than simpler media, and positively accepted by communities. If a printed sign or conventional screen performs equally well, choose the simpler technology and retain World-HoloBridge as the governance layer.

## Practical recommendation

Position the concept as **“HoloBridge Heat Commons: a governed, community-led public communication layer for urban heat resilience.”** (a proposed working name; there is no product, deployment or municipal partner by this name) Its strongest municipal proposition is not futuristic hardware by itself, but a combination of:

- attention-grabbing spatial media;
- verified heat-health messages and cooling-resource wayfinding;
- paid, consent-based local storytelling and public art;
- citizen reporting and participatory heat mapping;
- accessible, multilingual alternatives;
- transparent governance and auditable publication controls; and
- direct linkage to funded trees, shade, cool surfaces, water and cooling-centre services.

This framing is meant to be technically honest and testable. It has not been tested. It preserves the holographic fan’s capacity to attract attention while ensuring that health protection, community authority and real heat mitigation—not novelty—remain the program’s purpose.

---

## Author and AI-assistance note

- **Conflict of interest.** The author created and maintains World-HoloBridge and operates Spark AI NLP / FrederictonHolograms.com, which may benefit from interest in holographic displays.
- **Funding.** None declared.
- **Partners and endorsements.** None. No organisation or agency cited here has reviewed or endorses this document.
- **AI assistance.** AI tools assisted with drafting, editing and source and link checks, including comparing the claims in this document with the repository's code. The author is responsible for the content.

## References

Link status was checked on 2026-10-27 (Toronto time). "200" means the page loaded for a command-line fetch. Where a publisher blocked automated access, the entry says what was and was not read.

1. US EPA, *Heat Island Cooling Strategies* (archived 2021-01-19 snapshot). https://19january2021snapshot.epa.gov/heatislands/heat-island-cooling-strategies_.html. Status: 200. It is an archived snapshot, not the current page.
2. US EPA, *Adapting to Heat*. https://www.epa.gov/heatislands/adapting-heat. Status: 200.
3. US EPA, *Reduce Heat Islands*. https://www.epa.gov/green-infrastructure/reduce-heat-islands. Status: 200.
4. Brisson, J.-F., *World-HoloBridge: governance reference prototype and community plan generator*, v0.2.0. https://doi.org/10.5281/zenodo.23423942 (concept DOI [10.5281/zenodo.23423941](https://doi.org/10.5281/zenodo.23423941); code: https://github.com/sparkainlp-x/world-holobridge). Zenodo record read through a web fetch tool; a command-line fetch got 403. The description of the gates on that Zenodo page is broader than the code in one place: it says "non-public material cannot be attached to a project", but the code checks public-display permission only for Indigenous material.
5. Accio, *3D Holographic Fan: Best Picks for 2025*. https://www.accio.com/plp/3d-holographic-fan. Status: 200. **Vendor claim** (states 20 W to 150 W per unit).
6. FURSOL, *3D Holographic LED Fan Display*. https://www.fursol.com/3d-holographic-led-fan-display. Status: 200. **Vendor claim** (lists models at 36, 50, 60, 65, 130 and 150 W).
7. US EPA, *How Communities Can Reduce the Heat Island Effect* (brochure). https://www.epa.gov/sites/default/files/2016-09/documents/heat_island_4-page_brochure_508_120413.pdf. Status: 200; text read.
8. Wang, J., et al. (2022), *Resolving and Predicting Neighborhood Vulnerability to Urban Heat and Air Pollution: Insights From a Pilot Project of Community Science*, GeoHealth 6(5). https://doi.org/10.1029/2021GH000575. The publisher page returned 403 to automated fetches; the abstract was confirmed from a copy at https://arroma.uiowa.edu/docs/publication/paper_pdf/2022/Wang_et_al_2022.pdf as shown in a search extract. Full text not read.
9. Toloo, G., et al. (2013), *Evaluating the effectiveness of heat warning systems: systematic review of epidemiological evidence*, Int J Public Health. https://link.springer.com/article/10.1007/s00038-013-0465-2. Status: 200; abstract read, full text is behind a paywall. The abstract states: 15 articles; six studies asserted fewer deaths after introduction; eight studies showed mere availability did not change behaviour; "research in this area is limited".
10. (a) Conference abstract, European Journal of Public Health 36 (Supplement 5), *Systematic review of the effectiveness of heat-health protection interventions*. https://academic.oup.com/eurpub/article/36/Supplement_5/ckag169.183/8995160. The publisher returned 403 and a timeout; **not opened**. (b) The matching full review is an OSF preprint (posted 2026-05-07, not peer reviewed): *Effectiveness of interventions to reduce mortality, morbidity, and emergency service demand during extreme heat: a systematic review with meta-analyses*, https://doi.org/10.31235/osf.io/6djpz_v1 (resolves, 200). Its abstract, seen in a search extract, reports 49 studies, 18 on heat-health action plans, a pooled pre–post risk ratio for mortality of 0.93 (95% CI 0.89–0.99), and inconsistent evidence for warning systems alone. The wording of this document's claim follows (b). The link between (a) and (b) is by matching conclusion text and has not been confirmed.
11. Health Canada, *Extreme heat and COVID-19* (published 2021-07-30). https://www.canada.ca/en/health-canada/services/sun-safety/extreme-heat-covid-19.html. A command-line fetch from this machine timed out, but the page loaded through a web fetch tool on 2026-10-27 and lists cooling facilities as described. The page says it was prepared at the height of the COVID-19 pandemic and some information may be outdated.
12. *The Role of Digital Screens in Urban Life* (QUT ePrints). https://eprints.qut.edu.au/88894/1/04_v4mf.pdf. Status: 200; text partly read (a chapter on screens as connection to place and civic participation).
13. *Investigating the Role of Situated Public Displays and Hyperlocal Content* (IxDEA). https://ixdea.org/wp-content/uploads/IxDEA_art/25/25_4.pdf. Status: 200; text partly read (hyperlocal relevance, trust, enriched experiences).
14. Böhmer, M. and Müller, J. (2010), *Users' Opinions on Public Displays that Aim to Increase Social Cohesion*, IEEE Intelligent Environments, pp. 255–258. https://doi.org/10.1109/IE.2010.53 (resolves) and https://eref.uni-bayreuth.de/id/eprint/42105/ (200, abstract). A questionnaire of opinions, not a behavioural study. The original PDF link (joergmueller.info) did not respond from this machine and was replaced.
15. Wouters, N., Huyghe, J., Vande Moere, A. (2014), *StreetTalk: participative design of situated public displays for urban neighborhood interaction*, NordiCHI '14. Project page: https://rxd.architectuur.kuleuven.be/research/streettalk/. Status: 200; the page describes an eight-week in-the-wild field study.
16. NOAA NWS, *Extreme Heat Social and Behavioral Science Research* final report (2024). https://vlab.noaa.gov/documents/16126711/19519238/NWS-Extreme-Heat-Social-Science-Research-Final-Report-2024.pdf/496d8d8d-adc4-df4b-0e5b-87e7cdc64190?t=1710955597444. Status: 200; text searched for the measures cited.
17. NCCEH, *Pan-Canadian Heat Alert and Response Systems Stocktake, Public Report* (2025-04-22). https://ncceh.ca/sites/default/files/2025-04/NCCEH%20Pan%20Canadian%20HARS%20Stocktake%20Public%20Report%20-%20FINAL%20EN%20-%2022APR2025.pdf. Status: 200; text read for the components and the summary finding.
18. *3D Hologram Fan User Manual* (manuals.plus). https://manuals.plus/ae/1005005603030199. A command-line fetch got 403; **not opened**; the cited sentence is from the original search extract only. **Vendor claim** (product manual).
19. *Hologram 70CM 3D LED Fan Projector (Model MS710) User Manual* (manuals.plus). https://manuals.plus/asin/B0CRQFNX6B.pdf. A command-line fetch got 403; **not opened**; the cited sentence is from the original search extract only. **Vendor claim** (product manual).
20. Holofex, *FAQ*. https://holofex.com/en-ca/pages/faq. Status: 200; read. **Vendor claim**: states the units are not waterproof, recommends cover or enclosure outdoors and cover or out-of-reach mounting in public spaces. The vendor also sells these displays.
21. W3C, *Web Content Accessibility Guidelines (WCAG) 2.2*, SC 2.3.1. https://www.w3.org/TR/WCAG22/. Status: 200.
22. W3C WAI, *Understanding Success Criterion 2.3.1: Three Flashes or Below Threshold*. https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html. Status: 200.
