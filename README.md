# Engrix Agent — Architecture Portfolio

**Engrix Agent** is a self-hosted, single-owner AI engineering agent — a production system
that plans, executes, and verifies real work on a Windows machine: it browses the web,
controls Android devices, runs terminal commands, edits codebases, manages VPS boxes,
sends email/Telegram messages, and records its own screen as documentation.

This repository is the **architecture portfolio**: it documents how the system is built
and why. The source itself lives in a private repository; what you read here is the
distilled engineering.

> Owner & sole engineer: Ariel · Stack: Python 3.12 (FastAPI) · React + TypeScript (Vite) ·
> Electron · SQLite + Qdrant · FFmpeg

## What makes this system interesting

- **~425 registered tools across 22 categories**, routed to the LLM through a single
  registry with one wiring protocol — adding a tool touches 4 known files, never more.
- **Provider-agnostic model layer**: every LLM provider (multiple vendors, OpenAI-compatible
  or native) is one YAML file. Adding or re-prioritizing a provider requires zero code
  changes, including per-model reasoning-effort options surfaced in the UI.
- **Layered memory**: SQLite holds conversation history, verified facts, task positions,
  and episode summaries; Qdrant adds semantic recall — both behind a one-way
  `agent → memory → storage` import boundary.
- **The agent improves its own host**: every feature you see in `docs/` (artifact panel,
  desktop copilot, screen recording, tool registry) was built by the agent running on
  this engine, under a strict "never restart production without owner consent" rule.
- **Migration case study**: a live monolith (god files of 3.5k+ lines) was restructured
  into a src-layout package (`backend/src/engrix/`) in 25 incremental, verified waves —
  with zero production downtime and a green test suite at the end.

## Documentation index

| Document | Contents |
|---|---|
| [docs/architecture.md](docs/architecture.md) | System layout, request lifecycle, package layering, data flow |
| [docs/tool-system.md](docs/tool-system.md) | The 4-point tool wiring protocol, registry, routing, verification gates |
| [docs/design-decisions.md](docs/design-decisions.md) | Distilled ADRs: the "why" behind every major choice |

## Repository layout (of the private source)

```
engrix-agent/
├── backend/
│   ├── src/engrix/          # the engine package (src-layout)
│   │   ├── main.py          # FastAPI app, WebSocket chat, REST API
│   │   ├── agent/           # orchestration loop, model clients
│   │   ├── tools/           # ~22 tool category packages
│   │   ├── storage/         # SQLite infra + schema
│   │   ├── memory/          # domain memory (history, facts, episodes)
│   │   ├── routing/         # hint/skill routers, categories
│   │   ├── personality/     # prompts & persona layers
│   │   ├── formatting/      # rich message rendering
│   │   └── bootstrap/       # wiring & lifespan
│   └── tests/               # pytest suite (green)
├── frontend/                # React + TS (Vite) — served by the backend
├── desktop/                 # Electron always-on-top copilot shell
├── yaml/                    # one YAML per LLM provider (single source of truth)
├── skills/                  # disk-loaded skill library (vendor, not packaged)
└── exports/                 # user-facing generated artifacts
```

## License & contact

Architecture documentation only. The engine is private and not distributed.
Reach the owner via GitHub for questions.
