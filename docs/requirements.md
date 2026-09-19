# v0.1 implementation requirements

The [original handoff](../DO_IT_UP_BRO_CODEX_HANDOFF.md) is the baseline. This
addendum records the user's subsequent scope and evidence-driven boundaries.

## Herdr addition (2026-09-18)

Provide a unique Herdr invocation when official interfaces support it. Implement
`dub herdr --target <live-agent-name-or-pane> [--campaign] [--dry-run] "<goal>"`.
Map it to documented `herdr agent prompt ... --wait --timeout ...`; require an
explicit target and preserve the current Herdr session/socket context. Do not
broadcast to connected agents, change integrations, or start panes automatically.
Dry-run must make no control calls. Verify command construction with fakes, and
document lifecycle wait, ambiguous delivery on timeout, and no automatic retry.
Herdr is a transport to an existing host, not a sixth model vendor.

## Verified v0.1 boundaries

- Native DUB is the full execution protocol; campaign adds persistent host state.
- Federation is advisory analysis from independent provider roots with isolated
  working directories and a final host synthesis handoff. No source snapshot,
  autonomous patch integration, automatic judge, or automatic resume yet.
- Five vendor adapters are required. Four CLI contracts are enabled for live
  federation. Google native installation works; live headless use is deliberately
  gated because documented plan mode can auto-approve execution and supplementary
  policy precedence requires further local verification. Antigravity is separately
  documented; it is not silently aliased to Gemini.
- Antigravity installation follow-up: recognize `agy` explicitly in installer,
  configuration, and doctor; use its CLI-specific personal skill directory and
  shared `.agents/skills` project directory. Do not enable federation implicitly.
- Local auth/entitlements stay unknown. Unit tests and diagnostics incur no model
  calls. Actual provider runs are explicit user actions, not installation tests.
- The run ledger leaves observed model, effort, usage, and verification unknown
  unless independently exposed and parsed. CLI exit success is not task success.
- v0.1 federation and Herdr transport require POSIX process-group support.
  The protocol and installer remain portable Python 3.11+ assets.
- Secret minimization is required; no claim of perfect arbitrary-output DLP.
  Host logs/hooks and readable home credentials are outside DUB's artifact boundary.

Acceptance is checked by the automated suite, wheel installation test, local
doctor/dry-run checks, and the [verification report](verification.md).
