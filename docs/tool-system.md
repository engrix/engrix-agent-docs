# The Tool System

The defining feature of Engrix Agent: **~425 tools across 22 categories**, each
callable by the LLM, all registered through one protocol.

## The 4-point wiring protocol

Adding a tool family touches exactly four places — this checklist is enforced by
convention because history showed what happens when one point is missed (a forgotten
package import silently made whole categories invisible; it happened five times before
the protocol was written down):

| # | File | Role |
|---|---|---|
| 1 | `tools/<family>/<name>_tools.py` | The `@tool` functions. First docstring line is the model-facing description (English, action-verb first). |
| 2 | `tools/tool_categories.py` | Category entry (+ subdomain map when a category is split into drawers). |
| 3 | `tools/tool_router.py` | Router enum entry so the dispatcher recognizes the category. |
| 4 | `tools/<family>/__init__.py` | Side-effect import that triggers `@tool` registration. |

A tool that skips any point is either invisible to the model or dead on arrival.

## Categories (selection)

terminal · filesystem · kernel (stateful Python) · lsp · code_search · browser
(two engines: hardened Firefox + owner's real Chrome via CDP) · telegram (bot +
user account) · email (API + IMAP) · github · vps (48 tools) · security (recon,
scan, OSINT, intel — vendor binaries kept out of the package) · device_control
(Android via ADB, screen recording) · desktop_control (window-level UI automation) ·
vision · data_export · ops.

## Design rules that keep 425 tools manageable

- **Skip-approval tiers.** Tools are classified by blast radius, not by name:
  read-only probes and local file writes skip the approval round-trip; irreversible
  external actions always require it. Classification lives with the tool, not in a
  distant policy file.
- **Subdomains as drawers.** Large categories (github: 83 tools, vps: 48) are split
  into subdomains so the model can open exactly the drawer it needs — the full tool
  list is never dumped into context.
- **One recorder core, two entry points.** Screen recording is the canonical example:
  a single FFmpeg process owner (`screen_recorder.py`) serves both the LLM tool
  (records to a TTL-cleaned sandbox folder, delivers via Telegram) and a manual REST
  endpoint (records to `exports/`, surfaced as a UI button with a toast + open link).
  Starting from the UI and stopping from chat — or vice versa — is the same recording.
- **Availability guards at import time.** Optional binaries (ffmpeg, external vendor
  tools) are probed once at import; missing dependencies degrade to a clear message
  instead of crashing the boot. A missing optional tool must never take down the engine.
- **Registry verification.** `tools/registry_check.py` counts registered tools,
  categories, ghosts, and duplicates — the parity gate (`before == after`) that every
  structural change must pass.
