# Claude Code component review

Reviewed 2026-09-18 against commit `e142dd0` on `dub/v0.1`. Evidence sources:

- Local `claude --help`, `claude auth status --help`, and `claude --version`
  (2.1.277). No model calls were made.
- First-party docs opened the same day: skills, headless/print mode, CLI
  reference, sub-agents, workflows, Agent SDK structured outputs and result types.
- The installed bundle at `~/.claude/skills/do-it-up-bro/` loaded and executed
  as `/do-it-up-bro` inside a live Claude Code session. SKILL.md and
  `references/host-adapter.md` are byte-identical to the repo sources.

Scope: everything DUB does *for* or *through* Claude Code. The canonical skill,
the `claude` branch of `build_command`, the router's view of Claude, detection
and doctor, the environment allowlist, the installer paths, the adapter README,
and the tests that pin those behaviors.

## Verdict

Installation, discovery, and native invocation work today. The adapter's
factual claims match current docs. The problems are in the headless federation
contract, which leaves four documented safety flags unused, and in the adapter
text, which omits two facts a Claude host needs to run DUB well: when it is
allowed to call the Workflow tool, and which agent types give the fresh context
DUB's Attack phase demands. Telemetry that Claude already emits is discarded.

| Priority | Count | Theme |
| --- | --- | --- |
| Must | 5 | Federation flags, Workflow opt-in text, router capability split |
| Should | 8 | Telemetry parser, doctor auth, env allowlist, skill arguments, adapter gaps |
| Could | 6 | Structured output, plugin manifest, graceful stop, misc |

Two items cannot be closed without one opt-in live call. They are listed at
the end under "Needs a live check".

---

## 1. Federation command (`dub/providers/base.py`, `claude` branch)

Current argv:

```text
claude -p --output-format json --tools Read,Glob,Grep --disallowedTools mcp__* [--model M] [--effort E] -- <work order>
```

Proposed argv:

```text
claude -p --restricted --strict-mcp-config --permission-prompts none \
  --no-session-persistence --disable-slash-commands \
  --output-format json --tools Read,Glob,Grep --disallowedTools mcp__* \
  [--model M] [--effort E] -- <work order>
```

### F1. Add `--restricted` — Must

Present in local help; documented as requiring v2.1.248+. It does four things
the current command only approximates:

- Removes every command-running tool and WebFetch unless named in `--tools`.
  `--tools Read,Glob,Grep` already does this, so this part is belt-and-braces.
- **Confines the built-in file tools to the working directories.** This closes
  the gap `docs/federation.md` currently concedes: "an empty cwd is not proof
  that a worker cannot access the repository." With `--restricted`, Read/Glob/Grep
  cannot leave the isolated workspace.
- **Ignores user, project, and local settings files.** The user's `~/.claude`
  hooks, plugins, and MCP servers do not load into the worker. Without this,
  `claude -p` loads the same context an interactive session would, including
  hooks that run shell commands, which contradicts the analysis-only work order.
- Refuses `bypassPermissions`, which DUB never wants enabled.

Side effect to document: the user's `model` and `effortLevel` settings are also
ignored, so an unconfigured worker runs on Claude Code's built-in default model.
DUB passes `--model`/`--effort` explicitly when configured, so behavior stays
deterministic. Gate on flag presence (see F10).

### F2. Add `--strict-mcp-config` — Must

The docs confirm `--disallowedTools "mcp__*"` removes every MCP tool from the
model's view, so the current denial works. But the servers still *start*:
`-p` connects every server in the user's config, waits up to `MCP_TIMEOUT`
(30 s default) for pending ones, and runs their processes. `--strict-mcp-config`
with no `--mcp-config` means zero servers. Keep the `mcp__*` denial as well.

### F3. Add `--permission-prompts none` — Must

Requires v2.1.259+. In a `-p` run with no permission host, prompts are already
denied, but the flag additionally tells Claude "nobody can approve, do not
retry" and removes `AskUserQuestion`. Denials are listed in the result's
`permission_denials` field, which DUB should record (F11).

### F4. Add `--no-session-persistence` — Should

