# ADR-006 — Compression That Keeps the Core (Memory Design)

**Status:** Accepted

> *The question this ADR answers:* **What if compression erases exactly the detail the task needs later?**

## Problem

The original requirement was blunt:

> *"An assistant that can do anything, run anywhere, and never lose context."*

Chat history alone fails at exactly this. It either bloats until the model loses the beginning in the middle, or it gets cut and the agent forgets its own task. And forgetting is not one problem — it is at least five: forgetting facts, forgetting the current step, forgetting what was already verified, forgetting past sessions, forgetting what sibling conversations covered.

## Solution

Treat "never forget" as a set of **layered stores**, each owning one kind of forgetting — all designed around the same principle: *compress aggressively, but always keep the core.*

| Kind of forgetting | Store |
|---|---|
| Facts stated in-session | Mechanical fact extraction (zero hallucination, stopword-filtered) |
| Where am I in the task | A task-position block injected at **every** model turn |
| What was already checked | Verification state, with freshness — a conclusion cannot outlive its evidence |
| What happened in past sessions | Episode index formatted on demand |
| What other conversations covered | Pointer-only topic index; content retrieved from the vector store when needed |

The load-bearing detail: long tool outputs in history are **compacted at read time, not deleted**. The same layer that appends messages owns the caps applied when history is read for the model — so the model's view stays coherent while the database keeps the full record the UI can still show. Inside one task room, deeper chat means *more compression, same core*: the room's context grows smaller over time, not bigger.

The verification store is the part most memory designs skip. An agent that remembers a conclusion but not the evidence behind it will confidently repeat a stale conclusion — so the record of *what was checked* is treated as memory too, with a staleness signal rather than a permanent tick.

## Consequences

- An agent in hour four still carries its task's skeleton in front of it every turn.
- Hallucinated "memories" are structurally suppressed: facts enter only via mechanical extraction, never via the model summarizing itself freely.
- Cross-session experience compounds: new tasks start smarter because past task summaries are one retrieval away.
- The cost of read-time compaction is that two views of the same session exist (full record, compacted model view). That is deliberate — both are truthful, at different fidelities — but it means any debugging of "what the model actually saw" must read the compacted view, not the database.
