# SPDX-License-Identifier: MIT OR Apache-2.0
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import world_holobridge as wh

ROOT = Path(__file__).resolve().parents[1]
CITIES = [
    ("Fredericton", "Canada", "New Brunswick"), ("Moncton", "Canada", None), ("Toronto", "Canada", "Ontario"),
    ("Auckland", "New Zealand", None), ("Tromsø", "Norway", None), ("Phoenix", "United States", "Arizona"),
    ("Sydney", "Australia", "New South Wales"), ("São Paulo", "Brazil", None), ("Nairobi", "Kenya", None),
    ("Montréal", "Canada", "Québec"),
]
# Names the generator must never produce on its own (non-exhaustive).
NATION_NAMES = [
    "Wolastoq", "Maliseet", "Mi'kmaq", "Mi’kmaq", "Mikmaq", "Peskotomuhkati", "Passamaquoddy", "Wabanaki",
    "Cree", "Ojibwe", "Anishinaabe", "Haudenosaunee", "Mohawk", "Kanien", "Mississauga", "Huron-Wendat",
    "Innu", "Inuit", "Métis", "Dene", "Navajo", "Diné", "Hopi", "Apache", "Lakota", "Cherokee",
    "Māori", "Maori", "Sámi", "Sami", "Gadigal", "Eora", "Wurundjeri", "Guarani", "Tupi", "Maasai",
    "Treaty 6", "Peace and Friendship",
]
GATES = ["indigenous_rights_holders", "advisory_circle", "protocols", "consent", "accessibility",
         "payment", "incidents", "ai_use", "timeline", "evaluation", "legal"]


def section(plan, sid):
    return next(s for s in plan["sections"] if s["id"] == sid)


def all_text(plan):
    return wh.plan_to_json(plan) + wh.plan_to_markdown(plan)


@pytest.mark.parametrize("language", ["en", "fr"])
@pytest.mark.parametrize("city,country,region", CITIES)
def test_plan_mentions_location_and_has_all_gates(city, country, region, language):
    plan = wh.generate_community_plan(city, country, region, language)
    assert plan["location"]["city"] == city and plan["location"]["country"] == country
    assert city in plan["title"] and country in plan["title"]
    assert [s["id"] for s in plan["sections"]] == GATES
    md = wh.plan_to_markdown(plan)
    assert city in md and country in md


@pytest.mark.parametrize("language", ["en", "fr"])
@pytest.mark.parametrize("city,country,region", CITIES)
def test_no_nation_names_or_numbers_invented(city, country, region, language):
    plan = wh.generate_community_plan(city, country, region, language)
    text = all_text(plan)
    for name in NATION_NAMES:
        assert re.search(rf"(?<!\w){re.escape(name)}(?!\w)", text, re.IGNORECASE) is None, name
    # No statistics or figures: none of these inputs has digits, so neither may the plan.
    assert re.search(r"\d", text.replace("world-holobridge-community-plan/1", "")) is None


def test_plan_sections_match_framework_rules():
    for language in ["en", "fr"]:
        plan = wh.generate_community_plan("City", "Country", language=language)
        assert {i["label"] for i in section(plan, "protocols")["items"]} == set(wh.WorldHoloBridgeAdapter.REQUIRED_PROTOCOLS)
        assert {i["label"] for i in section(plan, "accessibility")["items"]} == wh.REQUIRED_ACCESSIBILITY
        assert wh.SEVERITIES <= {i["label"] for i in section(plan, "incidents")["items"]}
        assert {"role", "amount", "currency", "attribution", "license_terms", "revenue_share"} <= {
            i["label"] for i in section(plan, "payment")["items"]}
        assert len(section(plan, "timeline")["items"]) == 5
        assert len(section(plan, "advisory_circle")["items"]) >= 1


def test_indigenous_guidance_is_local_and_non_authoritative():
    plan = wh.generate_community_plan("Anytown", "Anyland")
    text = all_text(plan)
    sec = section(plan, "indigenous_rights_holders")
    assert "does not name any Indigenous nation" in sec["intro"]
    assert any("directly with those communities" in i["text"] for i in sec["items"])
    assert any("native-land.ca" in i["text"] and "not authoritative" in i["text"] for i in sec["items"])
    legal = " ".join(i["text"] for i in section(plan, "legal")["items"])
    assert "OCAP®" in legal and "CARE" in legal and "not legal advice" in legal
    assert "Not legal advice" in text
    fr = all_text(wh.generate_community_plan("Anytown", "Anyland", language="fr"))
    assert "PCAP®" in fr and "CARE" in fr and "ne fait pas autorité" in fr