Print-mode only. Without it, every federation work order (which the README now
tells users may contain sanitized source excerpts) is written to a transcript
under `~/.claude/projects/`, outside DUB's redaction boundary. The docs note
`CLAUDE_CODE_SKIP_PROMPT_HISTORY` does the same; the flag is cleaner.

### F5. Add `--disable-slash-commands` — Should

Skills load in `-p` mode by the same rules as interactive sessions. A federation
worker would therefore load the user's personal DUB skill from
`~/.claude/skills/`. A work order whose goal text contains "Do it up, Bro" could
re-trigger the protocol inside a worker that has no Agent tool, wasting tokens
on an orchestration it cannot perform. Federation roots are analysis-only and
need no skills.

### F6. Never add `--bare` — decision record

The headless docs recommend `--bare` for scripted calls and say it will become
the `-p` default. Local help is explicit: "OAuth and keychain are never read."
Bare mode therefore breaks subscription login, which is DUB's core auth model.
Record this in the adapter so a future maintainer does not adopt the docs'
recommendation. Watch the default-flip: if `-p` ever implies bare, DUB must
pass whatever opt-out exists.

### F7. Remove `ultracode` from the federation effort set — Should

`ultracode` means xhigh plus automatic workflow orchestration. With `--tools
Read,Glob,Grep` the Agent and Workflow tools are absent, so the orchestration
half is inert and the request is pure cost. Accept `low|medium|high|xhigh|max`
for federation; reject `ultracode` with a message pointing at native mode.
Also note the router's "deep effort" set is `("high","xhigh","max","ultra")`,
where `ultra` is a Codex level, not a Claude one; harmless but inconsistent.

### F8. Local help vs docs on `--effort ultracode` — Info

Local `--help` lists `low, medium, high, xhigh, max`. The CLI reference lists
`ultracode` as a sixth value since 2.1.203. Both are current. The adapter
should say the help text can omit it and that availability depends on model,
plan (Pro must enable workflows in `/config`), and `disableWorkflows`.

### F9. Prompt delivery — OK

Positional prompt after `--` is valid Commander syntax. `stdin=DEVNULL` is a
readable EOF, so the documented "can't read stdin" warning path is not hit.

### F10. Version gating — Must

F1 needs 2.1.248, F3 needs 2.1.259. `detect()` already captures `--version`.
Either parse the version or probe `claude --help` once per run for each flag,
and **fail closed**: if a required flag is absent, skip the Claude root with a
clear `skipped` reason rather than launching a less-restricted command. This
matches the existing policy in `docs/research/google-grok-kimi.md`.

---

## 2. Telemetry (`dub/supervisor.py`, `dub/ledger.py`)

### F11. Parse the JSON result envelope — Should

`--output-format json` returns one object. Documented fields (Agent SDK
`ResultMessage`): `subtype`, `is_error`, `num_turns`, `duration_ms`,
`duration_api_ms`, `session_id`, `total_cost_usd`, `usage`, `modelUsage`
(keyed by model ID), `permission_denials`, `result`, `structured_output`,
`errors`, `uuid`. Documented `subtype` values include `success`,
`error_max_turns`, `error_during_execution`, `error_max_budget_usd`,
`error_max_structured_output_retries`.

Today every one of these is thrown away and the ledger stores NULL. Add a
Claude-specific parser that:

- Sets `model_observed` from the `modelUsage` keys (join if several).
- Stores `usage`, `total_cost_usd`, `num_turns`, `duration_ms`,
  `permission_denials` into `usage_if_exposed` as JSON.
- Marks the task `failed` with `failure_reason = subtype` when `is_error` is
  true or `subtype != "success"`, **even if the exit code is 0**. This is the
  concrete fix for the "CLI exit success is not task success" boundary in
  `docs/requirements.md`.
- Leaves `effort_observed` NULL. Claude does not report it.
- Treats any parse failure as unknown, never as an error.

Parse the raw bytes before `redact()`, then redact the persisted copy;
redaction only rewrites string contents, so either order keeps valid JSON, but
parsing first avoids masking a model ID that happens to match a pattern.

---

## 3. Router (`dub/router.py`, `PROVIDERS["claude"].capabilities`)

