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

License: Apache-2.0 / MIT
Version: 1.0.0
"""

from datetime import date, datetime
import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Set
import uuid

# ---------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------

DB_PATH = Path("world_holobridge.db")
EXPORT_DIR = Path("output")
EXPORT_DIR.mkdir(exist_ok=True)

REQUIRED_ACCESSIBILITY: Set[str] = {
    "captions",
    "transcript",
    "plain_language_summary",
    "non_headset_alternative",
}


# ---------------------------------------------------------------------
# Database & Core Utilities
# ---------------------------------------------------------------------

def utc_now() -> str:
    """Returns ISO-8601 UTC timestamp string."""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def init_db(path: Path = DB_PATH) -> sqlite3.Connection:
    """Initializes the relational SQLite database with governance schema."""
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        details TEXT NOT NULL
    );

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
        resolved_at TEXT
    );
    """)
    con.commit()
    return con


# Initialize database connection
con = init_db()


def audit(actor: str, action: str, entity_type: str, entity_id: str, details: Dict[str, Any]) -> str:
    """Appends an immutable entry to the system audit trail."""
    record_id = str(uuid.uuid4())
    with con:
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


def rows(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    return [dict(r) for r in con.execute(query, params).fetchall()]


def row(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    results = rows(query, params)
    return results[0] if results else None


def validate_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    return value.strip()


def validate_future_date(value: str) -> str:
    try:
        if date.fromisoformat(value) < date.today():
            raise ValueError
    except ValueError as exc:
        raise ValueError("Use a future ISO date in YYYY-MM-DD format.") from exc
    return value


# ---------------------------------------------------------------------
# Governance Adapter Class
# ---------------------------------------------------------------------

class WorldHoloBridgeAdapter:
    """Central adapter instance governing regional policy and advisory parameters."""

    def __init__(self, country: str, city: str, cultural_context: str, lead_organization: str, advisory_circle: List[str]):
        self.id = str(uuid.uuid4())
        self.country = validate_text(country, "Country")
        self.city = validate_text(city, "City")
        self.cultural_context = validate_text(cultural_context, "Cultural context")
        self.lead_organization = validate_text(lead_organization, "Lead organization")

        if not advisory_circle:
            raise ValueError("A paid advisory circle is required.")

        self.advisory_circle = [validate_text(a, "Advisory-circle member") for a in advisory_circle]
        self.guardrails_active = True
        self.protocols: Dict[str, str] = {}

        audit("system", "initialize_adapter", "adapter", self.id, {
            "country": self.country,
            "city": self.city,
            "cultural_context": self.cultural_context,
            "lead_organization": self.lead_organization,
            "advisory_circle": self.advisory_circle,
        })

    def set_protocols(self, protocols: Dict[str, str]):
        required = {
            "data_scraping",
            "indigenous_leadership",
            "economic_fairness",
            "consent_withdrawal",
            "accessibility",
        }
        missing = required - set(protocols)
        if missing:
            raise ValueError(f"Missing required protocols: {sorted(missing)}")

        self.protocols = protocols
        audit("governance", "set_protocols", "adapter", self.id, protocols)

    def disable_guardrails(self):
        raise PermissionError("Guardrails cannot be disabled.")


# ---------------------------------------------------------------------
# Operational Functions
# ---------------------------------------------------------------------

def add_contributor(name: str, role: str, organization: Optional[str] = None, indigenous_authority: bool = False) -> str:
    contributor_id = str(uuid.uuid4())
    with con:
        con.execute(
            """INSERT INTO contributors
               (id, name, role, organization, indigenous_authority, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                contributor_id, validate_text(name, "Name"), validate_text(role, "Role"),
                organization, int(indigenous_authority), utc_now(),
            ),
        )

    audit("administrator", "add_contributor", "contributor", contributor_id, {
        "name": name,
        "role": role,
        "indigenous_authority": indigenous_authority,
    })
    return contributor_id


def register_consent(contributor_id: str, permitted_uses: List[str], prohibited_uses: List[str], expires_on: str) -> str:
    if not row("SELECT id FROM contributors WHERE id = ?", (contributor_id,)):
        raise ValueError("Contributor does not exist.")

    if not permitted_uses:
        raise ValueError("At least one permitted use is required.")

    consent_id = str(uuid.uuid4())
    with con:
        con.execute(
            """INSERT INTO consents
               (id, contributor_id, permitted_uses, prohibited_uses,
                expires_on, withdrawn, recorded_at)
               VALUES (?, ?, ?, ?, ?, 0, ?)""",
            (
                consent_id, contributor_id, json.dumps(permitted_uses),
                json.dumps(prohibited_uses), validate_future_date(expires_on), utc_now(),
            ),
        )

    audit("administrator", "register_consent", "consent", consent_id, {
        "contributor_id": contributor_id,
        "permitted_uses": permitted_uses,
        "prohibited_uses": prohibited_uses,
        "expires_on": expires_on,
    })
    return consent_id


def withdraw_consent(consent_id: str) -> bool:
    if not row("SELECT id FROM consents WHERE id = ?", (consent_id,)):
        raise ValueError("Consent record does not exist.")

    with con:
        con.execute(
            "UPDATE consents SET withdrawn = 1, withdrawn_at = ? WHERE id = ?",
            (utc_now(), consent_id),
        )

    audit("contributor_or_administrator", "withdraw_consent", "consent",
          consent_id, {"withdrawn": True})
    return True


def consent_allows(contributor_id: str, use: str) -> bool:
    records = rows(
        """SELECT * FROM consents
           WHERE contributor_id = ? AND withdrawn = 0 AND expires_on >= ?""",
        (contributor_id, date.today().isoformat()),
    )
    for record in records:
        permitted = json.loads(record["permitted_uses"])
        prohibited = json.loads(record["prohibited_uses"])
        if use in prohibited:
            return False
        if use in permitted:
            return True
    return False


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

    material_id = str(uuid.uuid4())
    with con:
        con.execute(
            """INSERT INTO indigenous_materials
               (id, title, authority_id, permissions, external_ai_training,
                public_display, retention_policy, created_at)
               VALUES (?, ?, ?, ?, 0, ?, ?, ?)""",
            (
                material_id, validate_text(title, "Title"), authority_id,
                json.dumps(permissions), int(public_display),
                validate_text(retention_policy, "Retention policy"), utc_now(),
            ),
        )

    audit(authority["name"], "register_indigenous_material",
          "indigenous_material", material_id, {
              "title": title,
              "permissions": permissions,
              "public_display": public_display,
              "external_ai_training": False,
              "retention_policy": retention_policy,
          })
    return material_id


def create_contract(contributor_id: str, project_id: str, role: str, amount: float, currency: str = "CAD", attribution: str = "Named contributor", license_terms: str = "To be agreed before production", revenue_share: str = "To be agreed before production") -> str:
    if amount <= 0:
        raise ValueError("Compensation must be greater than zero.")

    if not row("SELECT id FROM contributors WHERE id = ?", (contributor_id,)):
        raise ValueError("Contributor does not exist.")

    if not row("SELECT id FROM projects WHERE id = ?", (project_id,)):
        raise ValueError("Project does not exist.")

    contract_id = str(uuid.uuid4())
    with con:
        con.execute(
            """INSERT INTO contracts
               (id, contributor_id, project_id, role, amount, currency,
                payment_status, attribution, license_terms, revenue_share, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'agreed_not_paid', ?, ?, ?, ?)""",
            (
                contract_id, contributor_id, project_id, validate_text(role, "Role"),
                float(amount), currency, attribution, license_terms,
                revenue_share, utc_now(),
            ),
        )

    audit("administrator", "create_contract", "contract", contract_id, {
        "contributor_id": contributor_id,
        "project_id": project_id,
        "amount": amount,
        "currency": currency,
        "attribution": attribution,
        "license_terms": license_terms,
        "revenue_share": revenue_share,
    })
    return contract_id


def mark_paid(contract_id: str, payment_reference: str) -> bool:
    if not row("SELECT id FROM contracts WHERE id = ?", (contract_id,)):
        raise ValueError("Contract does not exist.")

    with con:
        con.execute(
            "UPDATE contracts SET payment_status = 'paid' WHERE id = ?",
            (contract_id,),
        )

    audit("finance", "mark_paid", "contract", contract_id, {
        "payment_reference": payment_reference
    })
    return True


def create_project(adapter: WorldHoloBridgeAdapter, theme: str, media_format: str, human_lead: str, contributor_ids: List[str], accessibility: Set[str], indigenous_material_ids: Optional[List[str]] = None) -> str:
    if not adapter.guardrails_active:
        raise PermissionError("Guardrails must remain active.")

    theme = validate_text(theme, "Theme")
    media_format = validate_text(media_format, "Media format")
    human_lead = validate_text(human_lead, "Human lead")

    if not contributor_ids:
        raise ValueError("At least one contributor is required.")

    missing = REQUIRED_ACCESSIBILITY - set(accessibility)
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

    project_id = str(uuid.uuid4())
    with con:
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

    for material_id in indigenous_material_ids or []:
        material = row(
            "SELECT * FROM indigenous_materials WHERE id = ?", (material_id,)
        )
        if not material:
            raise ValueError("Indigenous material does not exist.")
        if not material["public_display"]:
            raise PermissionError(
                "Material cannot be publicly displayed without permission."
            )
        with con:
            con.execute(
                "INSERT INTO project_materials VALUES (?, ?)",
                (project_id, material_id),
            )

    audit("project_lead", "create_project", "project", project_id, {
        "theme": theme,
        "media_format": media_format,
        "human_lead": human_lead,
        "contributors": contributor_ids,
        "indigenous_materials": indigenous_material_ids or [],
        "accessibility": sorted(accessibility),
    })
    return project_id


def publish_project(project_id: str, approved_by: str) -> bool:
    if not row("SELECT id FROM projects WHERE id = ?", (project_id,)):
        raise ValueError("Project does not exist.")

    unpaid = rows(
        """SELECT id FROM contracts
           WHERE project_id = ? AND payment_status != 'paid'""",
        (project_id,),
    )
    if unpaid:
        raise PermissionError(
            "Project cannot be published while contributor payments are outstanding."
        )

    with con:
        con.execute(
            "UPDATE projects SET status = 'published' WHERE id = ?",
            (project_id,),
        )

    audit(approved_by, "publish_project", "project", project_id,
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
    if severity not in {"low", "medium", "high", "critical"}:
        raise ValueError("Severity must be low, medium, high, or critical.")

    incident_id = str(uuid.uuid4())
    with con:
        con.execute(
            """INSERT INTO incidents
               (id, project_id, type, description, severity, status, reported_at)
               VALUES (?, ?, ?, ?, ?, 'open', ?)""",
            (
                incident_id, project_id, validate_text(incident_type, "Incident type"),
                validate_text(description, "Description"), severity, utc_now(),
            ),
        )

    audit("participant_or_staff", "report_incident", "incident", incident_id, {
        "project_id": project_id,
        "type": incident_type,
        "severity": severity,
    })
    return incident_id


def resolve_incident(incident_id: str, corrective_action: str) -> bool:
    if not row("SELECT id FROM incidents WHERE id = ?", (incident_id,)):
        raise ValueError("Incident does not exist.")

    with con:
        con.execute(
            """UPDATE incidents
               SET status = 'resolved', corrective_action = ?, resolved_at = ?
               WHERE id = ?""",
            (validate_text(corrective_action, "Corrective action"), utc_now(), incident_id),
        )

    audit("administrator", "resolve_incident", "incident", incident_id, {
        "corrective_action": corrective_action
    })
    return True


def generate_impact_report(adapter: WorldHoloBridgeAdapter) -> Dict[str, Any]:
    projects = rows("SELECT * FROM projects")
    contributors = rows("SELECT * FROM contributors")
    contracts = rows("SELECT * FROM contracts")
    consents = rows("SELECT * FROM consents")
    incidents = rows("SELECT * FROM incidents")

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
            "active_consents": len([c for c in consents if not c["withdrawn"]]),
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
                for feature in REQUIRED_ACCESSIBILITY
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

    path = EXPORT_DIR / f"holobridge_impact_report_{date.today()}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    audit("system", "generate_impact_report", "adapter", adapter.id,
          {"report_file": str(path)})
    return report


# ---------------------------------------------------------------------
# Reproducible Test & Deployment Verification
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("Executing World-HoloBridge Governance Pipeline Test Run...")

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

    artist_consent = register_consent(
        artist_id,
        permitted_uses=["community_storytelling", "public_display", "project_evaluation"],
        prohibited_uses=["external_ai_training", "commercial_resale_without_agreement"],
        expires_on="2027-10-16",
    )

    accessibility_consent = register_consent(
        accessibility_id,
        permitted_uses=["accessibility_review", "project_evaluation"],
        prohibited_uses=["external_ai_training"],
        expires_on="2027-10-16",
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
    report = generate_impact_report(adapter)
    print("Pipeline run completed successfully.")
    print(f"Exported Impact Report: {json.dumps(report, indent=2, ensure_ascii=False)}")
