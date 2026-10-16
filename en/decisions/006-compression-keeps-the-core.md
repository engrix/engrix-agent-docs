# ADR-006 — Compression That Keeps the Core (Memory Design)

**Status:** Accepted

> *The question this ADR answers:* **What if compression erases exactly the detail the task needs later?**

## Problem

The original requirement was blunt:

> *"An assistant that can do anything, run anywhere, and never lose context."*

Chat history alone fails at exactly this. It either bloats until the model loses the beginning in the middle, or it gets cut and the agent forgets its own task. And forgetting is not one problem — it is at least four: forgetting facts, forgetting the current step, forgetting past sessions, forgetting what sibling conversations covered.

## Solution

Treat "never forget" as a set of **layered stores**, each owning one kind of forgetting — all designed around the same principle: *compress aggressively, but always keep the core.*

| Kind of forgetting | Store |
|---|---|
| Facts stated in-session | Mechanical fact extraction (zero hallucination, stopword-filtered) |
| Where am I in the task | A task-position block injected at **every** model turn |
| What happened in past sessions | Episode index formatted on demand |
| What other conversations covered | Pointer-only topic index; content retrieved from the vector store when needed |

The load-bearing detail: long tool outputs in history are **compacted, not dropped** — the same layer that appends messages owns compaction, so the model's view of its own history stays coherent. Inside one task room, deeper chat means *more compression, same core* — the room's context grows smaller over time, not bigger.

## Consequences

- An agent in hour four still carries its task's skeleton in front of it every turn.
- Hallucinated "memories" are structurally suppressed: facts enter only via mechanical extraction, never via the model summarizing itself freely.
- Cross-session experience compounds: new tasks start smarter because past task summaries are one retrieval away.