### F12. Split native and federation capabilities — Must

Claude is registered with `subagents`, `effort`, `workflows`. The router uses
`subagents` to prefer Claude for the scout role and `workflows` to prefer it
for campaign architecture. But the federation command strips the Agent and
Workflow tools, so a Claude root can exercise neither. The `routing_note`
admits this in prose; the scoring still acts on it.

Add `federation_capabilities` to `Provider` (for Claude: `analysis`,
`model-selection`, `effort`) and route federation on that tuple. Keep
`capabilities` for doctor output and native documentation. The same split
applies to the other read-only roots but is out of scope here.

---

## 4. Detection and doctor (`dub/providers/base.py`, `dub/doctor.py`)

### F13. Report auth from `claude auth status --json` — Should

The subcommand exists, exits 0, returned instantly, and prints
`loggedIn`, `authMethod`, `apiProvider`, `subscriptionType`, `configDirectory`,
`analyticsDisabled`, `projectsDirectory`, plus PII: `email`, `orgId`, `orgName`.
Doctor can turn `Auth: unknown` into `Auth: yes (oauth, subscription)` using
only the first four fields. Never print, log, or persist the PII fields.
Confirm it makes no network request before adopting (see "Needs a live check").
Gate on subcommand presence; older CLIs lack it.

### F14. Doctor only checks the personal skill path — Could

`skill_installed` looks at `~/.claude/skills/do-it-up-bro/SKILL.md`. A
`--project` install is reported as absent. Accept an optional project path or
report both columns.

---

## 5. Environment allowlist (`dub/security.py`)

### F16. Forward `CLAUDE_CONFIG_DIR` — Should

Claude Code honors `CLAUDE_CONFIG_DIR` for its config root (credentials file,
skills, workflows). It is a path, not a secret, and the allowlist drops it. A
user who relocated their config would see the worker fail as "unauthenticated"
with no hint why. Add it alongside `XDG_CONFIG_HOME`. macOS keychain access
needs `HOME` and `USER`, which are already forwarded.

---

## 6. Installer (`dub/installer.py`, `docs/installing.md`)

### F17. Claude needs no restart after install — Could

Paths are correct (`~/.claude/skills`, `.claude/skills`). Claude Code watches
both for live changes, so the README's "start a new host session" advice is
unnecessary for this host. Say so in the adapter; keep the generic advice for
hosts that need it.

### F18. Optional plugin manifest — Could

`claude --plugin-dir <path>` loads a plugin for one session without touching
`~/.claude/skills`. A `.claude-plugin/plugin.json` at the repo root with the
skill under `skills/` would let a user trial DUB as `/do-it-up-bro:do-it-up-bro`
from a checkout. Also worth noting: `--add-dir <project>` loads that project's
`.claude/skills/`, which makes `dub install --project` usable from any cwd.

---

## 7. Canonical skill (`skills/do-it-up-bro/SKILL.md`)

### F19. Frontmatter is valid and well-sized — OK

Claude reads only `---`-first frontmatter; ours is. `name` matches the
directory. Description is ~210 characters, well under the 1,536-character
listing cap, and carries the trigger phrases Claude uses for automatic
invocation. `disable-model-invocation` is correctly unset; phrase triggering
requires model invocation.

### F20. Say what slash-command arguments mean — Should

The body never references `$ARGUMENTS`, so `/do-it-up-bro fix the parser`
causes Claude Code to append `ARGUMENTS: fix the parser` to the skill text.
The skill only explains the `Do it up, Bro: <goal>` phrase. Add one sentence:
"When invoked as a host command, the trailing arguments are the goal and may
carry `--campaign` or `--federate`." This is vendor-neutral and fixes the same
ambiguity on Codex (`$do-it-up-bro <goal>`) and Kimi.

### F21. `argument-hint` — Could, conditional

Claude Code shows `argument-hint` in `/` autocomplete. The Agent Skills spec
lists only `name`, `description`, `license`, `compatibility`, `metadata`,
`allowed-tools`. Add `argument-hint: "<goal> [--campaign|--federate]"` only
after confirming Gemini, Grok, and Kimi ignore unknown frontmatter keys rather
than rejecting the skill. Otherwise leave the canonical file spec-only.

