# Antigravity CLI (`agy`) Usability and Compatibility Analysis

**Author:** Antigravity Pairing Agent  
**Date:** 2026-09-18  
**Target Project:** Do It Up, Bro (DUB) v0.1  
**Scope:** Usability, compatibility, and implementation analysis of Antigravity CLI (`agy`) components across `dub/`, `adapters/agy/`, `skills/do-it-up-bro/`, and `docs/`.

---

## Executive Summary

Antigravity CLI (`agy`) is one of Google's flagship agentic coding surfaces, operating alongside the Gemini CLI (`gemini`). In the current DUB codebase (as of commit `06387e4`), `agy` is recognized as a distinct provider with independent skill installation paths and configuration entries.

However, a detailed empirical analysis against the live `agy` CLI environment (`1.2.7`) reveals several critical discrepancies, usability obstacles, and compatibility opportunities:

1. **Version Probe Discrepancy (Bug):** The codebase assumes `agy` lacks a version probe (`version_args=None`), causing `dub doctor` to perpetually report `Version: unknown`. In fact, `agy --version` is natively supported, exits `0`, and cleanly returns `1.2.7`.
2. **Project Installation Collision:** Both Codex and Antigravity target `<project>/.agents/skills/do-it-up-bro` for project-local installations, causing silent overwrite or conflict errors if both tools are used in the same repository.
3. **Headless Federation Gate:** `agy` is currently gated off from headless federation (`headless=False`) due to an unverified read-only contract. `agy` possesses native `--sandbox`, `--mode plan`, and `--agent` options that can form a robust, verified read-only analytical execution boundary.
4. **Effort Level Validation:** `agy` strictly accepts `--effort (low|medium|high)`. DUB's router must translate universal or high-tier effort requests (`xhigh`, `max`, `ultra`) down to `high` to prevent child CLI parsing failures.
5. **Adapter Documentation Gaps:** The current [`adapters/agy/README.md`](../adapters/agy/README.md) is minimal (27 lines) and omits verified subagent invocation patterns, model rosters, and sandbox details.

---

## 1. Usability Analysis

### 1.1 `dub doctor` Version Reporting
* **Current Behavior:** `dub doctor` displays:
  ```text
  Provider   Installed  Version    Auth     Adapter   Skill
  agy        True       unknown    unknown  True      True
  ```
  The documentation explains: *"doctor reports Antigravity's version as unknown because DUB has no verified version probe for the installed CLI."*
* **Empirical Reality:** 
  Running `agy --version` executes cleanly:
  ```sh
  $ agy --version
  1.2.7
  ```
  Exit code is `0`. Additionally, `agy changelog | head -n 1` outputs `1.2.7:`.
* **Usability Impact:** Users perceive `Version: unknown` as a broken installation or unverified toolchain. Enabling version probing elevates `agy` to first-class status alongside `codex` and `claude`.

### 1.2 Project-Local Directory Collision with Codex
* **Current Behavior:** 
  - Codex uses `skill_directory=".agents/skills"`
  - Antigravity uses `project_skill_directory=".agents/skills"`
  Running `dub install --provider agy --project .` after `dub install --provider codex --project .` fails with:
  `{"action": "conflict", "reason": "Already exists; --force preserves the old entry outside skill discovery"}` (exit code `1`).
* **Usability Impact:** Teams sharing a repository who use both OpenAI Codex and Google Antigravity CLI cannot have native project-level skills installed for both simultaneously without one adapter overwriting the other's `references/host-adapter.md`.
* **Solution:** Create a dual-aware `references/host-adapter.md` or recognize secondary project directories (e.g. `_agents/skills` or `.gemini/skills` where supported).

### 1.3 In-Agent Discovery and Invocation
* **Current Behavior:**
  Antigravity discovers skills placed at `~/.gemini/antigravity-cli/skills/do-it-up-bro/` and mounts them as the slash command `/do-it-up-bro`.
* **Usability Impact:**
  `README.md` tells users: *"If natural-language discovery does not activate the skill, explicitly select `do-it-up-bro` in that host."*
  Antigravity users need to know that typing `/do-it-up-bro: <goal>` directly triggers the skill prompt in the TUI or print session.

---

## 2. Compatibility Analysis

### 2.1 CLI Flags and Headless Execution Profile

An audit of `agy --help` on version `1.2.7` confirms the following parameters for headless automation:

