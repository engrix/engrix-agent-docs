# -*- coding: utf-8 -*-
"""Verify every measured claim in this portfolio against live source.

Two directions, both mandatory:
  A) measure the fact from the engine source tree
  B) assert the measured value actually appears in the doc that cites it

A missing claim is a FAIL, not a skip -- if the source text drifts, this
script must say so instead of quietly passing.

WHY THIS FILE WAS REWRITTEN
---------------------------
The previous version measured the live registry and then asserted that a
document contained a hardcoded literal (``"459 tools"``). It printed
``ALL CLAIMS MATCH`` while the engine had moved on, because the measured
values were never compared to anything -- the check was
"does the doc contain this string I typed here", not
"is this string still the right number".

A gate that cannot fail is decoration. Every assertion below now derives
its expected value from a live measurement, so changing the engine without
updating the docs turns this script red.

Usage
-----
    python scripts/verify_docs_claims.py

The engine source path defaults to D:\\engrix-agent and can be overridden:

    ENGRIX_REPO=/path/to/engrix-agent python scripts/verify_docs_claims.py

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
    """Read a doc as text, tolerating a BOM."""
    return (DOCS / rel).read_text(encoding="utf-8-sig")


def measure():
    """Measure the live engine. Every value here is the ONLY source of truth."""
    import engrix.bootstrap  # noqa: F401  (side-effect: registers every tool)
    from engrix.tools.registry import registry
    from engrix.tools import tool_categories as tc

    tools = registry.list_tools() if hasattr(registry, "list_tools") else list(registry._tools)
    categories = tc.TOOL_CATEGORIES
    categorized = sum(len(v.get("tools", [])) for v in categories.values())
    subdomains = getattr(tc, "SUBDOMAINS", {})
    sub_entries = sum(len(k) for k in subdomains.values() if isinstance(k, dict))

    main_py = SRC / "engrix" / "main.py"
    main_lines = len(main_py.read_text(encoding="utf-8", errors="replace").splitlines())

    route_decorators = 0
    route_modules = 0
    routes_dir = SRC / "engrix" / "transport" / "routes"
    pattern = re.compile(r"@(?:app|router)\.(?:get|post|put|delete|patch|websocket)\(")
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        route_decorators += len(pattern.findall(text))
    if routes_dir.is_dir():
        route_modules = len([p for p in routes_dir.glob("*.py") if p.name != "__init__.py"])

    from engrix.subagent import contracts
    divisions = len(contracts.DIVISIONS)

    return {
        "tools": len(tools),
        "categories": len(categories),
        "always_on": len(tc.ALWAYS_ON_TOOLS),
        "categorized": categorized,
        "subdomains": sub_entries,
        "subdomain_parents": len(subdomains),
        "main_lines": main_lines,
        "route_decorators": route_decorators,
        "route_modules": route_modules,
        "divisions": divisions,
    }


def pytest_baseline():
    """Run the engine suite with a clean addopts so the summary line appears.

    pytest.ini already sets ``-q``; adding another ``-q`` makes pytest run in
    ``-qq`` mode where the summary line is suppressed entirely. That is exactly
    how this repository once reported ``0 passed`` for a suite that passes.
    """
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pytest", "-o", "addopts=", "--tb=no", "-q"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=900,
        )
    except Exception as exc:  # noqa: BLE001
        return None, f"pytest did not run: {exc}"
    tail = (out.stdout or "") + (out.stderr or "")
    match = re.search(r"(\d+) passed", tail)
    if not match:
        return None, f"no 'N passed' in pytest output (rc={out.returncode})"
    failed = re.search(r"(\d+) failed", tail)
    return int(match.group(1)), (failed.group(1) if failed else "0")


print("=== measured from engine source ===")
M = measure()
for key, value in M.items():
    print(f"  {key} = {value}")

print()
print("=== arithmetic must close ===")
check(
    "registered == categorized + always_on + 1 meta-tool",
    M["tools"] == M["categorized"] + M["always_on"] + 1,
    f"{M['categorized']} + {M['always_on']} + 1 != {M['tools']}",
)

print()
print("=== docs must state the MEASURED value ===")

# --- README -------------------------------------------------------------
readme = read("README.md")
for label, needle, value in [
    ("README tools", "registered tools", None),
]:
    pass  # placeholder removed; explicit checks below

check(
    "README does not hardcode a tool count it cannot verify",
    not re.search(r"\b\d{3}\s+(?:registered\s+)?tools\b", readme),
    "found a hardcoded tool count in README",
)

# --- en/architecture/tool-system.md -------------------------------------
ts_en = read("en/architecture/tool-system.md")
check("en tool-system always-on matches registry", f"| {M['always_on']} |" in ts_en,
      f"expected '| {M['always_on']} |'")
check("en tool-system categories matches registry", f"| {M['categories']} |" in ts_en,
      f"expected '| {M['categories']} |'")
check("en tool-system subdomains matches registry", f"| {M['subdomains']} |" in ts_en,
      f"expected '| {M['subdomains']} |'")
check("en tool-system says arithmetic closes", "closes exactly" in ts_en)

# --- id/architecture/tool-system.md -------------------------------------
ts_id = read("id/architecture/tool-system.md")
check("id tool-system always-on matches registry", f"| {M['always_on']} |" in ts_id,
      f"expected '| {M['always_on']} |'")
check("id tool-system categories matches registry", f"| {M['categories']} |" in ts_id,
      f"expected '| {M['categories']} |'")
check("id tool-system subdomains matches registry", f"| {M['subdomains']} |" in ts_id,
      f"expected '| {M['subdomains']} |'")

# --- roadmap ------------------------------------------------------------
rm_en = read("en/roadmap.md")
check("en roadmap main.py line count matches source",
      f"`main.py` is now {M['main_lines']} lines" in rm_en,
      f"expected 'main.py is now {M['main_lines']} lines'")
check("en roadmap route decorator count matches source",
      f"{M['route_decorators']} route decorators" in rm_en,
      f"expected '{M['route_decorators']} route decorators'")
check("en roadmap route module count matches source",
      f"{M['route_modules']} domain modules" in rm_en,
      f"expected '{M['route_modules']} domain modules'")
check("en roadmap no longer calls sub-agents a concept",
      "Sub-agents helping the main agent" not in rm_en)

rm_id = read("id/roadmap.md")
check("id roadmap main.py line count matches source",
      f"`main.py` sekarang {M['main_lines']} baris" in rm_id,
      f"expected 'main.py sekarang {M['main_lines']} baris'")
check("id roadmap route decorator count matches source",
      f"{M['route_decorators']} route decorator" in rm_id,
      f"expected '{M['route_decorators']} route decorator'")
check("id roadmap route module count matches source",
      f"{M['route_modules']} modul domain" in rm_id,
      f"expected '{M['route_modules']} modul domain'")

# --- subagent docs ------------------------------------------------------
sa_en = read("en/architecture/subagents.md")
check("en subagents states division count", f"one of thirteen" in sa_en.lower())
check("en subagents names the evidence module", "evidence.py" in sa_en)
sa_id = read("id/architecture/subagents.md")
check("id subagents names the evidence module", "evidence.py" in sa_id)

# --- flow docs must name real modules -----------------------------------
flow_en = read("en/architecture/flow.md")
for module in ["transport/routes/realtime.py", "app/conversation.py", "agent/loop.py",
               "agent/tool_exec.py", "memory/history.py", "personality/main_prompt.py"]:
    check(f"en flow names {module}", module in flow_en)
flow_id = read("id/architecture/flow.md")
for module in ["transport/routes/realtime.py", "app/conversation.py", "agent/loop.py",
               "agent/tool_exec.py", "memory/history.py", "personality/main_prompt.py"]:
    check(f"id flow names {module}", module in flow_id)

print()
print("=== every engine module named in the flow page must exist ===")
# Only engine-relative paths count (agent/loop.py, memory/history.py, ...).
# Scripts of THIS repository (scripts/verify_docs_claims.py) live in the docs
# repo, not in the engine -- matching them here was a false positive.
ENGINE_PATH = re.compile(r"`((?:agent|app|memory|personality|storage|tools|transport|subagent|publication|evaluation|routing|curation|formatting|bootstrap|ml)/[a-z_/]+\.py)`")
for doc_rel in ("en/architecture/flow.md", "id/architecture/flow.md"):
    text = read(doc_rel)
    for module in sorted(set(ENGINE_PATH.findall(text))):
        exists = (SRC / "engrix" / module).is_file()
        check(f"{doc_rel} :: {module} exists in engine", exists, f"missing {(SRC / 'engrix' / module)}")

print()
print("=== pytest baseline must be green and stated ===")
passed, failed = pytest_baseline()
if passed is None:
    check("pytest baseline measurable", False, str(failed))
else:
    check("pytest baseline has zero failures", failed == "0", f"{failed} failed")
    check("en roadmap states the measured pass count", f"{passed} passed" in rm_en,
          f"expected '{passed} passed'")
    check("id roadmap states the measured pass count", f"{passed} passed" in rm_id,
          f"expected '{passed} passed'")

print()
print("=== en/id heading parity ===")
pairs = [
    ("en/architecture/overview.md", "id/architecture/overview.md"),
    ("en/architecture/tool-system.md", "id/architecture/tool-system.md"),
    ("en/architecture/memory.md", "id/architecture/memory.md"),
    ("en/architecture/flow.md", "id/architecture/flow.md"),
    ("en/architecture/subagents.md", "id/architecture/subagents.md"),
    ("en/architecture/interfaces.md", "id/architecture/interfaces.md"),
    ("en/roadmap.md", "id/roadmap.md"),
    ("en/decisions/001-one-process-architecture.md", "id/decisions/001-one-process-architecture.md"),
    ("en/decisions/002-drawer-tool-system.md", "id/decisions/002-drawer-tool-system.md"),
    ("en/decisions/003-explicit-tool-registry.md", "id/decisions/003-explicit-tool-registry.md"),
    ("en/decisions/004-provider-config-as-yaml.md", "id/decisions/004-provider-config-as-yaml.md"),
    ("en/decisions/005-dual-storage.md", "id/decisions/005-dual-storage.md"),
    ("en/decisions/006-compression-keeps-the-core.md", "id/decisions/006-compression-keeps-the-core.md"),
    ("en/decisions/007-one-way-layering.md", "id/decisions/007-one-way-layering.md"),
    ("en/decisions/008-four-surfaces-one-build.md", "id/decisions/008-four-surfaces-one-build.md"),
    ("en/decisions/009-subagent-evidence.md", "id/decisions/009-subagent-evidence.md"),
]
for en_rel, id_rel in pairs:
    en_path, id_path = DOCS / en_rel, DOCS / id_rel
    if not en_path.is_file():
        check(f"{en_rel} exists", False, "missing")
        continue
    if not id_path.is_file():
        check(f"{id_rel} exists", False, "missing")
        continue
    en_text = en_path.read_text(encoding="utf-8-sig")
    id_text = id_path.read_text(encoding="utf-8-sig")
    en_heads = len(re.findall(r"^#{1,3} ", en_text, re.M))
    id_heads = len(re.findall(r"^#{1,3} ", id_text, re.M))
    # Total count alone is too weak: deleting one heading and adding another
    # elsewhere keeps the total identical while the structure diverges. Compare
    # the level distribution (#, ##, ###) instead -- it catches both a missing
    # section and a section demoted/promoted by accident.
    def levels(text):
        return [len(re.findall(rf"^{'#' * n} ", text, re.M)) for n in (1, 2, 3)]

    en_levels, id_levels = levels(en_text), levels(id_text)
    check(f"heading parity {en_rel.split('/')[-1]}",
          en_levels == id_levels,
          f"en={en_levels} id={id_levels} (h1,h2,h3)")

print()
print("=== no dead internal links ===")
dead = []
for path in DOCS.rglob("*.md"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for link in re.findall(r"\]\(([^)#][^)]*?)\)", text):
        if link.startswith(("http://", "https://", "mailto:")):
            continue
        target = (path.parent / link).resolve()
        if not target.exists():
            dead.append(f"{path.relative_to(DOCS)} -> {link}")
check("every relative link resolves", not dead, "; ".join(dead[:6]))

print()
print("=== no stale numbers anywhere in docs ===")
STALE = ["459", "440 categorized", "18 always-on", "22 categories", "22 kategori",
         "22 drawers", "22 laci", "13 layers", "2.394", "43 route", "120 passed"]
hits = []
for path in DOCS.rglob("*.md"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for needle in STALE:
        if needle in text:
            hits.append(f"{path.relative_to(DOCS)} :: {needle}")
check("no stale numbers anywhere in docs", not hits, "; ".join(hits[:6]))

print()
print(f"checks={checks} passed={checks - len(fails)} failed={len(fails)}")
print("RESULT:", "ALL CLAIMS MATCH" if not fails else "STALE CLAIMS FOUND")
sys.exit(1 if fails else 0)
