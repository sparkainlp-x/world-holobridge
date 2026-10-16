# SPDX-License-Identifier: MIT OR Apache-2.0
"""Assembles the static site: site/* plus the shared plan_template.json."""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "_site"
if out.exists():
    shutil.rmtree(out)
shutil.copytree(root / "site", out)
shutil.copy2(root / "plan_template.json", out / "plan_template.json")
(out / ".nojekyll").write_text("", encoding="utf-8")
print(out)
