# Do It Up, Bro — Codex Implementation Handoff

**Target repository:** https://github.com/AtomicGaryBusey/do-it-up-bro  
**Primary objective:** Build a real, portable, vendor-aware **“Do It Up, Bro” (DUB)** orchestration protocol that can be installed into multiple AI coding-agent CLIs and invoked with one consistent phrase to make each harness use its strongest *native* multi-agent / sub-agent / workflow capabilities.

## Invocation

**Do it up, Bro.**

Treat that phrase as explicit authorization to use substantial reasoning, parallelism, sub-agents, independent verification, and iterative repair where those mechanisms create value.

This is **not** “burn as many tokens as possible.” The governing principle is:

> **Valuemax subscriptionmaxxing:** maximize expected solution quality, breadth, verification, and useful throughput from the user’s already-paid subscription capacity. Spend more inference when it buys useful independence, depth, execution throughput, falsification, or reduced uncertainty.

You are running locally in Codex on the user’s laptop. Use Codex’s native capabilities aggressively and intelligently. If multi-agent/sub-agent execution is available, use it rather than merely role-playing several agents in one context.

---

# 1. Operating instructions for this implementation session

1. Inspect the repository before making assumptions.
2. If the repo is effectively empty, create a branch named `dub/v0.1` from the current default branch.
3. Research the **current, official** documentation for:
   - OpenAI Codex CLI
   - Anthropic Claude Code
   - Google’s current coding-agent CLI surface (Gemini CLI, Antigravity CLI, or its current successor)
   - xAI Grok coding/build CLI
   - Moonshot/Kimi CLI
4. Prefer first-party docs and repositories over blog posts or community guesses.
5. Record the verified capabilities and limitations you actually find in `docs/research/vendor-capabilities.md`, with source URLs and the date checked.
6. Do **not** assume vendor feature names from this handoff are still current. Capability-detect and document reality.
7. Decompose the work and use parallel agents for independent research and implementation where useful.
8. Keep the root/orchestrator context thin. Delegate focused work with fresh context.
9. Use independent reviewers/verifiers on important architecture and implementation decisions.
10. Run tests and static checks before declaring completion.
11. Do not stop after producing a plan. Implement the repository.
12. Do not ask the user to confirm routine implementation choices. Use best judgment and continue.
13. Ask only when blocked by credentials, a genuinely destructive action, or an ambiguity that cannot be safely resolved.
14. Do not merge to `main`. Leave the work on a feature branch with clean commits and a concise final summary.

---

# 2. Product vision

The finished system should let a user drop a portable DUB skill/protocol into any supported agent harness and say:

```text
Do it up, Bro: <goal>
```

The host should then map the semantic DUB protocol onto that harness’s strongest supported native orchestration primitives.

Examples of the intended *semantic* behavior:

```text
User
  |
  v
"Do it up, Bro: solve X"
  |
  v
Universal DUB protocol
  |
  +--> triage
  +--> decomposition
  +--> role selection
  +--> model / reasoning-depth selection
  +--> parallel independent work
  +--> tournament / alternative approaches when justified
  +--> adjudication
  +--> execution in dependency-safe waves
  +--> adversarial verification
  +--> targeted repair
  +--> convergence
  |
  v
Synthesized result
```

The universal layer should define **what DUB means**. Thin vendor adapters should define **how that host performs it**.

Do not build a giant one-size-fits-all prompt pretending all CLIs work the same.

---

# 3. Core DUB lifecycle

The canonical protocol should implement this lifecycle.

## 3.1 Triage

Assess:

- ambiguity
- breadth
- depth
- decomposability
- number of independent axes
- availability of objective verification
- whether write-heavy work needs isolation/worktrees
- whether the task benefits from one strong agent, a small team, a tournament, a swarm, or a long-running campaign

Do not spawn agents merely to look impressive.

## 3.2 Scout

Use inexpensive/faster workers where suitable to explore independent dimensions:

- relevant files/subsystems
- documentation
- historical context
- alternative hypotheses
- constraints
- external facts
- test surfaces
- likely failure modes

## 3.3 Tournament

When multiple plausible solution families exist, create **independent** candidates.