@pytest.mark.parametrize("kwargs,message", [
    ({"city": "", "country": "C"}, "City is required"),
    ({"city": "  ", "country": "C"}, "City is required"),
    ({"city": None, "country": "C"}, "City is required"),
    ({"city": "A", "country": ""}, "Country is required"),
    ({"city": "a" * 101, "country": "C"}, "at most 100"),
    ({"city": "a\x00b", "country": "C"}, "not allowed"),
    ({"city": "a\nb", "country": "C"}, "not allowed"),
    ({"city": 5, "country": "C"}, "must be text"),
    ({"city": "A", "country": "C", "language": "de"}, "Language"),
])
def test_input_validation(kwargs, message):
    with pytest.raises(ValueError, match=message):
        wh.generate_community_plan(**kwargs)


def test_input_trimmed_and_optional_region():
    plan = wh.generate_community_plan("  Saint-Jean ", "Canada", "   ")
    assert plan["location"] == {"city": "Saint-Jean", "region": None, "country": "Canada", "display": "Saint-Jean, Canada"}


def test_placeholders_are_not_reexpanded():
    plan = wh.generate_community_plan("{country}", "X{location}")
    assert plan["location"]["display"] == "{country}, X{location}"
    assert plan["title"] == "Community plan for {country}, X{location}"


def test_markdown_escapes_user_input():
    plan = wh.generate_community_plan("*bold* [x](y) <b>", "C|D")
    md = wh.plan_to_markdown(plan)
    assert r"\*bold\* \[x\](y) \<b\>" in md and r"C\|D" in md and "<b>" not in md


def test_json_export_roundtrips():
    plan = wh.generate_community_plan("Moncton", "Canada", "NB", "fr")
    assert json.loads(wh.plan_to_json(plan)) == plan
    assert wh.generate_community_plan("Moncton", "Canada", "NB", "fr") == plan  # deterministic


def test_plan_pipeline_maps_to_gates():
    plan = wh.generate_community_plan("Anytown", "Anyland")
    result = wh.run_plan_pipeline(plan)
    checks = {(c["gate"], c["result"]) for c in result["checks"]}
    assert ("payment", "publication blocked while unpaid") in checks
    assert ("payment", "published after all contracts paid") in checks
    assert ("ai_use", "blocked_pending_governance") in checks
    assert not any("UNEXPECTED" in r for _, r in checks)
    assert result["report"]["location"] == "Anytown, Anyland"
    assert result["report"]["projects"]["published"] == 1


def test_plan_cli(tmp_path):
    cmd = [sys.executable, str(ROOT / "world_holobridge.py"), "plan", "--city", "Bathurst", "--country", "Canada",
           "--region", "NB", "--language", "fr", "--format", "json", "--out-dir", str(tmp_path),
           "--run-pipeline", "--output-dir", str(tmp_path / "reports")]
    out = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout)["location"]["city"] == "Bathurst"
    assert (tmp_path / "community_plan_bathurst-nb-canada_fr.md").is_file()
    assert (tmp_path / "community_plan_bathurst-nb-canada_fr.json").is_file()
    assert "published after all contracts paid" in out.stderr
    bad = subprocess.run([sys.executable, str(ROOT / "world_holobridge.py"), "plan", "--city", " ", "--country", "C"],
                         cwd=tmp_path, capture_output=True, text=True)
    assert bad.returncode == 2 and "City is required" in bad.stderr


def test_demo_subcommand_still_works(tmp_path):
    out = subprocess.run([sys.executable, str(ROOT / "world_holobridge.py"), "demo", "--db", ":memory:",
                          "--output-dir", str(tmp_path)], cwd=tmp_path, capture_output=True, text=True)
    assert out.returncode == 0 and "Pipeline run completed successfully." in out.stdout


def test_versions_agree():
    pyproject = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M).group(1)
    citation = re.search(r'^version: "([^"]+)"', (ROOT / "CITATION.cff").read_text(encoding="utf-8"), re.M).group(1)
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))["version"]
    assert pyproject == citation == zenodo == wh.__version__
