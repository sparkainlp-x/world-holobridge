# SPDX-License-Identifier: MIT OR Apache-2.0
import json
import math
import sqlite3
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

import world_holobridge as wh
from conftest import ACCESS, FUTURE

ROOT = Path(__file__).resolve().parents[1]


def count(table):
    return wh.row(f"SELECT COUNT(*) AS n FROM {table}")["n"]


def actions():
    return [r["action"] for r in wh.rows("SELECT action FROM audit_log ORDER BY rowid")]


# --- import / configuration --------------------------------------------------

def test_import_has_no_side_effects(tmp_path):
    code = ("import os, sys; sys.path.insert(0, sys.argv[1]); import world_holobridge; "
            "print(sorted(os.listdir('.')))")
    out = subprocess.run([sys.executable, "-c", code, str(ROOT)], cwd=tmp_path,
                         capture_output=True, text=True, check=True).stdout
    assert out.strip() == "[]"


def test_foreign_keys_enabled(db):
    assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        with db:
            db.execute("INSERT INTO consents VALUES ('x','missing','[]','[]',?,0,NULL,'t')", (FUTURE,))


def test_legacy_con_attribute_is_active_connection(db):
    assert wh.con is db


def test_utc_now_is_timezone_aware_z():
    ts = wh.utc_now()
    assert ts.endswith("Z") and "+" not in ts and len(ts) == 20


