# Native harness review remediation

Scope: the four supplied harness reviews, following worker safety → configuration
and routing → native usability → results and optional assets. Work stays on
`dub/v0.1`; no main merge. User review files are preserved as evidence.

## Acceptance criteria

- Supported federation workers use locally compatible, documented restrictions;
  required missing flags fail closed before work starts. Dry runs do not execute
  probes or models and label compatibility as unchecked.
- Provider-specific configuration roots survive only into the corresponding
  children. Credentials are not forwarded. Federation routing reflects tools
  actually exposed to the worker, not the interactive host's larger tool set.
- Native adapters document verified orchestration, discovery, and limitations.
  Shared Codex/Agy project installs cannot silently select the wrong adapter.
- Structured errors cannot become success solely because exit status is zero.
  Observed metadata is validated, bounded, redacted, and never inferred.
- Every review request has a disposition and evidence or a specific limitation.
  Optional features without a verified safe contract remain explicitly gated.
- Automated tests, packaged-install checks, and independent review pass before
  commit. No paid calls or personal host installations without explicit scope.

## Execution waves

1. **Worker contracts** (agent `worker_contracts`): verify official docs and local
   help; implement restrictions, capability probes, effort validation, Agy version
   detection. Root integrates live preflight and preserves no-execution previews.
2. **Configuration and routing** (root): scoped home variables, installer roots,
   effective federation capabilities, project-aware doctor, regression tests.
3. **Native adapters** (agent `native_adapters`, parallel research): native tool
   mappings, campaign and independent-review guidance, read-only Grok agent;
   investigate verifiable workflow/plugin assets. Root handles shared installs,
   canonical argument semantics, packaging and user-facing docs.
4. **Results and verification** (root): validated Claude/Grok telemetry and error
   envelopes, bounded shutdown if safely testable, review-item disposition table,
   combined tests/build, independent adversarial review, repairs and commit.

## Checkpoint

Implementation integrated across all four waves. The current per-finding status
is in [`disposition.md`](disposition.md), with test and live-run evidence in
[`verification.md`](../verification.md). Remaining gates are local host access
and native workflow validation, not an invitation to relax worker permissions.
