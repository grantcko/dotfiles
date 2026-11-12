# Global Codex Instructions

## Skills

At the start of each task, check enabled Notion skills through MCP (`notion_get_enabled_skills`); load and follow relevant skills before acting.

## Computer use

### Run sustained computer work on the machine that owns the app

When working on a VPS, use a T3 agent running locally on Grant's Mac for sustained Mac browser or desktop tasks, such as account setup, multi-step authenticated workflows, and visual verification. Keep repository coding and tests on the machine that owns the checkout. Grant authorizes starting a scoped Mac-local support thread for this purpose without asking again; this is standing permission for cross-machine computer work, not general parallel coding or review delegation. It is a specific exception to generic work-yourself or no-delegation defaults. Honor higher-priority runtime restrictions and an explicit current-task prohibition on a Mac-local helper.

Discover the linked Mac with `t3_environment_links`, and pass its `environmentId` to the relevant T3 tools. Prefer scoped delegation to that environment when supported; otherwise launch a Mac-local T3 support thread. Do not assume an SSH connection creates a local agent or that the Mac has working browser tools. Reuse a suitable task-owned support thread when available, preserving its account and session context.

Give the Mac agent the exact task, account, permitted actions, constraints, verification criteria, and stopping conditions. It must use the applicable Access skills and available local browser/desktop/device tools, preserve unrelated sessions, and keep secrets in the connected 1Password vault. A support thread inherits only the authority already granted to the task; creating it does not grant broader vault access, purchases, payments, customer changes, or publication.

Keep the parent responsible for coordination. Link the support thread immediately, read its result, verify the requested outcome, and report completed actions, evidence, and remaining blockers. Escalate human-only CAPTCHA, login, and approval steps through the supported user-input or private-secret tools. Follow T3's returned waiting instructions; do not poll a running delegate or start duplicate work.

SSH remains appropriate for brief diagnostics, builds, file transfer and port forwarding. Avoid sustained browser/desktop automation through nested SSH, AppleScript or JavaScript commands. If a Mac-local thread or its required tools are unavailable, report the exact limitation before using an authorized fallback; do not silently resume a long SSH automation sequence.

Work in the background without taking focus. Do not activate or raise apps or browser windows, switch Spaces, or use headed/physical input unless Grant explicitly asks for foreground interaction.

Prefer native CUA (`cua_repl`) for macOS accessibility-tree and screenshot inspection. Use `agent-desktop` for background semantic actions and as the fallback when native CUA is unavailable or fails. Do not assume native actions are better based only on inspection tests. For websites, use the browser workflow.

## Browser use

Use `agent-browser` with a named task session and the configured disposable Brave Work-profile launcher, headless by default. The source profile is read-only; never automate it directly. Keep browser sandboxing and certificate checks enabled. Follow the Browser automation skill for launcher details, Chrome exceptions and authentication.

At task end, close every automation browser session created or used for that task and verify its session and browser processes have exited. Preserve unrelated sessions and Grant's personal browser. Leave task automation open only when Grant explicitly asks.

## Authentication and phone use

Use the canonical connected 1Password vault for authorized credentials, including cards and the iPhone passcode. Reuse standing authorization and complete authorized authentication autonomously; do not ask again for access already granted. Never print or save secret values in chat, instructions, scripts or logs.

Prefer the connected 1Password plugin for all vault access. Avoid invoking the `op` CLI directly whenever the plugin can handle the task. Do not add CLI calls as a convenience fallback; use the CLI only when a required capability is unavailable through the plugin.

Use `agent-device` for phone/mobile interaction unless it cannot complete the task or a higher-priority instruction requires another tool. Load the iPhone automation and recovery skill before phone work, including signing and XCTest bootstrap recovery.

Grant authorizes the connected iPhone's saved device passcode as the normal fallback when Face ID is unavailable during authorized phone work. Verify Apple's device-passcode prompt and the matching device before entry; never use that code for an app-specific PIN. Do not ask again.

## Terminals and local servers

When Grant needs to run a command, inspect live tmux sessions and clients, then open a clearly named window in his active attached session with the exact command typed but unexecuted unless he asks you to start it. Close the tab when finished unless still needed.

Start local development servers in the project's Herdr space, in a tab named `server`, for auditability. Use the TASTY tmux tab with the named `tasty` Herdr session; close both without asking when Grant requests TASTY be ejected.

## Files and VPS access

For file and drive searches, check `/Users/granthall/MasterDrive` early and load Master Drive file search. Treat manifests as potentially stale; verify final source paths and destructive actions against the live mounted volume when possible.

Remove files with `trash` rather than permanent deletion; install it with brew if needed.

For `~/bin/codex-tunnel`, load Mac/VPS tunnel access. Use the smallest permission level, verify live ports/health, and confirm Grant intended full Mac account access before relying on `files-rw`. Do not inspect vaults, browser profiles, SSH private keys, tokens or unrelated personal folders without explicit authorization.
