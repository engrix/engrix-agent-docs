# Engrix Agent — Architecture Portfolio

**Engrix Agent** is a self-hosted, single-owner AI engineering agent that plans, executes, and verifies real work on a real machine: ~425 registered tools across 22 categories, layered memory that survives context compression, and four UI surfaces — from a full workspace to an always-on-top desktop copilot.

## See it run

An unedited screen recording of one real task (research across three source types → synthesis → terminal execution → Excel deliverable), captured by the agent's own screen-recorder:

[![Engrix Agent — live task demo](assets/demo-preview.jpg)](assets/demo.mp4)

▶ **[Watch the demo video](assets/demo.mp4)** — 8m34s, no audio, 1× speed. Recorded by pressing the in-app record button; that button is itself one of the agent's tools.

## Origin

This project did not start as an architecture exercise. It started with three questions:

> *"How do I make my work easier? How do I work more efficiently? How do I cut my workload by ~80%?"*

The answer became an assistant that can do everything, run anywhere, and never lose the thread of what it is doing — even after hours of continuous work inside one task.

## Status

Running in daily production on the owner's machine. What is shipped, what is partial, and what is still on the drawing board is stated honestly in the [roadmap](en/roadmap.md) — nothing on this page is aspirational.

## Documentation

Two languages, same content:

| Section | English | Indonesian |
|---|---|---|
| System overview, tool system, memory, interfaces | [en/architecture/](en/architecture/overview.md) | [id/architecture/](id/architecture/overview.md) |
| Design decisions (ADR, problem → solution) | [en/decisions/](en/decisions/001-one-process-architecture.md) | [id/decisions/](id/decisions/001-one-process-architecture.md) |
| Roadmap & honest status | [en/roadmap.md](en/roadmap.md) | [id/roadmap.md](id/roadmap.md) |

Start here if you only read one page: **[the tool system](en/architecture/tool-system.md)** — how an agent drives hundreds of tools without drowning in them.
