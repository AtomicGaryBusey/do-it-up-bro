# v0.1 verification report

Checked locally on 2026-09-18; Python 3.13 on macOS. Automated checks use no paid
provider prompts or live Herdr target submissions. A separate user-run dogfood
session is documented below.

## Checks

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
- Antigravity follow-up verifies separate personal/project skill paths, shared
  project-path conflicts, and executable detection without inventing a version
  command. `dub install --provider agy` is now accepted and packaged separately.
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

No cross-provider live authentication, entitlement, native swarm/team execution,
telemetry parser, or paid federation result was verified. Google safe unattended policy remains
gated; no permissive fallback exists. Host synthesis is required. Best-effort
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
access to other readable paths; an unknown Antigravity version reflects DUB's
unverified probe, not a universal host limitation; Windows/WSL2 runner support was
not established. Small sanitized excerpts replace the suggested general-purpose
shell file-dump example. First-party skill pages linked in the README were opened
again to confirm each invocation form and Gemini activation consent.

The next live step is to inspect the synthesized review and its evidence before
widening provider coverage. Cross-provider paid integration remains opt-in.
