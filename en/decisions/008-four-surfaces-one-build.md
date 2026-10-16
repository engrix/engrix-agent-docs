# ADR-008 — Four Surfaces from One Build

**Status:** Accepted

## Problem

An agent that lives on your desktop needs contradictory UIs: a full workspace for deep work, and a tiny always-available companion that floats above other applications. Building these as separate apps (web app + desktop app) means duplicated frontend logic, doubled maintenance, and surfaces that drift apart.

## Solution

**One frontend build, four modes.** A UI-mode store selects the surface at runtime:

| Mode | Form |
|---|---|
| Full | Workspace: chat, explorer, artifact canvas, review diffs |
| Panel | 380px floating panel over the workspace |
| Bubble | Single brand button with live status dot |
| Desktop | Frameless Electron window, always-on-top, tray + global hotkey |

The Electron shell is deliberately thin: it loads the **same served build** with a `?ui=desktop` query flag (explicitly winning over any persisted preference, and never persisting itself), and it never duplicates the engine — a health check detects the already-running engine and connects to it.

## Consequences

- A feature built once (streaming chat, file approval, uploads) is available on every surface the same moment it ships.
- The desktop window can behave like a real copilot — *above* other apps, silent spawn without focus stealing, excluded from screen capture — while containing zero business logic of its own.
- The one real constraint: the desktop shell needs the engine served locally, which the one-process architecture (ADR-001) guarantees anyway.