Avoid anchoring all workers on the same proposed answer.

Intentional duplicate work is justified for:

- independent reproduction
- consensus measurement
- alternative designs
- proof attempts
- competing implementations
- adversarial search

Otherwise, divide the work into distinct axes instead of cloning the same prompt N times.

## 3.4 Adjudicate

Use a stronger model / deeper reasoning tier where available to evaluate candidates against:

- requirements
- evidence
- tests
- constraints
- maintainability
- correctness
- risk

Do not select a candidate merely because more agents independently repeated the same assumption.

## 3.5 Execute

Convert the chosen plan into a dependency graph.

Run independent work in parallel waves.

Use worktrees, isolated directories, branches, or equivalent mechanisms where concurrent writes could conflict.

## 3.6 Attack

Fresh-context reviewers should actively try to disprove the result.

Examples:

- generate counterexamples
- break tests
- inspect edge cases
- challenge assumptions
- look for missing requirements
- inspect security implications
- compare implementation to source docs
- attempt an alternate derivation

## 3.7 Repair

Convert concrete failures into tightly scoped repair work.

Do not restart the entire process unless the architecture itself is invalidated.

## 3.8 Converge

Do not stop merely because a plausible answer exists.

Stop when:

- explicit acceptance criteria pass
- critical claims are supported or independently verified
- objective tests pass where available
- adversarial reviewers have no unresolved material objection
- remaining disagreement is documented
- another exploration wave is unlikely to materially change the answer

Preserve real disagreement. Do not manufacture consensus.

## 3.9 Synthesize

Return the result, not a giant swarm transcript.

Include:

- final result
- meaningful verification evidence
- consequential unresolved uncertainty
- failed approaches only when they materially inform the conclusion

---

# 4. Canonical portable skill

Create a canonical Agent Skills-compatible skill at:

```text
SKILL.md
```

and/or a canonical source tree such as:

```text
skills/do-it-up-bro/SKILL.md
skills/do-it-up-bro/references/
```

Choose the structure that best matches the current Agent Skills standard after checking the official spec.

The canonical skill must be vendor-neutral.

It should define:

- trigger semantics
- DUB lifecycle
- fan-out discipline
- model-role discipline
- verification rules
- convergence rules
- context discipline
- artifact/state discipline
- escalation semantics
- host-adapter loading

Avoid vendor-specific model names in the universal skill.

Prefer semantic model classes such as:

```text
director/judge      = strongest useful available model; high/max reasoning
hard specialist     = frontier/balanced model; high reasoning
implementer         = balanced model; medium/high reasoning
scout/searcher      = fast model; low/medium reasoning
mechanical worker   = fastest sufficient model; low/medium reasoning
```

The host adapter resolves those classes to real current models.

---

# 5. Invocation modes

Support these semantics in documentation and configuration.

## Native DUB

```text
Do it up, Bro: <goal>
```

Use the current host’s own best orchestration system.

## Campaign DUB

```text
Do it up, Bro --campaign: <goal>
```

Bias toward:

- long-horizon execution
- persistent artifacts/state
- milestones
- resumability
- larger dependency graphs
- repeated verification
- host-native workflow/team facilities

## Federated DUB

```text
Do it up, Bro --federate: <goal>
```

Invoke the optional local federation supervisor so multiple subscribed vendor CLIs can contribute to one problem.

## Escalation phrase

Inside an existing run:

```text
Spare no expense, Bro.
```

means:

- current fan-out or convergence threshold is too conservative
- widen search
- increase independent verification
- increase reasoning depth where it may alter the result
- try additional credible solution families
- do **not** blindly waste tokens on redundant clones

---

# 6. Repository architecture

Use this as a starting point, not an inflexible mandate:

