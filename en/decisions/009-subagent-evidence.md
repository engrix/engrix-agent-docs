# ADR-009 — Sub-agents Are Judged by Evidence, Not by Their Own Report

**Status:** Accepted

> *The question this ADR answers:* **If a child agent says "done", what in the system disagrees with it?**

## Problem

Parallel workers are attractive for exactly one reason: throughput. They are dangerous for exactly one reason: the parent cannot see what happened. A child returns a summary — model output, generated after the fact, carrying no authority. A confident summary of work that never happened is indistinguishable from a confident summary of work that did, unless something mechanical sits between them.

The naive design ("spawn children, collect their text, trust the text") converts *unverified* into *verified* in one step. For an agent whose entire value proposition is that it checks its own claims, that is not a throughput feature — it is a corruption of the core.

## Solution

Three decisions, each closing one hole.

**1. The tool pool is a contract, not an inheritance.** A child does not get the parent's drawers. It gets a *division* — one of thirteen named contracts, each declaring core tools, backup tools, and read-only status. Read-only divisions are fenced **per tool at the host**, not requested in the prompt, because a prompt-level fence is a suggestion.

**2. Every run is measured.** `subagent/evidence.py` aggregates what the run actually did — tool calls, verification-type calls, successes, edits, iterations — and derives a verdict from the counters. A child with tool calls but no verification carries an explicit unverified marker into the parent's context. A child that produced no tool calls at all is reported as such, not summarized as "completed".

**3. The report shape is fixed.** `subagent/report_form.py` defines the fields. The parent reads a structured handback plus the mechanical stats, so twenty children can be compared without re-reading twenty essays — and so the difference between "verified" and "wrote confidently" is visible in the data, not inferred from tone.

Two filters sit on the way back: `redact_secrets()` strips credential-shaped strings, and injection-line detection drops instructions that arrived from a page the child read. A child that was told by a website to report success is a **failed** child. Treating its output as data rather than orders is the whole point.

## Consequences

- Parallel delegation becomes usable for work whose result the parent will act on, not just for drafts.
- Some children legitimately return no evidence — read-only research runs that only read and synthesize. Those are labelled as unverified-by-design rather than silently passing; the label is honest, not punitive.
- Admission control is part of the same decision: a global concurrency ceiling and a RAM headroom guard evaluated **per task inside the loop**, not once per call. Evaluating it once would turn the guard into "the first batch is always allowed" — which is precisely the case where a fifty-task batch takes the machine down.
- The cost is ceremony: contracts to declare, evidence to count, a report shape to fill. That cost is paid once per subsystem and saves the parent from re-verifying every child's claim by hand.
