# Google host adapter

Checked 2026-09-18. DUB's `google` provider selects **Gemini CLI (`gemini`)**.
Google also ships **Antigravity CLI (`agy`)**; these are distinct harnesses,
not interchangeable executable names. No claim that either replaces the other.
Use `dub doctor` for the locally detected version; documentation is not a local
installation or entitlement check.

## Gemini native DUB

Install under `~/.gemini/skills/do-it-up-bro/` or project
`.gemini/skills/do-it-up-bro/`. `.agents/skills/` aliases also work. Skill activation
can require consent. [Skill management](https://geminicli.com/docs/cli/using-agent-skills/)

Use focused native subagents for scouting and independent review. Custom agent
Markdown goes in `.gemini/agents/` or `~/.gemini/agents/`; fields include `model`,
`tools`, `max_turns` (default 30), and `timeout_mins` (default 10). Subagents have
separate contexts but cannot spawn other subagents, even with wildcard tools.
No fixed concurrency ceiling was verified; keep fan-out bounded by useful axes
and available quota. [Subagents](https://geminicli.com/docs/core/subagents/)

Choose the root model using `--model`; use inherited defaults unless the user
requests a supported model. Thinking settings exist in model configuration
(`thinkingBudget` / `thinkingLevel`), not a portable `--effort` flag. Resolve
semantic scout/judge tiers against available models instead of freezing names.
[Configuration](https://geminicli.com/docs/reference/configuration/)

For concurrent writers use separate worktrees; native worktree support is
experimental. Context isolation alone does not isolate files.
[Worktrees](https://geminicli.com/docs/cli/git-worktrees/)

Documented headless shape: `gemini -p PROMPT --output-format json`. JSON includes
response/stats/error; `stream-json` adds init model and per-model usage events.
[Headless](https://geminicli.com/docs/cli/headless/)
Cached Google login works headlessly and can use the associated Pro/Ultra account;
without cached credentials another documented auth method is needed. Entitlements
and usable quota remain unknown until an authorized live call.
[Authentication](https://geminicli.com/docs/get-started/authentication/)

**Do not use headless Plan Mode as a read-only security boundary:** it can approve
exit automatically and transition to YOLO.
[Plan Mode](https://geminicli.com/docs/cli/plan-mode/)
Likewise `--allowed-tools` grants approval rather than restricting the toolset.
Policy restrictions require careful precedence validation: supplemental
`--admin-policy` is ignored when standard system policy files exist, and workspace
policies are documented as nonfunctional. DUB must fail closed if it cannot verify
its restriction. Consequently **Google live federation is gated off in v0.1**;
native skill installation and discovery remain supported. There is no unsafe
override. [Policy engine](https://geminicli.com/docs/reference/policy-engine/)

## Antigravity native alternative

Use `agy` directly, with the canonical skill at workspace `.agents/skills/` or
`~/.gemini/antigravity-cli/skills/` (not Gemini CLI's directory).
[Skills](https://antigravity.google/docs/skills)
Map parallel DUB work to `invoke_subagent`; `define_subagent` creates transient
roles. Workspace modes include inherit, branch/worktree, and share. Custom agents
support clean contexts and model tiers; `/teamwork-preview` is plan-dependent.
[Subagents](https://antigravity.google/docs/subagents?tab=cli)
Its documented headless command is `agy -p PROMPT --output-format json`, with
`--model` and `--effort low|medium|high`, cached login, structured events, and
`--print-timeout`. Workspace file writes are allowed by default; shell approvals
can be denied while the process still exits successfully. Inspect result status
and diagnostics, not exit code alone. DUB v0.1 does not auto-substitute `agy` for
`gemini` in federation. [Headless](https://antigravity.google/docs/cli/headless/)
