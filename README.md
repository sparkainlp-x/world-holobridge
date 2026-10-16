# World-HoloBridge

A small reference prototype of a **governance workflow** for community-led
cultural and spatial-media projects, written in standard-library Python with
SQLite. It turns a set of written safeguards into code that refuses to proceed
when a safeguard is not met, and records what happened in an audit log.

> **Scope.** This is a prototype for discussion and testing. It is **not legal
> advice**, **not a production system**, and not a substitute for protocols
> defined by the communities concerned. It does **not** claim endorsement by,
> or consultation with, Wolastoqey communities or any other community or
> organization. All names in the demo (for example "Local Artist A" or
> "Wolastoqey Governance Representative") are **placeholders**, not real people
> or bodies.

## Community plan generator

**Try it in the browser:** https://sparkainlp-x.github.io/world-holobridge/

Enter a city, an optional region and a country to get a starting plan built
from the framework's own rules: paid advisory-circle roles, the five required
protocols, a consent checklist, the required accessibility features, payment
before publication with a contract template, the incident process, the AI-use
assessment, a five-phase timeline, evaluation and the impact report. Each
section names the check in the code that enforces it. Download it as Markdown
or JSON, or print it. English and French.

The page runs entirely in the browser: no server, no external requests, no
storage, no analytics. The same plan comes from Python:

```sh
world-holobridge plan --city Moncton --region "New Brunswick" --country Canada
world-holobridge plan --city Moncton --country Canada --language fr --format json --out-dir plans
world-holobridge plan --city Moncton --country Canada --run-pipeline   # show the gates working
```

```python
plan = wh.generate_community_plan("Moncton", "Canada", region="New Brunswick", language="fr")
print(wh.plan_to_markdown(plan))
```

Both read `plan_template.json`; a test checks that Python and the browser
produce byte-identical JSON and Markdown.

**What the plan will not do.** It never says whose traditional territory a
city is on and never names an Indigenous nation, community or organization.
Instead it asks you to identify the nations and rights-holders through local
sources and to confirm directly with those communities; native-land.ca is
mentioned only as a starting point that is not authoritative. It contains no
local statistics, population figures or organization names and suggests no fee
amounts. It notes that laws on consent, privacy and Indigenous data vary (for
example OCAP® in Canada and the CARE Principles) and it is not legal advice.

## What it checks

| Gate | Behaviour |
| --- | --- |
| Consent | A contributor must hold an active consent (not withdrawn, not expired) that permits `community_storytelling`. A use prohibited in any active record is refused, even if another record permits it. |
| Consent lapse | Publishing is refused if a contributor's consent was withdrawn or expired after the project was created. |
| Indigenous authority | Indigenous material can only be registered by a contributor flagged as an Indigenous governance authority. Material is never marked for external AI training. |
| Public display | Material without public-display permission cannot be attached to a project. |
| Accessibility | Every project must include captions, a transcript, a plain-language summary and a non-headset alternative. |
| Fair payment | Compensation must be greater than zero; a project cannot be published while any of its contracts is unpaid. |
| Guardrails | `disable_guardrails()` and `adapter.guardrails_active = False` both raise `PermissionError`. |
| Incidents | Incidents (low/medium/high/critical) can be reported and resolved with a corrective action. |
| Audit log | Every action writes an entry in the same transaction. SQLite triggers reject `UPDATE`/`DELETE` on `audit_log` (this blocks edits through SQL; it does not make the file tamper-proof). |
| Impact report | JSON summary of governance, projects, payments, accessibility coverage and incidents, with stated limitations. |

`assess_ai_use()` records a simple assessment that marks sensitive-data or
Indigenous-material requests as blocked pending governance.

Validation happens before anything is written, and each operation is a single
transaction, so a failed check leaves no partial records.

## Run

Python 3.10–3.13, no dependencies.

The demo below is a labelled placeholder example set in Fredericton; its
names are not real people or bodies.

```sh
python world_holobridge.py                       # writes world_holobridge.db and output/
python world_holobridge.py --db :memory: --output-dir /tmp/holobridge
```

As a library:

```python
import world_holobridge as wh

wh.configure(db_path=":memory:", export_dir="output")   # nothing happens on import
cid = wh.add_contributor("Contributor A", "Artist")
wh.register_consent(cid, ["community_storytelling"], ["external_ai_training"], "2027-12-31")
```

## Tests

```sh
pip install pytest
python -m pytest -q                 # Python tests, including the Python/JS parity test (needs node)
node --test tests/js/plan.test.js   # JavaScript tests (rendering, XSS safety, validation)
python scripts/build_site.py _site && python -m http.server -d _site 8000   # preview the page
```

The Python suite covers every gate above, transactional behaviour, the
append-only audit log, idempotency, the impact report, the demo, the original
script's behaviour, and the plan generator (all sections present, location in
the output, no nation names or figures, input validation, Markdown escaping,
CLI, pipeline). CI runs it on Python 3.10, 3.11, 3.12 and 3.13 together with
the Node tests.

## Provenance and the original script

`world_holobridge_original.py` is the original script, kept unchanged. Its own
demo did not complete: `create_project` raised `PermissionError` because the
accessibility advocate's consent did not include `community_storytelling`. The
gate was right and the demo data was wrong. The working module adds that use to
the demo consent, and a test confirms the gate still blocks the original
consent. Note that importing the original file creates `world_holobridge.db`
and `output/` in the current directory; the working module does not.

See [CHANGELOG.md](CHANGELOG.md) for every change. The original header said
"Version: 1.0.0"; this first public release is numbered 0.1.0.

## License

Dual-licensed under either of

- MIT License ([LICENSE-MIT](LICENSE-MIT))
- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE))

at your option (SPDX: `MIT OR Apache-2.0`). Unless you explicitly state
otherwise, any contribution you submit for inclusion is dual-licensed as
above, without additional terms or conditions.

## Citation

See [CITATION.cff](CITATION.cff). Author: Jean-François Brisson (Spark AI NLP),
ORCID [0009-0000-9778-5374](https://orcid.org/0009-0000-9778-5374).