---

## 8. Adapter README (`adapters/claude/README.md` → `references/host-adapter.md`)

The existing text is accurate. These are additions.

### F24. State the Workflow opt-in rule — Must

Claude Code refuses to call the Workflow tool unless the user opted in. The
documented opt-ins are: the `ultracode` keyword typed by a human, `--effort
ultracode` or `/effort ultracode`, the user asking for a workflow in their own
words, **or the user invoking a skill or slash command whose instructions tell
Claude to call Workflow**. DUB is that skill. The adapter must say plainly:

> `Do it up, Bro --campaign` and any DUB task whose branch factor exceeds what
> one conversation can coordinate authorize calling the Workflow tool. Load the
> `workflow-authoring` skill first. Respect the session's size guideline
> (default `medium`, under 10 agents; `small` on Pro) unless the goal calls for
> more. The runtime caps concurrency at 16 agents and 1,000 per run.

Without this sentence a Claude host reading DUB will correctly decline to use
workflows for campaigns, and campaign mode degrades to turn-by-turn subagents.

Also record: the `ultracode` keyword in a `-p` prompt does *not* opt in (already
stated), and in `-p` a Workflow launch is subject to permission rules
(`Workflow` allow rule, auto mode, or a hook), so headless campaigns need one
of those.

### F25. Map DUB roles to agent types and fresh vs fork — Should

DUB's Attack phase requires fresh context. In Claude Code:

- Fresh-context agents (the default, including built-in `Explore`,
  `Plan`, `general-purpose`, and custom definitions) receive only their own
  system prompt and the task. Use these for scouts, independent candidates,
  and reviewers.
- `fork` agents inherit the parent conversation and its tool pool. They are
  unsuitable for independent verification and for tournament candidates that
  must not see a favored answer.
- `Explore` is read-only, inherits the session model capped at Opus, and takes
  a thoroughness level (`quick`, `medium`, `very thorough`): the natural Scout.
- Per-invocation `model` and `isolation: "worktree"` exist on the Agent call
  itself, not only in definition files. `effort` is definition-only.
- Nesting defaults to 3 levels; at the limit only forks keep the Agent tool.
- Concurrent cap is 20 unless ultracode is active.

### F26. Headless section additions — Must (paired with F1–F6)

List `--restricted` (2.1.248+), `--strict-mcp-config`, `--permission-prompts
none` (2.1.259+), `--no-session-persistence`, `--disable-slash-commands`, and
the `--bare` prohibition with the OAuth reason. State that `--tools default`
is incompatible with `--restricted`; names must be explicit.

### F27. Result envelope and exit semantics — Should

Document the `ResultMessage` fields from F11, that `is_error`/`subtype` are
authoritative over exit code, that SIGTERM yields exit 143 with no result
recorded, and that a `-p` run with background subagents stays open up to
`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` (10 min default). The last point is
moot while Agent is removed but matters if a future profile allows it.

### F28. Live skill reload — Could

Claude watches `~/.claude/skills/` and `.claude/skills/`; no restart needed.

---

## 9. Supervisor (`dub/supervisor.py`)

### F29. Graceful stop before SIGKILL — Could

`_kill` sends SIGKILL to the process group. Claude Code documents that SIGINT
ends the turn and records a result, while SIGTERM/SIGKILL leave it unfinished.
On timeout or cancellation, send SIGINT, wait a short grace period, then
SIGKILL. This would let the JSON result (and its `permission_denials`) reach
the ledger for a timed-out Claude root. Applies to all providers; Claude is
the one with documented semantics.

---

## 10. Structured output — Could

### F7b. Optional `--json-schema` for work orders

With `--json-schema`, the result carries `structured_output` validated against
a draft-07 schema, retried up to `MAX_STRUCTURED_OUTPUT_RETRIES`. A small DUB
findings schema (`findings[]`, `evidence[]`, `assumptions[]`, `uncertainties[]`,
`disagreements[]`) would make synthesis mechanical. Treat `subtype ==
"success"` with no `structured_output` as a failure, per the docs. Defer until
the plain-text path is proven live.