def test_demo_runs_end_to_end(tmp_path):
    out = subprocess.run([sys.executable, "-W", "error", str(ROOT / "world_holobridge.py"),
                          "--db", ":memory:", "--output-dir", str(tmp_path / "o")],
                         cwd=tmp_path, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "Pipeline run completed successfully." in out.stdout
    report = json.loads(next((tmp_path / "o").glob("*.json")).read_text(encoding="utf-8"))
    assert report["projects"] == {"total": 1, "published": 1, "draft": 0}
    assert report["economic_accountability"]["payments_by_currency"] == {"CAD": 5700.0}


def test_original_demo_consent_is_blocked_by_gate(adapter):
    """The original demo gave the accessibility advocate no community_storytelling
    consent; the gate correctly refuses to create the project."""
    artist = wh.add_contributor("Local Artist A", "Artist")
    wh.register_consent(artist, ["community_storytelling", "public_display"], ["external_ai_training"], FUTURE)
    advocate = wh.add_contributor("Accessibility Advocate A", "Accessibility reviewer")
    wh.register_consent(advocate, ["accessibility_review", "project_evaluation"], ["external_ai_training"], FUTURE)
    with pytest.raises(PermissionError, match="community storytelling"):
        wh.create_project(adapter, "Theme", "Format", "Lead", [artist, advocate], ACCESS)
    assert count("projects") == 0


# --- adapter / guardrails ----------------------------------------------------

def test_guardrails_cannot_be_disabled(adapter):
    with pytest.raises(PermissionError):
        adapter.disable_guardrails()
    with pytest.raises(PermissionError):
        adapter.guardrails_active = False
    assert adapter.guardrails_active is True


def test_adapter_requires_advisory_circle():
    with pytest.raises(ValueError, match="advisory circle"):
        wh.WorldHoloBridgeAdapter("Canada", "City", "Ctx", "Org", [])


def test_missing_protocols_rejected(adapter):
    with pytest.raises(ValueError, match="Missing required protocols"):
        adapter.set_protocols({"data_scraping": "No."})


# --- consent ------------------------------------------------------------------

def test_consent_requires_known_contributor_and_future_date(consenting):
    with pytest.raises(ValueError):
        wh.register_consent("nobody", ["community_storytelling"], [], FUTURE)
    cid = wh.add_contributor("A", "Role")
    with pytest.raises(ValueError, match="future ISO date"):
        wh.register_consent(cid, ["community_storytelling"], [], "2000-01-01")
    with pytest.raises(ValueError, match="future ISO date"):
        wh.register_consent(cid, ["community_storytelling"], [], "not-a-date")
    with pytest.raises(ValueError, match="At least one permitted use"):
        wh.register_consent(cid, [], [], FUTURE)
    with pytest.raises(ValueError, match="both permitted and prohibited"):
        wh.register_consent(cid, ["x"], ["x"], FUTURE)


def test_withdrawn_consent_blocks(consenting, adapter):
    cid, consent = consenting()
    assert wh.consent_allows(cid, "community_storytelling")
    assert wh.withdraw_consent(consent) is True
    assert wh.withdraw_consent(consent) is False  # idempotent
    assert not wh.consent_allows(cid, "community_storytelling")
    with pytest.raises(PermissionError):
        wh.create_project(adapter, "T", "F", "L", [cid], ACCESS)


def test_expired_consent_blocks(consenting, adapter, monkeypatch):
    cid, _ = consenting()
    monkeypatch.setattr(wh, "_today", lambda: date.today() + timedelta(days=400))
    assert not wh.consent_allows(cid, "community_storytelling")
    with pytest.raises(PermissionError):
        wh.create_project(adapter, "T", "F", "L", [cid], ACCESS)


def test_prohibition_wins_across_records(consenting):
    cid, _ = consenting(uses=("community_storytelling",))
    wh.register_consent(cid, ["public_display"], ["community_storytelling"], FUTURE)
    assert not wh.consent_allows(cid, "community_storytelling")
    # and regardless of record order
    other, _ = consenting(name="B", uses=("public_display",), prohibited=("community_storytelling",))
    wh.register_consent(other, ["community_storytelling"], [], FUTURE)
    assert not wh.consent_allows(other, "community_storytelling")


def test_permission_from_any_active_record(consenting):
    cid, _ = consenting(uses=("public_display",))
    wh.register_consent(cid, ["community_storytelling"], [], FUTURE)
    assert wh.consent_allows(cid, "community_storytelling")
    assert not wh.consent_allows(cid, "external_ai_training")


# --- Indigenous material -----------------------------------------------------

def test_indigenous_material_requires_authority(adapter):
    non_authority = wh.add_contributor("Not an authority", "Artist")
    with pytest.raises(PermissionError, match="Indigenous governance authority"):
        wh.register_indigenous_material(adapter, "Title", non_authority, ["community_storytelling"], "Pilot only")
    with pytest.raises(PermissionError):
        wh.register_indigenous_material(adapter, "Title", "missing", [], "Pilot only")
    assert count("indigenous_materials") == 0


def test_material_never_allows_external_ai_training(adapter, authority):
    mid = wh.register_indigenous_material(adapter, "Title", authority, ["community_storytelling"], "Pilot", public_display=True)
    assert wh.row("SELECT external_ai_training FROM indigenous_materials WHERE id=?", (mid,))["external_ai_training"] == 0


def test_non_public_material_blocks_project_atomically(adapter, authority, consenting):
    cid, _ = consenting()
    private = wh.register_indigenous_material(adapter, "Private", authority, ["community_storytelling"], "Pilot", public_display=False)
    before = len(actions())
    with pytest.raises(PermissionError, match="publicly displayed"):
        wh.create_project(adapter, "T", "F", "L", [cid], ACCESS, [private])
    # validation happens before any insert: no partial project or links
    assert count("projects") == 0
    assert count("project_contributors") == 0
    assert count("project_materials") == 0
    assert len(actions()) == before


def test_unknown_material_blocks_project(adapter, consenting):
    cid, _ = consenting()
    with pytest.raises(ValueError, match="does not exist"):
        wh.create_project(adapter, "T", "F", "L", [cid], ACCESS, ["missing"])
    assert count("projects") == 0


def test_public_material_links_to_project(adapter, authority, consenting):
    cid, _ = consenting()
    mid = wh.register_indigenous_material(adapter, "Public", authority, ["community_storytelling"], "Pilot", public_display=True)
    pid = wh.create_project(adapter, "T", "F", "L", [cid, cid], ACCESS, [mid, mid])
    assert count("project_contributors") == 1  # duplicates collapsed
    assert wh.rows("SELECT material_id FROM project_materials WHERE project_id=?", (pid,)) == [{"material_id": mid}]


# --- accessibility -------------------------------------------------------------

@pytest.mark.parametrize("missing", sorted(ACCESS))
def test_accessibility_features_required(adapter, consenting, missing):
    cid, _ = consenting()
    with pytest.raises(ValueError, match="accessibility"):
        wh.create_project(adapter, "T", "F", "L", [cid], ACCESS - {missing})
    assert count("projects") == 0


def test_project_requires_contributors(adapter):
    with pytest.raises(ValueError, match="At least one contributor"):
        wh.create_project(adapter, "T", "F", "L", [], ACCESS)


# --- contracts / payment / publishing ---------------------------------------

@pytest.fixture
def project(adapter, consenting):
    cid, consent = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [cid], ACCESS)
    return pid, cid, consent