```text
do-it-up-bro/
├── README.md
├── LICENSE
├── pyproject.toml
├── DUB.toml.example
│
├── skills/
│   └── do-it-up-bro/
│       ├── SKILL.md
│       └── references/
│           ├── protocol.md
│           ├── routing.md
│           ├── verification.md
│           ├── convergence.md
│           └── federation.md
│
├── adapters/
│   ├── claude/
│   ├── codex/
│   ├── google/
│   ├── grok/
│   └── kimi/
│
├── dub/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── doctor.py
│   ├── installer.py
│   ├── supervisor.py
│   ├── router.py
│   ├── ledger.py
│   ├── adjudicator.py
│   └── providers/
│       ├── base.py
│       ├── claude.py
│       ├── codex.py
│       ├── google.py
│       ├── grok.py
│       └── kimi.py
│
├── tests/
│   ├── fixtures/
│   ├── test_config.py
│   ├── test_detection.py
│   ├── test_install.py
│   ├── test_router.py
│   └── test_supervisor.py
│
└── docs/
    ├── architecture.md
    ├── installing.md
    ├── federation.md
    └── research/
        └── vendor-capabilities.md
```

Change names if current vendor conventions or a cleaner architecture justify it.

---

# 7. v0.1 scope

The first version should be **real and usable**, while remaining small enough to reason about.

## Required

### A. Canonical DUB skill

A portable, well-written `SKILL.md` plus progressively loaded references.

### B. Five provider adapters

For:

- Anthropic
- OpenAI
- Google
- xAI
- Kimi/Moonshot

Each adapter must document:

- current CLI executable(s)
- detected version if available
- skill/plugin installation location(s)
- native sub-agent/workflow/team primitives
- how model choice works
- how reasoning/effort choice works
- concurrency behavior
- worktree/isolation support
- headless/noninteractive invocation support
- limits or caveats
- how DUB maps onto those primitives

Where the vendor does not expose a capability, say so explicitly instead of simulating nonexistent knobs.

### C. Installer

Provide a safe install mechanism that can:

- detect supported CLIs
- show detected versions
- determine supported skill locations
- install/copy/symlink the canonical skill and host adapter
- support `--dry-run`
- avoid overwriting existing user files without explicit instruction
- print exactly what it changed

Prefer a deterministic Python installer and a `dub install` command.

### D. Doctor

Implement:

```text
dub doctor
```

It should report something like:

```text
Provider   CLI        Installed   Version    Auth/usable*   DUB adapter
OpenAI     codex      yes         ...        unknown/yes    yes
Anthropic  claude     yes         ...        unknown/yes    yes
Google     ...        ...         ...        ...            yes
xAI        ...        ...         ...        ...            yes
Kimi       kimi       ...         ...        ...            yes
```

Do not scrape credentials or print secrets.

`Auth/usable` should only be tested through a documented harmless command if one exists; otherwise report `unknown`.

### E. Local federation supervisor skeleton

Implement a usable first version of:

```text
dub federate "<goal>"
```

Requirements:

- use official local CLI executables
- use the user’s normal subscription-backed CLI authentication where supported
- do not require API keys if the official subscribed CLI already supports the requested invocation
- never attempt to bypass vendor quotas, rate limits, or access controls
- support dry-run planning
- launch provider roots through `subprocess`
- capture stdout/stderr separately
- persist run metadata
- tolerate one provider failing without losing all other results
- impose configurable timeouts
- support concurrency limits
- produce a run directory with artifacts
- perform final synthesis through a configurable provider or leave synthesis artifacts for a chosen host if fully automatic synthesis is not reliably supported yet

Do **not** invent unsupported command-line flags. Verify each CLI’s current documented noninteractive mode.

### F. Run ledger

Persist useful telemetry.

Start simple. SQLite is preferred if it remains lightweight.

Suggested fields:

```text
run_id
task_id
parent_task_id
provider
harness
model_requested
model_observed
effort_requested
effort_observed
role
task_class
started_at
ended_at
status
return_code
usage_if_exposed
verification_result
failure_reason
artifact_path
```

If a host does not expose observed model, effort, or usage, record NULL/unknown. Never fabricate it.

### G. Router

Do not hard-code “vendor X is always best.”

Implement explicit role/capability routing first.

The router should consider:

- task class
- provider availability
- native orchestration features
- requested mode
- model tiers exposed by that provider
- concurrency
- historical telemetry if available

For v0.1, deterministic rules are fine.

Design the interfaces so later versions can learn from historical verifier scores.

### H. Tests

