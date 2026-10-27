# Evidence register

Every substantive claim in the repository's README and in `docs/heat-resilience-use-case.md`, with an evidence tag and where it is checked. It is a map, not a proof: a tag says how strong the check is, and no tag here means "peer reviewed" or "independently audited". Register last updated for the Unreleased changes on `main` after v0.2.0 (2026-10-27, Toronto time).

## Tags

| Tag | Meaning |
|---|---|
| **measured by tests** | An automated test in this repository, run in CI on Python 3.10–3.13 (plus Node tests for the page), checks the behaviour. The test name is given in backticks. A passing test shows the repository does what the claim says, on the inputs the test uses. It does not show the control is sufficient for real-world safety. |
| **reported** | A cited source states it. The reference list in the use-case document says whether the source was read or only seen in a search extract. |
| **vendor claim** | A manufacturer or seller states it. Not independently verified. |
| **design rationale** | The author's reasoning. Not tested, not measured. |
| **unverified** | Could not be checked. |

The use-case document has its own tag legend whose "measured" means "the author measured it" (nothing there is). This register uses **measured by tests** only for repository behaviour covered by the test suite.

`tests/test_claims.py` checks that every test name cited below exists, that IDs are unique and that tags come from the table above. Rows are listed by ID.

## Part 1: claims about the repository (README, docs, code comments)

