"""
World-HoloBridge: Operational Safeguards & Governance Framework
===============================================================

Artifact for Open Science & Digital Humanities Infrastructure
Zenodo Metadata & Reference Engine

Description:
------------
This script provides an end-to-end, reproducible implementation of the 
HoloCommons safeguards framework for community-led cultural and spatial-media 
projects. It operationalizes data governance protocols, inclusive consent 
management, Indigenous cultural authority oversight, fair compensation gatekeeping, 
accessibility requirements, incident reporting, and structured evaluation export.

This is a reference prototype of a governance workflow. It is not legal advice
and not a production system. Names used in the demo are placeholders.

License: MIT OR Apache-2.0 (dual-licensed; see LICENSE-MIT and LICENSE-APACHE)
Version: 0.2.0
"""

# SPDX-License-Identifier: MIT OR Apache-2.0

from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
import argparse
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Set, Union
import uuid

__version__ = "0.2.0"

# ---------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------

# Defaults only. Nothing is opened or created on import: the database is
# connected lazily on first use and the export directory is created only when
# a report is written. Use configure() to point at another path or ":memory:".
DB_PATH: Union[str, Path] = Path("world_holobridge.db")
EXPORT_DIR: Path = Path("output")

REQUIRED_ACCESSIBILITY: Set[str] = {
    "captions",
    "transcript",
    "plain_language_summary",
    "non_headset_alternative",
}

SEVERITIES: Set[str] = {"low", "medium", "high", "critical"}

_con: Optional[sqlite3.Connection] = None


# ---------------------------------------------------------------------
# Database & Core Utilities
# ---------------------------------------------------------------------

def utc_now() -> str:
    """Returns ISO-8601 UTC timestamp string (timezone-aware, 'Z' suffix)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _today() -> date:
    """Current date used for consent expiry checks (patchable in tests)."""
    return date.today()


SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    details TEXT NOT NULL
);

-- Append-only audit trail: UPDATE and DELETE are rejected at the SQL level.
CREATE TRIGGER IF NOT EXISTS audit_log_no_update
BEFORE UPDATE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only');
END;

CREATE TRIGGER IF NOT EXISTS audit_log_no_delete
BEFORE DELETE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only');
END;

CREATE TABLE IF NOT EXISTS contributors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    organization TEXT,
    indigenous_authority INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consents (
    id TEXT PRIMARY KEY,
    contributor_id TEXT NOT NULL,
    permitted_uses TEXT NOT NULL,
    prohibited_uses TEXT NOT NULL,
    expires_on TEXT NOT NULL,
    withdrawn INTEGER NOT NULL DEFAULT 0,
    withdrawn_at TEXT,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY(contributor_id) REFERENCES contributors(id)
);

CREATE TABLE IF NOT EXISTS indigenous_materials (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    authority_id TEXT NOT NULL,
    permissions TEXT NOT NULL,
    external_ai_training INTEGER NOT NULL DEFAULT 0,
    public_display INTEGER NOT NULL DEFAULT 0,
    retention_policy TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(authority_id) REFERENCES contributors(id)
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    theme TEXT NOT NULL,
    media_format TEXT NOT NULL,
    human_lead TEXT NOT NULL,
    status TEXT NOT NULL,
    ai_role TEXT NOT NULL,
    accessibility TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS project_contributors (
    project_id TEXT NOT NULL,
    contributor_id TEXT NOT NULL,
    PRIMARY KEY(project_id, contributor_id),
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(contributor_id) REFERENCES contributors(id)
);

CREATE TABLE IF NOT EXISTS project_materials (
    project_id TEXT NOT NULL,
    material_id TEXT NOT NULL,
    PRIMARY KEY(project_id, material_id),
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(material_id) REFERENCES indigenous_materials(id)
);

CREATE TABLE IF NOT EXISTS contracts (
    id TEXT PRIMARY KEY,
    contributor_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    role TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    attribution TEXT NOT NULL,
    license_terms TEXT NOT NULL,
    revenue_share TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(contributor_id) REFERENCES contributors(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    corrective_action TEXT,
    reported_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);
"""


def init_db(path: Union[str, Path, None] = None) -> sqlite3.Connection:
    """Initializes the relational SQLite database with governance schema.

    ``path`` may be a filesystem path or ``":memory:"``. Foreign-key
    enforcement is switched on for the returned connection.
    """
    if path is None:
        path = DB_PATH
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
    con.commit()
    return con


def configure(
    db_path: Union[str, Path, None] = None,
    export_dir: Union[str, Path, None] = None,
    connection: Optional[sqlite3.Connection] = None,
) -> sqlite3.Connection:
    """Selects the database (path, ``":memory:"`` or an existing connection)
    and optionally the report export directory. Closes any previous
    module-managed connection. Returns the active connection."""
    global _con, DB_PATH, EXPORT_DIR
    if export_dir is not None:
        EXPORT_DIR = Path(export_dir)
    if _con is not None and _con is not connection:
        _con.close()
    _con = None
    if connection is not None:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA)
        connection.commit()
        _con = connection
    else:
        if db_path is not None:
            DB_PATH = db_path
        _con = init_db(DB_PATH)
    return _con


