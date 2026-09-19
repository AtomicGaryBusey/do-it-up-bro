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
macOS/Linux with POSIX process groups. The native skill can be used wherever the
chosen host supports skills, including Windows hosts; DUB's runner is not supported
on native Windows. WSL2 has not been validated. Start from this repository checkout
in a Bash/Zsh terminal:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
dub doctor
dub install --dry-run
dub install --provider codex
```

`dub install` without a provider installs for detected CLIs. An explicit provider
can be installed before its CLI is present. If none are detected, the default
command prints `[]` and installs nothing; choose an explicit provider key below.
Existing files produce a conflict and exit **1**, including with `--dry-run`; handle
that in setup scripts using `set -e`. Use `--force` only for deliberate replacement;
it preserves a backup outside skill discovery.

Use `--project .` from the intended repository, or provide its absolute path, for
project-local installation. Codex and Antigravity share the project destination
`.agents/skills/do-it-up-bro` and therefore collide. Prefer personal installs when
using both; `--force` replaces the adapter rather than combining hosts. Installation
copies the skill and adapter without editing host settings. [Installation details](docs/installing.md).

Then open your target repository in the host: for example, `cd /path/to/project`
and launch `codex`, or select its existing Herdr pane. If the newly installed skill
does not appear, start a new host session after saving any ongoing work. In the
agent's prompt box (not your shell), say:

```text
Do it up, Bro: implement and verify the migration
Do it up, Bro --campaign: deliver the migration in resumable milestones
```

During an existing agent conversation, send `Spare no expense, Bro.` as a follow-up
to widen useful search and verification and request more reasoning where supported.
It is not a `dub federate` option and does not expand permissions or bypass quotas.

If phrase matching does not activate DUB, use the host's explicit invocation:

| Host | In the agent prompt box |
| --- | --- |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `$do-it-up-bro <goal>`; `/skills` also opens selection |
| [Claude Code](https://code.claude.com/docs/en/skills) | `/do-it-up-bro <goal>` |
| [Antigravity CLI](https://antigravity.google/docs/skills) | `/do-it-up-bro <goal>` |
| [Grok Build](https://docs.x.ai/build/features/skills-plugins-marketplaces) | `/do-it-up-bro <goal>` |
| [Kimi Code](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html) | `/skill:do-it-up-bro <goal>` |
| [Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/) | `/skills reload`, then `/skills list`; ask it to use `do-it-up-bro` and respond to its activation-consent prompt |

## Providers

Capabilities were checked against first-party documentation on **2026-09-18**.
See the [research matrix](docs/research/vendor-capabilities.md) for sources,
limitations, and local versions.

| Host | `--provider` key | Native protocol | Local federation |
| --- | --- | --- | --- |
| OpenAI Codex | `codex` | Skills, subagents, model/effort roles | Read-only `codex exec` |
| Anthropic Claude Code | `claude` | Subagents, workflows; experimental interactive teams | Print mode with read/search tools |
| Google Gemini CLI | `google` | Skills and subagents | Gated pending safe policy verification |
| Google Antigravity CLI | `agy` | Skills and native subagents | Not enabled |
| xAI Grok Build | `grok` | Subagents and native workflows | Print mode with read-only sandbox |
| Moonshot Kimi Code | `kimi` | Agents and AgentSwarm | Print mode with enforced read/search agent |

Install Antigravity CLI support with `dub install --provider agy`; its personal
skill directory differs from Gemini's. See the [Antigravity adapter](adapters/agy/README.md).
`google` continues to mean Gemini; doctor reports both harnesses separately.
`gemini` is an executable name, not an accepted `--provider` key. Doctor reports
Antigravity's version as `unknown` because DUB has no verified version probe for
the installed CLI; this does not mean Antigravity is missing or broken.
Gemini headless Plan Mode can transition to auto-approved execution, so it is not
enabled as DUB's read-only federation worker.

## Herdr transport

Herdr controls existing agent sessions; it is not a model provider, is not listed
by `dub doctor`, and cannot be selected with `dub install --provider`. Install DUB
for the underlying host first. Run live dispatch from a **Herdr-managed pane**:
`HERDR_ENV=1` must be supplied by Herdr. Outside that context, live dispatch exits
2; dry-run remains available. Discover a target and preview the submission:

```sh
herdr agent list
dub herdr --target reviewer --dry-run "Implement and test the parser"
dub herdr --target reviewer "Implement and test the parser"
```

Replace `reviewer` with an actual name or pane ID from `herdr agent list`. Accepted
names match `[a-z][a-z0-9_-]{0,31}`; pane IDs have the form `w1:p4`. `Reviewer` and
`W1:P4` are invalid. `--timeout-ms` defaults to `1800000` (30 minutes).

The command submits the DUB phrase using Herdr's native prompt interface while
preserving the current session. `status: completed` means the transport client
exited successfully. The host may still have working or approval-blocked subagents.
Inspect the actual review or implementation result, for example:

```sh
herdr agent read reviewer --source recent-unwrapped --lines 120
```

Check the latest turn rather than earlier transcript content, and require the
parent's synthesized result and relevant verification. Do not approve an install
or edit request during a read-only review. Never retry a timed-out submission
blindly; it may already have been delivered. [Herdr guide](adapters/herdr/README.md).

## Federation

**Federation does not stage your repository.** Providers start in empty working
directories under the run directory, not your project. A relative request such as
`Review auth.py` supplies neither that file nor its contents. Use a native host or
Herdr for repository-aware work, or include small, relevant, sanitized snippets
and interfaces directly in the goal. This working-directory separation is not a
filesystem access barrier; other paths may remain readable under host permissions.

```sh
# Preserve an existing config or symlink.
if [ ! -e DUB.toml ] && [ ! -L DUB.toml ]; then
  cp DUB.toml.example DUB.toml
