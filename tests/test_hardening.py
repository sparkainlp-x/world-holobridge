# SPDX-License-Identifier: MIT OR Apache-2.0
"""Tests for the publication-gate hardening (Unreleased): payment, incidents,
accessibility evidence, public-display withdrawal, AI-training flag."""
import json
import sqlite3

import pytest

import world_holobridge as wh
from conftest import ACCESS, FUTURE


def codes(report, status=None):
    return [c["code"] for c in report["checks"] if status is None or c["status"] == status]


def last_publish_audit():
    entry = wh.row("SELECT details FROM audit_log WHERE action='publish_project' ORDER BY rowid DESC LIMIT 1")
    return json.loads(entry["details"])


@pytest.fixture
def evidence_files(tmp_path):
    d = tmp_path / "ev"
    d.mkdir()
    (d / "captions.vtt").write_text("WEBVTT\n\n00:00.000 --> 00:02.000\nHello\n", encoding="utf-8")
    (d / "transcript.txt").write_text("Hello there.\n", encoding="utf-8")
    (d / "summary.md").write_text("A short plain-language summary.\n", encoding="utf-8")
    (d / "alt.txt").write_text("Print version at the desk.\n", encoding="utf-8")
    return d


def good_evidence():
    return {
        "captions": "file:captions.vtt",
        "transcript": "file:transcript.txt",
        "plain_language_summary": "file:summary.md",
        "non_headset_alternative": "file:alt.txt",
    }


# --- 1. payment gate ---------------------------------------------------------

def test_no_contracts_is_reported_not_silent(adapter, consenting):
    cid, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [cid], ACCESS)
    report = wh.publication_report(pid)
    assert report["can_publish"] is True
    assert "no_contracts_recorded" in codes(report, "warn")
    # non-breaking: it still publishes, and the warning is written to the audit entry
    assert wh.publish_project(pid, "Circle") is True
    warned = [w["code"] for w in last_publish_audit()["warnings"]]
    assert "no_contracts_recorded" in warned


def test_strict_blocks_project_without_contracts(adapter, consenting):
    cid, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [cid], ACCESS)
    with pytest.raises(wh.PublicationBlocked) as exc:
        wh.publish_project(pid, "Circle", strict=True)
    assert "no_contracts_recorded" in [b["code"] for b in exc.value.blockers]
    assert isinstance(exc.value, PermissionError)
    assert wh.row("SELECT status FROM projects WHERE id=?", (pid,))["status"] == "draft"


def test_declared_paid_contributor_without_contract_blocks_by_default(adapter, consenting):
    a, _ = consenting("A")
    b, _ = consenting("B")
    pid = wh.create_project(adapter, "T", "F", "L", [a, b], ACCESS, paid_contributor_ids=[a, b])
    contract = wh.create_contract(a, pid, "Role", 10.0)
    wh.mark_paid(contract, "INV-1")
    with pytest.raises(PermissionError, match="declared as paid"):
        wh.publish_project(pid, "Circle")
    wh.mark_paid(wh.create_contract(b, pid, "Role", 10.0), "INV-2")
    assert wh.publish_project(pid, "Circle") is True
    assert "declared_paid_contributor_without_contract" not in codes(wh.publication_report(pid))


def test_declared_paid_with_zero_contracts_blocks(adapter, consenting):
    a, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, paid_contributor_ids=[a])
    with pytest.raises(PermissionError, match="declared as paid"):
        wh.publish_project(pid, "Circle")


def test_paid_contributors_must_be_project_contributors(adapter, consenting):
    a, _ = consenting("A")
    other, _ = consenting("B")
    with pytest.raises(ValueError, match="Paid contributors"):
        wh.create_project(adapter, "T", "F", "L", [a], ACCESS, paid_contributor_ids=[other])
    assert wh.row("SELECT COUNT(*) AS n FROM projects")["n"] == 0