Tests must not burn paid quota.

Use fake provider executables / fixtures to validate:

- executable detection
- subprocess handling
- timeout handling
- concurrent launches
- partial provider failure
- run ledger writes
- config loading
- dry-run behavior
- installer behavior
- routing

Actual provider invocations should be opt-in integration tests, clearly marked.

---

# 8. Configuration

Create `DUB.toml.example`.

A likely shape:

```toml
[dub]
default_mode = "native"
run_dir = ".dub/runs"
max_parallel_providers = 5
provider_timeout_seconds = 1800

[install]
strategy = "copy"

[federation]
enabled = true
synthesis_provider = "codex"

[providers.codex]
enabled = true
command = "codex"

[providers.claude]
enabled = true
command = "claude"

[providers.google]
enabled = true
command = "AUTO_DETECT"

[providers.grok]
enabled = true
command = "AUTO_DETECT"

[providers.kimi]
enabled = true
command = "kimi"
```

Do not freeze model names into the default config unless current CLIs require it.

Prefer runtime discovery and user overrides.

---

# 9. Federation strategy

Federation should not send the exact same prompt to five vendors by default.

The outer supervisor should create **work orders**.

Example:

```text
Goal
 |
 +--> architecture candidate / decomposition
 +--> implementation-focused analysis
 +--> alternate architecture
 +--> adversarial audit
 +--> exhaustive subsystem exploration
 |
 v
cross-provider adjudication / synthesis
```

Roles should not be permanently tied to brands.

The design should eventually allow empirical routing from historical outcomes.

For v0.1, use transparent deterministic assignment and document it.

When independent reproduction is valuable, deliberately assign the same question to multiple providers and label it as such.

---

# 10. “Valuemaxxing” rules

Encode these ideas in the protocol and docs.

1. **Parallelism must buy independence or throughput.**
2. **Stronger models belong on bottlenecks, judges, hard reasoning, and final synthesis.**
3. **Fast models belong on bounded leaf work when they are sufficient.**
4. **Objective verification beats model voting.**
5. **A majority of agents repeating one hidden assumption is not verification.**
6. **Fresh context reduces contamination and anchoring.**
7. **Targeted repair beats full restart.**
8. **More agents are justified by branch factor, not aesthetics.**
9. **Stop when marginal expected value approaches zero.**
10. **Escalate when unresolved contradictions remain material.**

---

# 11. Security and operational constraints

This tool will execute local agent CLIs, so be disciplined.

- Never log access tokens, cookies, OAuth material, API keys, or environment secrets.
- Redact obvious secrets from persisted command output where practical.
- Do not automatically pass the entire process environment to child processes if a narrower safe environment is sufficient.
- Never shell-interpolate untrusted goal text into `shell=True`.
- Use argument arrays with `subprocess`.
- Treat agent output as untrusted data.
- Do not execute code emitted by a child model merely because the child suggested it.
- Keep federation artifacts isolated under the configured run directory.
- Make destructive filesystem or Git operations opt-in.
- Do not bypass vendor quotas, rate limits, or account controls.
- Use only documented/supported CLI interfaces.
- Preserve provider stderr and return codes for debugging without leaking secrets.

---

# 12. README requirements

The README should immediately explain the joke and the real engineering idea.

Suggested opening concept:

> **Do It Up, Bro** is a portable multi-agent escalation protocol for AI coding agents. One phrase tells the current harness to stop treating a complex problem like a single-threaded chat and instead use the strongest useful orchestration machinery it actually has: sub-agents, workflows, teams, swarms, independent candidates, judges, verification, repair, and convergence.

Then explain:

- the inspiration from Richard Evan Schwartz’s short story
- the relationship to GSD-style orchestration discipline
- “valuemax subscriptionmaxxing”
- supported providers
- quick install
- `dub doctor`
- native invocation
- campaign invocation
- federated invocation
- `Spare no expense, Bro.`
- current experimental status

Link to the original story rather than reproducing it.

---

# 13. Research questions that must be answered before finalizing adapters

For each vendor, verify the answers from current official docs/source.

## OpenAI / Codex