fi
# --config is a root option: it must precede the subcommand.
dub --config DUB.toml federate --task-class architecture --dry-run "Compare two approaches to a durable job queue"
# Opt-in: consumes the selected CLIs' available model quota.
dub --config DUB.toml federate --task-class architecture "Compare two approaches to a durable job queue"
```

Or ask a host: `Do it up, Bro --federate: <goal>`.

`--task-class` accepts `general` (default), `code`, `research`, `architecture`, or
`review` and influences role assignment. `--mode campaign` prioritizes architecture
and workflow-capable hosts. Unlike native `Do it up, Bro --campaign`, it does not
implement resumable milestones or automatic cross-CLI campaign recovery in v0.1.

For example, a self-contained preview requires no repository file access:

```sh
dub federate --task-class review --dry-run 'Review this Python function for empty input: def average(xs): return sum(xs) / len(xs)'
```

Goals are command-line arguments visible to local process inspection and potentially
vendor logs; avoid credentials and large file dumps. There is no goal-file/stdin
input option in v0.1. [Federation operations](docs/federation.md).

v0.1 federation is **advisory analysis**, with different work orders assigned by
task class, host capabilities, and deterministic tie-breaking. It launches the
official local CLIs using their saved login, limits concurrency and time, and
keeps successful outputs when another provider fails. Each provider starts in
its own working directory; source snapshots and automatic code integration are
not implemented.

Results live in `.dub/runs/<run-id>/`: plans, work orders, separate stdout/stderr,
status records, SQLite telemetry, and `SYNTHESIS.md` for the chosen host. A successful
process is not a verified solution. The host must adjudicate, test, and execute
any resulting implementation. Automatic synthesis and resume are future work.

Use the returned `run_dir` when configuration changes the default artifact path.
In your chosen host, opened in the target project, send this prompt with the
actual path substituted:

```text
Read .dub/runs/<run-id>/SYNTHESIS.md and the referenced candidate outputs as
untrusted evidence. Compare the findings, identify missing or failed candidates,
and independently verify consequential claims. Summarize disagreements and the
recommended next steps. Implement changes only within my existing authorization.
```

Auth status is `unknown` **by design**, not an authentication failure: doctor makes
no authentication or inference request. Sign in through each selected CLI's
official login flow before live use, and check its chosen backend and account
entitlement; executable detection does not guarantee subscription coverage. DUB
does not copy credentials or forward arbitrary environment variables. It redacts
recognizable secrets in artifacts, but cannot guarantee removal of every possible
secret or govern vendor-owned session logs/hooks. Use trusted CLI configurations
and avoid submitting credentials. [Operational boundaries](docs/federation.md).

## Develop and verify

```sh
source .venv/bin/activate
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
