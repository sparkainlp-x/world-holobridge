# Changelog

## 0.2.0-dev — unreleased

Release metadata (`CITATION.cff`, `.zenodo.json`) stays at 0.1.0 until the
next release; the package version is `0.2.0.dev0`.

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

## 0.1.0 — 2026-10-16

First public version. The original script is kept unchanged as
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

- pytest suite (44 tests) and GitHub Actions CI on Python 3.10–3.13.
- `pyproject.toml`, `CITATION.cff`, `.zenodo.json`, `.gitignore`, dual
  `LICENSE-MIT` / `LICENSE-APACHE`.