---

## 11. Tests to add or change (`tests/`)

- `test_detection.py::test_prompt_stays_one_argument_and_restrictions_hold`:
  assert the new flags are present and `--bare` is absent.
- New: flag-gating test with a fake `claude` whose `--help` lacks
  `--restricted`; assert the provider is skipped with a reason, not launched.
- New: `ultracode` rejected for federation; `xhigh`/`max` accepted.
- New: telemetry parser fixtures for a success envelope, an `is_error`
  envelope with exit 0, a non-JSON stdout, and a missing `modelUsage`. Assert
  NULLs where data is absent and `failed` status on `is_error`.
- New: `child_environment()` forwards `CLAUDE_CONFIG_DIR`, still drops
  `ANTHROPIC_API_KEY`.
- `test_router.py`: Claude no longer wins scout/campaign on federation
  capabilities it cannot use.
- `test_ledger.py`: doctor auth row never contains `email`, `orgId`, `orgName`.

---

## Needs a live check (one opt-in call each, not run in this review)

1. **`--restricted` keeps OAuth/keychain login.** Docs say `--bare` never reads
   the keychain and say nothing about `--restricted`; its help text scopes it to
   settings files and tools. Run one `claude -p --restricted --tools "" "reply
   ok"` on the subscription and confirm `apiProvider`/cost fields in the result.
2. **`claude auth status --json` is offline.** It answered instantly, but the
   docs do not state it avoids the network. Run once with networking disabled.
3. **`--effort ultracode` parses on 2.1.277** despite absence from `--help`.
   Only relevant to the adapter's native-mode claim, not to federation.
4. **Capture one real JSON envelope** to lock the F11 parser fixture to the
   installed version's actual shape.

---

## Suggested change order

1. F1, F2, F3, F10 together: one `build_command` edit plus flag gating and tests.
2. F12 capability split, since it changes routing output visible in dry runs.
3. F24, F25, F26 adapter text; reinstall with `--force` and re-run
   `/do-it-up-bro` to confirm the host reads the new guidance.
4. F11 telemetry parser with fixtures.
5. F4, F5, F7, F16, F20 as small independent edits.
6. F13 doctor auth after live check 2.
7. Everything marked Could.

---

## Post-implementation verification (commit `802efdb`, 2026-09-18)

Fresh-context check of Codex's remediation against the findings above. No
paid model call was made. Independent runs on this machine: 61 tests pass, 1
skipped; `ruff check` clean; `dub doctor` shows Claude `compatible`; the
federation dry run lists Claude with `analysis, model-selection, effort` only.

| Finding | Status | Note |
| --- | --- | --- |
| F1–F5, F10, F26 flags + gating | Implemented | `REQUIRED_HELP` probe fails closed; `run()` probes, `plan()` does not (see V3) |
| F6 no `--bare` | Recorded | Adapter and worker-contracts state the OAuth reason |
| F7 reject `ultracode` | Implemented | |
| F11 result envelope | Implemented | Parsed a real envelope in run `3e7533f1…`; see V2 |
| F12 capability split | Implemented | `federation_capabilities` per provider |
| F13 auth status | Deferred | Correct call: offline behavior still unproven |
| F16 `CLAUDE_CONFIG_DIR` | Implemented | Provider-scoped forwarding |
| F20 slash arguments | Implemented | Confirmed loaded by this host after reinstall |
| F24, F25 Workflow consent, fresh vs fork | Implemented | Adapter text is accurate |
| F29 SIGINT grace | Implemented | 1 s ceiling, Claude only |

### V1. The live "Not logged in" failure was not caused by DUB's flags

Codex's one authorized live call returned `is_error=true`,
`terminal_reason=api_error`, `duration_api_ms=0`, result "Not logged in".
The disposition attributes this to the restricted profile. Three quota-free
experiments contradict that:

1. `claude auth status --json` reports `loggedIn=true` under DUB's exact
   `child_environment("claude")` (HOME, PATH, USER, LOGNAME, LANG, TERM, TMPDIR).