def get_connection() -> sqlite3.Connection:
    """Returns the active connection, opening ``DB_PATH`` lazily on first use."""
    global _con
    if _con is None:
        _con = init_db(DB_PATH)
    return _con


def close_connection() -> None:
    """Closes the module-managed connection, if any."""
    global _con
    if _con is not None:
        _con.close()
        _con = None


def __getattr__(name: str) -> Any:
    # Backwards compatibility: the original module exposed a global ``con``.
    if name == "con":
        return get_connection()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


@contextmanager
def _transaction() -> Iterator[sqlite3.Connection]:
    """One atomic unit of work: commits on success, rolls back on any error."""
    con = get_connection()
    with con:
        yield con


def _audit(con: sqlite3.Connection, actor: str, action: str, entity_type: str,
           entity_id: str, details: Dict[str, Any]) -> str:
    record_id = str(uuid.uuid4())
    con.execute(
        """INSERT INTO audit_log
           (id, timestamp, actor, action, entity_type, entity_id, details)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            record_id, utc_now(), actor, action, entity_type, entity_id,
            json.dumps(details, ensure_ascii=False),
        ),
    )
    return record_id


def audit(actor: str, action: str, entity_type: str, entity_id: str, details: Dict[str, Any]) -> str:
    """Appends an entry to the append-only audit trail (UPDATE/DELETE on
    ``audit_log`` are rejected by SQLite triggers)."""
    with _transaction() as con:
        return _audit(con, actor, action, entity_type, entity_id, details)


def rows(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    return [dict(r) for r in get_connection().execute(query, params).fetchall()]


def row(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    results = rows(query, params)
    return results[0] if results else None


def validate_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    return value.strip()


def validate_future_date(value: str) -> str:
    """Accepts today or a later date in ISO ``YYYY-MM-DD`` format."""
    try:
        if not isinstance(value, str) or date.fromisoformat(value) < _today():
            raise ValueError
    except ValueError as exc:
        raise ValueError("Use a future ISO date in YYYY-MM-DD format.") from exc
    return value


def _validate_uses(values: Any, label: str) -> List[str]:
    if isinstance(values, str) or not isinstance(values, (list, tuple, set, frozenset)):
        raise ValueError(f"{label} must be a list of strings.")
    return list(dict.fromkeys(validate_text(v, label) for v in values))


# ---------------------------------------------------------------------
# Governance Adapter Class
# ---------------------------------------------------------------------

class WorldHoloBridgeAdapter:
    """Central adapter instance governing regional policy and advisory parameters."""

    REQUIRED_PROTOCOLS = frozenset({
        "data_scraping",
        "indigenous_leadership",
        "economic_fairness",
        "consent_withdrawal",
        "accessibility",
    })

    def __init__(self, country: str, city: str, cultural_context: str, lead_organization: str, advisory_circle: List[str]):
        self.id = str(uuid.uuid4())
        self.country = validate_text(country, "Country")
        self.city = validate_text(city, "City")
        self.cultural_context = validate_text(cultural_context, "Cultural context")
        self.lead_organization = validate_text(lead_organization, "Lead organization")

        if not advisory_circle:
            raise ValueError("A paid advisory circle is required.")

        self.advisory_circle = [validate_text(a, "Advisory-circle member") for a in advisory_circle]
        self.protocols: Dict[str, str] = {}

        audit("system", "initialize_adapter", "adapter", self.id, {
            "country": self.country,
            "city": self.city,
            "cultural_context": self.cultural_context,
            "lead_organization": self.lead_organization,
            "advisory_circle": self.advisory_circle,
        })

    @property
    def guardrails_active(self) -> bool:
        """Always True: guardrails cannot be switched off on an adapter."""
        return True

    @guardrails_active.setter
    def guardrails_active(self, value: bool) -> None:
        if not value:
            raise PermissionError("Guardrails cannot be disabled.")

    def set_protocols(self, protocols: Dict[str, str]):
        missing = self.REQUIRED_PROTOCOLS - set(protocols)
        if missing:
            raise ValueError(f"Missing required protocols: {sorted(missing)}")

        cleaned = {validate_text(k, "Protocol name"): validate_text(v, f"Protocol '{k}'")
                   for k, v in protocols.items()}
        self.protocols = cleaned
        audit("governance", "set_protocols", "adapter", self.id, cleaned)

    def disable_guardrails(self):
        raise PermissionError("Guardrails cannot be disabled.")


# ---------------------------------------------------------------------
# Operational Functions
# ---------------------------------------------------------------------

def add_contributor(name: str, role: str, organization: Optional[str] = None, indigenous_authority: bool = False) -> str:
    name = validate_text(name, "Name")
    role = validate_text(role, "Role")
    contributor_id = str(uuid.uuid4())
    with _transaction() as con:
        con.execute(
            """INSERT INTO contributors
               (id, name, role, organization, indigenous_authority, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (contributor_id, name, role, organization, int(bool(indigenous_authority)), utc_now()),
        )
        _audit(con, "administrator", "add_contributor", "contributor", contributor_id, {
            "name": name,
            "role": role,
            "indigenous_authority": bool(indigenous_authority),
        })
    return contributor_id


def register_consent(contributor_id: str, permitted_uses: List[str], prohibited_uses: List[str], expires_on: str) -> str:
    if not row("SELECT id FROM contributors WHERE id = ?", (contributor_id,)):
        raise ValueError("Contributor does not exist.")

    if not permitted_uses:
        raise ValueError("At least one permitted use is required.")

    permitted = _validate_uses(permitted_uses, "Permitted use")
    prohibited = _validate_uses(prohibited_uses, "Prohibited use")
    overlap = set(permitted) & set(prohibited)
    if overlap:
        raise ValueError(f"Uses cannot be both permitted and prohibited: {sorted(overlap)}")
    expires_on = validate_future_date(expires_on)

    consent_id = str(uuid.uuid4())
    with _transaction() as con:
        con.execute(
            """INSERT INTO consents
               (id, contributor_id, permitted_uses, prohibited_uses,
                expires_on, withdrawn, recorded_at)
               VALUES (?, ?, ?, ?, ?, 0, ?)""",
            (consent_id, contributor_id, json.dumps(permitted), json.dumps(prohibited),
             expires_on, utc_now()),
        )
        _audit(con, "administrator", "register_consent", "consent", consent_id, {
            "contributor_id": contributor_id,
            "permitted_uses": permitted,
            "prohibited_uses": prohibited,
            "expires_on": expires_on,
        })
    return consent_id


def withdraw_consent(consent_id: str) -> bool:
    """Withdraws a consent. Returns False (no change, no new audit entry)
    if it was already withdrawn."""
    record = row("SELECT id, withdrawn FROM consents WHERE id = ?", (consent_id,))
    if not record:
        raise ValueError("Consent record does not exist.")
    if record["withdrawn"]:
        return False

    with _transaction() as con:
        con.execute(
            "UPDATE consents SET withdrawn = 1, withdrawn_at = ? WHERE id = ?",
            (utc_now(), consent_id),
        )
        _audit(con, "contributor_or_administrator", "withdraw_consent", "consent",
               consent_id, {"withdrawn": True})
    return True


def consent_allows(contributor_id: str, use: str) -> bool:
    """True only if at least one active (not withdrawn, not expired) consent
    permits ``use`` and no active consent prohibits it. A prohibition in any
    active record wins over permissions in other records."""
    records = rows(
        """SELECT * FROM consents
           WHERE contributor_id = ? AND withdrawn = 0 AND expires_on >= ?""",
        (contributor_id, _today().isoformat()),
    )
    permitted_somewhere = False
    for record in records:
        if use in json.loads(record["prohibited_uses"]):
            return False
        if use in json.loads(record["permitted_uses"]):
            permitted_somewhere = True
    return permitted_somewhere


def register_indigenous_material(adapter: WorldHoloBridgeAdapter, title: str, authority_id: str, permissions: List[str], retention_policy: str, public_display: bool = False) -> str:
    authority = row(
        """SELECT * FROM contributors
           WHERE id = ? AND indigenous_authority = 1""",
        (authority_id,),
    )
    if not authority:
        raise PermissionError(
            "Indigenous material requires a registered Indigenous governance authority."
        )

    title = validate_text(title, "Title")
    retention_policy = validate_text(retention_policy, "Retention policy")
    permissions = _validate_uses(permissions, "Permission")

    material_id = str(uuid.uuid4())
    with _transaction() as con:
        con.execute(
            """INSERT INTO indigenous_materials
               (id, title, authority_id, permissions, external_ai_training,
                public_display, retention_policy, created_at)
               VALUES (?, ?, ?, ?, 0, ?, ?, ?)""",
            (material_id, title, authority_id, json.dumps(permissions),
             int(bool(public_display)), retention_policy, utc_now()),
        )
        _audit(con, authority["name"], "register_indigenous_material",
               "indigenous_material", material_id, {
                   "title": title,
                   "permissions": permissions,
                   "public_display": bool(public_display),
                   "external_ai_training": False,
                   "retention_policy": retention_policy,
               })
    return material_id


def create_contract(contributor_id: str, project_id: str, role: str, amount: float, currency: str = "CAD", attribution: str = "Named contributor", license_terms: str = "To be agreed before production", revenue_share: str = "To be agreed before production") -> str:
    if (isinstance(amount, bool) or not isinstance(amount, (int, float))
            or not math.isfinite(amount) or amount <= 0):
        raise ValueError("Compensation must be greater than zero.")

    if not row("SELECT id FROM contributors WHERE id = ?", (contributor_id,)):
        raise ValueError("Contributor does not exist.")

    if not row("SELECT id FROM projects WHERE id = ?", (project_id,)):
        raise ValueError("Project does not exist.")

    role = validate_text(role, "Role")
    currency = validate_text(currency, "Currency")
    attribution = validate_text(attribution, "Attribution")
    license_terms = validate_text(license_terms, "License terms")
    revenue_share = validate_text(revenue_share, "Revenue share")

    contract_id = str(uuid.uuid4())
    with _transaction() as con:
        con.execute(
            """INSERT INTO contracts
               (id, contributor_id, project_id, role, amount, currency,
                payment_status, attribution, license_terms, revenue_share, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'agreed_not_paid', ?, ?, ?, ?)""",
            (contract_id, contributor_id, project_id, role, float(amount), currency,
             attribution, license_terms, revenue_share, utc_now()),
        )
        _audit(con, "administrator", "create_contract", "contract", contract_id, {
            "contributor_id": contributor_id,
            "project_id": project_id,
            "amount": float(amount),
            "currency": currency,
            "attribution": attribution,
            "license_terms": license_terms,
            "revenue_share": revenue_share,
        })
    return contract_id


def mark_paid(contract_id: str, payment_reference: str) -> bool:
    """Marks a contract paid. Returns False (no change, no new audit entry)
    if it was already paid."""
    contract = row("SELECT id, payment_status FROM contracts WHERE id = ?", (contract_id,))
    if not contract:
        raise ValueError("Contract does not exist.")
    payment_reference = validate_text(payment_reference, "Payment reference")
    if contract["payment_status"] == "paid":
        return False

    with _transaction() as con:
        con.execute(
            "UPDATE contracts SET payment_status = 'paid' WHERE id = ?",
            (contract_id,),
        )
        _audit(con, "finance", "mark_paid", "contract", contract_id, {
            "payment_reference": payment_reference
        })
    return True


def create_project(adapter: WorldHoloBridgeAdapter, theme: str, media_format: str, human_lead: str, contributor_ids: List[str], accessibility: Iterable[str], indigenous_material_ids: Optional[List[str]] = None) -> str:
    """Validates every gate first, then writes the project, its contributors,
    its materials and the audit entry in a single transaction."""
    if not adapter.guardrails_active:
        raise PermissionError("Guardrails must remain active.")

    theme = validate_text(theme, "Theme")
    media_format = validate_text(media_format, "Media format")
    human_lead = validate_text(human_lead, "Human lead")

    if not contributor_ids:
        raise ValueError("At least one contributor is required.")
    contributor_ids = list(dict.fromkeys(contributor_ids))
    material_ids = list(dict.fromkeys(indigenous_material_ids or []))

    accessibility = set(accessibility)
    missing = REQUIRED_ACCESSIBILITY - accessibility
    if missing:
        raise ValueError(f"Missing required accessibility features: {sorted(missing)}")

    unconsented = [
        cid for cid in contributor_ids
        if not consent_allows(cid, "community_storytelling")
    ]
    if unconsented:
        raise PermissionError(
            "All contributors need active consent for community storytelling."
        )

    for material_id in material_ids:
        material = row(
            "SELECT * FROM indigenous_materials WHERE id = ?", (material_id,)
        )
        if not material:
            raise ValueError("Indigenous material does not exist.")
        if not material["public_display"]:
            raise PermissionError(
                "Material cannot be publicly displayed without permission."
            )

    project_id = str(uuid.uuid4())
    with _transaction() as con:
        con.execute(
            """INSERT INTO projects
               (id, theme, media_format, human_lead, status, ai_role,
                accessibility, created_at)
               VALUES (?, ?, ?, ?, 'draft', ?, ?, ?)""",
            (
                project_id, theme, media_format, human_lead,
                "Assistive only; human-led cultural interpretation",
                json.dumps(sorted(accessibility)), utc_now(),
            ),
        )
        for cid in contributor_ids:
            con.execute(
                "INSERT INTO project_contributors VALUES (?, ?)",
                (project_id, cid),
            )
        for material_id in material_ids:
            con.execute(
                "INSERT INTO project_materials VALUES (?, ?)",
                (project_id, material_id),
            )
        _audit(con, "project_lead", "create_project", "project", project_id, {
            "theme": theme,
            "media_format": media_format,
            "human_lead": human_lead,
            "contributors": contributor_ids,
            "indigenous_materials": material_ids,
            "accessibility": sorted(accessibility),
        })
    return project_id


def publish_project(project_id: str, approved_by: str) -> bool:
    """Publishes a project. Blocks while any contract is unpaid or while any
    project contributor lacks active community-storytelling consent (e.g. it
    was withdrawn or expired after the project was created). Returns False if
    the project is already published."""
    project = row("SELECT id, status FROM projects WHERE id = ?", (project_id,))
    if not project:
        raise ValueError("Project does not exist.")
    approved_by = validate_text(approved_by, "Approver")
    if project["status"] == "published":
        return False

    unpaid = rows(
        """SELECT id FROM contracts
           WHERE project_id = ? AND payment_status != 'paid'""",
        (project_id,),
    )
    if unpaid:
        raise PermissionError(
            "Project cannot be published while contributor payments are outstanding."
        )

    contributor_ids = [r["contributor_id"] for r in rows(
        "SELECT contributor_id FROM project_contributors WHERE project_id = ?",
        (project_id,),
    )]
    if any(not consent_allows(cid, "community_storytelling") for cid in contributor_ids):
        raise PermissionError(
            "Project cannot be published: a contributor no longer has active "
            "consent for community storytelling."
        )

    with _transaction() as con:
        con.execute(
            "UPDATE projects SET status = 'published' WHERE id = ?",
            (project_id,),
        )
        _audit(con, approved_by, "publish_project", "project", project_id,
               {"status": "published"})
    return True


def assess_ai_use(adapter: WorldHoloBridgeAdapter, task: str, domain: str, proposed_use: str, decision_owner: str, sensitive_data: bool = False, indigenous_material: bool = False) -> Dict[str, Any]:
    assessment = {
        "task": validate_text(task, "Task"),
        "domain": validate_text(domain, "Domain"),
        "proposed_ai_use": validate_text(proposed_use, "Proposed AI use"),
        "human_decision_owner": validate_text(decision_owner, "Decision owner"),
        "ai_role": "Assistive only",
        "human_accountability": "Required for factual, cultural, ethical, and public-facing decisions",
        "blockers": [],
        "created_at": utc_now(),
    }

    if sensitive_data:
        assessment["blockers"].append(
            "Sensitive data requires consent, minimization, retention limits, and a lawful basis."
        )

    if indigenous_material:
        assessment["blockers"].append(
            "Indigenous material requires governance-authority approval and cannot be used for external AI training."
        )

    assessment["status"] = (
        "blocked_pending_governance" if assessment["blockers"]
        else "approved_for_low_stakes_testing"
    )

    audit("ai_adapter_studio", "assess_ai_use", "adapter", adapter.id, assessment)
    return assessment


def report_incident(project_id: Optional[str], incident_type: str, description: str, severity: str) -> str:
    if severity not in SEVERITIES:
        raise ValueError("Severity must be low, medium, high, or critical.")
    if project_id is not None and not row("SELECT id FROM projects WHERE id = ?", (project_id,)):
        raise ValueError("Project does not exist.")
    incident_type = validate_text(incident_type, "Incident type")
    description = validate_text(description, "Description")

    incident_id = str(uuid.uuid4())
    with _transaction() as con:
        con.execute(
            """INSERT INTO incidents
               (id, project_id, type, description, severity, status, reported_at)
               VALUES (?, ?, ?, ?, ?, 'open', ?)""",
            (incident_id, project_id, incident_type, description, severity, utc_now()),
        )
        _audit(con, "participant_or_staff", "report_incident", "incident", incident_id, {
            "project_id": project_id,
            "type": incident_type,
            "severity": severity,
        })
    return incident_id


def resolve_incident(incident_id: str, corrective_action: str) -> bool:
    """Resolves an incident. Returns False (no change) if already resolved."""
    incident = row("SELECT id, status FROM incidents WHERE id = ?", (incident_id,))
    if not incident:
        raise ValueError("Incident does not exist.")
    corrective_action = validate_text(corrective_action, "Corrective action")
    if incident["status"] == "resolved":
        return False

    with _transaction() as con:
        con.execute(
            """UPDATE incidents
               SET status = 'resolved', corrective_action = ?, resolved_at = ?
               WHERE id = ?""",
            (corrective_action, utc_now(), incident_id),
        )
        _audit(con, "administrator", "resolve_incident", "incident", incident_id, {
            "corrective_action": corrective_action
        })
    return True


def generate_impact_report(adapter: WorldHoloBridgeAdapter, export_dir: Union[str, Path, None] = None) -> Dict[str, Any]:
    projects = rows("SELECT * FROM projects")
    contributors = rows("SELECT * FROM contributors")
    contracts = rows("SELECT * FROM contracts")
    consents = rows("SELECT * FROM consents")
    incidents = rows("SELECT * FROM incidents")
    today = _today().isoformat()

    paid = [c for c in contracts if c["payment_status"] == "paid"]
    outstanding = [c for c in contracts if c["payment_status"] != "paid"]

    payments: Dict[str, float] = {}
    for contract in paid:
        curr = contract["currency"]
        payments[curr] = payments.get(curr, 0.0) + contract["amount"]

    report = {
        "report_type": "World-HoloBridge Community Impact Report",
        "location": f"{adapter.city}, {adapter.country}",
        "cultural_context": adapter.cultural_context,
        "lead_organization": adapter.lead_organization,
        "generated_at": utc_now(),
        "governance": {
            "advisory_circle_size": len(adapter.advisory_circle),
            "contributors": len(contributors),
            "active_consents": len([c for c in consents
                                    if not c["withdrawn"] and c["expires_on"] >= today]),
            "expired_consents": len([c for c in consents
                                     if not c["withdrawn"] and c["expires_on"] < today]),
            "withdrawn_consents": len([c for c in consents if c["withdrawn"]]),
            "guardrails_active": adapter.guardrails_active,
        },
        "projects": {
            "total": len(projects),
            "published": len([p for p in projects if p["status"] == "published"]),
            "draft": len([p for p in projects if p["status"] == "draft"]),
        },
        "economic_accountability": {
            "contracts": len(contracts),
            "paid_contracts": len(paid),
            "outstanding_contracts": len(outstanding),
            "payments_by_currency": payments,
            "attribution_required": True,
        },
        "accessibility": {
            "required_features": sorted(REQUIRED_ACCESSIBILITY),
            "coverage": {
                feature: len([
                    p for p in projects
                    if feature in json.loads(p["accessibility"])
                ])
                for feature in sorted(REQUIRED_ACCESSIBILITY)
            },
        },
        "rights_and_safety": {
            "incidents": len(incidents),
            "open_incidents": len([i for i in incidents if i["status"] == "open"]),
            "resolved_incidents": len([i for i in incidents if i["status"] == "resolved"]),
        },
        "limitations": [
            "This report records pilot activity and does not claim causal economic impact.",
            "Quantitative measures should be read alongside community feedback.",
            "Indigenous materials remain governed by the relevant authority.",
        ],
    }

    out_dir = Path(export_dir) if export_dir is not None else EXPORT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"holobridge_impact_report_{_today().isoformat()}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    audit("system", "generate_impact_report", "adapter", adapter.id,
          {"report_file": str(path)})
    return report


