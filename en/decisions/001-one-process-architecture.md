# ADR-001 — One Process Serves Everything

**Status:** Accepted

## Problem

A web UI and its API drift apart when deployed separately: two build pipelines, CORS configuration, version skew between what the frontend expects and what the backend serves, and multi-step deployment for a single-owner product that just needs to work.

## Solution

The FastAPI backend **serves the built frontend itself**. One process, one port, one version — a deployment is a single thing you start. The React app builds into static assets that the engine serves from disk; a browser refresh picks up a new build without touching the engine process.

## Consequences

- Version skew is structurally impossible: the UI you load is the UI this engine serves.
- Adding a UI surface costs nothing operationally — the Electron desktop shell loads the same served build with a query flag.
- One process needs reasonable startup discipline (health endpoints, graceful shutdown), which pays off in the desktop shell and restart tooling anyway.
