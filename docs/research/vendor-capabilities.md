# Verified vendor capability index

Checked **2026-09-18** against current first-party documentation. Adapters contain
claim-specific source URLs and all requested capability dimensions. These are
documentation-backed interfaces, not claims of successful paid execution.

| Vendor / harness | Native DUB | Federation v0.1 | Local metadata |
| --- | --- | --- | --- |
| OpenAI Codex | Subagents, role models/effort, worktrees | `codex exec`, read-only sandbox | 0.155.1 |
| Anthropic Claude Code | Subagents, workflows, experimental teams | `claude -p`, read/search tools only; no teams | 2.1.277 |
| Google Gemini CLI | Skills and subagents | Gated pending safe policy verification | Not found |
| Google Antigravity CLI | Separate skills/subagents/worktrees surface | Not aliased to Gemini | Executable found; not exercised |
| xAI Grok Build | Subagents and Rhai workflows | `grok -p`, read-only sandbox | 1.0.34 |
| Moonshot Kimi Code | Skills, isolated agents, AgentSwarm | `kimi -p`, enforced read/search agent | 2.0.1 |
| Herdr (transport) | Routes phrase to an existing host agent | Separate `dub herdr` command | 0.9.1 |

Detailed evidence:

- [Codex adapter](../../adapters/codex/README.md)
- [Claude adapter](../../adapters/claude/README.md)
- [Google adapter](../../adapters/google/README.md)
- [Grok adapter](../../adapters/grok/README.md)
- [Kimi adapter](../../adapters/kimi/README.md)
- [Portable standard and OpenAI/Anthropic research](codex-claude.md)
- [Google/xAI/Moonshot research](google-grok-kimi.md)
- [Herdr research](herdr.md)

Doctor only asks for version metadata and reports auth as `unknown`. Model/effort
levels depend on installed CLI and account; unset overrides inherit host defaults.
No DUB default freezes a model name. Installed CLIs may predate docs; unknown flags
fail in that provider and do not trigger a permissive fallback. Google is gated
because current docs establish a misleading headless plan-mode safety assumption,
not because Google lacks a CLI. Provider hooks, integrations, and administrator
policies remain part of the user's trusted local CLI setup.