# ---------------------------------------------------------------------
# Community plan generator
# ---------------------------------------------------------------------
#
# The plan text lives in plan_template.json, which the browser page
# (site/plan.js) reads too, so both produce identical plans. The template
# never names an Indigenous nation, community or organization for a city and
# contains no local statistics; it tells users to identify and confirm
# rights-holders locally and directly with the communities.

PLAN_TEMPLATE_NAME = "plan_template.json"
_PLAN_TEMPLATE: Optional[Dict[str, Any]] = None
_PLACEHOLDER = re.compile(r"\{(city|country|location)\}")
_TRIM = re.compile(r"^[ \t\n\r\u00a0\u3000\ufeff]+|[ \t\n\r\u00a0\u3000\ufeff]+$")
_CONTROL = re.compile(r"[\u0000-\u001f\u007f]")
_MD_SPECIAL = re.compile(r"([\\`*_\[\]<>|])")


def _template_candidates() -> List[Path]:
    env = os.environ.get("WORLD_HOLOBRIDGE_TEMPLATE")
    paths = [Path(env)] if env else []
    paths.append(Path(__file__).resolve().with_name(PLAN_TEMPLATE_NAME))
    paths.append(Path(sys.prefix) / "share" / "world-holobridge" / PLAN_TEMPLATE_NAME)
    return paths


