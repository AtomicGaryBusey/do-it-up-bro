# Do It Up, Bro

One phrase, useful native orchestration. **DUB** is a portable escalation protocol
for AI coding agents: independent subagents, competing approaches when justified,
evidence-based judgment, execution, adversarial review, repair, and convergence.

The joke comes from Richard Evan Schwartz's
[*The Fate of the Riemann Hypothesis*](https://www.math.brown.edu/reschwar/Stories/AI.pdf):
a casual prompt activates a sophisticated orchestration protocol. This project
turns that idea into a small, inspectable engineering tool. It shares
[GSD-style](https://github.com/gsd-build/get-shit-done) discipline around explicit
phases, persistent context, and verification; it is independent of GSD.

The principle is **valuemax subscriptionmaxxing**: spend available capacity on
independence, depth, verification, and useful throughput. Objective evidence beats
agent voting. More tokens are worthwhile only when they improve the result.

## Quick start

Python 3.11+; no runtime Python dependencies. Federation and Herdr transport require
macOS/Linux. Start from this repository checkout:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
dub doctor
dub install --dry-run
dub install --provider codex
```

`dub install` without a provider installs for detected CLIs. An explicit provider
can be installed before its CLI is present. Existing files produce a conflict;
`--force` moves the old bundle to a backup outside skill discovery. Use
`--project /absolute/project/path` for project-local installation. Installation
copies the canonical skill plus its host adapter, never edits host settings.

In your coding agent, say:

```text
Do it up, Bro: implement and verify the migration
Do it up, Bro --campaign: deliver the migration in resumable milestones
Spare no expense, Bro.
```

The final phrase escalates an existing run's useful search and verification. It
does not expand task permissions or bypass quotas. If natural-language discovery
does not activate the skill, explicitly select `do-it-up-bro` in that host.

## Providers and Herdr

Capabilities were checked against first-party documentation on **2026-09-18**.
See the [research matrix](docs/research/vendor-capabilities.md) for sources,
limitations, and local versions.

| Host | Native protocol | Local federation |
| --- | --- | --- |
| OpenAI Codex | Skills, subagents, model/effort roles | Read-only `codex exec` |
| Anthropic Claude Code | Subagents, workflows; experimental interactive teams | Print mode with read/search tools |
| Google Gemini CLI | Skills and subagents | Gated pending safe policy verification |
| xAI Grok Build | Subagents and native workflows | Print mode with read-only sandbox |
| Moonshot Kimi Code | Agents and AgentSwarm | Print mode with enforced read/search agent |
| Herdr | Target an existing host's agent | Separate prompt transport |

Google also has Antigravity CLI (`agy`). Its native mapping is documented in the
[Google adapter](adapters/google/README.md); DUB does not substitute it for Gemini.
Gemini headless Plan Mode can transition to auto-approved execution, so it is not
enabled as DUB's read-only federation worker.

Inside a Herdr-managed pane, discover a real target and preview the unique entrypoint:

```sh
herdr agent list
dub herdr --target reviewer --dry-run "Implement and test the parser"
dub herdr --target reviewer "Implement and test the parser"
```

Replace `reviewer` with an existing agent name or pane ID. This submits the DUB
phrase using Herdr's native prompt interface, preserving the current session.
The underlying agent must have DUB installed. Herdr waits for lifecycle state,
not proof of task completion; inspect the result and never retry a timed-out
submission blindly. [Herdr guide](adapters/herdr/README.md).

## Federation

```sh
cp DUB.toml.example DUB.toml
dub federate --dry-run "Compare two approaches to a durable job queue"
# Opt-in: consumes the selected CLIs' available model quota.
dub federate "Compare two approaches to a durable job queue"
```

Or ask a host: `Do it up, Bro --federate: <goal>`.

v0.1 federation is **advisory analysis**, with different work orders assigned by
task class, host capabilities, and deterministic tie-breaking. It launches the
official local CLIs using their saved login, limits concurrency and time, and
keeps successful outputs when another provider fails. Each provider starts in
an empty, isolated working directory. Include necessary context in the goal;
source snapshots and automatic code integration are not implemented.

Results live in `.dub/runs/<run-id>/`: plans, work orders, separate stdout/stderr,
status records, SQLite telemetry, and `SYNTHESIS.md` for the chosen host. A successful
process is not a verified solution. The host must adjudicate, test, and execute
any resulting implementation. Automatic synthesis and resume are future work.

Auth status remains `unknown`; doctor only checks executables and versions. DUB
does not copy credentials or forward arbitrary environment variables. It redacts
recognizable secrets in artifacts, but cannot guarantee removal of every possible
secret or govern vendor-owned session logs/hooks. Use trusted CLI configurations
and avoid submitting credentials. [Operational boundaries](docs/federation.md).

## Develop and verify

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
ruff check dub tests
ruff format --check dub tests
python -m build
```

The normal suite uses fake executables and consumes no model quota. Live testing
is separately opt-in. See [verification](docs/verification.md),
[architecture](docs/architecture.md), [installation](docs/installing.md), and
[requirements including Herdr](docs/requirements.md).

Experimental v0.1; no affiliation with any provider. MIT licensed.
