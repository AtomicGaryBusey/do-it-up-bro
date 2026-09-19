# Grok adapter: usability and compatibility changes

Checked **2026-09-19** against this checkout (`e142dd0` on `dub/v0.1`), local
`grok 1.0.34 (3736acbc8658) [stable]`, official [docs.x.ai](https://docs.x.ai/build/cli/reference),
and the CLI-shipped user guide under `~/.grok/docs/user-guide/`.

This is a change list, not a redesign of DUB. Grok is already a first-class
provider. The gaps below are what keep native DUB and Grok federation from
matching the host's actual primitives as tightly as Claude/Kimi already do.

Live paid Grok federation was **not** re-run for this note. Claims about
headless JSON fields and flags come from the installed CLI help, `grok inspect`,
and first-party docs.

## Current Grok surface in this repo

| Piece | Path | Role today |
| --- | --- | --- |
| Host adapter | `adapters/grok/README.md` | Copied to `references/host-adapter.md` on install |
| CLI contract | `dub/providers/base.py` (`PROVIDERS["grok"]`, `build_command`) | `grok --no-auto-update --sandbox read-only --output-format json -p …` |
| Install dest | `installer.py` + `skill_directory=".grok/skills"` | `~/.grok/skills/do-it-up-bro` or project `.grok/skills/` |
| Doctor | `version_args=("version",)` | Works; this machine reports `grok 1.0.34` |
| Canonical skill | `skills/do-it-up-bro/SKILL.md` | Vendor-neutral; Grok-specific mapping is only in the adapter |
| Example config | `DUB.toml.example` | `[providers.grok] command = "grok"`; synthesis default is Codex |

On this machine `grok inspect --json` discovers the installed skill from
`~/.grok/skills/do-it-up-bro/SKILL.md` (user scope, `userInvocable: true`). A
second copy exists at `~/.agents/skills/do-it-up-bro/` with a **Codex**
`host-adapter.md`. Grok currently prefers the `.grok/skills` copy. That
dedupe is host behavior, not something DUB tests.

## What already works

- Detection via `grok version` (not `--version`).
- Personal and project skill install into Grok's native directories.
- Native slash invocation `/do-it-up-bro` is documented in the README.
- Federation argv keeps the prompt as one argument (no shell interpolation).
- `--sandbox read-only` is a real kernel profile, and the adapter correctly
  warns that `~/.grok/` and temp stay writable, reads are not confined to the
  empty workdir, and child-network blocking is a no-op on macOS.
- Skill frontmatter `model` / `effort` / `allowed-tools` are correctly treated
  as non-enforcing. Official skills docs still say Grok accepts those keys and
  does not apply them.
- Campaign text already points at Rhai workflows rather than inventing a
  second orchestrator.

## Compatibility defects

These are places the Grok mapping is wrong or stale relative to Grok 1.0.34.

### 1. Subagent depth is one, and the adapter does not say so

The CLI-shipped subagents guide (`~/.grok/docs/user-guide/16-subagents.md`):
only the root session can spawn children; a child that calls `spawn_subagent`
fails. DUB's lifecycle (scout → tournament → attack) reads as nested
delegation. On Grok the **director must spawn every child**. Nested
"reviewer of a worker" has to be a new root-spawned agent, a
`resume_from` follow-on, or a workflow `parallel()` panel.

**Change:** state the depth-1 rule in `adapters/grok/README.md` and in the
native mapping section of `skills/do-it-up-bro/references/routing.md` as a
host constraint, not a universal DUB rule.

### 2. `explore` / `plan` shell access is documented two ways

| Source | Claim |
| --- | --- |
| Official [subagents](https://docs.x.ai/build/features/subagents) | `explore` / `plan`: no shell, no edits |
| Local user-guide `16-subagents.md` | they read, search, **and run shell**, but cannot edit |
| Current adapter | "cannot edit or run shell" |

Using `explore` as a read-only scout is unsafe if the installed CLI still
has shell. Do not treat the official table as enforcement.

**Change:** tell the host to use `isolation` and capability mode, not the
built-in type name, when a scout must not execute. Prefer a bundled
read-only custom agent (see additions). Disclose the docs split.

### 3. "No stable workflow API" is stale

The adapter and `docs/research/google-grok-kimi.md` still say there is no
stable hand-authored workflow schema and the host should generate one.
The installed `/create-workflow` skill **is** that schema: `agent()`,
`parallel()`, `phase()`, `complete()`, `capability_mode`,
`isolation_worktree`, `output_schema`, `agent_budget` 1–1024.

Campaign DUB on Grok should map to a saved `.rhai` workflow, not "ask the
model to invent a script."

**Change:** rewrite the campaign section of the Grok adapter. Update the
research row. Optionally ship a workflow (below).

### 4. Federation is weaker than Claude/Kimi on the same host class

Claude federation allowlists `Read,Glob,Grep` and denies MCP. Kimi loads an
enforced read/search agent. Grok federation is only:

```text
grok --no-auto-update --sandbox read-only --output-format json -p <prompt>
```

Missing, all documented on this CLI:

| Flag | Why it matters |
| --- | --- |
| `--tools read_file,grep,list_dir` | Actual tool allowlist (IDs are `read_file` / `grep` / `list_dir`, not Claude names) |
| `--disallowed-tools Agent` or `--no-subagents` | Stops a federation root from exploding into a nested swarm |
| `--disable-web-search` | Sandbox does not block in-process web tools |
| `--agent <readonly.md>` | Same pattern as Kimi `--agent-file` |
| `--max-turns N` | Bounds cost when the model loops |
| `--prompt-file PATH` | Avoid huge argv; supervisor already writes `work-order.txt` |
| `--json-schema …` | Structured analysis output for the ledger/handoff |

Sandbox is not a tool allowlist. Default permission mode still **asks** for
non-read tools. In headless that can stall until DUB's 1800s timeout. Do
**not** add `--always-approve` / `--yolo` to "fix" hangs; restrict tools
instead. The adapter already forbids blanket approval.

**Change:** tighten `build_command("grok", …)` to the flags above. Add
`adapters/grok/readonly-agent.md`. Extend `tests/test_detection.py` so Grok
is asserted the way Claude/Kimi already are.

### 5. Effort values are unvalidated

Codex and Claude reject unknown effort strings. Grok passes `--effort`
through. This CLI's canonical levels are `none`, `minimal`, `low`,
`medium`, `high`, `xhigh`, `max`. Invalid values fail at CLI parse time
rather than in DUB.

**Change:** validate the same way as the other providers.

### 6. `GROK_HOME` is ignored

Kimi install honors `KIMI_CODE_HOME`. Grok's config root is `$GROK_HOME`
(default `~/.grok`). The installer always uses `Path.home() / ".grok/skills"`.
`child_environment()` does not forward `GROK_HOME`, so doctor/federation
will miss relocated auth and config.

**Change:** resolve skill destination and child env against `GROK_HOME` when
set (path only, never secrets). Keep `XAI_API_KEY` out of the child env;
document that API-key-only auth will fail federation unless cached login
exists under that home.

### 7. Observed Grok telemetry is discarded

Headless `--output-format json` already emits `sessionId`, `usage`,
`modelUsage`, and sometimes cost. The ledger still stores
`model_observed` / `usage_if_exposed` as NULL for every provider. Grok is
the easiest provider to parse first because the JSON object is one shot.

**Change:** optional Grok-only parser from `stdout.txt` into ledger fields.
Fail closed: if the object is missing or partial (`usage_is_incomplete`,
`cost_is_partial`), leave NULL. Do not infer cost from tokens.

### 8. Research index is behind the installed CLI

`docs/research/vendor-capabilities.md` and `google-grok-kimi.md` are dated
2026-09-18. Re-check and record:

- depth-1 subagents
- workflow API now documented in-product
- `--tools` / `--agent` / `--json-schema` / `--prompt-file`
- `grok inspect --json` as a zero-quota discovery probe
- official vs local `explore`/`plan` disagreement

## Usability gaps

These are not incorrect, but they make Grok DUB worse than it could be.

### Native skill is too vendor-neutral for Grok's actual tools

The canonical `SKILL.md` never names `spawn_subagent`, `workflow`,
`isolation: worktree`, or Grok tool IDs. After install, Grok's
`host-adapter.md` is the only mapping, and it is easy to miss. Grok also
supports `when-to-use` and `argument-hint` frontmatter, which the skill
omits. Automatic invocation depends on `description` / `when-to-use`.

**Change (Grok adapter / installed copy only, not the universal body):**

- Add `when-to-use` and `argument-hint` if the installer can patch
  frontmatter per host, **or** keep the canonical skill vendor-neutral and
  put trigger phrases in the Grok adapter's first screen.
- In the Grok adapter, name the real tools: `spawn_subagent`, `workflow`,
  `get_command_or_subagent_output`, `read_file`, `grep`, `list_dir`.
- Tell the director: spawn all children from the root; use `explore` only
  as a non-editing scout; use `isolation: worktree` for writers; use a
  workflow for `--campaign`.

Do not put Grok tool IDs in the universal `SKILL.md`.

### No shipped Grok workflow

Campaign DUB currently says "ask the host to author a workflow." That is
the highest-value native mapping Grok has (phased `parallel()`,
`capability_mode: "read-only"` for attack, `isolation_worktree` for
execute, pause/resume). Claude users get adapter prose about workflows;
Grok users get none on disk.

**Add:** `adapters/grok/do-it-up-bro.rhai` (or
`.grok/workflows/do-it-up-bro.rhai` in a plugin). Keep it small:

1. Scout panel (`capability_mode: "read-only"`)
2. Optional tournament panel when args say so
3. Adversarial verify panel
4. `complete()` with evidence paths — no autonomous merge

Installer should copy it to `~/.grok/workflows/` / project
`.grok/workflows/` for `--provider grok`. Smoke-check with
`validate_only` before declaring it shippable. Do not invent flags the
workflow tool does not have.

### No Grok plugin / marketplace install path

`dub install --provider grok` copies a skill directory. Grok's native
distribution unit is a plugin (`skills/` + `agents/` + optional
`commands/` + `.grok-plugin/marketplace.json`). A plugin would also avoid
the Codex-adapter-in-`~/.agents/skills` collision that Grok otherwise
discovers through Agents.md compatibility.

**Add:** `adapters/grok/plugin/` (or repo-root `.grok-plugin/`) with:

```text
.grok-plugin/marketplace.json
plugins/do-it-up-bro/
  plugin.json
  skills/do-it-up-bro/     # or a pointer to the canonical skill + host-adapter
  agents/dub-reader.md
  agents/dub-implementer.md
  # workflows if the plugin format of this CLI discovers them
```

Document `grok plugin validate` and
`grok plugin marketplace add <this-repo>` as an alternative to `dub install`.
Keep `dub install` working; do not make a plugin the only path.

### Custom agents are missing

Grok `--agent` accepts a name or a markdown definition path. Kimi already
ships `adapters/kimi/readonly-agent.md`. Grok has nothing.

**Add:**

- `adapters/grok/readonly-agent.md` — Read/Grep/Glob (Grok IDs:
  `read_file`, `grep`, `list_dir`); no shell, writes, MCP, or delegation.
  Federation should pass `--agent` to this file.
- Optional `dub-implementer.md` for native (not federation) execute waves.

### Defaults and docs assume Codex as the primary host

- README quick start installs `--provider codex`.
- `DUB.toml.example` sets `synthesis_provider = "codex"`.
- Grok is listed correctly in the provider table, but a Grok-first user
  has no copy-paste install line.

**Change:** add a Grok-first install snippet (`dub install --provider grok`,
then `/do-it-up-bro <goal>`). Keep the Codex example; do not silently
change the synthesis default globally. Document that a Grok-only machine
should set `synthesis_provider = "grok"`.

### Claude-compat skill bleed

Grok scans `~/.claude/skills` and `~/.agents/skills` by default. Installing
DUB for Codex or Claude can expose those adapters to Grok sessions. The
canonical skill already warns about foreign `host-adapter.md`. Grok users
still need a concrete recovery:

```text
grok inspect --json   # confirm source.path is ~/.grok/skills/do-it-up-bro
dub install --provider grok --force
```

**Change:** put that recovery in the Grok adapter and `docs/installing.md`.

### Personas and roles unused

Grok personas can set `model`, `reasoning_effort`, and
`default_isolation` for children. DUB semantic roles (director / scout /
implementer / judge) map cleanly onto `[subagents.roles]` /
`[subagents.personas]`. v0.1 can skip shipping personas if custom agents
exist; mention them in the adapter so a user can add them without waiting
on DUB.

## Requested changes (priority)

### Must change (correctness / safety)

1. **Rewrite `adapters/grok/README.md`**
   - Depth-1 subagents; root-only `workflow` tool.
   - Campaign = saved Rhai workflow, not "invent a script."
   - `explore`/`plan` docs split; do not claim "no shell" as enforcement.
   - Federation flags: `--tools`, `--no-subagents` or
     `--disallowed-tools Agent`, `--disable-web-search`, `--agent`,
     `--prompt-file`; never `--yolo`.
   - `GROK_HOME`, API-key-only auth failure mode.
   - `grok inspect` recovery when the wrong host-adapter is loaded.
   - Real tool IDs and `isolation: worktree`.

2. **Tighten `dub/providers/base.py` Grok argv** to those flags. Validate
   effort. Honor `GROK_HOME` for install destination and child env
   (non-secret). Point `--agent` at a bundled readonly agent. Prefer
   `--prompt-file` using the work-order file the supervisor already writes.

3. **Add `adapters/grok/readonly-agent.md`** and wire it like Kimi.

4. **Tests** in `tests/test_detection.py` / `tests/test_install.py`:
   - Grok argv contains `read-only`, `--tools`, and the readonly agent.
   - Prompt remains a single argument (or `--prompt-file` path).
   - Invalid effort raises.
   - `GROK_HOME` relocates install destination.
   - No `--always-approve` / `--yolo` in the argv.

5. **Refresh** `docs/research/google-grok-kimi.md` and
   `docs/research/vendor-capabilities.md` for the items in §8.

### Should add (Grok-native usability)

6. Ship `adapters/grok/do-it-up-bro.rhai` and install it next to the skill
   for `--provider grok`. Smoke-check one path with `validate_only`.
7. Grok-first README / installing snippet; document
   `synthesis_provider = "grok"` for Grok-only machines.
8. Parse Grok headless JSON usage into the ledger when present.
9. Optional plugin layout + `grok plugin validate` instructions.

### Later (do not block v0.1 polish)

10. `[subagents.roles]` / personas for DUB semantic classes.
11. Learned routing from Grok `modelUsage` (the ledger history hook
    already exists and must stay unused until scores are real).
12. ACP `grok agent stdio` as an alternate federation transport.
13. Auto-merge of worktree isolation results — still requires explicit
    user authorization.

## Explicitly do not change

- Do not add `--always-approve` / `--yolo` to federation.
- Do not freeze model names (`grok-4.6`, etc.) into defaults.
- Do not put Grok-only tool IDs in the universal `SKILL.md`.
- Do not treat `--sandbox read-only` as a credential vault or a
  repository-isolation boundary.
- Do not copy the user's repository into the Grok federation workspace
  without a separate, explicit design.
- Do not claim observed model/effort/cost unless parsed from Grok JSON
  and the payload is complete.

## Suggested implementation order

1. Adapter prose + research refresh (no behavior change, unblocks native DUB).
2. Readonly agent + `build_command` + tests (federation safety).
3. `GROK_HOME` + effort validation.
4. Campaign workflow file + installer copy.
5. JSON usage parser.
6. Plugin packaging.

---

## Follow-up evaluation — 2026-09-19 (reviewer: Grok, after `802efdb`)

Codex implemented the original must-list in `802efdb`. This section is the
Grok-host review of that commit, plus the follow-on work done in this working
tree so Codex can review and commit it. Do not merge to `main`.

Verdict on `802efdb`: the original must-change items 1–5 and should-add items
7–9 landed correctly and are tested. Item 6 (saved workflow) and a live Grok
envelope were still open; both are addressed below, uncommitted.

### Evaluation of `802efdb` against this report

| Original request | On `802efdb` | Notes |
| --- | --- | --- |
| Depth-1 subagents; `explore`/`plan` docs split | Done | Adapter documents root-only spawn and the official vs installed-guide shell disagreement |
| Campaign = Rhai API, no invented script | Partial | API documented; no `.rhai` shipped yet (no offline validator) |
| Safe federation flags + reader agent | Done | `--tools read_file,grep,list_dir`, `--no-subagents`, `--disable-web-search`, `--max-turns 12`, `--agent` → `readonly-agent.md`, `--prompt-file`, `--permission-mode dontAsk`. No `--yolo` |
| Effort validation | Done | Canonical Grok levels |
| `GROK_HOME` | Done | Install dest + child env, Grok-only |
| JSON usage parser | Done, unproven on live JSON | `dub/telemetry.py`; fail-closed on incomplete/partial |
| Grok-first README | Done | Install snippet + `synthesis_provider = "grok"` |
| Plugin export | Done | `dub plugin`; not marketplace publish |
| Learned routing / ACP / auto-merge | Correctly excluded | |

Independently re-run on this machine after `802efdb`: **61 passed, 1 skipped**.

### Live federation (was the remaining gate)

Authorized Grok-only calls, self-contained prompt, other providers disabled.

| Run | Result |
| --- | --- |
| `0d88d7615be14a4185c1bacca46b904e` (Codex, on `802efdb`) | Exit 1 before prompt: could not create `~/.grok/hooks` under that execution environment |
| `43b30b1b3a664edc8a18a5a1ca247c5d` (this session, default sandbox) | Exit 1 in 0.2s. `~/.grok` was writable and `hooks/` existed. Grok 1.0.34 **fail-closes** `--sandbox read-only` because `/var/run/docker.sock` → `~/.docker/run/docker.sock` (Docker Desktop symlink). No model call |
| `24dc7239506f4168b35321d0b6d67479` (this session, `sandbox = false`) | **Success.** Exit 0, `stopReason=end_turn`, one-sentence answer, `model_observed=grok-4.6-build`, numeric `usage`/`modelUsage`/`num_turns` parsed into the ledger. About $0.006. Artifacts gitignored under `.dub/runs/` |

`federation.md` previously said Grok's sandbox can fail open. On 1.0.34 it
fail-closes. Tool restriction remains the principal worker boundary.

### Actions in this working tree (for Codex to review)

Not committed. Intended as one follow-up commit on `dub/v0.1`.

1. **`[providers.grok] sandbox`** (`dub/config.py`, `dub/providers/base.py`,
   `dub/supervisor.py`). Default **true** → `--sandbox read-only`. `false` →
   **`--sandbox off`** (not flag omission: Grok still honors `[sandbox] profile`
   in config if the CLI flag is absent). Other providers reject the key.
   Tool allowlist, reader agent, `dontAsk`, `--no-subagents` unchanged.
2. **Live-config example** in `DUB.toml.example` documenting the Docker Desktop
   socket case.
3. **`dub-campaign` workflow**, native `validate_only` on two canned-host paths
   (goal-only; `tournament: true`):
   - `adapters/grok/do-it-up-bro.rhai` (packaged; add `*.rhai` to the grok
     data-files glob)
   - `.grok/workflows/dub-campaign.rhai` (project discovery; **do commit this
     file**. It is the runnable copy, not session junk)
   Named `dub-campaign` so it does not collide with the `/do-it-up-bro` skill.
   `capability_mode: "read-only"`; no merge. After adversarial review, synthesis
   writes scout/alternative/verify output into `scratch/synthesis.md`, not just
   the goal. Empty `args.goal` pauses.
4. **Plugin export** includes `workflows/dub-campaign.rhai`. Grok plugin
   discovery **does not load** `workflows/` (`grok plugin validate` reports 0
   workflow dirs). Docs now say to copy the file into `.grok/workflows/` or
   `~/.grok/workflows/`. `dub install` still does not overwrite user workflows.
5. Adapter, `docs/federation.md`, `docs/plugins.md`,
   `docs/review/disposition.md`, `docs/verification.md` updated for the live
   envelope and the sandbox fail-close.
6. Tests: `tests/test_compatibility.py`, `tests/test_config.py`,
   `tests/test_plugins.py`. Suite after these edits: **61 passed, 1 skipped**.

A **live** `/workflow dub-campaign` run was not started. Offer:

```text
/workflow dub-campaign {"goal":"Map remaining DUB v0.1 gaps without editing files."}
```

### Disposition wording Codex should fix while committing

`docs/review/disposition.md` Grok 4–6 row still says `sandbox = false` *omits*
the OS profile. Current code passes `--sandbox off`. Update that sentence in
the same commit.

### Remaining (not blocking this follow-up)

- Claude and Kimi live federation still failed in this environment (auth /
  storage). Out of Grok scope.
- `dub install --provider grok` does not copy the workflow into
  `~/.grok/workflows/`. Intentional until file-level conflict/backup matches
  the skill installer. Personal installs copy the packaged `.rhai` by hand or
  use the project `.grok/workflows/` path.
- Plugin export is not a working campaign install path on Grok 1.0.34.
- Canned-host `validate_only` is not a live-tool proof.
- `plan()` dry-run still validates Grok with `-p`; live uses `--prompt-file`.
  Pre-existing; not introduced here.

### Do not do in the follow-up commit

- Do not add `--always-approve` / `--yolo`.
- Do not default `sandbox` to false.
- Do not merge to `main`.
- Do not commit `.dub/` live-run artifacts.
- Do not put Grok tool IDs in the universal `SKILL.md`.
- Do not treat `.grok/` as something to gitignore wholesale; commit only
  `.grok/workflows/dub-campaign.rhai`.
