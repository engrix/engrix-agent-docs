# Roadmap — what is real, what is next

Nothing on this page is dressed up. Each item states what exists today and what does not.

| Item | Status | Where it stands |
|---|---|---|
| Core agent loop, tools, memory | **Shipped** | Daily production use |
| 4 UI surfaces incl. desktop copilot | **Shipped** | One build, Electron shell included |
| Screen recording (button + tool) | **Shipped** | In-app button; used to capture this repo's demo |
| Portable pack + backup repos | **Shipped** | `engrix.exe` launcher; GitHub backups |
| Sub-agents helping the main agent | **Concept** | Not started — open design questions below |
| ML to reduce information gaps | **Partial** | `ml/` online learning exists; the gap-reduction goal below is unfinished |
| Deeper desktop overlay over other apps | **Partial** | Always-on-top copilot ships; richer interaction with host apps does not |
| COM Office as tools (Word/Excel/PPT) | **Not started** | File-level Excel/CSV/PDF export ships today; controlling live Office apps is separate |

## The honest open questions

**Sub-agents — can their output even be trusted?** *What if a sub-agent edits code while the main loop is mid-task — who arbitrates conflicting writes?* The working answer: start read-only (research, verification, drafting), earn write access per trust tier, and make every sub-agent write land through the same approval gates the main agent uses. Nothing is built yet.

**ML — what if frequency-based recommendations create a feedback loop?** The goal is not a "smarter" agent but a better-*informed* one: which tools actually mattered this week, which mistakes keep repeating across sessions. *How it could fail:* if the model keeps being fed "what you already use", it never discovers the better path — so any ranking signal must include outcome quality (did the task succeed), not just usage counts.

**Desktop overlay — how far can "runs above other apps" go?** The copilot already floats above applications. *What if it could read the document you're editing and act inside it?* That is where COM (next item) and desktop-control tools meet — designed together, not bolted on.

**COM Office — why tools and not another integration layer?** Word, Excel, and PowerPoint as first-class tools would let the agent work *inside* live documents (edit a spreadsheet the owner has open) instead of only producing files. Not started; file-level export covers part of the need today.

**Known bugs — why say it out loud?** Several small bugs remain across surfaces. They are tracked and fixed continuously — a portfolio that claims zero bugs is claiming zero usage.