@pytest.mark.parametrize("amount", [0, -5, math.nan, math.inf, True, "100"])
def test_contract_amount_must_be_positive_finite(project, amount):
    pid, cid, _ = project
    with pytest.raises(ValueError, match="greater than zero"):
        wh.create_contract(cid, pid, "Role", amount)


def test_contract_requires_known_contributor_and_project(project):
    pid, cid, _ = project
    with pytest.raises(ValueError):
        wh.create_contract("missing", pid, "Role", 10)
    with pytest.raises(ValueError):
        wh.create_contract(cid, "missing", "Role", 10)


def test_unpaid_contract_blocks_publish(project):
    pid, cid, _ = project
    contract = wh.create_contract(cid, pid, "Role", 100.0)
    with pytest.raises(PermissionError, match="payments are outstanding"):
        wh.publish_project(pid, "Circle")
    assert wh.mark_paid(contract, "INV-1") is True
    assert wh.publish_project(pid, "Circle") is True
    assert wh.row("SELECT status FROM projects WHERE id=?", (pid,))["status"] == "published"
    assert wh.publish_project(pid, "Circle") is False  # already published


def test_mark_paid_is_idempotent(project):
    pid, cid, _ = project
    contract = wh.create_contract(cid, pid, "Role", 100.0)
    assert wh.mark_paid(contract, "INV-1") is True
    assert wh.mark_paid(contract, "INV-1") is False
    assert actions().count("mark_paid") == 1
    with pytest.raises(ValueError):
        wh.mark_paid("missing", "INV-1")
    with pytest.raises(ValueError):
        wh.mark_paid(contract, "  ")


def test_withdrawal_after_creation_blocks_publish(project):
    pid, cid, consent = project
    wh.withdraw_consent(consent)
    with pytest.raises(PermissionError, match="no longer has active"):
        wh.publish_project(pid, "Circle")


def test_publish_unknown_project():
    with pytest.raises(ValueError):
        wh.publish_project("missing", "Circle")


# --- AI-use assessment ---------------------------------------------------------

def test_assess_ai_use(adapter):
    ok = wh.assess_ai_use(adapter, "Draft captions", "Accessibility", "Caption draft", "Editor")
    assert ok["status"] == "approved_for_low_stakes_testing" and ok["blockers"] == []
    blocked = wh.assess_ai_use(adapter, "T", "D", "U", "Owner", sensitive_data=True, indigenous_material=True)
    assert blocked["status"] == "blocked_pending_governance" and len(blocked["blockers"]) == 2


# --- incidents --------------------------------------------------------------

def test_incident_lifecycle(project):
    pid, _, _ = project
    iid = wh.report_incident(pid, "Consent concern", "Description", "high")
    assert wh.row("SELECT status FROM incidents WHERE id=?", (iid,))["status"] == "open"
    assert wh.resolve_incident(iid, "Removed material") is True
    rec = wh.row("SELECT * FROM incidents WHERE id=?", (iid,))
    assert rec["status"] == "resolved" and rec["corrective_action"] == "Removed material" and rec["resolved_at"]
    assert wh.resolve_incident(iid, "Again") is False
    general = wh.report_incident(None, "General", "No project", "low")
    assert wh.row("SELECT project_id FROM incidents WHERE id=?", (general,))["project_id"] is None


