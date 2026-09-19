# Anthropic Claude Code adapter

Checked 2026-09-18. Executable: `claude`; locally observed `2.1.277 (Claude Code)` through `--version`. Features below may be absent in older or policy-restricted installations.

## Discovery

Install DUB at `~/.claude/skills/do-it-up-bro/` or project `.claude/skills/do-it-up-bro/`. Invoke `/do-it-up-bro` or the DUB phrase. Plugin skills use a plugin namespace. The installer copies this adapter into `references/host-adapter.md`. [Skills](https://code.claude.com/docs/en/skills).

## Native mapping

Use the `Agent` primitive for bounded work. Definitions in `.claude/agents/` or `~/.claude/agents/` support `model`, `effort`, background operation, and `isolation: worktree`. Check the starting revision: worktree agents default to the default branch, which may omit the parent's changes. Current nesting defaults to three layers; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` controls depth. The ordinary concurrent default is 20 with `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` override; ultracode is exempt from that limit. Do not hard-code these as DUB targets. [Subagents](https://code.claude.com/docs/en/sub-agents).

Map campaigns with substantial branching to native dynamic workflows when available. These are JavaScript orchestration scripts with agent/parallel/pipeline helpers, saved under `.claude/workflows/` or `~/.claude/workflows/`. Load the host's `/workflow-authoring` guidance before writing one. Workflows retain results for relaunch but require session-aware recovery. A plain `ultracode` keyword in `-p` input does not trigger the interactive keyword behavior. [Workflows](https://code.claude.com/docs/en/workflows).

`--effort ultracode` (since 2.1.203) requests xhigh plus workflow orchestration. Availability depends on model support, effort caps, and enabled workflows. Ordinary effort and per-agent model selection remain useful for smaller work. Resolve semantic DUB roles against the user's available models; keep defaults inherited when unsure. [Model and effort controls](https://code.claude.com/docs/en/model-config).

Teams remain experimental, enabled with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, and support peer messaging and shared tasks. They are interactive-only: `-p` does not spawn teammates. No nested teams; in-process teammates are not restored by resume. Prefer ordinary agents unless peer coordination is useful and teams are already enabled. [Agent teams](https://code.claude.com/docs/en/agent-teams).

## Headless and telemetry

Core invocation: `claude -p --output-format json "<work order>"`; streaming JSON is also documented. `--model`, `--effort`, and `--worktree` are supported. `--tools` restricts built-in tools; `--allowedTools` only grants permission and is not a tool allowlist. MCP tools require separate restriction. DUB must not enable permission bypass to make automation work. [CLI reference](https://code.claude.com/docs/en/cli-reference).

Print mode runs normal agent behavior with structured result output and supports JSON-schema responses. Its permissions still apply. DUB captures output, but does not infer observed model/effort or usage from the requested values; unparsed telemetry is unknown. [Programmatic usage](https://code.claude.com/docs/en/headless).
