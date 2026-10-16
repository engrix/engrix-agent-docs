# Design Decisions (Distilled ADRs)

The private repository keeps full ADRs in Indonesian (the owner's working language);
this is the English distillation of the decisions that shaped the architecture.

## ADR-0002 — One wiring protocol for all tools
**Decision.** Every tool family registers through the same 4-point protocol
(module → categories → router → package `__init__`).
**Why.** Before the protocol, forgotten imports made tool categories silently vanish
five separate times. A single checklist that can be mechanically verified ends an
entire class of bugs. Trade-off accepted: four files touched per new family, in
exchange for zero invisible tools.

## ADR-0009 — src-layout package with one-way layering
**Decision.** The engine lives in `backend/src/engrix/` with a strict import
direction: `config → storage → memory → routing → … → agent → bootstrap → main`.
**Why.** The original tree grew organically into god files (3.5k-line orchestration
loop, 3k-line database module) with circular imports hidden inside the monolith.
The migration to this layout ran in 25 verified waves with zero downtime; cycles were
broken by demoting shared pieces (e.g. `routing/`) rather than by patching symptoms.

## ADR-0011 — SQLite first, Postgres later
**Decision.** Embedded SQLite (WAL) behind a `storage/` boundary; no Postgres today.
**Why.** Single user, single machine — SQLite removes an entire server from the
failure surface and matches the packaged-EXE distribution goal. All database access is
concentrated in one layer so a second driver (Postgres) can be added for a
multi-instance server deployment without touching domain code.

## ADR-0012 — Runtime data never enters the package
**Decision.** Vendor binaries (security tooling), skill libraries, provider YAML, and
generated data stay at the repository root, outside the importable package.
**Why.** 1.7 GB of vendor files inside a Python package pollutes diffs, installs, and
packaging. Root-level assets have their own lifecycle (backup, not review).

## Providers as YAML — single source of truth
**Decision.** Every LLM provider is exactly one YAML file (endpoints, models,
priority, reasoning-effort options). No provider is hardcoded.
**Why.** The provider landscape churns monthly. Onboarding a new provider is a file
drop; re-prioritizing is editing a number. The UI reads the same registry through an
API — there is no second source of truth to drift.

## Skills as a disk-loaded library
**Decision.** Skills (prompt-level playbooks) live in `skills/` as folders with
markdown manifests, loaded at runtime, never imported as code.
**Why.** Skills change at documentation speed, not code speed. Keeping them outside
the package means editing a skill never risks the engine's import graph.

## Migration discipline (the meta-decision)
**Decision.** Structural changes ship as a sequence of small, independently verified
waves: one logical change per commit, a behavioral fingerprint (pytest baseline)
before and after, and a sandbox instance (`ENGRIX_SANDBOX=1`) proving the change on a
real boot before promotion.
**Why.** The engine that builds the engine cannot be taken down. Every wave in the
monolith-to-package migration kept production serving traffic; the final promotion was
a folder swap plus a venv rebuild, measured in minutes.

## Language policy
**Decision.** Code, tool docstrings (model-facing), logs, and agent-facing results in
English; owner-facing docs, READMEs, and architecture records in Indonesian.
**Why.** Each artifact is written in the language of its actual reader. LLM tool
descriptions are prompts; comments and docs are read by the owner.
