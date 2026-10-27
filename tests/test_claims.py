# SPDX-License-Identifier: MIT OR Apache-2.0
"""Tests that back claims in the README and docs (see docs/evidence-register.md),
including a check that the register only cites tests that exist."""
import ast
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

import world_holobridge as wh
from conftest import ACCESS

ROOT = Path(__file__).resolve().parents[1]
MODULE_SOURCE = (ROOT / "world_holobridge.py").read_text(encoding="utf-8")


def test_consent_expiring_after_creation_blocks_publish(adapter, consenting, monkeypatch):
    cid, _ = consenting()
    pid = wh.create_project(adapter, "T", "F", "L", [cid], ACCESS)
    monkeypatch.setattr(wh, "_today", lambda: date.today() + timedelta(days=400))
    with pytest.raises(PermissionError, match="no longer has active"):
        wh.publish_project(pid, "Circle")


def test_only_indigenous_material_is_modelled(db):
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {t for t in tables if "material" in t} == {"indigenous_materials", "project_materials"}


def test_ai_assessment_status_is_not_consumed_elsewhere():
    """The status string appears once, where it is produced; nothing branches on it."""
    assert MODULE_SOURCE.count("blocked_pending_governance") == 1
    assert "approved_for_low_stakes_testing" in MODULE_SOURCE
    assert 'assessment["status"]' in MODULE_SOURCE


def test_no_heat_alert_or_hardware_functionality_in_the_module():
    lowered = MODULE_SOURCE.lower()
    for word in ("heat", "alert", "hologram", "temperature", "firmware", "serial"):
        assert word not in lowered, word


def test_module_imports_only_the_standard_library():
    tree = ast.parse(MODULE_SOURCE)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names.add(node.module.split(".")[0])
    assert names and names <= set(sys.stdlib_module_names)
    assert 'dependencies = []' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")


def test_register_cites_only_existing_tests():
    register = (ROOT / "docs" / "evidence-register.md").read_text(encoding="utf-8")
    defined = set()
    for path in (ROOT / "tests").glob("test_*.py"):
        defined |= set(re.findall(r"^def (test_\w+)", path.read_text(encoding="utf-8"), re.M))
    cited = set(re.findall(r"`(test_\w+)`", register))
    assert cited, "register cites no Python tests"
    assert cited <= defined, sorted(cited - defined)
    js = (ROOT / "tests" / "js" / "plan.test.js").read_text(encoding="utf-8")
    for title in re.findall(r"`js:([^`]+)`", register):
        assert f"test('{title}'" in js, title


def test_register_ids_are_unique_and_tags_are_from_the_legend():
    register = (ROOT / "docs" / "evidence-register.md").read_text(encoding="utf-8")
    legend = {"measured by tests", "reported", "vendor claim", "design rationale", "unverified"}
    ids, tags = [], []
    for line in register.splitlines():
        m = re.match(r"\| ((?:C|D)\d+) \|", line)
        if m:
            ids.append(m.group(1))
            tags.append(line.split("|")[3].strip().split(" (")[0])
    assert ids and len(ids) == len(set(ids))
    assert set(tags) <= legend, set(tags) - legend