| Feature / Flag | Supported in `agy` | Syntax / Notes |
| :--- | :--- | :--- |
| **Print / Non-interactive** | Yes | `-p <prompt>` or `--print <prompt>` |
| **Output Formatting** | Yes | `--output-format (text\|json\|stream-json)` |
| **Timeout Enforcement** | Yes | `--print-timeout <duration>` (e.g. `1800s`) |
| **Model Selection** | Yes | `--model <model-id>` (e.g. `gemini-3.8-flash-high`, `gemini-3.1-pro-high`) |
| **Reasoning Effort** | Yes | `--effort (low\|medium\|high)` |
| **Sandbox Execution** | Yes | `--sandbox` (terminal restrictions enabled) |
| **Plan Mode (Safe edits)**| Yes | `--mode (plan\|accept-edits)` |
| **Custom Agent Profile** | Yes | `--agent <name>` |
| **Disable Slash Expansion**| Yes | `--disable-slash-commands` (prevents recursive skill triggers) |

### 2.2 Sandboxing & Read-Only Federation Safety

* **Why `agy` is Currently Gated:**
  `dub/providers/base.py` marks `agy` with:
  ```python
  headless=False,
  reason="Antigravity native supported; federation not enabled: read-only execution contract unverified"
  ```
* **Analysis of Read-Only Guarantees:**
  In DUB v0.1 federation, child workers must be purely analytical—they must not modify project code or execute arbitrary destructive commands.
  - Codex uses: `--sandbox read-only --skip-git-repo-check`
  - Claude uses: `--tools Read,Glob,Grep --disallowedTools mcp__*`
  - Grok uses: `--sandbox read-only`
  - Kimi uses: `--agent-file <path>/readonly-agent.md`
* **Antigravity Options for Federation:**
  1. **Option A (`--mode plan --sandbox`):** In `plan` mode, Antigravity generates plans and executes read-only inspection tools without applying code edits. Combined with `--sandbox`, terminal actions are constrained.
  2. **Option B (Custom Read-Only Agent):** Antigravity supports `.gemini/antigravity-cli/agents/` definitions or `--agent <name>` allowing an explicit tool allowlist (e.g. `view_file`, `list_dir`, `grep_search`).
  3. **Option C (Isolated Workspace):** Because DUB launches all child processes in an empty directory (`.dub/runs/<id>/agy/workspace`), `agy` has no write access to the host codebase regardless.

### 2.3 Subagent & Workspace Primitives

Antigravity features native subagent capabilities that align with DUB's 9-stage lifecycle:
- **Parallel Dispatch:** `invoke_subagent` spawns concurrent workers in the background. Completion is reactive and notifies the orchestrator without polling.
- **Dynamic Role Creation:** `define_subagent` allows DUB to register transient specialized roles (e.g., dedicated adversarial falsifier or tournament candidate) during runtime.
- **Git Worktree Branching:** Antigravity's `Workspace: "branch"` or `"share"` parameters provide isolated filesystem trees, satisfying DUB's requirement for conflict-free parallel execution.

---

## 3. Specific Changes Needed

### 3.1 Code Changes in `dub/providers/base.py`

