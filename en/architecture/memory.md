# Layered Memory

## The origin problem

The very first question behind this project:

> *"How can the agent never forget context — even inside one long task room, even across tasks?"*

Naive chat history has two failure modes: it bloats until the model loses the beginning in the middle, or it gets truncated and the agent literally forgets what it is doing. Both are unacceptable for an agent that runs hours-long engineering sessions.

## The solution: compress, but keep the core

Memory is a domain layer (`memory/`) with specialized stores, each solving one kind of forgetting:

| Store | Role |
|---|---|
| **Facts (Layer 1)** | Persistently extracted session facts — mechanical extraction only, no model-written facts, with a stopword filter against confabulated entries |
| **History** | Message history with tool-block sanitization and **compaction built in** — long tool outputs are compressed, not the meaning |
| **Task position** | A `TASK_CONTEXT` block injected at every model turn: what task is active, what step it is on, what was decided — the agent always knows what it is doing |
| **Task summaries** | Per-task grade and summary; a room's history grows *smaller*, not bigger, as work progresses |
| **Verification state** | What was actually verified this task, and whether the evidence is still fresh — a claim cannot silently outlive the check behind it |
| **Episode index** | Cross-session digests formatted for the prompt — past experiences are available on demand, not dumped by default |
| **Cross-room topics** | Pointers only — the index lists what other conversations covered; content is retrieved on demand from the vector store |

How the pieces feed one turn of the loop:

```mermaid
flowchart TD
    TURN["model turn starts"]
    TASK["task_position<br/>TASK_CONTEXT block — always injected"]
    HIST["history<br/>compacted messages, tool noise stripped"]
    EP["episode index<br/>past sessions, on demand"]
    TURN --> TASK
    TURN --> HIST
    HIST -->|too deep?| COMP["compaction — compress outputs, keep the skeleton"]
    COMP --> HIST
    EP -.->|"only when relevant"| TURN
    TASK --> PROMPT["assembled prompt"]
    HIST --> PROMPT
    PROMPT --> OUT["model answers"]
    OUT -->|facts worth keeping| FACT["facts store (mechanical extraction only)"]
    OUT -->|task closes| SUM["task summary + grade"]
    OUT -->|tool ran| VER["verification state"]
    VER -.->|"stale?"| TASK
    SUM -.->|"next session"| EP
```

The design principle: **the deeper the chat, the more it compresses — but the core stays.** An agent in hour four of a session still has the task's skeleton in front of it every single turn.

## Compaction is read-time, not destructive

This distinction is the one that makes the design safe: the database keeps the full tool output, and `memory/history.py` applies caps when *reading* history for the model. The stored record is never rewritten to the compressed form. That means the UI can still show the full output the agent actually received, while the model sees a pointer-style summary — the same session viewed at two different fidelities, both truthful.

The window is deliberately bounded: a hard cap on how many tool-bearing turns stay fully intact, and a message limit from `config.conversation.max_messages`. Older turns collapse to their skeleton rather than disappearing entirely.

## Verification state, not just memory

Most memory designs stop at "what was said". This one also stores "what was checked", because an agent that remembers a conclusion but not the evidence behind it will happily repeat a stale conclusion. `memory/verification.py` classifies tool calls by whether they actually verify something, records the event, and can report whether a task's verification is fresh. A plan that was closed without verification is labelled as such instead of being presented as tested.

## Ranking and relevance

Retrieval returns candidates; it does not decide what the model actually sees. A rerank layer reorders retrieved chunks by query relevance (a reranking service over the candidates, with configurable candidate/keep counts and empirically calibrated score thresholds that decide between a confident hit, a weak hit worth flagging, and a clean miss). Weak hits are labelled as weak instead of being presented as solid answers — the agent knows when the evidence is thin.

A small online-learning layer (`ml/`) keeps models that hold learnable state (per-session preference baselines, route selection). It is deliberately modest: its goal is to reduce information gaps — which tools actually get used, which routes prove stable — not to make the agent "smarter".

## What the agent sees each turn

The injected context is not folklore; it is inspectable. Each model turn receives, among other things: a structured task-context block (active task, current step, decisions so far), the compacted message history, and — on demand — digests of past sessions plus pointers to what other rooms covered. Because the assembly is explicit, anything in it can be audited: the agent can quote the exact blocks it received, and a reader can verify each claim against what was actually injected.

## Storage underneath

The infrastructure layer (`storage/`) holds a single SQLite connection (WAL mode, foreign keys, busy timeout, guarded write-lock cursor) with schema versioning and migrations. Domain code never touches raw SQL wiring — one layer owns the mechanics, one owns the meaning. Concurrency is solved by staying single-writer: WAL lets readers proceed while one write lock is held, and the deployment rule is one engine process per database — parallel instances share a server-mode Qdrant, never the same SQLite file. Semantic recall rides a separate vector store (Qdrant) that can run embedded for a single instance or in server mode for parallel instances.

Next: [Sub-agents](subagents.md) — what happens when the agent needs more than one worker.
