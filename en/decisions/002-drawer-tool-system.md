# ADR-002 — A Drawer System for Hundreds of Tools

**Status:** Accepted

> *The question this ADR answers:* **How do hundreds of tools stay visible without drowning every request?**

## Problem

> *How can an agent use hundreds of tools without getting confused — and select the right one?*

At 425 tools, the two obvious designs both fail:

- **All schemas always in the prompt** — token cost explodes, similar tool names blur, selection quality degrades. The model drowns.
- **Similarity search over tool descriptions** — a retrieval layer *guesses* which tools might be relevant. Guesses are wrong in ways that are hard to debug, and the model never sees the full catalog, so it cannot even know what to ask for.

## Solution

A **three-layer drawer taxonomy** modeled on a library: the full catalog is always listed (names + counts + trigger examples), but full schemas load only when a drawer is opened.

1. **17 always-on tools** — planning, search, self-management; needed by every request.
2. **22 categories** — opened explicitly by the model via a rule-based router call. Opening loads schemas for the rest of the session. A family shortcut opens five code-drawers at once.
3. **40 subdomains** — subsets of oversized categories, so "I only need devtools" does not drag in all 37 browser tools.

Selection stays precise because:

- **Routing is explicit** — the model names the drawer it wants; the router resolves exactly that. No similarity guessing anywhere.
- **Categories group by real usage ecosystems** (GitHub+Gist together; local git vs remote GitHub strictly apart), and oversized families are split granularly so small jobs do not carry big payloads.
- **Hot/cold decay** — unused categories drop their descriptions from the static menu after 3 idle tasks; names and examples remain so the model can always open them.

## Consequences

- Iteration-0 payload stays small regardless of how large the tool inventory grows.
- Adding tools never degrades the default prompt — only the drawer it belongs to grows.
- The tradeoff is one extra router call when a drawer is needed; observed behavior shows the model opens drawers eagerly and correctly when trigger examples are written well.
