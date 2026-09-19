# Federation worker contract verification

Checked 2026-09-18 using first-party references and installed CLI help. No model
requests or authentication probes were run. Help compatibility means the required
flags are advertised, not that a live enforcement test has passed.

## Claude Code

Local 2.1.277 help and the [CLI reference](https://code.claude.com/docs/en/cli-reference)
confirm `--restricted`, `--strict-mcp-config`, `--permission-prompts none`,
`--no-session-persistence`, and `--disable-slash-commands`. DUB requires them and
retains the built-in reader allowlist and MCP tool denial. Restricted mode ignores
ordinary settings and confines built-in file access; managed policy still applies.
Configured model/effort values are passed explicitly. `--bare` is deliberately not
used because it omits subscription credential discovery. Federation rejects
`ultracode`: that native orchestration mode does not describe a restricted worker.
Subscription authentication under this combination remains an opt-in live check.

## Grok

The [CLI reference](https://docs.x.ai/build/cli/reference) and local 1.0.34 help
confirm reader tool selection, disabled delegation/web access, a turn ceiling,
custom agents, and file prompt transport. The installed first-party guide
`~/.grok/docs/user-guide/14-headless-mode.md` additionally documents the hidden
`--no-auto-update` flag and seven canonical effort tiers; `grok --no-auto-update
--help` exits successfully. DUB accepts those tiers only; model-specific aliases
are not treated as portable settings.

The installed `18-sandbox.md` explicitly permits continuation when sandbox setup
fails. The sandbox is therefore supplementary, not the worker's tool boundary.
DUB combines it with a restricted reader profile and explicit allowlist. Neither
is a confidentiality promise for arbitrary local credentials or proof that
user-managed startup hooks never run. Production use must trust the installed
harness configuration. A sandbox failure must not be represented as verified
filesystem isolation.

## Kimi Code

The [command reference](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html)
and [agent specification](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html)
agree with local 2.0.1 help on `--agent-file` and `stream-json`. DUB requires these
help markers to reject incompatible legacy binaries. The reader profile remains
necessary because print mode is not a read-only permission mode. No generic effort
flag is added.

## Antigravity and compatibility policy

`agy --version` returned `1.2.7` with exit zero even though its help omitted the
flag. Version detection is enabled. Local help exposes plan mode and sandbox, but
the [first-party CLI entrypoint](https://antigravity.google/docs/cli) does not prove
a complete noninteractive read-only contract. Federation remains gated; an empty
working directory does not remove access to other paths. Gemini remains gated too.

Dry planning does not launch help/version processes and labels compatibility
unchecked. An explicit help probe fails closed on missing flags, errors, or timeout;
it never falls back to a weaker worker command. Native capabilities and restricted
federation capabilities are separate fields. Native delegation/workflows are not
advertised as capabilities of workers that cannot use them.