2. The same command with `--restricted` also reports `loggedIn=true`.
3. A bisect of `claude -p` with `ANTHROPIC_BASE_URL` pointed at a loopback stub
   that answers 400: baseline, each of the five flags alone, and the full DUB
   set all passed the login check and reached the stub, under both the minimal
   and the full environment. No case produced "Not logged in".

The remaining difference is the execution surface. Codex ran the check from
inside its own sandbox, and the same session's Grok and Kimi attempts failed on
hooks-directory creation and home-directory storage denials. A keychain or
credentials-file read blocked by that sandbox produces exactly this client-side
message. Conclusion: rerun the single live Claude smoke check from a normal
terminal, not from inside Codex. Update `docs/verification.md` and the adapter's
"still requires an opt-in live smoke check" sentence once it succeeds.

Caveat: the bisect proves the credential lookup and request construction work
with the DUB flag set. It does not prove a model response; that still needs the
one real call.

### V2. Redaction false positives in persisted stdout — Should fix

The real envelope in `.dub/runs/3e7533f1…/claude/stdout.txt` shows
`output_tokens_details`, `ephemeral_1h_input_tokens`, and
`ephemeral_5m_input_tokens` replaced by `[REDACTED]`. These are token counts
whose names match the `token` pattern but are missing from `_NUMERIC_METRICS`.
Simplest durable rule in `redact()`: under a secret-named key, redact only
string values; leave numbers, booleans, and nested objects intact. A credential
is never a bare number or a dict of counters. Add the real envelope as a parser
fixture now that one exists.

### V3. Dry run does not probe compatibility — Could

`dub federate --dry-run` reports `compatibility: unchecked` while `run()`
probes. The probe is help-only and costs nothing; running it in the dry run
would surface an incompatible CLI before the user commits to a live run.

### V4. Formatting

`ruff format --check` fails only on `docs/review/agy-analysis.md`, an untracked
review document, not on any committed file. Codex's lint claim stands.

### V5. Installed bundle refreshed

The personal Claude bundle was stale after the commit. Reinstalled with
`dub install --provider claude --force`; backup at
`~/.claude/dub-backups/do-it-up-bro-20260919T021642Z-e92f4187`. SKILL.md and
`references/host-adapter.md` now match the repo, and `/do-it-up-bro` loads the
new arguments paragraph in this session.

### V6. Live smoke check passed (run `c3573496d14649f0ab8da5a3ccc69b91`) — closes V1

User-authorized single call from a normal terminal, Claude-only config, 180 s
ceiling, no retries. Goal: "Explain why an empty list has length zero. Do not
use tools." Result: exit 0, `status=completed`, `subtype=success`,
`is_error=false`, `terminal_reason=completed`, one turn, no permission denials,
a substantive answer in the `result` field, 21.5 s wall time. Artifacts under
`.dub/runs/c3573496…/` contain no credential-like strings.

This confirms the full restricted flag set works with subscription (claude.ai)
login when the parent process can reach the keychain. The "still requires an
opt-in live smoke check" sentence in `adapters/claude/README.md` and the
Claude row in `docs/verification.md` can now be updated by Codex.

Observed side effect, as documented: `--restricted` ignored the user's
`model` setting and the worker ran on `claude-opus-5[1m]`, not the user's
configured `claude-fable-5-1[1m]`. Users who want a specific worker model must
set `providers.claude.model` in `DUB.toml`.

### V7. Parser rejects real Claude model IDs — Must fix

`modelUsage` came back keyed by `claude-opus-5[1m]`. The regex in
`dub/telemetry.py` (`[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}`) has no `[` or `]`, so
the key was discarded, `model_observed` stayed null, and the per-model cost and
token block was dropped from `usage_if_exposed`. Add `[]` to the character
class (and consider `+` and `@`, which appear in some provider-qualified IDs).
Use this run's `stdout.txt` as the fixture: it is the first successful real
envelope and also carries `canonicalModel`, `contextWindow`, `maxOutputTokens`,
`costBasis`, and `provider` fields the parser may want to whitelist.

### V2 addendum

The successful envelope shows `thinkingTokens` inside `modelUsage` also
replaced by `[REDACTED]`, alongside the three fields noted above. Same fix.