def load_plan_template() -> Dict[str, Any]:
    """Loads (and caches) the shared plan template."""
    global _PLAN_TEMPLATE
    if _PLAN_TEMPLATE is None:
        for candidate in _template_candidates():
            if candidate.is_file():
                _PLAN_TEMPLATE = json.loads(candidate.read_text(encoding="utf-8"))
                break
        else:
            raise FileNotFoundError(f"{PLAN_TEMPLATE_NAME} not found next to the module or in sys.prefix/share.")
    return _PLAN_TEMPLATE


def clean_plan_field(value: Any, label: str, required: bool = True, max_length: Optional[int] = None) -> Optional[str]:
    """Same rules as cleanField in site/plan.js: trim, reject empty (when
    required), over-long or control-character input."""
    if max_length is None:
        max_length = load_plan_template()["max_field_length"]
    if value is None:
        if required:
            raise ValueError(f"{label} is required.")
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text.")
    value = _TRIM.sub("", value)
    if not value:
        if required:
            raise ValueError(f"{label} is required.")
        return None
    if len(value) > max_length:
        raise ValueError(f"{label} must be at most {max_length} characters.")
    if _CONTROL.search(value):
        raise ValueError(f"{label} contains characters that are not allowed.")
    return value


def _fill(node: Any, values: Dict[str, str]) -> Any:
    if isinstance(node, str):
        return _PLACEHOLDER.sub(lambda m: values[m.group(1)], node)
    if isinstance(node, list):
        return [_fill(n, values) for n in node]
    if isinstance(node, dict):
        return {k: _fill(v, values) for k, v in node.items()}
    return node


