# Architecture

The canonical `skills/do-it-up-bro/SKILL.md` owns universal semantics. Five
progressively loaded references cover state, routing, verification, convergence,
and federation. Adapter READMEs map semantics to actual host primitives; only the
selected adapter is copied into an installed skill as `references/host-adapter.md`.
The skill-creator guidance informed the short entrypoint and reference separation.

The Python distribution contains no runtime dependencies:

| Component | Responsibility |
| --- | --- |
| `config.py` | Strict TOML loading, relative-path resolution, inherited model defaults |
| `providers/base.py` | Five explicit executable/skill/command contracts |
| `assets.py`, `installer.py` | Checkout/wheel assets, staged copy, conflicts and backups |
| `doctor.py` | Version-only diagnostics; auth remains unknown |
| `router.py` | Task-class role ordering, capability preferences, deterministic ties |
| `supervisor.py` | Separate working directories, bounded concurrent subprocess roots |
| `security.py` | Environment allowlist and best-effort artifact redaction |
| `ledger.py` | SQLite run/task records; unobserved metadata is NULL |
| `adjudicator.py` | Structured manifest and explicit host synthesis handoff |
| `herdr.py` | Single-target native Herdr prompt transport, no automatic retry |

Providers remain a small shared registry rather than five empty wrapper classes.
Routing considers supported headless availability first, then task priorities,
campaign workflow capability, effort availability/request, configured models for
implementation, and subagent capability for scouting. Ties rotate by task class
and mode, not vendor reputation. A history argument reserves an extension point;
there are no learned quality claims. Capability preferences describe hosts, not
a promise that restricted federation roots can exercise every native feature.

Concurrency is a bounded worker queue. Plan `wave` numbers describe scheduling
batches; later jobs can start as soon as a slot frees, without a full-wave barrier.
Campaign changes role preference and records mode, while full checkpoint/resume
semantics remain in the host skill. The outer runner is intentionally not a
second agent runtime or autonomous patch integrator.

Run completion is process completion. `verification_result=not_performed` and
`synthesis_status=awaiting_host_synthesis` remain explicit. Token usage, model,
and effort observed from vendor output are NULL until a trustworthy parser is
implemented; raw redacted output is available for inspection.
