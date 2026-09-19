"""Auditable CLI contracts. Flags are sourced in the corresponding adapters."""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass

from dub.assets import asset_root
from dub.config import Config
from dub.security import child_environment, redact


@dataclass(frozen=True)
class Provider:
    key: str
    executable: str
    skill_directory: str
    headless: bool = True
    capabilities: tuple[str, ...] = ("analysis", "model-selection")
    reason: str = ""
    project_skill_directory: str | None = None
    version_args: tuple[str, ...] | None = ("--version",)
    federation_capabilities: tuple[str, ...] = ("analysis", "model-selection")


PROVIDERS = {
    "codex": Provider(
        "codex",
        "codex",
        ".agents/skills",
        capabilities=("analysis", "model-selection", "subagents", "effort", "sandbox"),
        federation_capabilities=("analysis", "model-selection", "effort", "sandbox"),
    ),
    "claude": Provider(
        "claude",
        "claude",
        ".claude/skills",
        capabilities=("analysis", "model-selection", "subagents", "effort", "workflows"),
        federation_capabilities=("analysis", "model-selection", "effort"),
    ),
    "google": Provider(
        "google",
        "gemini",
        ".gemini/skills",
        headless=False,
        capabilities=("analysis", "model-selection", "subagents"),
        reason="Native supported; federation gated: headless plan mode auto-approves execution, and admin-policy overrides require local verification",
    ),
    "agy": Provider(
        "agy",
        "agy",
        ".gemini/antigravity-cli/skills",
        headless=False,
        capabilities=("analysis", "model-selection", "subagents", "effort"),
        reason="Antigravity native supported; federation not enabled: read-only execution contract unverified",
        project_skill_directory=".agents/skills",
    ),
    "grok": Provider(
        "grok",
        "grok",
        ".grok/skills",
        capabilities=("analysis", "model-selection", "subagents", "effort", "sandbox", "workflows"),
        version_args=("version",),
        federation_capabilities=("analysis", "model-selection", "effort"),
    ),
    "kimi": Provider(
        "kimi",
        "kimi",
        ".kimi-code/skills",
        capabilities=("analysis", "model-selection", "subagents"),
    ),
}


def build_command(
    provider_key: str,
    command: str,
    prompt: str,
    model: str | None = None,
    effort: str | None = None,
    *,
    prompt_file: str | None = None,
) -> list[str]:
    provider = PROVIDERS[provider_key]
    if not provider.headless:
        raise ValueError(provider.reason)
    if prompt_file is not None and provider_key != "grok":
        raise ValueError("File prompt transport is currently supported only for Grok")
    for value in (model, effort):
        if value is not None and (not value or value.startswith("-") or "\0" in value):
            raise ValueError("Model/effort must be nonempty values, not flags")
    if provider_key == "codex":
        args = [command, "exec", "--json", "--sandbox", "read-only", "--skip-git-repo-check"]
        if model:
            args += ["--model", model]
        if effort:
            if effort not in {"minimal", "low", "medium", "high", "xhigh", "max", "ultra"}:
                raise ValueError(
                    "Unsupported Codex effort; available levels depend on model and CLI"
                )
            args += ["-c", "model_reasoning_effort=" + json.dumps(effort)]
        return args + ["--", prompt]
    if provider_key == "claude":
        args = [
            command,
            "-p",
            "--restricted",
            "--strict-mcp-config",
            "--permission-prompts",
            "none",
            "--no-session-persistence",
            "--disable-slash-commands",
            "--output-format",
            "json",
            "--tools",
            "Read,Glob,Grep",
            "--disallowedTools",
            "mcp__*",
        ]
        if model:
            args += ["--model", model]
        if effort:
            if effort not in {"low", "medium", "high", "xhigh", "max"}:
                raise ValueError("Unsupported Claude effort")
            args += ["--effort", effort]
        return args + ["--", prompt]
    if provider_key == "grok":
        args = [command, "--no-auto-update", "--sandbox", "read-only", "--output-format", "json"]
        args += [
            "--tools",
            "read_file,grep,list_dir",
            "--no-subagents",
            "--disable-web-search",
            "--max-turns",
            "12",
            "--permission-mode",
            "dontAsk",
            "--agent",
            str(asset_root() / "adapters/grok/readonly-agent.md"),
        ]
        if model:
            args += ["--model", model]
        if effort:
            if effort not in {"none", "minimal", "low", "medium", "high", "xhigh", "max"}:
                raise ValueError("Unsupported Grok effort")
            args += ["--effort", effort]
        if prompt_file is not None:
            if not prompt_file or prompt_file.startswith("-") or "\0" in prompt_file:
                raise ValueError("Prompt file must be a nonempty path, not a flag")
            return args + ["--prompt-file", prompt_file]
        return args + ["-p", prompt]
    if effort:
        raise ValueError(
            "Kimi effort overrides are not exposed by DUB v0.1; use host configuration"
        )
    args = [
        command,
        "--agent-file",
        str(asset_root() / "adapters/kimi/readonly-agent.md"),
        "--output-format",
        "stream-json",
    ]
    if model:
        args += ["--model", model]
    return args + ["-p", prompt]