def generate_community_plan(city: str, country: str, region: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
    """Builds a structured community plan for any city from the framework's
    rules. Deterministic: the same input gives the same plan (no timestamp),
    in Python and in the browser."""
    template = load_plan_template()
    if language not in template["languages"]:
        raise ValueError(f"Language must be one of {template['languages']}.")
    city = clean_plan_field(city, "City")
    country = clean_plan_field(country, "Country")
    region = clean_plan_field(region, "Region", required=False)
    display = ", ".join(p for p in (city, region, country) if p)
    content = _fill(template["content"][language], {"city": city, "country": country, "location": display})
    plan: Dict[str, Any] = {
        "schema": template["schema"],
        "language": language,
        "location": {"city": city, "region": region, "country": country, "display": display},
    }
    plan.update(content)
    return plan


def _md(text: str) -> str:
    return _MD_SPECIAL.sub(r"\\\1", text)


def plan_to_markdown(plan: Dict[str, Any]) -> str:
    """Markdown export; identical to planToMarkdown in site/plan.js."""
    lines = [f"# {_md(plan['title'])}", "", f"**{plan['md']['location']}:** {_md(plan['location']['display'])}", ""]
    for notice in plan["notices"]:
        lines.append(f"> {_md(notice)}")
        lines.append(">")
    if plan["notices"]:
        lines.pop()
        lines.append("")
    for section in plan["sections"]:
        lines += [f"## {_md(section['title'])}", ""]
        if section["intro"]:
            lines += [_md(section["intro"]), ""]
        for item in section["items"]:
            if item["label"]:
                lines.append(f"- **{_md(item['label'])}:** {_md(item['text'])}")
            else:
                lines.append(f"- {_md(item['text'])}")
        if section["items"]:
            lines.append("")
        if section["note"]:
            lines += [_md(section["note"]), ""]
        if section["gate"]:
            lines += [f"*{plan['md']['gate']}: {_md(section['gate'])}*", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def plan_to_json(plan: Dict[str, Any]) -> str:
    """JSON export; identical to planToJson in site/plan.js."""
    return json.dumps(plan, indent=2, ensure_ascii=False) + "\n"


def _plan_section(plan: Dict[str, Any], section_id: str) -> Dict[str, Any]:
    for section in plan["sections"]:
        if section["id"] == section_id:
            return section
    raise KeyError(section_id)


def run_plan_pipeline(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Runs the governance pipeline on the active database using the plan's
    advisory roles, protocols and accessibility features, with placeholder
    contributors, to show how each section maps to a gate. Indigenous
    material is deliberately not exercised: it needs a governance authority
    designated by the communities themselves."""
    checks: List[Dict[str, str]] = []
    loc = plan["location"]
    adapter = WorldHoloBridgeAdapter(
        country=loc["country"], city=loc["city"],
        cultural_context="To be identified and confirmed with local communities",
        lead_organization="To be confirmed",
        advisory_circle=[i["text"] for i in _plan_section(plan, "advisory_circle")["items"]],
    )
    checks.append({"gate": "advisory_circle", "result": "accepted"})
    adapter.set_protocols({i["label"]: i["text"] for i in _plan_section(plan, "protocols")["items"]})
    checks.append({"gate": "protocols", "result": "all five accepted"})

    expires_on = (_today() + timedelta(days=365)).isoformat()
    people = []
    for name in ("Placeholder contributor A", "Placeholder contributor B"):
        cid = add_contributor(name, "Placeholder role")
        register_consent(cid, ["community_storytelling", "project_evaluation"], ["external_ai_training"], expires_on)
        people.append(cid)
    checks.append({"gate": "consent", "result": "active community_storytelling consent recorded"})

    features = {i["label"] for i in _plan_section(plan, "accessibility")["items"]}
    project_id = create_project(adapter, "Placeholder theme", "Placeholder format", "Placeholder human lead", people, features)
    checks.append({"gate": "accessibility", "result": "project created with all required features"})

    contracts = [create_contract(cid, project_id, "Placeholder role", 1.0) for cid in people]
    try:
        publish_project(project_id, "Advisory circle")
        checks.append({"gate": "payment", "result": "UNEXPECTED: published while unpaid"})
    except PermissionError:
        checks.append({"gate": "payment", "result": "publication blocked while unpaid"})
    for n, contract in enumerate(contracts, 1):
        mark_paid(contract, f"PLACEHOLDER-{n}")
    publish_project(project_id, "Advisory circle")
    checks.append({"gate": "payment", "result": "published after all contracts paid"})

    assessment = assess_ai_use(adapter, "Placeholder task", "Placeholder domain", "Placeholder AI use",
                               "Placeholder decision owner", sensitive_data=True)
    checks.append({"gate": "ai_use", "result": assessment["status"]})
    incident = report_incident(project_id, "Placeholder incident", "Pipeline check", "low")
    resolve_incident(incident, "Placeholder corrective action")
    checks.append({"gate": "incidents", "result": "reported and resolved"})
    checks.append({"gate": "indigenous_rights_holders",
                   "result": "not exercised: requires a governance authority designated by the communities"})
    report = generate_impact_report(adapter)
    checks.append({"gate": "evaluation", "result": "impact report generated"})
    return {"checks": checks, "report": report}


def _slug(text: str) -> str:
    slug = re.sub(r"[^\w]+", "-", text.lower(), flags=re.UNICODE).strip("-")
    return slug or "plan"


def _plan_main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="world-holobridge plan",
                                     description="Generate a community plan for a city.")
    parser.add_argument("--city", required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--region")
    parser.add_argument("--language", default="en", choices=load_plan_template()["languages"])
    parser.add_argument("--format", default="md", choices=["md", "json"], help="Printed format (default: md)")
    parser.add_argument("--out-dir", help="Also write <slug>.md and <slug>.json here")
    parser.add_argument("--run-pipeline", action="store_true",
                        help="Run the governance pipeline from the plan (in-memory database by default)")
    parser.add_argument("--db", default=":memory:", help="Database for --run-pipeline (default: %(default)s)")
    parser.add_argument("--output-dir", default=str(EXPORT_DIR), help="Impact-report directory for --run-pipeline")
    args = parser.parse_args(argv)
    try:
        plan = generate_community_plan(args.city, args.country, args.region, args.language)
    except ValueError as exc:
        parser.error(str(exc))
    print(plan_to_markdown(plan) if args.format == "md" else plan_to_json(plan), end="")
    if args.out_dir:
        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        stem = f"community_plan_{_slug(plan['location']['display'])}_{plan['language']}"
        (out / f"{stem}.md").write_text(plan_to_markdown(plan), encoding="utf-8")
        (out / f"{stem}.json").write_text(plan_to_json(plan), encoding="utf-8")
    if args.run_pipeline:
        configure(db_path=args.db, export_dir=args.output_dir)
        try:
            result = run_plan_pipeline(plan)
        finally:
            close_connection()
        print(json.dumps(result["checks"], indent=2, ensure_ascii=False), file=sys.stderr)
    return 0


# ---------------------------------------------------------------------
# Reproducible Test & Deployment Verification
# ---------------------------------------------------------------------

def run_demo() -> Dict[str, Any]:
    """End-to-end demo pipeline on the active database. All names are
    placeholders; no real person, organization or community is represented."""
    # Consent expiry is one year from today so the demo does not go stale.
    expires_on = (_today() + timedelta(days=365)).isoformat()

    # 1. Initialize Adapter
    adapter = WorldHoloBridgeAdapter(
        country="Canada",
        city="Fredericton",
        cultural_context="Wolastoqey Territory and diverse municipal community",
        lead_organization="To be confirmed",
        advisory_circle=[
            "Wolastoqey representative or knowledge holder",
            "Local artist or cultural worker",
            "Neighbourhood or newcomer representative",
            "Disability and accessibility advocate",
            "Small business or non-profit representative",
            "Youth representative",
            "Older adult representative",
        ],
    )

    adapter.set_protocols({
        "data_scraping": "Prohibited by default; no local heritage material may be scraped or used for AI training.",
        "indigenous_leadership": "Wolastoqey representatives hold governance authority over Wolastoqey cultural material.",
        "economic_fairness": "Contributors receive paid contracts before project publication.",
        "consent_withdrawal": "Participants may withdraw consent at any time.",
        "accessibility": "Every public project includes full multi-modal accessibility.",
    })

    # 2. Add Contributors & Record Consent
    artist_id = add_contributor("Local Artist A", "Spatial-media artist", "Fredericton creative community")
    accessibility_id = add_contributor("Accessibility Advocate A", "Accessibility reviewer", "Community disability org")
    wolastoqey_authority_id = add_contributor("Wolastoqey Governance Representative", "Governance authority", "Wolastoqey community", indigenous_authority=True)

    register_consent(
        artist_id,
        permitted_uses=["community_storytelling", "public_display", "project_evaluation"],
        prohibited_uses=["external_ai_training", "commercial_resale_without_agreement"],
        expires_on=expires_on,
    )

    # Demo fix: the original script omitted "community_storytelling" here, so
    # its own create_project gate (correctly) raised PermissionError.
    register_consent(
        accessibility_id,
        permitted_uses=["community_storytelling", "accessibility_review", "project_evaluation"],
        prohibited_uses=["external_ai_training"],
        expires_on=expires_on,
    )

    # 3. Register Indigenous Material
    river_material = register_indigenous_material(
        adapter=adapter,
        title="Wolastoqey river-related cultural reference",
        authority_id=wolastoqey_authority_id,
        permissions=["community_storytelling", "public_display"],
        retention_policy="Retain only for agreed pilot period.",
        public_display=True,
    )

    # 4. Create Project & Contracts
    project_id = create_project(
        adapter=adapter,
        theme="Neighbourhood change, river ecology, and future livelihoods",
        media_format="Layered spatial audio and projection, with non-headset access",
        human_lead="Wolastoqey and local artist collaborators",
        contributor_ids=[artist_id, accessibility_id],
        accessibility={
            "captions",
            "transcript",
            "plain_language_summary",
            "non_headset_alternative",
            "audio_description",
            "mobility_accessible_venue",
        },
        indigenous_material_ids=[river_material],
    )

    artist_contract = create_contract(
        contributor_id=artist_id,
        project_id=project_id,
        role="Lead spatial-media artist",
        amount=4500.00,
        attribution="Named artist credit in all public presentations",
        license_terms="Non-exclusive community exhibition license.",
        revenue_share="50 percent of net revenue.",
    )

    accessibility_contract = create_contract(
        contributor_id=accessibility_id,
        project_id=project_id,
        role="Accessibility reviewer",
        amount=1200.00,
        attribution="Accessibility review credit",
        license_terms="Pilot review license.",
        revenue_share="Fixed fee.",
    )

    # 5. Pay & Publish
    mark_paid(artist_contract, "INV-001-PAID")
    mark_paid(accessibility_contract, "INV-002-PAID")
    publish_project(project_id, approved_by="Community advisory circle")

    # 6. Export Impact Report
    return generate_impact_report(adapter)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """``world-holobridge [demo] [--db ...]`` runs the demo pipeline;
    ``world-holobridge plan --city ... --country ...`` generates a plan."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "plan":
        return _plan_main(argv[1:])
    if argv and argv[0] == "demo":
        argv = argv[1:]
    parser = argparse.ArgumentParser(prog="world-holobridge [demo]",
                                     description="Run the World-HoloBridge demo pipeline (placeholder Fredericton/Wolastoqey example).")
    parser.add_argument("--db", default=str(DB_PATH),
                        help="SQLite database path, or ':memory:' (default: %(default)s)")
    parser.add_argument("--output-dir", default=str(EXPORT_DIR),
                        help="Directory for the exported impact report (default: %(default)s)")
    args = parser.parse_args(argv)

    configure(db_path=args.db, export_dir=args.output_dir)
    try:
        print("Executing World-HoloBridge Governance Pipeline Test Run...")
        report = run_demo()
        print("Pipeline run completed successfully.")
        print(f"Exported Impact Report: {json.dumps(report, indent=2, ensure_ascii=False)}")
    finally:
        close_connection()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
