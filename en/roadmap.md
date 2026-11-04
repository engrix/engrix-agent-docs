# Roadmap — what is real, what is next

Nothing on this page is dressed up. Each item states what exists today and what does not.

| Item | Status | Where it stands |
|---|---|---|
| Core agent loop, tools, memory | **Shipped** | Daily production use |
| Sub-agents with division-scoped tool pools | **Shipped** | Thirteen divisions, admission control, mechanical evidence per run, resume on a finished child. Read-only divisions fenced at the host |
| 4 UI surfaces incl. desktop copilot | **Shipped** | All four surfaces render from one build; the desktop shell is a thin Electron wrapper (always-on-top, global hotkey, tray, capture exclusion) |
| Screen recording (button + tool) | **Shipped** | In-app button; used to capture this repo's demo |
| Portable pack + backup repos | **Shipped** | `engrix.exe` launcher; GitHub backups |
| Transport split (`main.py` → per-domain routers) | **Shipped** | `main.py` is app assembly only (509 lines, one catch-all route); the other 50 route decorators live in 13 modules under `transport/routes/` |
| Contract gates on tools and routes | **Shipped** | Registry parity, category/subdomain contracts with a self-test, route snapshot, prompt-mirror sync, docs-claim gate |
| Capture engine (evaluation) | **Partial** | `evaluation/capture.py` records what the agent actually saw and did; analysis on top of that capture is not built |
| ML to reduce information gaps | **Partial** | `ml/` online learning exists; the gap-reduction goal below is unfinished |
| Deeper desktop overlay over other apps | **Partial** | Always-on-top copilot ships; richer interaction with host apps does not |
| COM Office as tools (Word/Excel/PPT) | **Not started** | File-level Excel/CSV/PDF export ships today; controlling live Office apps is separate |

## Recently landed

Every number below is measured from the live tree by `scripts/verify_docs_claims.py`, which fails the document when it drifts.

| Change | What it actually means |
|---|---|
| The engine stopped being one giant entry file | `main.py` is now 509 lines holding app assembly and a single catch-all route; the HTTP surface is 50 route decorators spread across 13 domain modules in `transport/routes/` |
| Sub-agents became a real subsystem | `subagent/` holds contracts, evidence, report shape, artifacts, resume, watchdog, and worktrees — the "concept, not started" line from the previous roadmap is gone because the work landed |
| Backend test baseline is green | `349 passed, 13 skipped, 9 xfailed` with no failures. The two subprocess failures that used to be excused as an environment gap are fixed, not documented |
| The claim gates became real gates | A gate that reports PASS while measuring nothing is worse than no gate: the pytest section used to print `0 passed` because a duplicate `-q` suppressed pytest's summary line, and the event-sync section used to scan zero files because its path pattern never matched. Both now fail loudly on an empty scan |

**Still not built:** analysis on top of the capture engine, richer desktop overlay interaction, and COM Office control. Each is stated here until it ships.

## The honest open questions

**Sub-agents — can their output even be trusted?** This was an open question; it now has a working answer, and the answer is mechanical rather than procedural. Every child run carries evidence counters, a verdict derived from them, secret redaction, and injection filtering, and a child that reports success with zero verification is labelled unverified instead of believed. What is *still* open is the arbitration question below the surface: two children editing the same file. Worktrees isolate them, but a merge policy for conflicting edits is a human decision, not something the engine should guess.

**ML — what if frequency-based recommendations create a feedback loop?** The goal is not a "smarter" agent but a better-*informed* one: which tools actually mattered this week, which mistakes keep repeating across sessions. *How it could fail:* if the model keeps being fed "what you already use", it never discovers the better path — so any ranking signal must include outcome quality (did the task succeed), not just usage counts.

**Desktop overlay — how far can "runs above other apps" go?** The copilot already floats above applications. *What if it could read the document you're editing and act inside it?* That is where COM (next item) and desktop-control tools meet — designed together, not bolted on.

**COM Office — why tools and not another integration layer?** Word, Excel, and PowerPoint as first-class tools would let the agent work *inside* live documents (edit a spreadsheet the owner has open) instead of only producing files. Not started; file-level export covers part of the need today.

**Known bugs — why say it out loud?** Several small bugs remain across surfaces. They are tracked and fixed continuously — a portfolio that claims zero bugs is claiming zero usage.
