# ADR-003 — An Explicit, Verified Tool Registry

**Status:** Accepted

## Problem

Tool registration by convention fails silently. The historical evidence: **five separate incidents** where a whole tool category vanished from the agent's reach because a single package import was forgotten. Nothing crashed; the tools just quietly stopped existing for the model. Silent disappearance is the worst failure mode an agent can have — you only notice when the agent fails a task it should have aced.

## Solution

Registration is **explicit at four fixed points**, and a **live parity checker** turns the contract into a test:

1. The tool module defines functions with model-facing docstrings.
2. The category definition lists the tool names.
3. The router knows the category.
4. The package `__init__` imports the module for side-effect registration.

The parity checker compares all four layers against the live registry at runtime and reports: ghosts (defined but never registered), missing tools, uncategorized strays, and duplicates. The current live run: **ghost 0, missing 0, duplicates 0** across 425 tools.

## Consequences

- "Why can't the agent use X?" became a checkable question with a one-command answer instead of an archaeology dig.
- The historical five failures are structurally impossible to repeat silently — they would light up the parity check the moment they happen.
- New tools require touching four points, which sounds heavier — but the discipline replaced repeated debugging sessions that each cost more than the ceremony.
