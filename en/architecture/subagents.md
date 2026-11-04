# Sub-agents

## The question

> *If a child agent reports "done", how do you know it actually did anything — and what stops it from editing the code you are mid-way through changing?*

That question is why this subsystem exists in the shape it does. A parallel worker that reports success without evidence is worse than no worker at all: it converts "I did not check" into "it is checked", which is the exact failure mode a verification-driven agent is built to avoid.

## What exists

Sub-agents are shipped, not a concept. `subagent/` holds the whole lifecycle, and the module list is the design:

| Module | Owns |
|---|---|
| `contracts.py` | The 13 division contracts — each declares core tools, backup tools, and whether it is read-only |
| `runner.py` | Spawn admission, per-task slot and RAM checks, child execution, stop paths |
| `evidence.py` | Mechanical evidence counting, verdicts, secret redaction, injection filtering |
| `report_form.py` | The fixed-shape report a child must return |
| `artifacts.py` | Where a child's output lands on disk, outside the disposable sandbox |
| `resume_context.py` | Handing a finished child's context back for a follow-up run |
| `watchdog.py` | Deadline enforcement |
| `worktree.py` | Isolated working copies so two children cannot write the same file |

## Divisions: the pool is the contract

A child does not inherit the parent's tools. It gets a **division** — one of thirteen keys — and the division declares which categories the child may reach:

| Division | Shape |
|---|---|
| `coding` | filesystem + git + test runner, plus LSP and terminal as backup |
| `analysis` | read-only: LSP, code search, debugger, read |
| `qc` | read-only: tests, diagnostics, diffs, read |
| `research` | web search, extraction, crawl, KB, past sessions |
| `browser` | navigation, text, click/fill, screenshots, devtools |
| `documents` | PDF, DOCX, XLSX read/create/edit |
| `data` | SQL, CSV/XLSX/PDF export, Python kernel |
| `ops` | VPS shell, systemd, server status, background processes |
| `devices` | ADB control, desktop input and capture |
| `github` | repo read/search/tree/history, PRs, issues, branches, gists |
| `email` | Gmail and IMAP read/send/draft/label |
| `telegram` | bot posting plus personal-account access |
| `design` | HTML/SVG render, image ops, charts, mockups |

Read-only divisions are fenced per tool, not just per category — a read-only child cannot write even if its division happens to contain a category with write tools in it. The fence is enforced at the host, not requested in the prompt.

## Evidence, not self-report

Every child run is measured. `evidence.py` aggregates what the run actually did — how many tool calls, how many of them were verification-type calls, how many succeeded, how many edits landed, how many iterations — and `evidence_verdict()` turns that into a label.

The consequence is blunt and intentional: a child that claims success while its evidence counters are zero is reported as unverified, no matter how confident its prose sounds. Two prefixes carry this into the parent's context: a run with tool calls but no verification evidence, and a read-only run with no verify at all.

Summaries are also filtered before they reach the parent: `redact_secrets()` strips credential-shaped strings, and `_is_injection_line()` drops lines that look like instructions injected by a page the child read. A child that was told by a web page to "report success" is a failed child, not a successful one — and the pipeline treats it that way.

## Lifecycle and limits

Spawning is admission-controlled, not fire-and-forget:

- A global concurrency ceiling (`SUBAGENT_MAX_CONCURRENT`, default 50) across all rooms.
- A **RAM headroom guard** evaluated **per task** inside the loop, not once per call. This detail matters: evaluating it once would turn the guard into "the first batch is always allowed", which is exactly the case where a 50-task batch can take the machine down.
- Tasks beyond either limit are rejected with a reason, not silently queued.
- A watchdog enforces the deadline; children that overrun are stopped and their partial artifacts stay inspectable.
- `resume_context.py` allows continuing a finished child on the same session, with the old run row preserved as an audit trail rather than overwritten.

## What the parent gets back

A fixed report shape, not free-form prose. `report_form.py` defines the fields; the parent reads a structured handback plus the mechanical evidence stats. This is the part that makes parallel delegation usable at all: the parent can compare twenty children without re-reading twenty essays, and it can tell the difference between "this child verified its claim" and "this child wrote confidently".

Next: [Interfaces](interfaces.md) — four ways to talk to the same engine.
