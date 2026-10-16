# Changelog

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
