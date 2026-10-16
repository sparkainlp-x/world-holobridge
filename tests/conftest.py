# SPDX-License-Identifier: MIT OR Apache-2.0
from datetime import date, timedelta
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import world_holobridge as wh  # noqa: E402

FUTURE = (date.today() + timedelta(days=365)).isoformat()
ACCESS = {"captions", "transcript", "plain_language_summary", "non_headset_alternative"}
PROTOCOLS = {
    "data_scraping": "Prohibited by default.",
    "indigenous_leadership": "Placeholder authority governs its material.",
    "economic_fairness": "Paid before publication.",
    "consent_withdrawal": "Withdraw any time.",
    "accessibility": "Full multi-modal access.",
}


@pytest.fixture(autouse=True)
def db(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    con = wh.configure(db_path=":memory:", export_dir=tmp_path / "output")
    yield con
    wh.close_connection()


@pytest.fixture
def adapter():
    a = wh.WorldHoloBridgeAdapter(
        country="Canada", city="Placeholder City", cultural_context="Placeholder context",
        lead_organization="Placeholder org", advisory_circle=["Member A", "Member B"],
    )
    a.set_protocols(PROTOCOLS)
    return a


@pytest.fixture
def consenting():
    def make(name="Contributor A", uses=("community_storytelling",), prohibited=(), **kw):
        cid = wh.add_contributor(name, "Role", **kw)
        consent = wh.register_consent(cid, list(uses), list(prohibited), FUTURE)
        return cid, consent
    return make


@pytest.fixture
def authority():
    return wh.add_contributor("Authority A", "Governance authority", indigenous_authority=True)