| ID | Claim (source) | Tag | Where checked |
|---|---|---|---|
| C1 | A contributor needs active consent that permits `community_storytelling` before being added to a project (README "Consent") | measured by tests | `test_original_demo_consent_is_blocked_by_gate`, `test_withdrawn_consent_blocks`, `test_expired_consent_blocks` |
| C2 | A use prohibited in any active consent record is refused even if another record permits it; permission from any active record suffices otherwise (README "Consent") | measured by tests | `test_prohibition_wins_across_records`, `test_permission_from_any_active_record` |
| C3 | Publishing is refused if consent was withdrawn after the project was created (README "Consent lapse") | measured by tests | `test_withdrawal_after_creation_blocks_publish` |
| C4 | Publishing is refused if consent expired after the project was created (README "Consent lapse") | measured by tests | `test_consent_expiring_after_creation_blocks_publish` |
| C5 | Indigenous material can only be registered by a contributor flagged as an Indigenous governance authority (README "Indigenous authority") | measured by tests | `test_indigenous_material_requires_authority` |
| C6 | The `external_ai_training` flag is stored as 0 and cannot be set to 1 through SQL (README "Indigenous authority", Unreleased) | measured by tests | `test_material_never_allows_external_ai_training`, `test_ai_training_flag_cannot_be_set` |
| C7 | `ai_training_allowed()` reads the flag; a legacy row with the flag set is reported as a blocker by `assess_ai_use(material_ids=...)` (Unreleased) | measured by tests | `test_ai_training_allowed_unknown_material`, `test_assess_ai_use_blocks_if_a_legacy_row_allows_training`, `test_assess_ai_use_with_material_ids` |
| C8 | Nothing in the repository trains a model, so the AI-training flag is a recorded refusal that a downstream tool must honour (README) | measured by tests | `test_module_imports_only_the_standard_library`, `test_no_heat_alert_or_hardware_functionality_in_the_module` (these show the module has no ML or hardware imports and no such functions; they do not show that no other software ignores the flag) |
| C9 | Registered material without public-display permission cannot be attached to a project (README "Public display") | measured by tests | `test_non_public_material_blocks_project_atomically`, `test_public_material_links_to_project` |
| C10 | Public-display permission is checked again at publication; `withdraw_public_display()` revokes it (Unreleased) | measured by tests | `test_withdrawn_public_display_blocks_publish`, `test_withdraw_public_display_unknown_material`, `test_public_display_check_passes_with_permission` |
| C11 | The only material type the code models is Indigenous material, so non-Indigenous material has no public-display check (README) | measured by tests | `test_only_indigenous_material_is_modelled` |
| C12 | A project cannot be created without declaring captions, transcript, plain-language summary and non-headset alternative (README "Accessibility") | measured by tests | `test_accessibility_features_required` |
| C13 | The accessibility declaration is re-checked at publication (Unreleased) | measured by tests | `test_publish_rechecks_declaration` |
| C14 | Evidence references are verified when given: non-empty file, UTF-8 text not blank, caption files contain a cue, URL syntax only (not fetched), text declared only; and again at publication (Unreleased) | measured by tests | `test_valid_evidence_is_recorded_and_publishes`, `test_bad_references_rejected_at_creation`, `test_empty_or_cueless_files_rejected`, `test_binary_file_checked_for_size_only_and_directory_rejected`, `test_invalid_utf8_text_rejected`, `test_url_and_text_levels_are_honest`, `test_evidence_for_undeclared_feature_rejected`, `test_evidence_rechecked_at_publish`, `test_changed_file_is_a_warning`, `test_without_evidence_warns_by_default` |
| C15 | The accessibility gate cannot judge whether captions are accurate, a summary is plain or an alternative is usable (README, use-case document) | design rationale | Limit of any automated check; the tests only show what is and is not verified. Review by disabled residents and accessibility staff is required (pilot protocol, section 5) |
| C16 | Compensation must be a finite number greater than zero (README "Fair payment") | measured by tests | `test_contract_amount_must_be_positive_finite` |
| C17 | A project cannot be published while any of its contracts is unpaid (README "Fair payment") | measured by tests | `test_unpaid_contract_blocks_publish` |
| C18 | A declared-paid contributor without a contract blocks publication (Unreleased) | measured by tests | `test_declared_paid_contributor_without_contract_blocks_by_default`, `test_declared_paid_with_zero_contracts_blocks`, `test_paid_contributors_must_be_project_contributors` |
| C19 | A project with no contracts and no declared paid contributors still publishes by default, with a `no_contracts_recorded` warning in the audit entry; strict mode refuses it (README, Unreleased) | measured by tests | `test_no_contracts_is_reported_not_silent`, `test_strict_blocks_project_without_contracts`, `test_contributor_without_contract_is_warning_then_strict_blocker`, `test_fully_contracted_project_publishes_strict` |
| C20 | An open `high` or `critical` incident linked to a project blocks its publication until resolved; other open incidents are warnings, blockers in strict mode (README "Incidents", Unreleased; behaviour change from 0.2.0) | measured by tests | `test_open_serious_incident_blocks_until_resolved`, `test_open_minor_incident_warns_and_strict_blocks`, `test_incident_on_another_project_does_not_block`, `test_unlinked_serious_incident_warns_and_strict_blocks`, `test_resolved_incident_does_not_block` |
| C21 | Incidents can be reported (low/medium/high/critical, free-text type) and resolved with a corrective action (README "Incidents") | measured by tests | `test_incident_lifecycle`, `test_incident_validation` |
| C22 | `publication_report()` changes nothing, lists every failing and warning check, and `publish_project` raises `PublicationBlocked`, a `PermissionError` carrying the report (README) | measured by tests | `test_report_is_read_only`, `test_multiple_blockers_are_all_reported`, `test_publication_report_unknown_project` |
| C23 | `disable_guardrails()` and `adapter.guardrails_active = False` raise `PermissionError` (README "Guardrails") | measured by tests | `test_guardrails_cannot_be_disabled` |
| C24 | Every action writes an audit entry in the same transaction; a failed gate writes none (README "Audit log") | measured by tests | `test_audit_log_records_actions`, `test_failed_gate_writes_no_audit_entry`, `test_non_public_material_blocks_project_atomically` |
| C25 | SQLite triggers reject `UPDATE`/`DELETE` on `audit_log` (README) | measured by tests | `test_audit_log_is_append_only` |
| C26 | The audit log blocks edits through SQL only and the database file is not tamper-proof (README) | design rationale | By construction: triggers live in the file and can be dropped by anyone with write access; the tests show only the SQL-level rejection |
| C27 | `assess_ai_use()` returns and logs an assessment, marks sensitive-data or Indigenous-material requests `blocked_pending_governance`, and is advisory: nothing else refuses to proceed on that status (README) | measured by tests | `test_assess_ai_use`, `test_ai_assessment_status_is_not_consumed_elsewhere` (a source-text check: the status string occurs once, where it is produced) |
| C28 | The impact report summarises governance, projects, payments, accessibility coverage (declared features, not evidence) and incidents (README) | measured by tests | `test_impact_report` |
| C29 | Validation happens before anything is written and each operation is one transaction (README) | measured by tests | `test_non_public_material_blocks_project_atomically`, `test_failed_gate_writes_no_audit_entry` |
| C30 | Importing the module has no side effects; the database opens lazily (README, CHANGELOG) | measured by tests | `test_import_has_no_side_effects` |
| C31 | The module is standard-library only (README, `pyproject.toml`) | measured by tests | `test_module_imports_only_the_standard_library` |
| C32 | The demo runs end to end with placeholder names and produces one published project with total payments of 5700 CAD (README "Run") | measured by tests | `test_demo_runs_end_to_end`, `test_demo_subcommand_still_works` |
| C33 | The original script's own demo stops at the consent gate (README "Provenance") | measured by tests | `test_original_script_demo_stops_at_consent_gate` (skipped after 2027-10-16, the date hard-coded in the original) |
| C34 | The plan generator is deterministic, and the Python and browser versions produce byte-identical JSON and Markdown (README) | measured by tests | `test_json_export_roundtrips`, `test_python_and_js_agree` |
| C35 | The plan never names an Indigenous nation or invents figures, and includes the required sections (README "What the plan will not do") | measured by tests | `test_no_nation_names_or_numbers_invented`, `test_plan_mentions_location_and_has_all_gates`, `test_indigenous_guidance_is_local_and_non_authoritative` |
| C36 | The plan's incident section states the publication block for high/critical incidents in English and French (Unreleased) | measured by tests | `test_plan_template_describes_the_incident_gate_in_both_languages`, `js:incident section names the publication block for high and critical incidents (EN and FR)` |
| C37 | The page makes one same-origin request, for `plan_template.json`, and uses no storage, cookie or beacon APIs; the Content-Security-Policy allows connections to the page's own origin only (README) | measured by tests | `js:page makes exactly one request (the same-origin template) and uses no storage or cookie APIs`, `js:page has a strict CSP and no external resources` (source-text checks, not a network trace) |
| C38 | The page renders user input as text only (XSS-safe) (README, CHANGELOG) | measured by tests | `js:user input is rendered as text only (XSS-safe)`, `js:page scripts never use HTML-string sinks`, `js:markdown escapes user input`, `test_markdown_escapes_user_input` |
| C39 | The page does not track visitors, and GitHub Pages, the host, sees ordinary page requests (README) | unverified | No test or log inspection covers host-side logging; the first half is a statement of the page's source only |
| C40 | CI runs the suite on Python 3.10–3.13 with Node tests (README) | measured by tests | `.github/workflows/tests.yml`; run results are visible on each pull request |
| C41 | The Python suite covers every gate listed in the README (README "Tests") | measured by tests | This register: every row tagged measured by tests cites a test or workflow. Coverage of each gate is by example, not exhaustive, and no coverage tool is run |
| C42 | The repository is a prototype, not legal advice, not a production system, and claims no endorsement by or consultation with any community; demo names are placeholders (README "Scope") | design rationale | Scope statements. They describe the repository's status; there is nothing to test. A grep for partner or endorsement language would show only that none is written, not that none exists |
| C43 | The release DOIs resolve to the Zenodo records for this software (README "DOI") | reported | Link status in the use-case document, reference 4. Re-check before any release |
| C44 | The Zenodo description of v0.2.0 says "non-public material cannot be attached to a project"; the code checks public display for registered Indigenous material only (use-case document reference 4; `.zenodo.json`) | reported | Read on the Zenodo record by a web fetch on 2026-10-27, and in the repository's `.zenodo.json`. Not changed by this work; correcting it needs a new Zenodo version or a metadata edit by the author |
| C45 | Zenodo's licence field says MIT only, while the repository is dual-licensed MIT OR Apache-2.0 (`.zenodo.json` "notes") | reported | `.zenodo.json` states the field holds a single licence identifier |

