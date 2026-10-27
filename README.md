# World-HoloBridge

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23423941.svg)](https://doi.org/10.5281/zenodo.23423941)

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

The plan is built in your browser from a template file. The page makes one
same-origin request, for `plan_template.json`, and no other request; what you
type is not sent anywhere (its Content-Security-Policy allows connections to
its own origin only). It uses no storage and no analytics (nothing in `site/`
calls the storage or cookie APIs). It is still served by a web host (GitHub
Pages), which sees ordinary page requests. The same plan comes from Python (install with
`pip install .` from a checkout to get the `world-holobridge` command, or use
`python world_holobridge.py plan ...`):

```sh
world-holobridge plan --city Moncton --region "New Brunswick" --country Canada
world-holobridge plan --city Moncton --country Canada --language fr --format json --out-dir plans
world-holobridge plan --city Moncton --country Canada --run-pipeline   # show the gates working
```

```python
import world_holobridge as wh

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

## Use case: urban heat resilience

[docs/heat-resilience-use-case.md](docs/heat-resilience-use-case.md) describes how these gates could support a community heat-communication project built around holographic LED-fan displays, and compares each gate with what the code actually does. A holographic fan does not cool the air, and no evidence was found that it reduces temperatures or heat-related illness; the document treats it as a communication layer to be tested against ordinary signage. The heat-specific extensions it lists (alert feeds, two-person approval, expiry, security) are **not implemented** here. No municipal partner or deployment is claimed. [docs/pilot-protocol.md](docs/pilot-protocol.md) is a pre-registration-style protocol for evaluating that idea (nothing has been run), and [docs/evidence-register.md](docs/evidence-register.md) lists each claim in the repository docs with an evidence tag and where it is checked.

## What it checks

Each row says exactly what the code does today (the Unreleased changes on
`main` are included and marked; release 0.2.0 did less, see
[CHANGELOG.md](CHANGELOG.md)). Nothing here is verified outside the repository's
own tests, and none of it identifies a person: the prototype has no log-in, so
it records the actor names it is given but cannot check who is calling.

| Gate | Behaviour |
| --- | --- |
| Consent | A contributor must hold an active consent (not withdrawn, not expired) that permits the single use `community_storytelling` before being added to a project and again at publication. A use prohibited in any active record is refused, even if another record permits it. |
| Consent lapse | Publishing is refused if a contributor's consent was withdrawn or expired after the project was created. |
| Indigenous authority | Indigenous material can only be registered by a contributor flagged as an Indigenous governance authority. The material's `external_ai_training` flag is stored as 0 and SQLite triggers reject any attempt to set it to 1 (*Unreleased*). `ai_training_allowed(material_id)` reads it. Nothing in this repository trains a model, so a downstream tool has to call that function and honour the answer. |
| Public display | Registered material without public-display permission cannot be attached to a project. At publication the permission is checked again for every attached material, and `withdraw_public_display(material_id)` revokes it (*Unreleased*). The only material type the code models is Indigenous material; there is no generic material type, so non-Indigenous material (for example a non-public interview) is not checked because it is not represented. |
| Accessibility | Every project must declare captions, a transcript, a plain-language summary and a non-headset alternative; the declaration is re-checked at publication. Optionally (*Unreleased*), `create_project(..., accessibility_evidence={...})` takes a reference for each feature: `file:<path>` must be a non-empty regular file (text files must be UTF-8 and not blank; `.vtt`/`.srt` must contain a cue), `http(s)://` is checked for syntax only and is **not fetched**, and `text:<description>` is recorded as declared, not verifiable. File references are verified again at publication. Without evidence references only the feature names are checked, and publication reports a warning for each. The code cannot judge whether captions are accurate or the alternative is usable. |
| Fair payment | Compensation must be greater than zero. A project cannot be published while any of its contracts is unpaid. A project can declare contributors as paid with `paid_contributor_ids` (*Unreleased*); publication is refused while any of them has no contract on the project. A project with no contracts and no declared paid contributors can still be published by default, but the result carries a `no_contracts_recorded` warning that is written into the audit entry. |
| Incidents | Incidents (low/medium/high/critical, free-text type) can be reported and resolved with a corrective action. An open `high` or `critical` incident linked to a project blocks that project's publication until resolved (*Unreleased*; **a behaviour change**). Open lower-severity incidents linked to the project, and open high/critical incidents that name no project, are reported as warnings. |
| Strict publication | `publish_project(..., strict=True)` and `publication_report(..., strict=True)` (*Unreleased*) turn these warnings into blockers: no contracts recorded, a contributor without a contract, missing accessibility evidence, any open linked incident, and an open unlinked high/critical incident. Default is `strict=False`. |
| Publication report | `publication_report(project_id)` runs every publication gate without changing anything and returns each check as `pass`, `warn` or `fail` with a code and message. `publish_project` raises `PublicationBlocked` (a `PermissionError`) carrying that report. |
| Guardrails | `disable_guardrails()` and `adapter.guardrails_active = False` both raise `PermissionError`. |
| Audit log | Every action writes an entry in the same transaction. SQLite triggers reject `UPDATE`/`DELETE` on `audit_log` (this blocks edits through SQL; it does not make the file tamper-proof). |
| Impact report | JSON summary of governance, projects, payments, accessibility coverage (declared features, not evidence) and incidents, with stated limitations. |

`assess_ai_use()` records and returns an assessment that marks sensitive-data or
Indigenous-material requests as `blocked_pending_governance`. It is **advisory**:
nothing else in the code refuses to proceed on that status. Passing
`material_ids` also checks each material's stored AI-training flag.

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

The Python suite covers every gate above (publication gates in `tests/test_hardening.py`), transactional behaviour, the
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
"Version: 1.0.0"; the first public release is numbered 0.2.0 (0.1.0 was
prepared but never released).

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

## DOI

Concept DOI (all versions): [10.5281/zenodo.23423941](https://doi.org/10.5281/zenodo.23423941). Version DOI for v0.2.0: [10.5281/zenodo.23423942](https://doi.org/10.5281/zenodo.23423942).
