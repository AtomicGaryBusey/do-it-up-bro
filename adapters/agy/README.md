# Google Antigravity CLI adapter

Checked 2026-09-18. Executable: `agy`. DUB uses an explicit `agy` entry;
`google` continues to mean Gemini CLI. Installed `agy --help` advertises no
version command, so doctor reports the version as unknown without guessing one.

Install with `dub install --provider agy` into
`~/.gemini/antigravity-cli/skills/do-it-up-bro/`. Project installation uses
`.agents/skills/do-it-up-bro/`, which is shared with Codex: an existing bundle
produces a conflict, never an automatic replacement. Invoke `/do-it-up-bro` or
the DUB phrase in the CLI. These are the CLI paths, distinct from Antigravity
desktop/IDE paths. [Official skills documentation](https://antigravity.google/docs/skills).

Map independent tasks to `invoke_subagent`; use `define_subagent` for transient
roles. Workspace modes include inherited, branched/worktree, and shared workspaces.
Choose isolation deliberately for simultaneous writers. Resolve role models from
available host models; do not assume a fixed concurrency limit or recursive
delegation depth. [Subagents](https://antigravity.google/docs/subagents?tab=cli).

Headless supports `agy -p PROMPT --output-format json`, model selection, effort
`low|medium|high`, and `--print-timeout`. Workspace writes may be allowed by
default, and denied tool actions need not produce a failing process exit.
DUB does not yet enable Antigravity federation; native installation and Herdr
targeting work independently of that gate. Authentication, quotas, and observed
model/usage remain unknown until explicitly exercised.
[Headless documentation](https://antigravity.google/docs/cli/headless/).