## Part 2: claims in `docs/heat-resilience-use-case.md`

| ID | Claim | Tag | Where checked |
|---|---|---|---|
| D1 | A holographic display fan cannot meaningfully cool outdoor air; the electricity it uses ends up as heat | design rationale | Physical reasoning. Nothing was measured and no airflow or temperature source was found |
| D2 | No study was found showing that these fans reduce temperatures or heat-related mortality, or comparing them with ordinary signage | unverified | A search result of "no hit" is not proof of absence; the document says so |
| D3 | The devices use persistence of vision on rotating LED blades; they do not project a volumetric hologram and are not sold to move useful air | design rationale | General description consistent with the vendor pages (refs 5, 6, 20), none of which measures airflow |
| D4 | Electrical draw is roughly 36–150 W by model | vendor claim | Refs 5, 6 (product pages, status 200 on 2026-10-27) |
| D5 | Units are not waterproof; vendors recommend a cover or enclosure outdoors and out-of-reach mounting | vendor claim | Refs 18, 19 (manuals, not opened; search extracts only), ref 20 (read) |
| D6 | Trees, vegetation, green and reflective roofs and cool pavements reduce heat exposure | reported | Refs 1, 3, 7 (EPA pages, read) |
| D7 | Early warning, public communication, awareness of symptoms and cooling centres are short-term protections | reported | Ref 2 (EPA, read) |
| D8 | Heat-warning-system review: 15 articles, six reported fewer deaths, eight showed availability alone did not change behaviour; research is limited | reported | Ref 9 (abstract read; full text paywalled) |
| D9 | Comprehensive heat-health action plans appear to lower mortality; evidence for warnings alone is limited or inconsistent; pooled pre–post risk ratio 0.93 (95% CI 0.89–0.99) from 49 studies | reported | Ref 10 (preprint abstract seen in a search extract; not peer reviewed; link to the conference abstract not confirmed) |
| D10 | NOAA social-science report mentions cooling centres on Google Maps, text alerts, video PSAs and bus-stop signs | reported | Ref 16 (text searched) |
| D11 | A 2025 Canadian stocktake describes three components of heat alert and response systems and finds few include an evaluation plan | reported | Ref 17 (text read for the components and summary finding) |
| D12 | Community-science projects show neighbourhood-scale heat variation | reported | Ref 8 (abstract seen via a search extract; full text not read) |
| D13 | Urban-screen and situated-display literature: connection to place, civic participation, hyperlocal relevance, trust | reported | Refs 12, 13 (partly read) |
| D14 | Social-cohesion displays: an opinion questionnaire and one in-the-wild neighbourhood study | reported | Refs 14, 15 (abstract and project page read; a questionnaire is not a behavioural study) |
| D15 | Health Canada lists malls, libraries, community centres, pools, beaches and splash pads as cooling facilities; the page is from 2021 and may be outdated | reported | Ref 11 (loaded through a web fetch tool on 2026-10-27) |
| D16 | WCAG 2.2 SC 2.3.1 limits flashes to three per second unless below thresholds | reported | Refs 21, 22 (W3C pages, status 200) |
| D17 | "No flashing at all" is a stricter kit default than the standard, and refresh behaviour of a given unit has not been assessed | design rationale | Author's rule; the document states no unit was assessed |
| D18 | The causal-pathways table: which companion actions are needed and how strong the evidence is for each pathway | reported | Per-row tags and references in the document; the display itself is *unverified* for every row |
| D19 | The content loop (0–30 s) and the recommended pilot sites | design rationale | Untested; the document says so |
| D20 | The risks and minimum mitigations table | design rationale | Untested; not a safety certification |
| D21 | The municipal extensions (alert connector, two-person approval, expiry, fail-safe, privacy, security, records, ownership, Indigenous governance) are **not implemented** in the repository | measured by tests | `test_no_heat_alert_or_hardware_functionality_in_the_module` (the module contains no such words or functions; it does not check the browser files, which have no such feature either by reading) |
| D22 | Each World-HoloBridge control row (consent, Indigenous authority, public display, accessibility, payment, incidents, audit log, AI-use assessment) describes the code on `main` | measured by tests | Part 1, rows C1–C28 |
| D23 | The browser plan generator makes one same-origin request and sends nothing typed anywhere | measured by tests | C37 |
| D24 | Pilot design phases 1–5, decision gate and outcome ordering | design rationale | Outline in the use-case document; the detailed design is in [pilot-protocol.md](pilot-protocol.md), which has not been run, registered or reviewed |
| D25 | Heat-communication examples ("Map your hottest walk" etc.) link campaigns to real interventions and metrics | design rationale | Untested proposals |
| D26 | No municipal partner, deployment, pilot or endorsement exists | unverified | Absence statement by the author; it cannot be verified by a test and is true only as far as the author knows |
| D27 | Conflict-of-interest, funding and AI-assistance statements | design rationale | Declarations by the author; not independently checked |

## What this register does not cover

- The CHANGELOG's account of changes in release 0.2.0 and 0.1.0 is checked by the git history and the tests above, not claim by claim.
- The Zenodo records themselves, the hosted web page's server logs and any third-party link beyond the status noted in the reference list.
- Real-world safety, effectiveness or legal compliance of any control. The tests show what the code does, not that it is enough.
