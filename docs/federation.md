# Federation operations and boundaries

Run `dub federate --dry-run "<goal>"` first. Dry-run uses executable discovery but
does not issue prompts, probe versions, or write artifacts. `--task-class` supports
general, code, research, architecture, and review. `--mode campaign` prioritizes
workflow-capable hosts and records campaign mode; it does not add automatic resume.

Live `dub federate` sends independent analysis work orders to available, enabled
providers. Normal saved CLI authentication is reused. No API-key environment
variables are forwarded, no credentials are read by DUB, and failed authentication
is a provider failure. Local CLI configurations can themselves select billable
backends; DUB cannot guarantee subscription coverage. No automatic quota retries.

The runner requires POSIX process groups. It starts each root in its own empty
directory below the run ID. This prevents accidental shared working-directory
conflicts; it is **not** an OS-level confidentiality boundary. Codex/Grok use
read-only sandbox profiles, Claude has a read/search built-in allowlist plus MCP
denial, and Kimi loads an enforced read/search custom agent. Google is gated.
Home state, hooks, vendor logs, configured integrations, administrator policy,
and readable paths still belong to the trusted host environment. Never assume
a prompt instruction prevents a malicious tool or connector from changing state.

Argument arrays avoid shell interpolation. The goal remains visible to the local
process table and vendor session handling. DUB's persisted artifacts redact known
secret environment values, common token prefixes, bearer strings, and labelled
credentials. Redaction is best-effort, not an arbitrary-secret detector. DUB does
not execute emitted code or treat child instructions as trusted authority.

Each stream has a 1 MiB limit. Overflow terminates the process group and discards
that child's partial streams rather than saving a truncated secret. Timeouts and
Ctrl-C terminate owned process groups, including ordinary descendants; detached
processes that deliberately escape their session are outside this guarantee.
Pending jobs are marked interrupted without launch. Provider failure preserves
other results. A filesystem failure can still prevent complete artifact recording.

Artifacts:

```text
.dub/runs/<id>/
  plan.json
  ledger.sqlite3
  <provider>/work-order.txt
  <provider>/workspace/
  <provider>/stdout.txt
  <provider>/stderr.txt
  <provider>/result.json
  summary.json
  synthesis.json
  SYNTHESIS.md
```

The private run directory is created with mode 0700. Telemetry records requested
models/effort, role, timestamps, statuses, return codes, failure reasons, and paths.
Observed model/effort, usage, and parent IDs are NULL when unavailable. There is no
cross-run learned routing yet. `completed` means all selected processes exited
successfully; inspect payload-level failures and test claims during synthesis.
The CLI returns 0 for completed or partial runs, 1 for all-failed/interrupted runs,
and 2 for configuration/OS errors. A partial run still needs attention.

Set `federation.synthesis_provider` to label a chosen host in the handoff. Open that
host and ask it to read `SYNTHESIS.md`, assess the candidate evidence, perform
objective verification, and implement only authorized changes. No automatic
cross-provider voting or model-produced command execution occurs.

For opt-in live testing, see `tests/integration/test_live.py`. The ordinary tests
never consume model quota. Google safe headless policy verification is the main
remaining blocker to five-provider CLI federation; account access and quotas must
also work independently for each selected provider.
