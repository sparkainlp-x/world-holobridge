# Changelog

## Unreleased

No version bump, tag, release or Zenodo change is part of these entries.

### Behaviour changes

- **BREAKING (narrow): an open `high` or `critical` incident linked to a project now blocks `publish_project` until it is resolved.** In 0.2.0 an open incident never blocked publication. Projects with no such incident are unaffected; the plan template's incident gate text (English and French) now says so. Open lower-severity incidents linked to the project, and open high/critical incidents that name no project, are warnings (written to the audit entry), and block only with `strict=True`.
- **BREAKING (narrow): `publish_project` re-checks, and can now refuse on, three more conditions:** a contributor declared as paid (new `paid_contributor_ids`) with no contract; a recorded accessibility evidence reference that no longer verifies (or a declaration missing a required feature); attached material whose public-display permission was withdrawn. None of these can occur for a project created without the new options, except through direct database edits, so existing callers see no change.
- `publish_project(project_id, approved_by, strict=False)` raises `PublicationBlocked` (a subclass of `PermissionError`; existing `except PermissionError` code and the existing message text still work). Its audit entry now also records `strict` and the list of `warnings`.
- Not breaking: a project with no contracts and no declared paid contributors still publishes by default, but now carries a `no_contracts_recorded` warning in the audit entry and in `publication_report()`. `strict=True` refuses it.
- Not breaking: `indigenous_materials.external_ai_training` is now constrained to 0 by SQLite triggers (insert and update). Databases created by 0.2.0 gain the triggers and two new tables when they are next opened; existing rows are not rewritten.

### Added

- `publication_report(project_id, strict=False)`: runs every publication gate (payment, consent, incidents, accessibility, public display) without changing anything and returns each check as pass/warn/fail with a code and message.
- `create_project(..., paid_contributor_ids=None, accessibility_evidence=None, evidence_base_dir=None)`: declare who is expected to be paid; record a reference for each accessibility feature. `verify_accessibility_reference()` checks `file:` (non-empty regular file; text must be UTF-8 and not blank; `.vtt`/`.srt` need a cue; SHA-256 recorded), `http(s)://` (syntax only, **not fetched**) and `text:` (declared only, not verifiable).
- `withdraw_public_display(material_id)`, `ai_training_allowed(material_id)`, and `assess_ai_use(..., material_ids=...)`, which checks each material's AI-training flag.
- `BLOCKING_INCIDENT_SEVERITIES`, `PublicationBlocked`.
- New tables `project_paid_contributors` and `accessibility_evidence`.
- `docs/pilot-protocol.md`: a pre-registration-style protocol for evaluating the heat-resilience idea (hypotheses, outcomes and instruments, arms A/B/C, sample-size method with no invented numbers, safety stopping rules, independent evaluator, data plan, fixed analysis plan, deviations log, negative-result commitment). It is a draft: nothing has been registered, reviewed or run.
- `docs/evidence-register.md`: each claim in the README and the use-case document with an evidence tag and where it is checked. `tests/test_claims.py` checks that it cites only existing tests.
- Tests: 58 new Python tests (104 to 162, in `tests/test_hardening.py` and `tests/test_claims.py`) and 2 new Node tests (7 to 9).

### Changed (documentation corrected to match the code)

- README "What it checks" rewritten so every control is described as implemented: consent checks one use, `community_storytelling`; public display applies to registered Indigenous material only because that is the only material type; accessibility is a declaration unless evidence references are given; the payment gate depends on contracts existing or being declared; `assess_ai_use` is advisory; the audit log blocks SQL edits only.
- README: the plan page makes one same-origin request (`plan_template.json`) and is served by a web host; the earlier wording "no server, no external requests" in the 0.2.0 README and changelog was too broad. The statement is now backed by a Node test.
- Use-case document: control table updated to say where `main` differs from 0.2.0; pointer to the pilot protocol and evidence register.
- `run_plan_pipeline` declares its placeholder contributors as paid so the new gate is exercised. The pipeline's output strings are otherwise unchanged except for the accessibility line, which now says only the feature names are declared in that placeholder run.

### Not changed (known, left for the author)

- `.zenodo.json` and the published Zenodo record for 0.2.0 still say "non-public material cannot be attached to a project" and list the licence as MIT only. Fixing them needs a metadata edit or a new version.
- There is no generic (non-Indigenous) material type, no log-in or role check on any function, and no alert, display or hardware code.

### Added (earlier, now merged)

- `docs/heat-resilience-use-case.md`: a documented use case on holographic display fans as a heat-risk communication layer. It states that a holographic fan does not cool air and that no evidence was found for temperature or mortality effects, maps each governance gate to what the code does and does not do for this use, lists municipal extensions that are **not implemented**, adds a photosensitivity rule (no flashing; WCAG 2.2 SC 2.3.1), an evidence-tag legend, a pilot design that compares against ordinary signage, and a numbered reference list with link status. Documentation only: no code, version, tag or release change.

## 0.2.0 — 2026-10-16

First release. Version 0.1.0 (below) was prepared and pushed to the
repository but never released; its changes ship in 0.2.0.

### Added

