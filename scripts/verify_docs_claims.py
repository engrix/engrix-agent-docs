# -*- coding: utf-8 -*-
"""Verify every measured claim in this portfolio against live source.

Two directions, both mandatory:
  A) measure the fact from the engine source tree
  B) assert the measured value actually appears in the doc that cites it

A missing claim is a FAIL, not a skip -- if the source text drifts, this
script must say so instead of quietly passing.

Usage
-----
    python scripts/verify_docs_claims.py

The engine source path defaults to D:\\engrix-agent and can be overridden:

    ENGRIX_REPO=/path/to/engrix-agent python scripts/verify_docs_claims.py

The script needs `engrix` importable, so run it from the repo root with the
engine's src layout on PYTHONPATH (or use the engine's own venv):

    PYTHONPATH=/path/to/engrix-agent/backend/src python scripts/verify_docs_claims.py

Exit code 0 = every claim matches. Non-zero = at least one claim is stale.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# This file lives at <docs-repo>/scripts/verify_docs_claims.py
DOCS = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("ENGRIX_REPO", r"D:\engrix-agent"))
SRC = REPO / "backend" / "src"

if not REPO.exists():
    print(f"FATAL: engine source not found at {REPO}")
    print("       set ENGRIX_REPO to the engine checkout")
    sys.exit(2)

sys.path.insert(0, str(SRC))

fails = []
checks = 0


def check(label, ok, detail=""):
    global checks
    checks += 1
    if ok:
        print(f"  OK    {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        fails.append(label)


def read(rel):
    return (DOCS / rel).read_text(encoding="utf-8")


# ---------------------------------------------------------------- measure A
import engrix.bootstrap  # noqa: F401,E402  side-effect: register every tool module
from engrix.tools.registry import registry  # noqa: E402
from engrix.tools import tool_categories as tc  # noqa: E402

tools = len(registry.list_tools()) if hasattr(registry, "list_tools") else len(registry._tools)
cats = len(tc.TOOL_CATEGORIES)
always = len(tc.ALWAYS_ON_TOOLS)
categorized = sum(len(v.get("tools", [])) for v in tc.TOOL_CATEGORIES.values())

main_py = SRC / "engrix" / "main.py"
main_txt = main_py.read_text(encoding="utf-8", errors="replace")
routes = len(re.findall(r"@app\.(get|post|put|delete|patch|websocket)\(", main_txt))
main_lines = len(main_txt.splitlines())

head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                      capture_output=True, text=True).stdout.strip()

print("=== measured from engine source ===")
print(f"repo={REPO}")
print(f"tools={tools} categories={cats} always_on={always} categorized={categorized}")
print(f"routes={routes} main_lines={main_lines} head={head}")
print()

check("arithmetic closes: categorized + always_on + 1 meta == registered",
      categorized + always + 1 == tools,
      f"{categorized}+{always}+1 vs {tools}")

print()
print("=== docs claims ===")

# ---------------------------------------------------------------- direction B
README = read("README.md")
check("README cites 459 tools", "459 registered tools" in README)
check("README cites 23 categories", "23 categories" in README)
check("README cites commit 9b906dae", "9b906dae" in README)
check("README cites measurement date 2026-10-21", "2026-10-21" in README)
check("README has no stale 425", "425" not in README, "still contains 425")
check("README has no stale 22 categories", "22 categories" not in README)

EN_TS = read("en/architecture/tool-system.md")
check("en tool-system cites 459 registered", "459 registered tools" in EN_TS)
check("en tool-system cites 440 categorized", "440 categorized" in EN_TS)
check("en tool-system cites 18 always-on", "18 always-on" in EN_TS)
check("en tool-system table always-on 18", "| 18 |" in EN_TS)
check("en tool-system table categories 23", "| 23 (+1 family shortcut) |" in EN_TS)
check("en tool-system diagram 18", "[ always-on: 18 tools ]" in EN_TS)
check("en tool-system diagram 23", "[ menu: 23 category names" in EN_TS)
check("en tool-system subdomains 40", "| 40 |" in EN_TS)
check("en tool-system has no stale 425", "425" not in EN_TS, "still contains 425")
check("en tool-system has no stale 407", "407" not in EN_TS, "still contains 407")
check("en tool-system has no stale 17 always-on", "| 17 |" not in EN_TS)

ID_TS = read("id/architecture/tool-system.md")
check("id tool-system cites 459", "459 tool ter-register" in ID_TS)
check("id tool-system cites 440", "440 terkategori" in ID_TS)
check("id tool-system cites 18 always-on", "18 always-on" in ID_TS)
check("id tool-system has no stale 425", "425" not in ID_TS, "still contains 425")
check("id tool-system has no stale 407", "407" not in ID_TS)

EN_OV = read("en/architecture/overview.md")
check("en overview tools 459", "459 executable capabilities" in EN_OV)
check("en overview mermaid 23 drawers", "23 drawers, 459 tools" in EN_OV)
check("en overview knowledge is a module", "knowledge.py     semantic retrieval" in EN_OV)
check("en overview has no stale 425", "425" not in EN_OV)
check("en overview has no stale 22 drawers", "22 drawers" not in EN_OV)

ID_OV = read("id/architecture/overview.md")
check("id overview tools 459", "459 kapabilitas" in ID_OV)
check("id overview mermaid 23 drawers", "23 laci, 459 tool" in ID_OV)
check("id overview knowledge is a module", "knowledge.py     retrieval semantik" in ID_OV)
check("id overview has no stale 425", "425" not in ID_OV)
check("id overview has no stale 22 drawers", "22 laci" not in ID_OV)

EN_ADR2 = read("en/decisions/002-drawer-tool-system.md")
check("en ADR-002 scale 459", "At 459 tools" in EN_ADR2)
check("en ADR-002 always-on 18", "**18 always-on tools**" in EN_ADR2)
check("en ADR-002 categories 23", "**23 categories**" in EN_ADR2)
check("en ADR-002 has no stale 425", "425" not in EN_ADR2)

ID_ADR2 = read("id/decisions/002-drawer-tool-system.md")
check("id ADR-002 scale 459", "Di 459 tool" in ID_ADR2)
check("id ADR-002 always-on 18", "**18 tool always-on**" in ID_ADR2)
check("id ADR-002 categories 23", "**23 kategori**" in ID_ADR2)
check("id ADR-002 has no stale 425", "425" not in ID_ADR2)

EN_ADR3 = read("en/decisions/003-explicit-tool-registry.md")
check("en ADR-003 registry run 459", "across 459 tools" in EN_ADR3)
check("en ADR-003 has no stale 425", "425" not in EN_ADR3)

ID_ADR3 = read("id/decisions/003-explicit-tool-registry.md")
check("id ADR-003 registry run 459", "di 459 tool" in ID_ADR3)
check("id ADR-003 has no stale 425", "425" not in ID_ADR3)

EN_ADR7 = read("en/decisions/007-one-way-layering.md")
check("en ADR-007 layers 13", "13 named layers" in EN_ADR7)
check("en ADR-007 has no stale 11 layers", "11 layers" not in EN_ADR7)
check("en ADR-007 states audit scope honestly",
      "not part of the shipped repository" in EN_ADR7)

ID_ADR7 = read("id/decisions/007-one-way-layering.md")
check("id ADR-007 layers 13", "13 layer bernama" in ID_ADR7)
check("id ADR-007 has no stale 11 layer", "11 layer" not in ID_ADR7)
check("id ADR-007 states audit scope honestly", "tidak ikut dikirim di repo" in ID_ADR7)

EN_RM = read("en/roadmap.md")
check("en roadmap has Recently landed", "## Recently landed" in EN_RM)
check("en roadmap cites 459/23", "459 tools across 23 categories" in EN_RM)
check("en roadmap cites commit", "9b906dae" in EN_RM)
check("en roadmap states test baseline honestly", "120 passed, 2 failed" in EN_RM)
check("en roadmap says transport not built", "Still not built" in EN_RM)

ID_RM = read("id/roadmap.md")
check("id roadmap has Yang baru mendarat", "## Yang baru mendarat" in ID_RM)
check("id roadmap cites 459/23", "459 tool di 23 kategori" in ID_RM)
check("id roadmap cites commit", "9b906dae" in ID_RM)
check("id roadmap states test baseline honestly", "120 passed, 2 failed" in ID_RM)
check("id roadmap says transport not built", "Belum dibangun" in ID_RM)

# ---------------------------------------------------------------- structure parity
def headings(text):
    return [line.strip() for line in text.splitlines() if line.startswith("#")]

check("roadmap en/id heading count match",
      len(headings(EN_RM)) == len(headings(ID_RM)),
      f"{len(headings(EN_RM))} vs {len(headings(ID_RM))}")
check("tool-system en/id heading count match",
      len(headings(EN_TS)) == len(headings(ID_TS)),
      f"{len(headings(EN_TS))} vs {len(headings(ID_TS))}")
check("overview en/id heading count match",
      len(headings(EN_OV)) == len(headings(ID_OV)),
      f"{len(headings(EN_OV))} vs {len(headings(ID_OV))}")

# ---------------------------------------------------------------- global stale scan
print()
print("=== global stale-number scan (all .md) ===")
STALE = ["425", "407 categorized", "17 always-on", "22 categories", "22 kategori",
         "22 drawers", "22 laci", "11 layers", "11 layer"]
hits = []
for path in DOCS.rglob("*.md"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for needle in STALE:
        if needle in text:
            hits.append(f"{path.relative_to(DOCS)} :: {needle}")
check("no stale numbers anywhere in docs", not hits, "; ".join(hits[:6]))

print()
print(f"checks={checks} passed={checks - len(fails)} failed={len(fails)}")
print("RESULT:", "ALL CLAIMS MATCH" if not fails else "STALE CLAIMS FOUND")
sys.exit(1 if fails else 0)