def test_contributor_without_contract_is_warning_then_strict_blocker(adapter, consenting):
    a, _ = consenting("A")
    b, _ = consenting("B")
    pid = wh.create_project(adapter, "T", "F", "L", [a, b], ACCESS)
    wh.mark_paid(wh.create_contract(a, pid, "Role", 10.0), "INV-1")
    assert "contributors_without_contract" in codes(wh.publication_report(pid), "warn")
    assert "contributors_without_contract" in codes(wh.publication_report(pid, strict=True), "fail")


def test_fully_contracted_project_publishes_strict(adapter, consenting):
    a, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, paid_contributor_ids=[a],
                            accessibility_evidence=None)
    wh.mark_paid(wh.create_contract(a, pid, "Role", 10.0), "INV-1")
    # strict also wants accessibility evidence, so it is still blocked for that reason only
    with pytest.raises(wh.PublicationBlocked) as exc:
        wh.publish_project(pid, "Circle", strict=True)
    assert {b["code"] for b in exc.value.blockers} == {"accessibility_evidence_missing"}


# --- 2. incidents --------------------------------------------------------------

@pytest.fixture
def paid_project(adapter, consenting):
    a, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, paid_contributor_ids=[a])
    wh.mark_paid(wh.create_contract(a, pid, "Role", 10.0), "INV-1")
    return pid


@pytest.mark.parametrize("severity", sorted(wh.BLOCKING_INCIDENT_SEVERITIES))
def test_open_serious_incident_blocks_until_resolved(paid_project, severity):
    iid = wh.report_incident(paid_project, "Consent concern", "Description", severity)
    with pytest.raises(wh.PublicationBlocked, match="open incident"):
        wh.publish_project(paid_project, "Circle")
    assert wh.row("SELECT status FROM projects WHERE id=?", (paid_project,))["status"] == "draft"
    wh.resolve_incident(iid, "Fixed")
    assert wh.publish_project(paid_project, "Circle") is True


@pytest.mark.parametrize("severity", ["low", "medium"])
def test_open_minor_incident_warns_and_strict_blocks(paid_project, severity):
    wh.report_incident(paid_project, "Minor", "Description", severity)
    report = wh.publication_report(paid_project)
    assert report["can_publish"] and "open_minor_incidents" in codes(report, "warn")
    assert "open_minor_incidents" in codes(wh.publication_report(paid_project, strict=True), "fail")
    assert wh.publish_project(paid_project, "Circle") is True
    assert "open_minor_incidents" in [w["code"] for w in last_publish_audit()["warnings"]]


def test_incident_on_another_project_does_not_block(adapter, consenting, paid_project):
    b, _ = consenting("B")
    other = wh.create_project(adapter, "T2", "F", "L", [b], ACCESS, paid_contributor_ids=[b])
    wh.mark_paid(wh.create_contract(b, other, "Role", 10.0), "INV-2")
    wh.report_incident(other, "Serious", "Elsewhere", "critical")
    assert wh.publish_project(paid_project, "Circle") is True


def test_unlinked_serious_incident_warns_and_strict_blocks(paid_project):
    wh.report_incident(None, "General", "No project named", "critical")
    report = wh.publication_report(paid_project)
    assert report["can_publish"] and "open_unlinked_serious_incidents" in codes(report, "warn")
    assert "open_unlinked_serious_incidents" in codes(wh.publication_report(paid_project, strict=True), "fail")


def test_resolved_incident_does_not_block(paid_project):
    iid = wh.report_incident(paid_project, "Concern", "Description", "critical")
    wh.resolve_incident(iid, "Fixed")
    assert "no_open_incidents" in codes(wh.publication_report(paid_project), "pass")


# --- 3. accessibility evidence -------------------------------------------------

