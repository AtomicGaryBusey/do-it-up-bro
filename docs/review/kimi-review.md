# Kimi Code component review — usability and compatibility

Date: 2026-09-18. Reviewer host: Kimi Code CLI 2.0.1 (locally installed and exercised).

## Method

- Read every Kimi-touching surface: `dub/providers/base.py` (kimi entry, `build_command`, `detect`), `dub/config.py`, `dub/installer.py`, `dub/security.py`, `dub/supervisor.py`, `adapters/kimi/README.md`, `adapters/kimi/readonly-agent.md`, `tests/test_detection.py`, `tests/integration/test_live.py`, `README.md`, `docs/installing.md`, `docs/federation.md`.
- Verified flags against the **live** local CLI: `kimi --help` (2.0.1) and `kimi doctor` (no model calls, no quota consumed).
- Re-fetched the official docs today: [Agents and Sub-Agents](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html) and [kimi command](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html).
- Full test suite: 32 tests pass (`python3 -m unittest discover -s tests`).

## Verified correct — no change needed

- Headless shape `kimi --agent-file PATH --output-format stream-json -p PROMPT` matches the documented flags; `-p` non-interactive mode and `stream-json` are current.
- The adapter's central safety claim is now directly documented: `-p` uses the `auto` permission policy by default, and `--prompt` cannot combine with `--yolo`, `--auto`, or `--plan`. Tool restriction therefore must come from the agent file — which is exactly what DUB does.
- `readonly-agent.md` matches the documented agent-file schema: kebab-case `name`, required `description`, `tools` allowlist. Docs confirm allowlists "shape the tools shown to the model and are enforced again before execution", and the body correctly states the self-contained-result contract for delegated agents.
- No generic `--effort` flag exists; DUB's `ValueError` for Kimi effort overrides is correct, and `plan()` validates it even on dry runs.
- `kimi --version` detection works (reports `2.0.1`); `build_command` keeps the prompt a single argument (tested).
- Agent-file validity is fail-closed in the CLI: an invalid `--agent-file` errors and exits.
- Packaging includes `adapters/kimi/*.md`, so `readonly-agent.md` ships in the wheel and `asset_root()` resolves it.
- The installed skill at `~/.kimi-code/skills/do-it-up-bro/` loads and works (dogfooded in this session).

## Required changes

### 1. Forward `KIMI_CODE_HOME` to federation children (bug)

`dub/installer.py:18` and `docs/installing.md:29` honor `KIMI_CODE_HOME` for skill
installation, but `child_environment()` in `dub/security.py` does not include it, so
`supervisor.capture` launches `kimi` without it. A user with a relocated data root gets
children that read the default `~/.kimi-code`: wrong `config.toml` (default model,
permissions) and a missing OAuth token — silent misconfiguration or failed runs.

- Fix: pass `KIMI_CODE_HOME` through for the kimi provider, mirroring the `HERDR_*`
  passthrough in `dub/herdr.py` (it is a path variable, not a secret).
- Add a test in `tests/test_supervisor.py` or `tests/test_detection.py` asserting the
  variable survives into the child environment.

### 2. Detect legacy `kimi-cli` instead of failing at run time (usability)

The adapter documents that legacy `kimi-cli` releases have incompatible flags, but
`dub doctor` and `plan()` only check that `kimi` exists and `--version` parses. A legacy
binary on `PATH` passes detection and then fails mid-federation with a confusing
provider error.

- Fix: extend the doctor probe for kimi to run `kimi --help` (no model call) and require
  both `--agent-file` and `stream-json` to appear; report an incompatible CLI with a
  distinct reason instead of treating it as usable.
- Add a fake-executable test alongside `tests/test_detection.py:33`.

## Recommended additions (low priority)

1. **Adapter refresh** (`adapters/kimi/README.md`) with facts verified today:
   - `-p` auto-permission default and its flag incompatibilities (now first-party documented; strengthens the readonly-agent rationale).
   - `--agent-file` accepts exactly one file and cannot combine with `--agent`, `--session`, or `--continue` (DUB complies).
   - `--model` takes a **model alias** (e.g. `kimi-code/kimi-for-coding`) resolved against `config.toml`, not a raw model ID — document this for `providers.kimi.model` in `DUB.toml.example`.
   - `--skills-dir` **replaces** auto-discovered skill directories (DUB correctly does not use it; note for users with team skill setups).
   - The CLI's own help points to `https://moonshotai.github.io/kimi-code/` while the adapter cites `https://www.kimi.com/code/docs/en/…`; both resolve today — record the canonical one.
