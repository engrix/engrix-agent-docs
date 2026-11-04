# ADR-002 — A Drawer System for Hundreds of Tools

**Status:** Accepted

> *The question this ADR answers:* **How do hundreds of tools stay visible without drowning every request?**

## Problem

At this scale, the two obvious designs both fail:

- **All schemas always in the prompt** — token cost explodes, similar tool names blur, selection quality degrades. The model drowns.
- **Similarity search over tool descriptions** — a retrieval layer *guesses* which tools might be relevant. Guesses are wrong in ways that are hard to debug, and the model never sees the full catalog, so it cannot even know what to ask for.

The problem is not "too many tools". It is that **the model's per-request view must stay bounded while the inventory keeps growing**.

## Solution

A **three-layer drawer taxonomy** modeled on a library: the full catalog is always listed (names + counts + trigger examples), but full schemas load only when a drawer is opened.

1. **Always-on tools** — planning, search, self-management; needed by every request.
2. **Categories** — opened explicitly by the model via a rule-based router call. Opening loads schemas for the rest of the session. A family shortcut opens five code-drawers at once.
3. **Subdomains** — subsets of oversized categories, so "I only need devtools" does not drag in an entire browser drawer.

The exact counts are deliberately **not written here**. They live in the code and are asserted by `scripts/verify_docs_claims.py`, which fails the document when a number drifts. A decision record should state the decision; the inventory count is a measurement, and measurements belong to the gate.

Selection stays precise because:

- **Routing is explicit** — the model names the drawer it wants; the router resolves exactly that. No similarity guessing anywhere.
- **Categories group by real usage ecosystems** (GitHub+Gist together; local git vs remote GitHub strictly apart), and oversized families are split granularly so small jobs do not carry big payloads.
- **Hot/cold decay** — unused categories drop their descriptions from the static menu after 3 idle tasks; names and examples remain so the model can always open them.

## Consequences

- Iteration-0 payload stays small regardless of how large the tool inventory grows.
- Adding tools never degrades the default prompt — only the drawer it belongs to grows.
- The tradeoff is one extra router call when a drawer is needed; observed behavior shows the model opens drawers eagerly and correctly when trigger examples are written well.
- The second-order cost is real and worth naming: the drawer system only works if the *menu* is honest. A category whose trigger examples are vague makes the model open the wrong drawer, and the failure looks like a reasoning error rather than a catalog error.