def test_incident_validation():
    with pytest.raises(ValueError, match="Severity"):
        wh.report_incident(None, "T", "D", "urgent")
    with pytest.raises(ValueError, match="Project does not exist"):
        wh.report_incident("missing", "T", "D", "low")
    with pytest.raises(ValueError):
        wh.resolve_incident("missing", "Fix")


# --- impact report ------------------------------------------------------------

def test_impact_report(project, adapter, tmp_path, consenting, monkeypatch):
    pid, cid, consent = project
    contract = wh.create_contract(cid, pid, "Role", 250.0, currency="CAD")
    wh.mark_paid(contract, "INV-1")
    wh.create_contract(cid, pid, "Role 2", 50.0, currency="EUR")
    wh.report_incident(pid, "T", "D", "low")
    other, other_consent = consenting(name="B")
    wh.withdraw_consent(other_consent)

    report = wh.generate_impact_report(adapter)
    g = report["governance"]
    assert (g["contributors"], g["active_consents"], g["withdrawn_consents"], g["expired_consents"]) == (2, 1, 1, 0)
    assert g["guardrails_active"] is True
    assert report["projects"] == {"total": 1, "published": 0, "draft": 1}
    e = report["economic_accountability"]
    assert (e["contracts"], e["paid_contracts"], e["outstanding_contracts"]) == (2, 1, 1)
    assert e["payments_by_currency"] == {"CAD": 250.0}
    assert report["accessibility"]["coverage"] == {f: 1 for f in sorted(ACCESS)}
    assert report["rights_and_safety"] == {"incidents": 1, "open_incidents": 1, "resolved_incidents": 0}
    files = list((tmp_path / "output").glob("holobridge_impact_report_*.json"))
    assert len(files) == 1 and json.loads(files[0].read_text(encoding="utf-8")) == report

    monkeypatch.setattr(wh, "_today", lambda: date.today() + timedelta(days=400))
    later = wh.generate_impact_report(adapter, export_dir=tmp_path / "later")
    assert (later["governance"]["active_consents"], later["governance"]["expired_consents"]) == (0, 1)


# --- audit log --------------------------------------------------------------

def test_audit_log_records_actions(project):
    acts = actions()
    for expected in ["initialize_adapter", "set_protocols", "add_contributor", "register_consent", "create_project"]:
        assert expected in acts
    entry = wh.row("SELECT * FROM audit_log WHERE action='create_project'")
    assert entry["timestamp"].endswith("Z")
    assert json.loads(entry["details"])["accessibility"] == sorted(ACCESS)


def test_audit_log_is_append_only(db, project):
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        with db:
            db.execute("UPDATE audit_log SET actor = 'tampered'")
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        with db:
            db.execute("DELETE FROM audit_log")
    assert count("audit_log") > 0
    assert wh.row("SELECT COUNT(*) AS n FROM audit_log WHERE actor='tampered'")["n"] == 0


def test_failed_gate_writes_no_audit_entry(adapter):
    cid = wh.add_contributor("No consent", "Role")
    before = len(actions())
    with pytest.raises(PermissionError):
        wh.create_project(adapter, "T", "F", "L", [cid], ACCESS)
    assert len(actions()) == before


def test_file_database_persists(tmp_path):
    path = tmp_path / "x.db"
    wh.configure(db_path=path)
    cid = wh.add_contributor("Persisted", "Role")
    wh.close_connection()
    wh.configure(db_path=path)
    assert wh.row("SELECT name FROM contributors WHERE id=?", (cid,))["name"] == "Persisted"


def test_original_script_demo_stops_at_consent_gate(tmp_path):
    """Documents the finding: the unchanged original script's own demo raises
    PermissionError at create_project (accessibility advocate lacks
    community_storytelling consent)."""
    out = subprocess.run([sys.executable, str(ROOT / "world_holobridge_original.py")],
                         cwd=tmp_path, capture_output=True, text=True)
    assert out.returncode != 0
    if date.today() > date(2027, 10, 16):  # original hard-codes this consent expiry
        pytest.skip("original demo's fixed expiry date has passed")
    assert "PermissionError: All contributors need active consent for community storytelling." in out.stderr