2. **Optional doctor enhancement**: `kimi doctor` validates `config.toml`/`tui.toml` locally with no model call and exit code semantics; DUB doctor could surface config validity for kimi (still keeping auth as `unknown`).
3. **One live smoke test when convenient**: `DUB_LIVE_PROVIDER=kimi pytest tests/integration -m integration` exists and is opt-in; run it once after change (1) lands to prove the end-to-end federation path on a real CLI. This consumes quota — do not automate it.

## Non-issues checked and dismissed

- `subagents` allowlist omitted in `readonly-agent.md`: unreachable anyway because `Agent`/`AgentSwarm` are not in its `tools` allowlist. No hardening needed.
- `disallowedTools` omitted: redundant given an allowlist of only Read/Grep/Glob.
- Prompt placement after `-p` and flag ordering: accepted by the CLI parser.
- stream-json telemetry: thinking is excluded from JSONL, tool progress goes to stderr; DUB captures both streams and leaves observed model/effort/usage NULL, as designed.

---

## Remediation evaluation — 2026-09-18 (reviewer: Kimi, on commit 802efdb)

Verdict: both required findings are correctly implemented and tested. Approved.

### Required finding 1 — `KIMI_CODE_HOME` passthrough: resolved

- `dub/security.py` adds `PROVIDER_HOME_VARIABLES` and `child_environment(provider)`,
  forwarding only the provider's own home variable. It is resolved to an absolute path
  before the cwd change into the isolated worker directory — a subtlety this review
  did not specify and the implementation got right.
- `dub/supervisor.py` `capture()` threads the provider through, so the variable reaches
  the actual child process, not just the doctor probe.
- Tests: `tests/test_security.py` (passthrough set) and `tests/test_supervisor.py`
  (end-to-end assertion that `KIMI_CODE_HOME` is visible inside the child).

### Required finding 2 — legacy `kimi-cli` detection: resolved

- `probe_compatibility` in `dub/providers/base.py` checks `kimi --help` for
  `--agent-file`, `--output-format`, and `stream-json` with word-boundary matching,
  no model call, fail-closed on probe errors.
- Critically, `run()` enables it (`plan(..., check_compatibility=True)` in
  `dub/supervisor.py`), so live federation fails fast instead of mid-run; `plan()`
  alone defaults it off, which is correct for offline dry runs.
- Verified live: `dub doctor` on this machine reports kimi 2.0.1 as
  `Federation compatibility: compatible`; codex, claude, and grok likewise.
- Test: `tests/test_compatibility.py` covers the missing-flag path.

### Low-priority items

Dispositioned acceptably: adapter doc refresh landed; `kimi doctor` correctly kept as
a manual check rather than an auth inference; the live smoke test was attempted once
and failed on local storage/watch errors — an environment limitation, not a defect.
The opt-in integration path (`DUB_LIVE_PROVIDER=kimi`) remains the right next step
once local login/storage is healthy.

### Suite verification on this machine

`python3 -m pytest -q`: 61 passed, 1 skipped (opt-in live integration), matching the
implementer's report. Ruff not installed locally; not independently re-run.

### Actions taken by this reviewer

- Committed the four review reports (`agy-analysis`, `claude-adapter-review`,
  `grok-usability`, `kimi-review`) as `c91d515` on `dub/v0.1` and pushed; the
  disposition table previously cited reports that were not in the repository.
- Added `.DS_Store` to `.gitignore`.

### Note for Codex

At the time of this review the working tree contained in-flight modifications
(`dub/config.py`, `dub/supervisor.py`, `dub/providers/base.py`, `dub/plugins.py`,
Grok adapter, new `adapters/grok/do-it-up-bro.rhai`, untracked `.grok/`). These were
left untouched. `.grok/` at the repo root looks like tool state, not a deliverable —
confirm whether it belongs in the commit set or in `.gitignore` before the next
commit.
