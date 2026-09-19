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

Use native `spawn_subagent` for bounded DUB work and
`get_command_or_subagent_output` for background results. The installed first-party
1.0.34 guide documents depth one: the root spawns all scouts and reviewers.
The public page says `explore`/`plan` cannot execute shell; the installed guide
says they can. Treat these names as non-editing roles, not execution boundaries.
Use explicit read/search restrictions when execution is forbidden.
Custom definitions belong in `.grok/agents/` or `~/.grok/agents/`.
[Subagents](https://docs.x.ai/build/features/subagents)
Route child models with `[subagents.models]`; root `--model` and `--effort` select
supported runtime controls. The installed guide documents role/persona defaults
for model, `reasoning_effort`, and isolation. Preserve inherited settings when
capabilities are unavailable. [Settings](https://docs.x.ai/build/settings/reference)

For DUB campaigns, ask the host to author and smoke-check a native workflow with
independent phases and skeptical verification. Saved workflows reside in
`.grok/workflows/` or `~/.grok/workflows/` and expose slash commands. Officially
described run budgets are 128 agents, up to 1,024 for large jobs; these are budgets,
not a requirement to spawn that many concurrently. Workflows persist progress.
The installed `/create-workflow` skill is the first-party Rhai API reference:
`agent()`, `parallel()`, `phase()`, `complete()`, `capability_mode`,
`isolation_worktree`, and output schemas. Load it before authoring. Validate
representative paths using the workflow tool's `validate_only: true` before
execution. This is not a shell flag and does not test live tools or every branch.
No prevalidated DUB script ships: no standalone offline validator was found.
Same-process pause/resume is supported; a process exit is not resumable, and
external effects are not exactly-once. Inspect state before repeating work.
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
Use `isolation: worktree` for parallel child writers. `resume_from` continues a
completed child's context; it is not fresh independent verification.
For federation prefer narrow tools plus `--sandbox read-only`. That profile still
allows writes to Grok state and temp, permits reads beyond the project, and does
not block child network on macOS. Managed policy can override CLI selection. This
is not a credential vault or an isolation guarantee for arbitrary hooks/MCPs.
[Sandbox](https://docs.x.ai/build/features/sandbox)
Permission rules and sandboxing solve different problems; do not enable blanket
approval to repair an unattended permission failure.
[Permissions](https://docs.x.ai/build/features/permissions)

## DUB-specific operation

Install with `dub install --provider grok`, then `/do-it-up-bro <goal>` in Grok.
Personal configuration uses `$GROK_HOME` when set. API-key-only credentials are
not forwarded by federation; use a cached login. A Grok-only setup can select
`synthesis_provider = "grok"` without changing the global default.

Federation selects the bundled reader, explicitly allowlists
`read_file,grep,list_dir`, disables subagents and web tools, and bounds turns.
Tool restriction is the principal execution boundary. Do not claim sandbox
enforcement unless the actual host supports it; never substitute blanket approval.

Grok can discover foreign adapters in `.agents/skills` and `.claude/skills`.
Inspect the selected skill source with `grok inspect --json`; do not publish the
whole configuration dump. Preview `dub install --provider grok --dry-run`, then
install the native copy. Use `--force` only for a conflicting copy with backup.
Plugin packaging is an optional distribution path, not required by DUB.
