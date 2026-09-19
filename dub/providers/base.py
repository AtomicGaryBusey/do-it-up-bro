"""Auditable CLI contracts. Flags are sourced in the corresponding adapters."""

import json
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


PROVIDERS = {
    "codex": Provider(
        "codex",
        "codex",
        ".agents/skills",
        capabilities=("analysis", "model-selection", "subagents", "effort", "sandbox"),
    ),
    "claude": Provider(
        "claude",
        "claude",
        ".claude/skills",
        capabilities=("analysis", "model-selection", "subagents", "effort", "workflows"),
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
        version_args=None,
    ),
    "grok": Provider(
        "grok",
        "grok",
        ".grok/skills",
        capabilities=("analysis", "model-selection", "subagents", "effort", "sandbox", "workflows"),
        version_args=("version",),
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
) -> list[str]:
    provider = PROVIDERS[provider_key]
    if not provider.headless:
        raise ValueError(provider.reason)
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
            if effort not in {"low", "medium", "high", "xhigh", "max", "ultracode"}:
                raise ValueError("Unsupported Claude effort")
            args += ["--effort", effort]
        return args + ["--", prompt]
    if provider_key == "grok":
        args = [command, "--no-auto-update", "--sandbox", "read-only", "--output-format", "json"]
        if model:
            args += ["--model", model]
        if effort:
            args += ["--effort", effort]
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


def detect(config: Config, *, versions: bool = True) -> list[dict]:
    """Only version commands; auth always unknown, never trigger a model call."""
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
                    env=child_environment(),
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
            }
        )
    return rows
