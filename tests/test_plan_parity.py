# SPDX-License-Identifier: MIT OR Apache-2.0
"""The browser (site/plan.js) and Python must produce byte-identical plans."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import world_holobridge as wh

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")

INPUTS = [
    {"city": "Fredericton", "country": "Canada", "region": "New Brunswick", "language": "en"},
    {"city": "Fredericton", "country": "Canada", "region": "Nouveau-Brunswick", "language": "fr"},
    {"city": "  Tromsø ", "country": "Norway", "language": "en"},
    {"city": "São Paulo", "country": "Brasil", "region": "SP", "language": "fr"},
    {"city": "東京", "country": "日本", "language": "en"},
    {"city": "<script>alert(1)</script>", "country": "*x* [y] | `z` \\ _w_", "language": "en"},
    {"city": "{country}", "country": "{location}{city}", "language": "fr"},
    {"city": "🌊" * 100, "country": "C", "language": "en"},
    {"city": "\u00a0Paris\ufeff", "country": "France", "region": "", "language": "fr"},
    {"city": "", "country": "C", "language": "en"},
    {"city": "a" * 101, "country": "C", "language": "en"},
    {"city": "🌊" * 101, "country": "C", "language": "en"},
    {"city": "a\u0007b", "country": "C", "language": "en"},
    {"city": "A", "country": "C", "language": "de"},
    {"city": "A", "language": "en"},
]


def python_side(inp):
    try:
        plan = wh.generate_community_plan(inp.get("city"), inp.get("country"), inp.get("region"), inp["language"])
    except ValueError:
        return {"ok": False}
    return {"ok": True, "json": wh.plan_to_json(plan), "markdown": wh.plan_to_markdown(plan)}


def test_python_and_js_agree():
    if NODE is None:
        if os.environ.get("REQUIRE_NODE"):
            pytest.fail("node is required for the parity test")
        pytest.skip("node not installed")
    out = subprocess.run([NODE, str(ROOT / "tests" / "js" / "parity_cli.js")], input=json.dumps(INPUTS),
                         capture_output=True, text=True, encoding="utf-8", check=True)
    js = json.loads(out.stdout)
    assert len(js) == len(INPUTS)
    for inp, js_result in zip(INPUTS, js):
        py = python_side(inp)
        assert py["ok"] == js_result["ok"], inp
        if py["ok"]:
            assert py["json"] == js_result["json"], inp
            assert py["markdown"] == js_result["markdown"], inp
