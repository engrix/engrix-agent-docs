# Interfaces & Reach

## The question

> *How do you keep four different UI surfaces identical — without paying four times the frontend maintenance?*

The wrong answer is four apps. The right answer is one app rendered at four sizes, with only the desktop wrapper being genuinely native code.

**In one line:** one frontend build, four renderings of it; all four reach the engine the same way, and the desktop shell adds window-level features (always-on-top, global hotkey, tray, capture exclusion) without touching the app itself.

## Four surfaces, one engine

The same chat engine is reachable through four UI modes, all rendered from one frontend build:

| Mode | Form |
|---|---|
| **Full** | Complete workspace: chat, file explorer, artifact canvas, review diffs |
| **Panel** | 380px floating copilot panel over the workspace |
| **Bubble** | A single brand-mark button with a live status dot |
| **Desktop** | Frameless Electron window (400×640), always-on-top *above other applications*, global hotkey, tray icon, excluded from screen capture |

```
one build (frontend/dist)
    │
    ├─ full   workspace   ← browser, default route
    ├─ panel  380px       ← same route, ui-mode flag
    ├─ bubble button      ← same route, ui-mode flag
    └─ desktop window     ← Electron shell loads dist with ?ui=desktop
                             (frameless · always-on-top · global hotkey · tray)
```

The desktop shell is a thin layer: it loads the identical frontend build with a `?ui=desktop` flag and never duplicates or spawns its own engine — it detects an already-running engine via health check and connects. One codebase, one dist, four surfaces.

## What the agent can reach

The tool inventory (details in the [tool system](tool-system.md)) gives the agent real reach across environments:

- **Local machine** — sandboxed terminal, filesystem, persistent Python kernel, LSP semantic code tools, debugger, test runner
- **Browsers** — dual-engine: an anti-detection Firefox fork for automation/multi-account work, and the owner's real Chrome via CDP when a task needs the owner's actual logged-in sessions (with protected-profile guards)
- **Devices** — full ADB Android control (tap/swipe/type/install/scrcpy) and native Windows desktop control (see/click/type in any window, UI Automation, pixel template matching)
- **Remote** — SSH-based VPS administration: shell (incl. persistent PTY), full remote filesystem, file transfer, systemd, port forwarding
- **Communication** — Telegram bot channel management + personal-account access, Gmail API and IMAP email
- **Security research** — a recon→scan→exploit pipeline, OSINT, threat intel, binary reverse engineering
- **Git/GitHub** — local repo operations and full remote GitHub administration

## Deployment

A portable pack bundles source, virtual environment, and the frontend build behind a single `engrix.exe` launcher — drop the folder on any path on the machine and double-click. The engine itself stays a normal local process (it needs real hardware access: cameras, ADB, desktop control), while supporting services run in Docker Compose.
