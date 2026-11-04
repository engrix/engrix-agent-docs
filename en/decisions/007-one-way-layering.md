# ADR-007 — One-Way Layering

**Status:** Accepted

> *The question this ADR answers:* **How do you stop a codebase from quietly growing circular imports?**

## Problem

A grown codebase drifts into cycles: UI code imports storage, storage imports the agent loop, everything imports everything. Each new feature then costs more than the last, and "it worked yesterday" breaks become routine. The trigger event here was structural reorganization itself — the question was not just *where files go*, but *how to make the structure enforceable*.

## Solution

The engine is a package with **one direction of dependency**:

```
config → paths → storage → memory → knowledge → formatting → curation
       → routing → personality → tools → ml → agent → subagent
       → publication → evaluation → transport → app → bootstrap → main
```

Higher layers may import lower ones; never the reverse. Domain code never writes SQL plumbing; orchestration never reads config files directly. The separation is the maintenance contract: one logical fix lands in one layer.

## What is actually enforced, and what is not

This is the part worth being precise about, because "we have a layering rule" is easy to say and hard to mean.

**Enforced by a gate:**

- Route modules may not import `engrix.main`. `scripts/route_module_check.py` fails the build on violation, and also verifies that each route module's `parents[N]` path arithmetic still points at the real repository root — a class of bug that produces no exception, no red test, and a feature that silently operates on the wrong folder.
- A module-level name that is referenced but never bound fails `scripts/module_binding_check.py`. That gate exists because an `import` statement once landed inside a docstring: it was inert text, `import engrix.main` still succeeded, every gate passed, and the chat path raised `NameError` on the next turn.
- Tool and category wiring is checked against the live registry (`check_registry_sync.py`, `check_contracts.py`).

**Not enforced by a gate:**

- The full cross-package import direction. The dependency audit that mapped every cross-package import was a one-off during the migration and is not part of the shipped repository. It found the only two real back-edges at the time (router modules importing from the agent loop), which were dissolved by moving the routers down a layer — but a new back-edge introduced tomorrow would be caught in review, not by a failing build.

Stating that gap is more useful than claiming the whole contract is machine-checked. The gates above cover the violations that have actually happened; the rest is a review-time contract with a documented history.

## Consequences

- "Where does this fix go?" has exactly one right answer per change.
- The two failure classes that already bit this codebase are now gates rather than habits.
- The migration itself was executed as ~35 disciplined commits (move → verify → commit) with a live registry-parity gate before and after each step — zero-downtime, fully reversible, every step pushed to a backup remote before touching production.
