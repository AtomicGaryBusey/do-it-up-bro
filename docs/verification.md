# v0.1 verification report

The original v0.1 baseline was checked on 2026-09-18 with Python 3.13 on macOS.
Its automated checks used no paid provider prompts. The later native review
remediation and user-authorized live attempts are recorded below.

## Original baseline checks

- Automated suite: **32 passed**, one explicitly opt-in live-provider test skipped.
  Uses real fake executable subprocesses for stdout/stderr, failure, timeout,
  descendant cleanup, output limits, and cancellation. Also covers dry-run,
  configuration, capability routing, ledger unknowns/redaction, installer conflicts,
  recoverable replacement, partial installation reporting, and Herdr context.
- Ruff lint and formatting checks, Python compileall, and Git whitespace check
  for authored files (the supplied handoff retains its original Markdown line break).
- Canonical skill passes the skill-creator frontmatter validator.
- Source distribution and wheel build successfully. An isolated temporary venv
  outside the checkout installs the wheel without dependencies; the entrypoint,
  skill installation, Kimi policy asset, and Herdr preview work there.
- Local `dub doctor`: Codex 0.155.1, Claude 2.1.277, Grok 1.0.34, Kimi 2.0.1.
  Gemini is absent; Antigravity is a separate installed executable. Auth stays
  unknown. Herdr version/help confirms 0.9.1 and the prompt interface.
- The original Antigravity follow-up verified separate personal/project skill
  paths and discovered their collision. Its version probe and shared bundle
  behavior were corrected in the native review remediation below.
- Local installer/federation/Herdr dry runs complete without model calls.

## Review and repairs

Independent native agents researched the vendor contracts and built the protocol
and supervisor in separate file scopes. A separate review pass found unsupported
Codex effort rejection, installer backups remaining discoverable as duplicate
skills, and insufficient Ctrl-C cancellation. These were repaired and regression
tests added. Agents reached their available quota before a final additional
review pass; the root completed repair, integration, and verification locally.

The skill's campaign behavior was inspected against a migration with an ambiguous
endpoint and dirty worktree: triage must identify acceptance uncertainty, preserve
unrelated edits, isolate independent writers, checkpoint decisions, and request
only the missing material choice while progressing independent work. This is a
static protocol review, not evidence that every vendor follows it in practice.

Packaging inspection also found that the source distribution initially omitted
the example config and nested integration test. `MANIFEST.in` now includes both
and the research/requirements docs. Herdr session/socket variables are explicitly
preserved only in its transport, not passed to federation children.

## Remaining boundaries

A Grok-only restricted federation envelope was obtained (`24dc7239506f4168b35321d0b6d67479`)
and the numeric telemetry parser accepted it. Claude and Kimi live calls in this
environment still failed before a successful model response. Cross-provider
entitlement, native swarm/team execution, and Google unattended policy remain
unverified. Google stays gated; no permissive fallback exists. Host synthesis is required. Best-effort
redaction cannot promise arbitrary secret removal or control vendor-owned logs.
Windows federation, detached-process containment, automatic source snapshots,
patch integration, live campaign resume, and learned routing are outside v0.1.

## User-run Herdr dogfood and README audit

The user supplied the result of a live `dub herdr` README-review request to
Antigravity. It returned exit 0 and a Herdr `done` state. A subsequent transcript
showed native review subagents still running, including one blocked on an install
command outside the read-only assignment. A later supplied report contained the
completed audit. This is evidence of prompt delivery and native delegation, not
a guarantee that transport completion means all child work has finished. DUB
did not approve that install request or submit a replacement prompt.

The audit's command/config findings were independently checked against source
and parser behavior without model calls. Documentation now explains the exact
provider keys, explicit skill invocation, host startup, install no-op/conflict
states, project collisions, root-only `--config`, Herdr context/target/deadline,
campaign differences, and the host synthesis handoff.

Three recommendations were qualified: empty working directories do not prevent
access to other readable paths; the prior unknown Antigravity version reflected
DUB's missing probe, now corrected; Windows/WSL2 runner support was not
established. Small sanitized excerpts replace the suggested general-purpose
shell file-dump example. First-party skill pages linked in the README were opened
again to confirm each invocation form and Gemini activation consent.

## Native review remediation follow-up

The supplied Grok, Kimi, Agy, and Claude reviews led to the
[implementation plan](review/implementation-plan.md) and
[finding disposition](review/disposition.md). Current
offline tests cover worker flag compatibility, effective routing capabilities,
provider-specific configuration roots, shared Codex/Agy project installs,
Claude/Grok result errors and numeric telemetry, and plugin exports. The current
automated suite passes 61 tests, skips one live integration test, and passes 47
unittest subtests. Ruff and the canonical skill validator pass. Offline
`uv build --no-build-isolation` using installed setuptools 80.9.0 succeeds for
both wheel and source distribution; isolated build could not fetch setuptools in
this restricted environment. Wheel inspection confirms the shared adapter, Grok
reader, and plugin exporter are packaged. Claude and Grok plugin bundles passed
native validators without model calls.

The user authorized up to one minimal live federation call per Claude, Grok, and
Kimi. Each was attempted once with a 90-second ceiling and no retries:

| Provider | Run | Observed result |
| --- | --- | --- |
| Claude | `3e7533f162834049986adee134d80eaa` | Exit 1; JSON result reported `is_error=true`, `terminal_reason=api_error`, and “Not logged in”. No successful model response. |
| Grok | `0d88d7615be14a4185c1bacca46b904e` | Exit 1 before prompt; could not create its hooks directory in the current execution environment, and refused to start without its sandbox. |
| Grok | `43b30b1b3a664edc8a18a5a1ca247c5d` | After creating `~/.grok/hooks`, still exit 1 in 0.2s: `--sandbox read-only` fail-closed because `/var/run/docker.sock` is a Docker Desktop symlink. No model call. |
| Grok | `24dc7239506f4168b35321d0b6d67479` | Success with `[providers.grok] sandbox = false`. Exit 0, `stopReason=end_turn`, one-sentence answer, parser recorded `grok-4.6-build` and numeric usage. Tool allowlist/reader/dontAsk/no-subagents unchanged. ~$0.006. |
| Kimi | `22ecfa2dce42434490628af0e6e0afd1` | Exit 1; watcher `EMFILE` and storage permission denial under its home directory. Only a version event reached stdout. |

The first three authorized live attempts demonstrate failure handling. The later
Grok retry (`24dc7239506f4168b35321d0b6d67479`) is a successful restricted
federation envelope after `--sandbox off` on a host where read-only cannot
apply. Raw outputs are under `.dub/runs/<id>/` locally and remain outside Git.
