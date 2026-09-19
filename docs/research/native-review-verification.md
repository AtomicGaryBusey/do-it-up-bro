# Native review verification and disposition

Rechecked 2026-09-18. Review documents are candidate findings, not vendor
contracts. Local probes below did not submit prompts or consume model quota.

## Evidence

| Host | First-party reference | Local evidence and consequence |
| --- | --- | --- |
| Claude | [CLI](https://code.claude.com/docs/en/cli-reference), [headless](https://code.claude.com/docs/en/headless) | `claude --help` advertises restricted mode, strict MCP, prompt denial, disabled skills, and no persistence. Bare explicitly excludes OAuth/keychain. Required safety flags must be compatibility-gated. |
| Claude native | [Subagents](https://code.claude.com/docs/en/sub-agents), [workflows](https://code.claude.com/docs/en/workflows), [skills](https://code.claude.com/docs/en/skills) | Fresh versus fork guidance and explicit campaign Workflow instructions added. Avoid hard-coded fan-out targets or treating relayed text as human consent. |
| Grok | [Subagents](https://docs.x.ai/build/features/subagents), [CLI](https://docs.x.ai/build/cli/reference), [skills/plugins](https://docs.x.ai/build/features/skills-plugins-marketplaces) | `grok --help`, `grok plugin --help`, and `grok inspect --help` checked. Public no-shell description conflicts with installed guide; role names are not execution boundaries. |
| Kimi | [Command](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html), [agents](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html) | `kimi --help` checked. Agent-file restriction, alias semantics, replacement skill directories, and print-mode incompatibilities clarified. |
| Antigravity | [Subagents](https://antigravity.google/docs/subagents?tab=cli), [headless](https://antigravity.google/docs/cli/headless/), [skills](https://antigravity.google/docs/skills) | `agy --help` and `agy --version` checked; version exits zero with `1.2.7`. Flag presence does not justify lifting federation gate. |

The installed Grok 1.0.34 first-party files are additional version-specific
evidence: `~/.grok/docs/user-guide/16-subagents.md` (root-only depth one,
roles/personas, tool frontmatter, MCP inheritance) and
`~/.grok/bundled/skills/create-workflow/SKILL.md` (Rhai language and validation).
The latter explicitly documents `workflow({script, validate_only: true})` as a
native tool call. It validates compilation and one canned-host execution path,
not every branch, model output, or external side effect. Process-exit recovery is
not the same as same-process resumption and effects are not exactly-once.

## Optional asks and acceptance gates

- **Saved Grok workflow:** API is documented, correcting the stale claim that
  no schema exists. No native workflow tool or standalone offline validator is
  available to this Codex execution surface. Do not ship a guessed or unvalidated
  script. Native Grok must author, validate representative arguments with
  `validate_only`, then separately opt into a live run before promotion. Require
  read-only panels, explicit failure handling, evidence output, and no merge.
- **Grok/Claude plugins:** A host-specific local bundle exporter now copies the
  canonical skill and selected adapter. Claude strict validation and Grok plugin
  validation pass on exported bundles. Grok's local guide does not establish
  workflow discovery in plugins; no workflow file is included. Marketplace
  registration is separate from local plugin export. Keep the copy installer too.
- **Grok personas/implementer:** Native configuration is documented; optional
  user model/effort/isolation defaults belong there, not frozen DUB defaults.
  A permissive implementer is unnecessary for restricted federation.
- **Structured output schemas:** Keep plain report compatibility until one
  opted-in live envelope proves schema and error handling. CLI support alone
  does not validate DUB's proposed findings schema.
- **Claude auth status:** Local help is not proof of offline behavior. Keep auth
  unknown until an isolated no-network test verifies it; never persist email or
  organization identifiers. Restricted-profile subscription reuse and native
  ultracode parsing likewise need opted-in live evidence, not inference.
- **Kimi doctor:** A useful optional configuration validation command, not login
  proof. A live Kimi smoke check remains explicit and quota-consuming.
- **Grok learned routing/ACP:** Defer until trustworthy observed quality and
  transport lifecycle contracts exist. Never manufacture quality scores.
- **Auto-merge:** Remains unauthorized without a separate explicit request.
- **Universal argument hints:** Keep host-specific frontmatter out of the shared
  skill until cross-host parser acceptance is tested. Explain trailing arguments
  in prose instead.

These are explicit unfulfilled acceptance gates, not claims that optional assets
or live checks were completed. Safety corrections and portable native guidance
can ship independently of them.
