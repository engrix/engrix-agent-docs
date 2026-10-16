# ADR-004 — Providers as Configuration, Not Code

**Status:** Accepted

> *The question this ADR answers:* **What if the owner wants to add a provider at 2 a.m. without touching code?**

## Problem

Model providers change constantly: new endpoints, new model names, new auth schemes, new reasoning-effort options. Hardcoding providers means every provider change is a code change — a code review, a redeploy, a risk to the whole engine just to rename an endpoint.

## Solution

Every provider is a **YAML file**: base URL, auth flow, model list, and per-model capabilities (including nested reasoning-effort options) live entirely in configuration. The engine loads the registry at startup and exposes the result to the UI through one API — the frontend never reads the config files itself, so there is exactly one source of truth.

## Consequences

- Adding or retiring a provider = editing a YAML file, zero code changes.
- The UI's model picker and the engine's request path can never disagree — both read the same registry.
- Per-model options (like reasoning effort levels) are data, not UI code — the picker renders whatever the YAML declares.