def test_valid_evidence_is_recorded_and_publishes(adapter, consenting, evidence_files):
    a, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, paid_contributor_ids=[a],
                            accessibility_evidence=good_evidence(), evidence_base_dir=evidence_files)
    wh.mark_paid(wh.create_contract(a, pid, "Role", 10.0), "INV-1")
    rows = wh.rows("SELECT * FROM accessibility_evidence WHERE project_id=?", (pid,))
    assert {r["feature"] for r in rows} == ACCESS
    assert all(r["verification"] == "file_non_empty" and len(r["sha256"]) == 64 for r in rows)
    assert wh.publication_report(pid, strict=True)["can_publish"] is True
    assert wh.publish_project(pid, "Circle", strict=True) is True


@pytest.mark.parametrize("reference,message", [
    ("", "non-empty"),
    ("   ", "non-empty"),
    (None, "non-empty"),
    ("captions.vtt", "must start with"),
    ("file:", "needs a path"),
    ("file:missing.vtt", "does not exist"),
    ("text:", "needs a description"),
    ("text:   ", "needs a description"),
    ("ftp://example.org/x", "must start with"),
    ("https://", "not a valid"),
    ("https://exa mple.org", "not a valid"),
])
def test_bad_references_rejected_at_creation(adapter, consenting, evidence_files, reference, message):
    a, _ = consenting()
    ev = good_evidence()
    ev["captions"] = reference
    with pytest.raises(ValueError, match=message):
        wh.create_project(adapter, "T", "F", "L", [a], ACCESS, accessibility_evidence=ev,
                          evidence_base_dir=evidence_files)
    assert wh.row("SELECT COUNT(*) AS n FROM projects")["n"] == 0
    assert wh.row("SELECT COUNT(*) AS n FROM accessibility_evidence")["n"] == 0


@pytest.mark.parametrize("name,content,message", [
    ("empty.txt", "", "is empty"),
    ("blank.txt", "  \n\t\n", "only whitespace"),
    ("nocues.vtt", "WEBVTT\n\n", "no cues"),
    ("nocues.srt", "1\n", "no cues"),
])
def test_empty_or_cueless_files_rejected(tmp_path, name, content, message):
    (tmp_path / name).write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        wh.verify_accessibility_reference(f"file:{name}", tmp_path)


def test_binary_file_checked_for_size_only_and_directory_rejected(tmp_path):
    (tmp_path / "audio.mp3").write_bytes(b"\x00\x01\x02")
    result = wh.verify_accessibility_reference("file:audio.mp3", tmp_path)
    assert result["verification"] == "file_non_empty" and result["sha256"]
    (tmp_path / "dir").mkdir()
    with pytest.raises(ValueError, match="not a regular file"):
        wh.verify_accessibility_reference("file:dir", tmp_path)


def test_invalid_utf8_text_rejected(tmp_path):
    (tmp_path / "bad.txt").write_bytes(b"\xff\xfe\xfa")
    with pytest.raises(ValueError, match="UTF-8"):
        wh.verify_accessibility_reference("file:bad.txt", tmp_path)


def test_url_and_text_levels_are_honest(tmp_path):
    url = wh.verify_accessibility_reference("https://example.org/captions.vtt")
    assert url["verification"] == "url_syntax_only" and url["sha256"] is None
    text = wh.verify_accessibility_reference("text: Staffed desk with a printed copy ")
    assert text["verification"] == "text_declared_only" and text["reference"] == "text:Staffed desk with a printed copy"


def test_evidence_for_undeclared_feature_rejected(adapter, consenting):
    a, _ = consenting()
    with pytest.raises(ValueError, match="undeclared"):
        wh.create_project(adapter, "T", "F", "L", [a], ACCESS,
                          accessibility_evidence={"audio_description": "text:Audio describer on site"})
    with pytest.raises(ValueError, match="must map"):
        wh.create_project(adapter, "T", "F", "L", [a], ACCESS, accessibility_evidence=["captions"])


