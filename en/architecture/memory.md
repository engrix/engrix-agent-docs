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
    SUM -.->|"next session"| EP
```

The design principle: **the deeper the chat, the more it compresses — but the core stays.** An agent in hour four of a session still has the task's skeleton in front of it every single turn.

## Storage underneath

The infrastructure layer (`storage/`) holds a single SQLite connection (WAL mode, foreign keys, busy timeout, guarded write-lock cursor) with schema versioning and migrations. Domain code never touches raw SQL wiring — one layer owns the mechanics, one owns the meaning. Concurrency is solved by staying single-writer: WAL lets readers proceed while one write lock is held, and the deployment rule is one engine process per database — parallel instances share a server-mode Qdrant, never the same SQLite file. Semantic recall rides a separate vector store (Qdrant) that can run embedded for a single instance or in server mode for parallel instances.

Next: [Interfaces](interfaces.md) — four ways to talk to the same engine.
