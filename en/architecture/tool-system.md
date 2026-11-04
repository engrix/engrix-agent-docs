# The Tool System

The defining feature of Engrix Agent: a large, explicitly registered tool surface behind a drawer system, so the per-request prompt stays small no matter how big the inventory grows. The arithmetic closes exactly: `registered = categorized + always-on + 1 meta-tool` — `open_tool_category`, the drawer-opener itself, lives outside categories by design. Every number on this page is measured from the live registry by `scripts/verify_docs_claims.py`; the document fails its own gate if it drifts.

## The question

> *How can an agent use hundreds of tools without getting confused — and pick the right one?*

Naive approaches fail at this scale. Dumping every tool schema into every request makes the prompt enormous and the model drowns: similar names blur together, selection quality drops, and token cost explodes. Hiding tools from the model entirely means it cannot even know what exists.

## The solution: a three-layer drawer system

Tools are organized like a physical library — the catalog is always visible, but you only carry the shelf you need:

| Layer | What it is | Count |
|---|---|---|
| **Always-on** | Planning, search, and self-management tools every request needs | 19 |
| **Categories** | The drawers — opened explicitly when a task needs them | 25 |
| **Subdomains** | Drawers inside drawers — a subset of a big category | 46 |

The subdomains are not spread thin: they exist for the eight categories large enough to need them — `github` (12), `vps` (7), `security` (6), `browser` (5), `design` (5), `desktop_control` (5), `device_control` (3), `telethon` (3).

The per-request view stays flat no matter how deep the inventory goes:

```
every request ──▶ [ always-on: 19 tools ]
                  [ menu: 25 category names + counts + triggers ]   ◀── small, static
                          │
        model picks by intent, one call:  open_tool_category("github")
                          │
                          ▼
        rest of session ──▶ [ github drawer: 83 full schemas ]  ◀── loaded once
                             [ subdomain option: repo_code (16) · pr (3) · … ]
```

When a task starts, the model sees a compact menu: category names, tool counts, and short trigger examples. Opening a category (`open_tool_category`) loads that drawer's full schemas and detailed usage instructions **for the rest of the session** — no need to reopen. A family shortcut (`code_workspace`) opens five code-related drawers at once for heavy engineering sessions.

The drawers are deliberately unbalanced, because real work is unbalanced: `github` (83) and `vps` (48) are ecosystems, while `code_search` (2) and `debugger` (3) are surgical. A single `code_exec` family was split into six granular drawers precisely so "I just want to run pytest" does not drag in terminal + kernel + LSP + file operations at once.

## Selection discipline

Three mechanisms keep selection precise:

1. **Explicit routing, not similarity search.** The model *chooses* a category by name through a rule-based router. There is no embedding retrieval guessing "which tools might be relevant" — the model reasons about intent, and the router resolves exactly what it asked for.
2. **Grouping by real usage, not by name.** Categories reflect how work actually happens: GitHub + Gists share one drawer (same ecosystem), while *local* git and *remote* GitHub are deliberately separated (different domains, never mixed).
3. **Hot/cold decay.** Categories unused for the last 3 tasks drop their full descriptions from the static menu (only names and examples remain) — the always-on payload stays small, and full descriptions re-inject only when a category becomes hot again.

## Why the tools are trustworthy

The registry is a verified contract, not a convention. `scripts/check_registry_sync.py` compares the category definitions against what actually registers at import time and **hard-fails** on ghosts (defined but unregistered), missing tools, always-on drift, and duplicates. `scripts/check_contracts.py` extends the same idea to category literals, subdomains, and the always-on set, with a self-test that proves the gate can fail.

This is not ceremony. The history that produced it is specific: five separate incidents where a whole tool category vanished from the agent's reach because one package import was forgotten. Nothing crashed — the tools just quietly stopped existing for the model. Silent disappearance is the worst failure mode an agent can have, and the gate exists to make it loud.

Every addition goes through an explicit four-point registration protocol — see [the registry decision](../decisions/003-explicit-tool-registry.md).

Next: [Layered Memory](memory.md) — how the agent never loses the thread.