def test_evidence_rechecked_at_publish(adapter, consenting, evidence_files):
    a, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, paid_contributor_ids=[a],
                            accessibility_evidence=good_evidence(), evidence_base_dir=evidence_files)
    wh.mark_paid(wh.create_contract(a, pid, "Role", 10.0), "INV-1")
    (evidence_files / "captions.vtt").write_text("", encoding="utf-8")  # emptied after creation
    with pytest.raises(wh.PublicationBlocked, match="captions"):
        wh.publish_project(pid, "Circle")
    (evidence_files / "captions.vtt").unlink()  # deleted
    assert "accessibility_evidence_failed" in codes(wh.publication_report(pid), "fail")


def test_changed_file_is_a_warning(adapter, consenting, evidence_files):
    a, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, paid_contributor_ids=[a],
                            accessibility_evidence=good_evidence(), evidence_base_dir=evidence_files)
    wh.mark_paid(wh.create_contract(a, pid, "Role", 10.0), "INV-1")
    (evidence_files / "transcript.txt").write_text("Edited transcript.\n", encoding="utf-8")
    report = wh.publication_report(pid)
    assert report["can_publish"] and "accessibility_evidence_changed" in codes(report, "warn")


def test_without_evidence_warns_by_default(paid_project):
    report = wh.publication_report(paid_project)
    assert report["can_publish"]
    assert codes(report, "warn").count("accessibility_evidence_missing") == len(ACCESS)


def test_publish_rechecks_declaration(paid_project, db):
    db.execute("UPDATE projects SET accessibility = ? WHERE id = ?",
               (json.dumps(["captions"]), paid_project))
    db.commit()
    with pytest.raises(wh.PublicationBlocked, match="not declared"):
        wh.publish_project(paid_project, "Circle")


# --- 4. public display -----------------------------------------------------------

def test_withdrawn_public_display_blocks_publish(adapter, authority, consenting):
    a, _ = consenting()
    mid = wh.register_indigenous_material(adapter, "Public", authority, ["community_storytelling"], "Pilot", public_display=True)
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, [mid], paid_contributor_ids=[a])
    wh.mark_paid(wh.create_contract(a, pid, "Role", 10.0), "INV-1")
    assert wh.withdraw_public_display(mid) is True
    assert wh.withdraw_public_display(mid) is False  # idempotent, no second audit entry
    assert [r["action"] for r in wh.rows("SELECT action FROM audit_log")].count("withdraw_public_display") == 1
    with pytest.raises(wh.PublicationBlocked, match="public-display permission"):
        wh.publish_project(pid, "Circle")


def test_withdraw_public_display_unknown_material():
    with pytest.raises(ValueError, match="does not exist"):
        wh.withdraw_public_display("missing")


def test_public_display_check_passes_with_permission(adapter, authority, consenting):
    a, _ = consenting()
    mid = wh.register_indigenous_material(adapter, "Public", authority, ["community_storytelling"], "Pilot", public_display=True)
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, [mid])
    assert "public_display_ok" in codes(wh.publication_report(pid), "pass")


# --- 5. AI-training flag ---------------------------------------------------------------

def test_ai_training_flag_cannot_be_set(adapter, authority, db):
    mid = wh.register_indigenous_material(adapter, "T", authority, ["community_storytelling"], "Pilot")
    with pytest.raises(sqlite3.IntegrityError, match="never permitted"):
        with db:
            db.execute("UPDATE indigenous_materials SET external_ai_training = 1 WHERE id = ?", (mid,))
    with pytest.raises(sqlite3.IntegrityError, match="never permitted"):
        with db:
            db.execute("INSERT INTO indigenous_materials VALUES ('x', 't', ?, '[]', 1, 0, 'r', 'now')", (authority,))
    assert wh.ai_training_allowed(mid) is False


def test_ai_training_allowed_unknown_material():
    with pytest.raises(ValueError, match="does not exist"):
        wh.ai_training_allowed("missing")


