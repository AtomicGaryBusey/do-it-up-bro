# Kimi Code host adapter

Checked 2026-09-18. Current official Kimi Code CLI uses `kimi`; `--version`
reports the local build. Current docs describe the successor's `.kimi-code`
data root. Older `kimi-cli` releases can have incompatible flags and `.kimi`
directories; inspect help and upgrade manually rather than guessing compatibility.
[Command reference](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command)

Install at `~/.kimi-code/skills/do-it-up-bro/` (or `$KIMI_CODE_HOME/skills/`) or
project `.kimi-code/skills/do-it-up-bro/`. Generic `.agents/skills/` is also
supported. The canonical directory-style `SKILL.md` is compatible. Inline skills
load on demand; `/skill:do-it-up-bro` is an explicit fallback invocation.
[Skills](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html)

Map bounded native DUB work to `Agent`: isolated context, foreground/background
execution, resumption, and `coder`, `explore`, `plan` profiles. Built-in children
cannot delegate further; custom allowlists can opt into deeper delegation. File
isolation is separate: use explicit worktrees for writers; no automatic worktree
flag was verified. Agent Markdown tool lists are enforced before execution.
[Agents](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents)

Map homogeneous, independently scoped campaign leaves to `AgentSwarm`. It accepts
a template and items, supports up to 128 total children, and aggregates results.
Only one swarm tool call is allowed per model response. Configure a positive
`KIMI_CODE_AGENT_SWARM_MAX_CONCURRENCY` to cap concurrency; the documented default
ramps from five workers without an upper cap. Do not confuse the 128-item limit
with concurrency. `Agent` and swarms can select a configured secondary-model pool
alias or `primary`; otherwise children inherit the main model. Resume preserves
the child's model. [Tools](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/tools.html)

Configure model pools through `[secondary_model.models]`; ordinary agent and swarm
timeouts use separate configuration. Print mode defaults these timeouts to zero,
so an external deadline matters. No generic CLI reasoning-effort flag was verified;
do not encode a fabricated knob or model frontmatter in custom agents.
[Configuration](https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/config-files)

Federation must use the bundled `readonly-agent.md` through an absolute
`--agent-file` path. It permits only Read/Grep/Glob and excludes shell, writes,
MCP, and delegation. Current headless shape is
`kimi --agent-file PATH -p PROMPT --output-format stream-json`.
Bare `-p` uses auto permissions and cannot combine with `--plan`, `--auto`, or
`--yolo`; it is unsafe to
treat a read-only prompt as enforcement. JSONL exposes messages/tool calls, not a
guaranteed observed model/effort/usage schema; leave unavailable ledger fields null.
Cached OAuth from `kimi login` is reused. Do not export session debug archives to
collect telemetry: they can contain credentials. See the command and agent docs
above. Restricted federation deliberately has less capability than native DUB.

`--agent-file` accepts one file and cannot combine with `--agent`, `--session`,
or `--continue`. DUB's model override is a configured model alias, not an assumed
raw vendor model ID. `--skills-dir` replaces automatic discovery rather than
adding a directory; DUB does not use it. The public command reference above is
the documentation source; installed help also points to Moonshot's GitHub Pages.

Compatibility requires local help advertising `--agent-file` and `stream-json`;
an executable named `kimi` alone does not establish successor-CLI compatibility.
Forward `KIMI_CODE_HOME` for workers so relocated cached login and configuration
match the skill install. `kimi doctor` is an optional local configuration check,
not authentication proof. End-to-end subscription execution needs a separately
opted-in live smoke test; do not automatically consume quota during diagnostics.
