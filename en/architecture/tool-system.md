# The Tool System

The defining feature of Engrix Agent: **425 registered tools across 22 categories** (live registry check: `425 tool registered | 22 kategori | 407 tool terkategori | 17 always-on`, zero ghosts, zero missing, zero duplicates).

## The critical question

> *How can an agent use hundreds of tools without getting confused — and pick the right one?*

Naive approaches fail at this scale. Dumping 425 tool schemas into every request makes the prompt enormous and the model drowns: similar names blur together, selection quality drops, and token cost explodes. Hiding tools from the model entirely means it cannot even know what exists.

## The solution: a three-layer drawer system

Tools are organized like a physical library — the catalog is always visible, but you only carry the shelf you need:

| Layer | What it is | Count |
|---|---|---|
| **Always-on** | Planning, search, and self-management tools every request needs | 17 |
| **Categories** | The drawers — opened explicitly when a task needs them | 22 (+1 family shortcut) |
| **Subdomains** | Drawers inside drawers — a subset of a big category | 40 |

The per-request view stays flat no matter how deep the inventory goes:

```
every request ──▶ [ always-on: 17 tools ]
                  [ menu: 22 category names + counts + triggers ]   ◀── small, static
                          │
        model picks by intent, one call:  open_tool_category("github")
                          │
                          ▼
        rest of session ──▶ [ github drawer: 83 full schemas ]  ◀── loaded once
                             [ subdomain option: repo_code (16) · pr (3) · … ]
```

When a task starts, the model sees a compact menu: category names, tool counts, and short trigger examples. Opening a category (`open_tool_category`) loads that drawer's full schemas and detailed usage instructions **for the rest of the session** — no need to reopen. A family shortcut (`code_workspace`) opens five code-related drawers at once for heavy engineering sessions.

## Selection discipline

Three mechanisms keep selection precise:

1. **Explicit routing, not similarity search.** The model *chooses* a category by name through a rule-based router. There is no embedding retrieval guessing "which tools might be relevant" — the model reasons about intent, and the router resolves exactly what it asked for.
2. **Grouping by real usage, not by name.** Categories reflect how work actually happens: GitHub + Gists share one drawer (same ecosystem), while *local* git and *remote* GitHub are deliberately separated (different domains, never mixed). A huge `code_exec` family was split into six granular drawers precisely so "I just want to run pytest" does not drag in terminal + kernel + LSP + file operations at once.
3. **Hot/cold decay.** Categories unused for the last 3 tasks drop their full descriptions from the static menu (only names and examples remain) — the always-on payload stays small, and full descriptions re-inject only when a category becomes hot again.

## Why the tools are trustworthy

The registry is a verified contract, not a convention. A live parity checker compares the category definitions against what actually registers at import time and reports ghosts (defined but unregistered), missing tools, and duplicates. The current run: **all zeros**. Every addition goes through an explicit four-point registration protocol — see [the registry decision](../decisions/003-explicit-tool-registry.md).

Next: [Layered Memory](memory.md) — how the agent never loses the thread.
