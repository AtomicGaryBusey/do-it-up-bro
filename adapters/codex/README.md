# OpenAI Codex adapter

Checked 2026-09-18. Executable: `codex`; locally observed `codex-cli 0.155.1` through `--version`. Availability is installation-specific; run `dub doctor` again on your machine.

## Discovery and invocation

Install DUB in `~/.agents/skills/do-it-up-bro/` or project `.agents/skills/do-it-up-bro/`. Codex scans ancestor project skill directories, accepts symlinked skills, and supports explicit `$do-it-up-bro` invocation. DUB's installer places this adapter at `references/host-adapter.md`. [Official skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Native mapping

Explicitly delegate scouts, independent candidates, and reviewers. Native threads support spawning, follow-up, waiting, and closing; `/agent` exposes CLI threads. Current releases enable subagents by default, but actual session tools govern availability. Custom agents live in `.codex/agents/` or `~/.codex/agents/`. Their `model` and `model_reasoning_effort` fields allow role-specific configuration; unspecified values normally inherit. Resolve DUB roles against available models rather than freezing a model name. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

The concurrency setting is `agents.max_concurrent_threads_per_session`; `agents.max_threads` is a legacy alias. Runtime chooses the unset default. A current documented recursion-depth setting was not established; do not encode older `max_depth` assumptions. Nested delegation is session-capability-dependent, so keep decomposition at the root when unavailable. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

Use disjoint ownership or explicit worktrees for simultaneous writers. Desktop managed worktrees provide separate checkouts; local `codex exec --help` also advertises `--worktree`. Do not infer automatic per-subagent isolation. [Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees).

## Headless and telemetry

Documented core invocation: `codex exec --json --sandbox read-only "<work order>"`. `--model` chooses the root model; `-c 'model_reasoning_effort="high"'` requests compatible effort. JSONL events include completion usage. `--output-schema` constrains final output, and `--output-last-message` saves it. Saved CLI authentication is reused. Git-repository checks apply unless explicitly bypassed for a safe non-repository workspace. [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

DUB v0.1 captures outputs and requested configuration; observed model, effort, and usage remain unknown unless parsed and validated. Read-only shell sandboxing does not establish a universal boundary for configured external integrations. Inspect local policies and connectors before a live run. Campaign mode should checkpoint artifacts and use supported session resume; the adapter does not promise unattended persistence.
