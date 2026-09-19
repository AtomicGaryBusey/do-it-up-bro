# Grok Build host adapter

Checked 2026-09-18. Official executable: `grok`; inspect local version with
`grok version` (the official repository also documents `--version`). DUB doctor
reports the installed version, not the latest release number.
[CLI reference](https://docs.x.ai/build/cli/reference)

Install DUB at `~/.grok/skills/do-it-up-bro/` or project
`.grok/skills/do-it-up-bro/`. Plugins and user `.agents/skills` are also supported.
**Skill frontmatter `model` and `effort` are accepted but ignored**, and
`allowed-tools` metadata does not enforce permissions.
[Skills](https://docs.x.ai/build/features/skills-plugins-marketplaces)

Use native independent child sessions for bounded DUB work. Built-in `explore`
and `plan` cannot edit or run shell; `general-purpose` has broader access.
Custom definitions belong in `.grok/agents/` or `~/.grok/agents/`.
[Subagents](https://docs.x.ai/build/features/subagents)
Route child models with `[subagents.models]`; root `--model` and `--effort` select
supported runtime controls. No universal per-child effort field or ordinary-agent
concurrency/recursion ceiling was verified. Preserve inherited settings when
capabilities are unavailable. [Settings](https://docs.x.ai/build/settings/reference)

For DUB campaigns, ask the host to author and smoke-check a native workflow with
independent phases and skeptical verification. Saved workflows reside in
`.grok/workflows/` or `~/.grok/workflows/` and expose slash commands. Officially
described run budgets are 128 agents, up to 1,024 for large jobs; these are budgets,
not a requirement to spawn that many concurrently. Workflows persist progress and
can pause/resume. The source reviewed does not define a stable hand-authored
workflow API schema; let the host generate it instead of inventing one.
[Workflows](https://x.ai/news/workflows)
The reusable file format is **Rhai (`.rhai`)**, authored through
`/create-workflow`; `/workflow <name>` accepts optional JSON arguments.
[Modes and commands](https://docs.x.ai/build/modes-and-commands)
The changelog documents `/workflow --agent-budget` and `--effort`, and limits the
workflow tool to root sessions. It also documents `grok usage <session-id>` for
persisted turn token/cost data. DUB does not infer observed telemetry from requested
settings. [Changelog](https://x.ai/build/changelog)

Headless uses `grok -p PROMPT --output-format json`; `streaming-json` is the event
format. `--no-auto-update` suppresses background update checks. Cached local
authentication is usable; do not require an API key when already signed in.
[Headless](https://docs.x.ai/build/cli/headless-scripting)
Browser login and device authentication are documented; a specific subscription's
entitlement is not proven by executable presence.
[Getting started](https://docs.x.ai/build/overview)

For write-heavy native work use `--worktree`; never merge without authorization.
For federation prefer narrow tools plus `--sandbox read-only`. That profile still
allows writes to Grok state and temp, permits reads beyond the project, and does
not block child network on macOS. Managed policy can override CLI selection. This
is not a credential vault or an isolation guarantee for arbitrary hooks/MCPs.
[Sandbox](https://docs.x.ai/build/features/sandbox)
Permission rules and sandboxing solve different problems; do not enable blanket
approval to repair an unattended permission failure.
[Permissions](https://docs.x.ai/build/features/permissions)
