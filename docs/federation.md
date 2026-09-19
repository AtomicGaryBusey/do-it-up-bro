# Federation operations and boundaries

Run `dub federate --dry-run "<goal>"` first. Dry-run uses executable discovery but
does not issue prompts, probe versions, or write artifacts. `--task-class` supports
general, code, research, architecture, and review. `--mode campaign` prioritizes
architecture using effective worker capabilities and records campaign mode; it
does not add automatic resume. Previews label compatibility `unchecked`. Live
runs probe required local help flags and skip incompatible workers before launch.
This verifies syntax availability, not runtime enforcement or authentication.

Select another configuration with `dub --config /path/DUB.toml federate ...`;
`--config` must precede the subcommand. The default is `./DUB.toml` if present.
Use the returned `run_dir` for artifact inspection when its configured location
differs from `.dub/runs`.

Live `dub federate` sends independent analysis work orders to available, enabled
providers. Normal saved CLI authentication is reused. No API-key environment
variables are forwarded, no credentials are read by DUB, and failed authentication
is a provider failure. Local CLI configurations can themselves select billable
backends; DUB cannot guarantee subscription coverage. No automatic quota retries.

The runner requires POSIX process groups. It starts each root in its own empty
directory below the run ID. This prevents accidental shared working-directory
conflicts; it is **not** an OS-level confidentiality boundary. Codex/Grok use
read-only sandbox profiles. Grok additionally restricts tool selection to readers,
disables subagents/web, uses a reader profile with no inherited MCP, and bounds
model rounds to 12. Grok 1.0.34 refuses to start when `--sandbox read-only` cannot
apply (Docker Desktop `docker.sock` symlink on this machine). `[providers.grok]
sandbox = false` passes `--sandbox off`; tool restrictions remain. Do not treat
`--sandbox off` as isolation. Claude uses restricted mode, strict MCP configuration, no
permission prompts, no skill expansion or session persistence, and explicit
read/search tools. Kimi loads an enforced read/search custom agent. Both Google
harnesses remain gated. Grok's sandbox can fail open; it is supplementary to tool
restriction, not proof of OS isolation. Managed policy and startup hooks require
trusted local configuration; DUB does not override administrators.
Home state, hooks, vendor logs, configured integrations, administrator policy,
and readable paths still belong to the trusted host environment. Never assume
a prompt instruction prevents a malicious tool or connector from changing state.

No repository snapshot is copied to that working directory. A goal such as
`Review auth.py` therefore supplies no file contents and does not establish the
intended repository path. Prefer a native host or Herdr for repository-aware work;
for self-contained federation, include small sanitized excerpts and relevant
interfaces in the goal. Absolute paths may still be readable if the host permits
them; an empty cwd is not proof that a worker cannot access the repository.

Argument arrays avoid shell interpolation. The goal remains visible to the local
process table and vendor session handling. DUB's persisted artifacts redact known
secret environment values, common token prefixes, bearer strings, and labelled
credentials. Redaction is best-effort, not an arbitrary-secret detector. DUB does
not execute emitted code or treat child instructions as trusted authority.
Grok reads the redacted work-order artifact through `--prompt-file`; the original
goal still entered DUB through argv. Other providers retain single-argument prompts.
`CLAUDE_CONFIG_DIR`, `GROK_HOME`, and `KIMI_CODE_HOME` are passed only to their own
workers. Claude restricted mode ignores ordinary model/effort settings: configure
explicit DUB overrides if needed. DUB deliberately does not use Claude `--bare`,
which excludes normal subscription credential discovery.

Each stream has a 1 MiB limit. Overflow terminates the process group and discards
that child's partial streams rather than saving a truncated secret. Timeouts and
Ctrl-C terminate owned process groups, including ordinary descendants; detached
processes that deliberately escape their session are outside this guarantee.
Claude receives SIGINT and up to one second of concurrent stream draining before
forced cleanup. This can retain a final result but never converts timeout or
cancellation into success. Output overflow still kills immediately.
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
cross-run learned routing yet. Validated Claude/Grok numeric usage and model rows
are recorded when exposed. Claude denial inputs are not copied into telemetry;
only their count is retained. Grok incomplete/partial payloads leave telemetry
unknown. Costs are vendor-reported estimates, not a DUB billing calculation.
`completed` means all launched workers exited successfully without a recognized
error envelope; malformed/new payload formats remain unknown and still need
inspection. No status establishes correctness of the proposed solution.
The CLI returns 0 for completed or partial runs, 1 for all-failed/interrupted runs,
and 2 for configuration/OS errors. A partial run still needs attention.

Set `federation.synthesis_provider` to label a chosen host in the handoff. Open that
host and ask it to read `SYNTHESIS.md`, assess the candidate evidence, perform
objective verification, and implement only authorized changes. No automatic
cross-provider voting or model-produced command execution occurs.
The [README](../README.md#federation) includes a copyable synthesis prompt.

For opt-in live testing, see `tests/integration/test_live.py`. The ordinary tests
never consume model quota. Google safe headless policy verification is the main
remaining blocker to five-provider CLI federation; account access and quotas must
also work independently for each selected provider.
