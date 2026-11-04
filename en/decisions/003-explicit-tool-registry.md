# ADR-003 — An Explicit, Verified Tool Registry

**Status:** Accepted

> *The question this ADR answers:* **What silently breaks when someone adds a tool and forgets one wiring point?**

## Problem

Tool registration by convention fails silently. The historical evidence: **five separate incidents** where a whole tool category vanished from the agent's reach because a single package import was forgotten. Nothing crashed; the tools just quietly stopped existing for the model. Silent disappearance is the worst failure mode an agent can have — you only notice when the agent fails a task it should have aced.

## Solution

Registration is **explicit at four fixed points**, and a **live parity checker** turns the contract into a test:

1. The tool module defines functions with model-facing docstrings.
2. The category definition lists the tool names.
3. The router knows the category.
4. The package `__init__` imports the module for side-effect registration.

The parity checker (`scripts/check_registry_sync.py`) compares all four layers against the live registry at runtime and reports: ghosts (defined but never registered), missing tools, uncategorized strays, and duplicates. `scripts/check_contracts.py` extends the same discipline to category literals, subdomains, and the always-on set, and ships a self-test that proves the gate is capable of failing — a gate that has never been seen to fail is not a gate.

## Consequences

- "Why can't the agent use X?" became a checkable question with a one-command answer instead of an archaeology dig.
- The historical five failures are structurally impossible to repeat silently — they would light up the parity check the moment they happen.
- New tools require touching four points, which sounds heavier — but the discipline replaced repeated debugging sessions that each cost more than the ceremony.

## The part that took longer to learn

The four-point protocol catches a *forgotten* wiring point. It does not catch a **gate that measures nothing**. Two gates in this repository spent months reporting success while scanning zero files: one because a duplicate quiet flag suppressed the summary line it was parsing, another because its path pattern never matched the layout the repository actually uses.

The lesson generalizes beyond this project: *"no findings" and "scanned nothing" are identical when the only output is an exit code.* Both gates now treat an empty scan as a failure, and the rule is written down as a known issue with its own verification command.
