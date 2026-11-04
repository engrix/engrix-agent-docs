# System Overview

## The question

> *What happens when an agent like this runs for eight hours straight — does it hold together, or does every piece eventually need babysitting?*

That question drove every decision on this page. A one-off demo script is easy; a system that still makes correct choices at hour eight — with a compressed context, dozens of opened tool drawers, and three side quests from earlier in the session — is an architecture problem.

Engrix Agent is a local-first engineering agent: one FastAPI backend process, one React frontend served by that process, and an optional Electron shell that reuses the same frontend as an always-on-top desktop copilot. It runs on Windows — the deployment target is the owner's machine — and every hard number on these pages is measured from the live source tree by `scripts/verify_docs_claims.py`, which fails when a document drifts from the code.

## Why the folders are separated

The engine is a Python package (`engrix/`) with a strict one-way layering. Each folder answers one question, and higher layers may depend on lower ones — never the reverse:

```
engrix/
├── config.py        configuration & paths (depends on nothing)
├── paths.py         filesystem layout, one accessor per data location
├── storage/         INFRASTRUCTURE: SQLite connections, schema, migrations
├── memory/          DOMAIN: what the agent "knows" (history, facts, tasks)
├── knowledge.py     semantic retrieval (vector store)
├── formatting/      output rendering
├── curation/        knowledge curation pipeline
├── routing/         category drawer state & routing hints
├── personality/     persona & prompt assembly
├── tools/           the executable capability surface
├── ml/              online learning & ranking
├── agent/           the orchestration loop (planning, execution, verification)
├── subagent/        child runs: contracts, evidence, reports, lifecycle
├── publication/     the artifact store behind the panel
├── evaluation/      capture engine — what the agent actually saw and did
├── transport/       HTTP routes and the WebSocket hub
├── app/             conversation orchestration, approvals, request models
├── bootstrap/       wiring: connects everything at startup
└── main.py          FastAPI entry point (app assembly only)
```

The separation is not aesthetics — it is the maintenance contract:

- **`agent/` may call `memory/`, never `storage/` directly.** Storage details cannot leak into orchestration logic.
- **`memory/` owns the domain, `storage/` owns the mechanics.** Swapping a storage engine means touching one layer, not twenty call sites.
- **`transport/` owns HTTP and sockets; `app/` owns what a turn means.** A route handler parses a request and delegates — it never contains agent logic.
- **`bootstrap/` is the only place that knows how pieces connect.** Every other module can be imported and tested in isolation.

## One process, many surfaces

The backend serves the built frontend itself, so a deployment is one process, one port, one version:

```mermaid
flowchart LR
    subgraph clients["Clients"]
        B["Browser — full workspace"]
        D["Electron copilot — always-on-top"]
    end
    subgraph engine["One process (port 8420)"]
        M["FastAPI main.py"]
        TR["transport/ routes + ws_hub"]
        APP["app/ conversation"]
        A["agent/ orchestration loop"]
        T["tools/ 25 drawers"]
        SA["subagent/ child runs"]
        MEM["memory/ + storage/ + knowledge/"]
    end
    subgraph externals["Reach"]
        GH["GitHub"]
        BR["Browsers"]
        VP["VPS over SSH"]
        DV["Android + desktop"]
        EM["Email + Telegram"]
    end
    B --> M
    D --> M
    M --> TR
    TR --> APP
    APP --> A
    A --> T
    A --> SA
    A --> MEM
    T --> externals
```

The browser gets the full workspace; the Electron copilot loads the identical build with a query flag (`?ui=desktop`), so all UI modes share one codebase and one dist.

## The transport split, and why it happened

`main.py` used to be a single file holding every route. It is now app assembly only: it creates the FastAPI instance, mounts static directories, and includes one router per domain. The routes themselves live in `transport/routes/`, one module per domain — sessions, filesystem, publications, realtime, subagents, recording, and so on.

This is worth stating plainly because it is the difference between a document that describes an intention and one that describes a system: the split is not planned here, it is shipped. `main.py` keeps a single route of its own — the catch-all that serves the frontend — and everything else arrives through `app.include_router()`.

## Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, WebSocket chat streaming |
| Frontend | React + TypeScript + Vite |
| Desktop | Electron (frameless, always-on-top copilot window) |
| Storage | SQLite (WAL) + Qdrant (local embedded or server mode) |
| Packaging | Portable pack: source + venv + frontend build, single `engrix.exe` launcher |

## Alternatives considered

- **Microservices** (backend split into services) — rejected: the agent needs shared in-process state (registry, drawer state, memory) and single-machine deployment; splitting buys distributed-systems problems no one here has.
- **PostgreSQL first** — rejected for now: a single writer with embedded SQLite in WAL mode covers the load; the storage layer isolates the swap decision (see [dual storage](../decisions/005-dual-storage.md)).
- **Vector-only memory** — rejected: semantic recall cannot reproduce exact facts; mechanical extraction and vector search solve different modes of forgetting, so both stay.

Next: [Tool System](tool-system.md) — the part that makes an agent able to drive hundreds of tools coherently.
