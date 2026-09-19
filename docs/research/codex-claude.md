# OpenAI, Anthropic, and portable skill research

Checked 2026-09-18 against opened first-party pages, not search snippets. Local metadata checks consumed no model quota: Codex 0.155.1 and Claude Code 2.1.277. Live authentication, subscription entitlement, model execution, and provider telemetry were not exercised.

The capability-by-capability findings and source links are maintained in the [Codex adapter](../../adapters/codex/README.md) and [Claude adapter](../../adapters/claude/README.md), which also ship with installed skills. Keeping the mapping there avoids conflicting research and runtime instructions.

Notable corrections to older assumptions: current Claude documentation covers nested subagents, dynamic workflows, ultracode, and per-agent effort; teams cannot run in print mode. Current Codex documentation uses a renamed concurrency setting and does not establish a depth knob. DUB does not encode unverified limits or freeze vendor model names.

## Agent Skills standard

The [official specification](https://agentskills.io/specification), opened on the date above, defines a skill directory containing `SKILL.md` with YAML `name` and `description`, plus optional references. The canonical directory is `skills/do-it-up-bro/`, with a matching lowercase hyphenated name. Host-specific fields stay in adapter prose; progressive references keep the entrypoint short. The installer supplies `references/host-adapter.md`; an uninstalled source skill can detect available host tools without that file.

## Verification boundary

Vendor documentation establishes supported interfaces, not this account's entitlement or the installed configuration's effective permissions. `--version` and help inspection do not prove credentials work. Provider help/configuration can be more restrictive or older than the cited pages. v0.1 avoids automatic model calls during tests and doctor checks; actual integration runs remain opt-in.