- **Community plan generator.** `generate_community_plan(city, country,
  region=None, language="en")` returns a structured, deterministic plan for any
  city, built from the framework's own rules: advisory-circle roles, the five
  required protocols with default text, a consent checklist, the four required
  accessibility features, payment-before-publication and a contract template,
  the incident process and severities, the AI-use assessment, a five-phase
  timeline (discovery, governance setup, co-design, pilot, evaluation),
  evaluation and the impact report, and a note that laws and principles vary.
  Each section names the framework check that enforces it.
- `plan_to_markdown()` and `plan_to_json()` exports; `run_plan_pipeline(plan)`
  runs the governance pipeline from a plan with placeholder contributors to
  show how each section maps to a gate.
- CLI: `world-holobridge plan --city ... --country ... [--region ...]
  [--language en|fr] [--format md|json] [--out-dir DIR] [--run-pipeline]`.
  `world-holobridge` / `world-holobridge demo` still run the original demo.
- **Static web page** (`site/`, deployed to GitHub Pages): form for city,
  optional region and country; renders the same plan in the browser; download
  as Markdown or JSON; print view; EN/FR toggle. No server, no external
  requests, no storage, no tracking; strict Content-Security-Policy; user input
  is rendered as text nodes only.
- **Shared template** `plan_template.json` read by both Python and the page,
  with a parity test that checks byte-identical JSON and Markdown output and
  identical input validation, plus Node tests for XSS-safe rendering.

### Honesty constraints built into the plan

- The generator never says whose traditional territory a city is on and never
  names an Indigenous nation, community or organization. It tells users to
  identify rights-holders through local sources and confirm directly with the
  communities, and points to native-land.ca only as a non-authoritative
  starting point. Tests check that no nation names (and no figures) appear.
- It includes no local statistics, populations or organizations, and does not
  suggest fee amounts.
- It notes that consent, privacy and Indigenous-data rules vary (OCAP® in
  Canada, CARE Principles) and that it is not legal advice.
- The Fredericton / Wolastoqey names remain only in the existing demo, which
  is labelled as a placeholder example.

## 0.1.0 — 2026-10-16 (never released)

First public version of the repository; not released. The original script is kept unchanged as
`world_holobridge_original.py` (its header said "Version: 1.0.0" and
"License: Apache-2.0 / MIT"); the working module is `world_holobridge.py`.
The commit history shows the original, then each change.

### Finding in the original

- The original demo did not run to completion. `create_project` raised
  `PermissionError: All contributors need active consent for community
  storytelling.` because the accessibility advocate's consent listed only
  `accessibility_review` and `project_evaluation`. The gate behaved correctly;
  the demo data was wrong. The demo now adds `community_storytelling` to that
  consent, and a test shows the gate still blocks the original consent.

### Fixed

- **No import side effects.** Importing no longer opens `world_holobridge.db`
  or creates `output/`. The connection opens lazily on first use;
  `configure(db_path=..., export_dir=..., connection=...)` selects a file,
  `":memory:"` or an existing connection. `con` still works as a module
  attribute. The report directory is created only when a report is written.
- **Timezone-aware UTC.** `datetime.utcnow()` (deprecated) replaced by
  `datetime.now(timezone.utc)`; the timestamp format (`...Z`) is unchanged.
- **Atomic `create_project`.** All gates (accessibility, consent, material
  existence and public-display permission) are checked before anything is
  written; project, contributor links, material links and the audit entry are
  written in one transaction. The original inserted the project before checking
  materials, so a failed check left a partial project.
- **Action and audit entry in one transaction** for every write, so a write
  cannot land without its audit entry (or the reverse).
- **Append-only audit log enforced.** SQLite triggers reject `UPDATE` and
  `DELETE` on `audit_log`. (This protects against edits through SQL; it does
  not make the database file tamper-proof.)
- **Foreign keys enforced** with `PRAGMA foreign_keys = ON`;
  `incidents.project_id` now references `projects(id)` for new databases.
- **Consent precedence.** A use prohibited in any active consent record is
  refused even if another active record permits it (previously the outcome
  depended on row order). A single record cannot both permit and prohibit the
  same use.
- **Idempotent state changes.** `mark_paid`, `withdraw_consent`,
  `resolve_incident` and `publish_project` return `False` and write no
  duplicate audit entry when the record is already in the target state.
- **Publish re-checks consent.** `publish_project` refuses to publish if any
  project contributor's community-storytelling consent was withdrawn or
  expired after the project was created.
- **Guardrails really cannot be disabled.** `guardrails_active` is a read-only
  property; assigning a false value raises `PermissionError`.
- **Input validation.** Compensation must be a finite number greater than zero
  (NaN, infinity, booleans and strings rejected); currency, attribution,
  license terms, revenue share, payment reference and approver must be
  non-empty; incidents must reference an existing project or none. Audit
  entries store the validated values.
- **Impact report.** "Active consents" now excludes expired ones (new
  `expired_consents` count); accessibility coverage keys are sorted; the export
  directory can be passed per call.
- **Demo does not go stale.** Demo consent expiry is one year from the run
  date instead of the fixed `2027-10-16`. The demo is `run_demo()` / `main()`
  with `--db` and `--output-dir` options.

### Added

- pytest suite (44 tests at the time) and GitHub Actions CI on Python 3.10–3.13.
- `pyproject.toml`, `CITATION.cff`, `.zenodo.json`, `.gitignore`, dual
  `LICENSE-MIT` / `LICENSE-APACHE`.
