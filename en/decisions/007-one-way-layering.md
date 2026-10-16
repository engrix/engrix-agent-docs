# ADR-007 — One-Way Layering, Verified Live

**Status:** Accepted

## Problem

A grown codebase drifts into cycles: UI code imports storage, storage imports the agent loop, everything imports everything. Each new feature then costs more than the last, and "it worked yesterday" breaks become routine. The trigger event here was structural reorganization itself — the question was not just *where files go*, but *how to make the structure enforceable*.

## Solution

The engine is a package with **11 layers in one direction**:

```
config → storage → memory → knowledge → formatting → curation
       → routing → personality → tools → ml → agent → bootstrap → main
```

Higher layers may import lower ones; never the reverse. Domain code never writes SQL plumbing; orchestration never reads config files directly. The separation is the maintenance contract: one logical fix lands in one layer.

The rule is verified, not aspirational: a dependency audit script maps every cross-package import and flags violations — the tool that found the only two real back-edges (router imports from the agent loop) during the restructure, which were then dissolved by moving the routers down a layer.

## Consequences

- "Where does this fix go?" has exactly one right answer per change.
- Cycles surface at the audit step instead of as runtime import errors.
- The migration itself was executed as ~35 disciplined commits (move → verify → commit) with a live registry-parity gate before and after each step — zero-downtime, fully reversible, every step pushed to a backup remote before touching production.