- Current multi-agent/sub-agent primitives
- Whether nested agents exist and how recursion/concurrency is controlled
- Per-agent model selection
- Per-agent reasoning/effort selection
- current skill directory conventions
- headless/noninteractive invocation
- machine-readable output if any
- worktree/isolation facilities
- what usage/model telemetry is exposed

## Anthropic / Claude Code

- Current sub-agent primitive
- current dynamic workflow / team primitives
- current “ultracode” or equivalent feature status
- model/effort assignment controls
- worktree/background-agent support
- skill installation paths
- noninteractive invocation
- structured output and telemetry

## Google

Determine the current product reality first.

- Which CLI is the current strategic coding-agent surface?
- Gemini CLI?
- Antigravity CLI?
- Both?
- Something newer?
- skills support
- subagents/teams
- model selection
- reasoning controls
- noninteractive invocation
- workspace isolation
- structured output

## xAI / Grok

- current coding/build CLI name
- workflow support
- sub-agent limits
- reusable workflow format
- skill paths
- whether model/effort metadata in skills is actually honored
- noninteractive mode
- structured output
- account/subscription auth behavior

## Kimi / Moonshot

- current CLI name
- Agent Skills compatibility
- `AgentSwarm` or current equivalent
- maximum/concurrent sub-agent controls
- sub-agent model pools
- regular isolated sub-agents
- noninteractive invocation
- structured output
- telemetry exposure

If prior assumptions conflict with current official docs, current reality wins.

---

# 14. Commit strategy

Prefer several coherent commits rather than one giant dump.

Example:

```text
docs: define DUB protocol and architecture
feat: add portable DUB skill and provider adapters
feat: add installer and doctor command
feat: add federation supervisor and run ledger
test: add provider and federation test harness
docs: add usage guide and verified provider research
```

Use normal descriptive commit messages.

---

# 15. Acceptance criteria for v0.1

The implementation is not done until all of the following are true:

- [ ] The repository contains a canonical portable DUB skill.
- [ ] The protocol clearly defines triage → scout → tournament → adjudicate → execute → attack → repair → converge → synthesize.
- [ ] All five provider adapters exist.
- [ ] Provider capability claims are backed by current first-party research.
- [ ] `dub doctor` works locally without paid model calls.
- [ ] `dub install --dry-run` safely reports intended installation actions.
- [ ] The installer can install the skill/adapters without blindly overwriting user files.
- [ ] `dub federate --dry-run "<goal>"` emits a clear multi-provider execution plan.
- [ ] Real federation uses safe subprocess invocation.
- [ ] Partial provider failure is handled.
- [ ] Runs produce inspectable artifacts and telemetry.
- [ ] Unit tests do not consume paid quota.
- [ ] Tests pass.
- [ ] README provides usable quick-start instructions.
- [ ] No secrets or credentials are persisted.
- [ ] The work is committed on a feature branch and not merged to `main`.

---

# 16. Stretch goals — only after v0.1 is coherent and tested

If v0.1 is complete and additional work clearly improves it:

- cross-provider judge panel
- pairwise candidate comparison
- Bradley-Terry/Elo-style empirical role scoring
- epsilon-greedy provider exploration
- learned task-class routing from verifier outcomes
- resume interrupted federation runs
- TUI/live run dashboard
- JSONL event stream
- provider-specific concurrency backpressure
- Git worktree manager
- model/effort drift detection
- “Spare no expense, Bro” runtime escalation command
- benchmark suite for comparing DUB vs single-agent execution

Do not sacrifice a clean v0.1 to chase these.

---

# 17. Final report back to the user

When the implementation session is complete, report:

1. branch name
2. commits created
3. concise architecture summary
4. files/modules added
5. current verified provider support matrix
6. commands the user should run next
7. tests run and results
8. any provider features that could not be verified or exercised locally
9. any blockers for actual five-provider live federation
10. the single highest-value next step

Do not dump internal chain-of-thought or worker transcripts.

---

# 18. Prime directive

Build the system, verify it, and leave the repository in a state that can actually be dogfooded.

**Do it up, Bro.**

And when an unresolved hard problem genuinely warrants further escalation:

**Spare no expense, Bro.**