REQUIRED_HELP = {
    "codex": ("--json", "--sandbox", "--skip-git-repo-check"),
    "claude": (
        "--restricted",
        "--strict-mcp-config",
        "--permission-prompts",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--tools",
        "--disallowedTools",
        "--output-format",
    ),
    "grok": (
        "--sandbox",
        "--tools",
        "--no-subagents",
        "--disable-web-search",
        "--max-turns",
        "--permission-mode",
        "--agent",
        "--output-format",
        "--prompt-file",
    ),
    "kimi": ("--agent-file", "--output-format", "stream-json"),
}


def probe_compatibility(provider_key: str, command: str) -> dict:
    """Probe required help contracts without a model call; never weaken missing flags."""
    provider = PROVIDERS[provider_key]
    if not provider.headless:
        return {"compatible": False, "reason": provider.reason}
    args = [command, "exec", "--help"] if provider_key == "codex" else [command, "--help"]
    try:
        result = subprocess.run(
            args,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=5,
            env=child_environment(provider_key),
            check=False,
        )
        if result.returncode != 0:
            return {"compatible": False, "reason": "Required local help probe failed"}
        help_text = result.stdout + result.stderr
        missing = [
            token
            for token in REQUIRED_HELP[provider_key]
            if re.search(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])", help_text) is None
        ]
        if missing:
            return {
                "compatible": False,
                "reason": "Missing required help contract: " + ", ".join(missing),
            }
        return {
            "compatible": True,
            "reason": "Required local help flags present; enforcement is vendor-defined",
        }
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return {"compatible": False, "reason": "Required local help probe unavailable"}


def detect(config: Config, *, versions: bool = True, compatibility: bool = False) -> list[dict]:
    """Local version/help commands only; auth remains unknown, no model calls."""
    rows = []
    for key, provider in PROVIDERS.items():
        settings = config.providers[key]
        command = settings.command or provider.executable
        executable = shutil.which(command)
        version = "unknown"
        if executable and versions and provider.version_args is not None:
            try:
                result = subprocess.run(
                    [executable, *provider.version_args],
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    env=child_environment(key),
                    check=False,
                )
                if result.returncode == 0:
                    version = (
                        redact(result.stdout.strip().splitlines()[0])[:200]
                        if result.stdout.strip()
                        else "unknown"
                    )
            except (OSError, subprocess.SubprocessError, UnicodeError):
                pass
        contract = "unchecked" if provider.headless else "gated"
        contract_reason = (
            "Local help compatibility not checked" if provider.headless else provider.reason
        )
        if executable and compatibility and provider.headless:
            probe = probe_compatibility(key, executable)
            contract = "compatible" if probe["compatible"] else "incompatible"
            contract_reason = probe["reason"]
        rows.append(
            {
                "provider": key,
                "command": executable or command,
                "installed": executable is not None,
                "version": version,
                "auth": "unknown",
                "enabled": settings.enabled,
                "headless": provider.headless,
                "reason": provider.reason,
                "capabilities": list(provider.capabilities),
                "federation_capabilities": list(provider.federation_capabilities)
                if provider.headless
                else [],
                "compatibility": contract,
                "compatibility_reason": contract_reason,
            }
        )
    return rows
