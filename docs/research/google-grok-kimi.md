# Google, xAI, and Kimi research record

Date checked: **2026-09-18**. First-party pages were searched and opened. The
per-provider adapters contain capability-by-capability links and operational
mapping: [Google](../../adapters/google/README.md),
[Grok](../../adapters/grok/README.md), [Kimi](../../adapters/kimi/README.md).

These are documentation observations, not paid integration results. Local
availability/version comes from `dub doctor`; auth, quota, and entitlement remain
unknown without an authorized provider call. No fixed model identifiers are
required in DUB defaults.

| Question | Verified conclusion | v0.1 consequence |
| --- | --- | --- |
| Google's current CLI | Both Gemini CLI and Antigravity CLI have current official documentation | Use Gemini for `google`; do not alias `agy` |
| Google native fan-out | Gemini subagents forbid recursive delegation; Antigravity supports concurrent subagents and worktree branching | Load harness-specific adapter guidance |
| Google headless safety | Gemini Plan Mode can automatically exit into YOLO; supplementary policies may be ignored under system policies | Do not call Plan Mode a read-only boundary |
| Grok CLI existence | Official Grok Build executable and headless JSON are documented | Real adapter, not speculative unsupported stub |
| Grok workflows | Host-authored Rhai workflows and bounded run agent budgets are documented | Campaign maps to workflow, no invented script API |
| Grok skill knobs | Model/effort skill metadata is ignored | Select models via runtime controls |
| Kimi current generation | Current Kimi Code uses `.kimi-code`; legacy docs differ | Use current schema and inspect local CLI |
| Kimi AgentSwarm | 128-item limit, separate concurrency cap, secondary model pool | Bound fan-out intentionally |
| Kimi headless safety | Print mode defaults to automatic tool approval | Bundle an enforced read/search-only agent |

Research distinction: a feature in a vendor's current docs is not necessarily in
an older installed CLI. Doctor probes versions/help without issuing prompts;
missing required flags must prevent launching that provider. CLI flags do not
neutralize administrator policy, user hooks, or every external integration.

Gaps: no guaranteed ordinary Grok subagent concurrency ceiling, stable Grok
hand-authored workflow API schema, generic Kimi effort CLI flag, or automatic Kimi
worktree switch was established. No provider billing amount or subscription
entitlement is inferred. Google policy documentation contains conflicting tier
numbers in examples; depend on documented precedence, not those example numbers.
