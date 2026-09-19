# Harness review finding disposition

Checked against the four supplied review reports and the current local CLI help.
First-party references and local limitations are recorded in
[`worker-contracts.md`](../research/worker-contracts.md) and
[`native-review-verification.md`](../research/native-review-verification.md).
Review requests are proposals; a documented flag alone does not establish a safe
worker contract. The exact artifacts and current results are in
[`verification.md`](../verification.md).

| Review requests | Disposition |
| --- | --- |
| Claude F1–F6, F10, F26: restricted read tools, strict MCP, no unattended prompts, session/skill isolation, no bare mode, fail-closed flags | Implemented in worker command and local help preflight. Auth with the restricted profile failed in this environment; no weaker fallback is used. |
| Claude F7–F8: ultracode effort distinction | Federation rejects `ultracode`; native adapter explains version/plan dependence. |
| Claude F11/F27: result envelope, permission denials, status vs exit | Validated success/error parser; errors and aborts override exit 0. Numeric metrics and denial count only; raw inputs omitted from telemetry. Graceful SIGINT on timeout uses a one-second ceiling. |
| Claude F12: native vs federation routing | Separate capability sets implemented for every provider; restricted workers receive no subagent/workflow routing bonus. |
| Claude F13–F18: auth status, project doctor, config root, reload, plugin | Project doctor, `CLAUDE_CONFIG_DIR`, reload guidance and validated local plugin export implemented. Auth stays unknown: a network-denied local probe could not establish that `claude auth status --json` is offline. |
| Claude F19–F25/F28: skill arguments, Workflow consent, fresh reviewers, autocomplete hint | Canonical arguments and host-specific guidance updated. Host-specific `argument-hint` omitted from portable frontmatter because cross-host parser acceptance remains unverified. |
| Claude F7b: structured findings schema | Deferred pending a successful live result envelope and schema failure tests; the approved minimal live call failed auth. Plain report remains supported. |
| Grok compatibility 1–3: depth one, scout execution ambiguity, Rhai schema | Adapter now documents root-only delegation, contradictory first-party shell descriptions, and installed Rhai authoring/validation API. Stale research claim corrected. |
| Grok compatibility 4–6: safe worker flags, effort, `GROK_HOME` | Reader agent, explicit tool allowlist, no subagents/web, turn ceiling, permission denial, file prompt, effort validation, and scoped home handling implemented and tested. No blanket approval. `--sandbox read-only` remains the default and fail-closes on Grok 1.0.34 when the profile cannot apply (Docker Desktop `docker.sock` symlink). `[providers.grok] sandbox = false` passes `--sandbox off`; tool restrictions stay required. |
| Grok compatibility 7–8: result metrics and research | Bounded numeric parser verified on a live Grok envelope (`24dc7239506f4168b35321d0b6d67479`): `model_observed=grok-4.6-build`, numeric `usage`/`modelUsage`/`num_turns`, `stopReason=end_turn`. Cost floats were present and complete. `effort_observed` stayed NULL (not in the envelope). |
| Grok native usability: real tools, roles, bleed, Grok-first usage | Adapter and README updated with native IDs, role constraints, source inspection, recovery, and synthesis configuration. No frozen model/persona roster. |
| Grok saved workflow | Native `validate_only` passed on two canned-host paths (goal-only; `tournament: true`) for `dub-campaign`. Script shipped as `adapters/grok/do-it-up-bro.rhai` and project `.grok/workflows/dub-campaign.rhai`. Plugin export includes it. `dub install` still does not overwrite `~/.grok/workflows/`. Live workflow tools were not exercised. |
| Grok plugin/marketplace | Local plugin exporter and `grok plugin validate` pass. Marketplace publication is a distinct Git index/registration workflow; the exporter does not mutate host marketplace state. |
| Grok optional learned routing, ACP, auto merge | Excluded: no observed quality data, transport lifecycle proof, or merge authorization. |
| Kimi required 1–2: home and legacy compatibility | Provider-scoped `KIMI_CODE_HOME` and help probe for `--agent-file`/`stream-json` implemented. Incompatible old CLIs are skipped. |
| Kimi low-priority facts and doctor | Adapter documents print permissions, aliases, skill directory replacement. Config diagnosis remains `kimi doctor` as a documented manual check; DUB does not infer auth from it. One approved live call encountered local storage/watch failures. |
| Agy version and project collision | `agy --version` is probed; new shared Codex/Agy project bundles contain both adapters. Identical second installs are no-ops; modified bundles remain explicit conflicts. |
| Agy headless gate, effort, native guidance | Gate retained. Plan mode, sandbox, an empty cwd, and high-effort mapping do not prove a read-only headless contract. Native subagent/worktree guidance improved without freezing model names. |

The remaining validation gates are concrete: Claude and Kimi live authentication
and storage access; a live (not canned-host) `dub-campaign` run if the user wants
one; a real structured result fixture before adding provider schemas; and evidence
that Claude auth status is network-free before doctor probes it. Grok live
federation and canned-host workflow validation are no longer open gates.
