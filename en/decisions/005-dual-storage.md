# ADR-005 — Two Storage Engines, Each for What It's Good At

**Status:** Accepted

> *The question this ADR answers:* **Why carry two databases when one could technically do both jobs?**

## Problem

An agent needs two incompatible kinds of memory: **structured, relational state** (session facts, task positions, verification records) that must be consistent and queryable, and **semantic content** (documents, conversation digests, knowledge points) that must be found by meaning, not by exact match. Forcing either into the wrong engine makes both harder.

## Solution

**SQLite (WAL mode)** owns structured state: one connection, guarded write-lock cursor, schema versioning with migrations. **Qdrant** owns semantic recall, with a dual-mode client — embedded for a single instance, server mode when instances run in parallel. A storage layer (`storage/`) owns the mechanics; a memory layer (`memory/`) owns the meaning; domain code touches storage through that boundary only.

## Consequences

- Zero-dependency deployment: the whole agent runs from a folder — no database server required for structured state.
- Parallel instances become safe by flipping one setting (embedded → server vector mode) instead of rearchitecting.
- Schema evolution is controlled by migrations, not by `ALTER TABLE` scattered across code — the agent's memory outlives any single version.