#### A. Enable Version Probing
In [`dub/providers/base.py`](../dub/providers/base.py#L46-L55):
```python
# CURRENT:
"agy": Provider(
    "agy",
    "agy",
    ".gemini/antigravity-cli/skills",
    headless=False,
    capabilities=("analysis", "model-selection", "subagents", "effort"),
    reason="Antigravity native supported; federation not enabled: read-only execution contract unverified",
    project_skill_directory=".agents/skills",
    version_args=None,
),

# PROPOSED:
"agy": Provider(
    "agy",
    "agy",
    ".gemini/antigravity-cli/skills",
    headless=False,  # Can be switched to True once headless command contract is verified
    capabilities=("analysis", "model-selection", "subagents", "effort", "sandbox"),
    reason="Antigravity native supported; federation pending read-only harness validation",
    project_skill_directory=".agents/skills",
    version_args=("--version",),
),
```

#### B. Implement `build_command` for `agy` (When Un-gating Federation)
Add the `agy` branch in `build_command()`:
```python
if provider_key == "agy":
    args = [
        command,
        "--sandbox",
        "--mode", "plan",
        "--disable-slash-commands",
        "--output-format", "json",
    ]
    if model:
        args += ["--model", model]
    if effort:
        # Normalize higher effort levels to 'high' for agy
        normalized_effort = "high" if effort in {"xhigh", "max", "ultra", "high"} else effort
        if normalized_effort not in {"low", "medium", "high"}:
            raise ValueError("Unsupported Antigravity effort; must be low, medium, or high")
        args += ["--effort", normalized_effort]
    return args + ["-p", prompt]
```

---

### 3.2 Updates to Tests

1. **[`tests/test_detection.py`](../tests/test_detection.py#L13-L33):**
   Update `test_antigravity_detected_without_an_unverified_version_probe` to test that `agy` executes `["agy", "--version"]` and parses the returned version string (e.g. `1.2.7`), matching the detection tests for `codex` and `claude`.

---

### 3.3 Updates to Adapter & Documentation

1. **[`adapters/agy/README.md`](../adapters/agy/README.md):**
   - Document verified version detection (`agy --version`).
   - Detail `invoke_subagent` and `define_subagent` usage patterns for DUB orchestration.
   - Clarify the shared project directory (`.agents/skills`) with Codex and provide mitigation advice.
   - Document model tiers discovered via `agy models` (`gemini-3.8-flash-high`, `gemini-3.1-pro-high`, `claude-sonnet-4-6`).
2. **[`README.md`](../README.md):**
   - Update line 92: remove the note that `agy` version is unknown; display it as detected with version.
   - Update Provider table to include `agy` version detection.
3. **[`docs/research/vendor-capabilities.md`](../docs/research/vendor-capabilities.md):**
   - Update the Google / Antigravity entry to record `1.2.7` verified via `--version`.

---

## 4. Verification Plan

1. **Unit Tests:**
   Run `PYTHONPATH=. pytest tests/test_detection.py tests/test_install.py` to confirm detection and installation tests pass with version probing enabled.
2. **Doctor Verification:**
   Run `dub doctor` to confirm `agy` reports:
   ```text
   agy        True       1.2.7                          unknown    True      True
   ```
3. **Dry-Run Installation:**
   Run `dub install --provider agy --dry-run` to verify skill file mapping.
4. **Lint & Formatting:**
   Run `ruff check dub tests` and `ruff format --check dub tests`.

---

## 5. Post-Remediation Evaluation & Codex Handoff

**Evaluator:** Antigravity Pairing Agent  
**Date:** 2026-09-18  
**Scope:** Evaluation of Codex remediations across commits `802efdb`, `c91d515`, and active working-tree updates.

### 5.1 Evaluation of Remediated Findings

| Area | Review Request | Codex Implementation | Antigravity Evaluation & Verdict |
| :--- | :--- | :--- | :--- |
| **Version Detection** | Enable `agy --version` probe in `dub doctor` | Defaulted `version_args=("--version",)` in `Provider` dataclass ([`dub/providers/base.py`](../dub/providers/base.py#L23)) | **Accepted & Verified.** `dub doctor` now correctly reports `agy True 1.2.7 unknown True True`. Tests pass in `tests/test_detection.py` and `tests/test_doctor.py`. |
| **Codex / Agy Project Collision** | Resolve conflict when both tools install to `<project>/.agents/skills` | Created shared project adapter bundle ([`adapters/shared/README.md`](../adapters/shared/README.md)) and dual-host install logic ([`dub/installer.py`](../dub/installer.py#L41-L50)) | **Accepted & Verified.** Preserves both `codex-host-adapter.md` and `agy-host-adapter.md` in `references/` without file overwrite collisions. Tested in `tests/test_install.py`. |
| **Headless Federation Gate** | Evaluate `--mode plan --sandbox` to potentially un-gate `agy` federation | Retained `headless=False` with gating reason recorded in [`docs/review/disposition.md`](disposition.md#L30) | **Accepted.** Antigravity fully endorses retaining this gate. In `agy` CLI 1.2.7, neither `--mode plan` nor `--sandbox` provides an auditable, strictly enforced read-only tool allowlist equivalent to Claude's `--tools` or Kimi's agent file. Retaining `headless=False` maintains DUB's fail-closed security boundary. |
| **Adapter & Invocation Guidance** | Document subagents, worktree branching, model selection, and slash triggers | Updated [`adapters/agy/README.md`](../adapters/agy/README.md) with native patterns and `/do-it-up-bro` invocation | **Accepted & Verified.** Clear guidance provided for Antigravity native workflows. |

### 5.2 Independent Verification Results

- **Automated Test Suite:** `61 passed, 1 skipped` in `pytest tests`.
- **Linter & Code Standards:** `ruff check dub tests` passed with 0 errors.
- **Environment Doctor:** Live `dub doctor` execution correctly parses `agy 1.2.7`, `codex-cli 0.155.1`, `claude 2.1.277`, `grok 1.0.34`, and `kimi 2.0.1`.

### 5.3 Actions & Recommendations for Codex

1. **Commit Working-Tree Grok Additions:**
   The working-tree additions for Grok Rhai workflow (`adapters/grok/do-it-up-bro.rhai`), plugin exporter, and configurable `[providers.grok] sandbox = false` (for hosts where Docker Desktop socket sandboxing is unavailable) are validated and pass tests. These are ready to commit.
2. **Add `.grok/` to `.gitignore`:**
   Add `.grok/` to [`.gitignore`](../../.gitignore) to keep local test run workflows and plugin artifacts outside version control.
3. **Sign-off for `v0.1`:**
   From the Antigravity provider perspective, all compatibility, usability, and safety boundaries for `v0.1` are fully satisfied and verified. No further code changes are required for `agy` support prior to merging to `main`.