def test_assess_ai_use_with_material_ids(adapter, authority):
    mid = wh.register_indigenous_material(adapter, "T", authority, ["community_storytelling"], "Pilot")
    result = wh.assess_ai_use(adapter, "Summarise", "Heat", "Summaries", "Editor", material_ids=[mid, mid])
    assert result["status"] == "blocked_pending_governance"
    assert result["material_ids"] == [mid]
    with pytest.raises(ValueError):
        wh.assess_ai_use(adapter, "T", "D", "U", "Owner", material_ids=["missing"])
    plain = wh.assess_ai_use(adapter, "T", "D", "U", "Owner")
    assert "material_ids" not in plain


def test_assess_ai_use_blocks_if_a_legacy_row_allows_training(adapter, authority, db):
    """Simulates a database written before the triggers existed."""
    mid = wh.register_indigenous_material(adapter, "T", authority, ["community_storytelling"], "Pilot")
    db.execute("DROP TRIGGER indigenous_materials_no_ai_training_update")
    db.execute("UPDATE indigenous_materials SET external_ai_training = 1 WHERE id = ?", (mid,))
    db.commit()
    assert wh.ai_training_allowed(mid) is True
    result = wh.assess_ai_use(adapter, "T", "D", "U", "Owner", material_ids=[mid])
    assert any("marked as available" in b for b in result["blockers"])


# --- general ------------------------------------------------------------------------------

def test_report_is_read_only(paid_project):
    before = wh.row("SELECT COUNT(*) AS n FROM audit_log")["n"]
    wh.publication_report(paid_project)
    wh.publication_report(paid_project, strict=True)
    assert wh.row("SELECT COUNT(*) AS n FROM audit_log")["n"] == before
    assert wh.row("SELECT status FROM projects WHERE id=?", (paid_project,))["status"] == "draft"


def test_publication_report_unknown_project():
    with pytest.raises(ValueError, match="does not exist"):
        wh.publication_report("missing")


def test_multiple_blockers_are_all_reported(adapter, consenting):
    a, consent = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [a], ACCESS, paid_contributor_ids=[a])
    wh.create_contract(a, pid, "Role", 10.0)  # unpaid
    wh.report_incident(pid, "Concern", "Description", "high")
    wh.withdraw_consent(consent)
    with pytest.raises(wh.PublicationBlocked) as exc:
        wh.publish_project(pid, "Circle")
    assert {b["gate"] for b in exc.value.blockers} == {"payment", "consent", "incidents"}
    assert "payments are outstanding" in str(exc.value) and "no longer has active" in str(exc.value)


def test_existing_database_gains_new_tables_and_triggers(tmp_path):
    """A database created with the 0.2.0 schema opens cleanly with the new one."""
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    schema = wh.SCHEMA
    start = schema.index("-- Contributors a project declares as paid.")
    end = schema.index("CREATE TABLE IF NOT EXISTS contracts")
    old = schema[:start] + schema[end:]
    trig = old.index("-- External AI training is never permitted")
    trig_end = old.index("CREATE TABLE IF NOT EXISTS incidents")
    old = old[:trig] + old[trig_end:]
    con.executescript(old)
    con.close()
    con = wh.configure(db_path=path)
    names = {r[0] for r in con.execute("SELECT name FROM sqlite_master")}
    assert {"project_paid_contributors", "accessibility_evidence",
            "indigenous_materials_no_ai_training_insert"} <= names


def test_plan_template_describes_the_incident_gate_in_both_languages():
    for language in ("en", "fr"):
        plan = wh.generate_community_plan("Anytown", "Anyland", language=language)
        gate = wh._plan_section(plan, "incidents")["gate"]
        assert "publish_project" in gate and "critical" in gate


def test_plan_pipeline_declares_paid_contributors():
    plan = wh.generate_community_plan("Anytown", "Anyland")
    wh.run_plan_pipeline(plan)
    assert wh.row("SELECT COUNT(*) AS n FROM project_paid_contributors")["n"] == 2
