"""Small, strict TOML configuration. No credentials belong in this file."""

import math
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

COMMANDS = {
    "codex": "codex",
    "claude": "claude",
    "google": "gemini",
    "grok": "grok",
    "kimi": "kimi",
}


@dataclass(frozen=True)
class ProviderConfig:
    enabled: bool = True
    command: str = ""
    model: str | None = None
    effort: str | None = None


@dataclass(frozen=True)
class Config:
    run_dir: Path = Path(".dub/runs")
    max_parallel_providers: int = 3
    provider_timeout_seconds: float = 1800
    enabled: bool = True
    synthesis_provider: str | None = None
    default_mode: str = "native"
    install_strategy: str = "copy"
    providers: dict[str, ProviderConfig] = field(
        default_factory=lambda: {key: ProviderConfig(command=cmd) for key, cmd in COMMANDS.items()}
    )


def _keys(table: dict, allowed: set[str], label: str) -> None:
    if not isinstance(table, dict):
        raise ValueError(f"{label} must be a TOML table")
    extra = set(table) - allowed
    if extra:
        raise ValueError(f"Unknown {label} options: {', '.join(sorted(extra))}")


def _boolean(value, label):
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be true or false")
    return value


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or "\0" in value:
        raise ValueError(f"{label} must be a nonempty string without NUL")
    return value


def load_config(path: Path | str | None = None) -> Config:
    selected = Path(path) if path is not None else Path("DUB.toml")
    if not selected.exists() and path is None:
        return Config()
    with selected.open("rb") as stream:
        raw = tomllib.load(stream)
    _keys(raw, {"dub", "install", "federation", "providers"}, "root")
    general = raw.get("dub", {})
    install = raw.get("install", {})
    federation = raw.get("federation", {})
    providers = raw.get("providers", {})
    _keys(
        general,
        {"default_mode", "run_dir", "max_parallel_providers", "provider_timeout_seconds"},
        "dub",
    )
    _keys(install, {"strategy"}, "install")
    _keys(federation, {"enabled", "synthesis_provider"}, "federation")
    _keys(providers, set(COMMANDS), "providers")
    parallel = general.get("max_parallel_providers", 3)
    timeout = general.get("provider_timeout_seconds", 1800)
    if type(parallel) is not int or not 1 <= parallel <= 32:
        raise ValueError("max_parallel_providers must be an integer from 1 to 32")
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("provider_timeout_seconds must be finite and positive")
    mode = general.get("default_mode", "native")
    if mode not in ("native", "campaign", "federate"):
        raise ValueError("default_mode must be native, campaign, or federate")
    strategy = install.get("strategy", "copy")
    if strategy != "copy":
        raise ValueError("v0.1 supports install strategy 'copy' only")
    synthesis = federation.get("synthesis_provider")
    if synthesis is not None:
        synthesis = _text(synthesis, "synthesis_provider")
    if synthesis is not None and synthesis not in COMMANDS:
        raise ValueError("Unknown synthesis_provider")
    configured = {}
    for key, command in COMMANDS.items():
        settings = providers.get(key, {})
        _keys(settings, {"enabled", "command", "model", "effort"}, f"providers.{key}")
        command = settings.get("command", command)
        if command == "AUTO_DETECT":
            command = COMMANDS[key]
        command = _text(command, f"{key}.command")
        # A command names one executable, never an argument string. Absolute paths
        # with spaces are valid and are passed as a single subprocess argument.
        if "/" in command:
            command_path = Path(command).expanduser()
            if not command_path.is_absolute():
                command_path = selected.resolve().parent / command_path
            command = str(command_path)
        configured[key] = ProviderConfig(
            enabled=_boolean(settings.get("enabled", True), f"{key}.enabled"),
            command=command,
            model=_text(settings["model"], f"{key}.model") if "model" in settings else None,
            effort=_text(settings["effort"], f"{key}.effort") if "effort" in settings else None,
        )
    run_dir = Path(_text(general.get("run_dir", ".dub/runs"), "run_dir")).expanduser()
    if not run_dir.is_absolute():
        run_dir = selected.resolve().parent / run_dir
    return Config(
        run_dir=run_dir,
        max_parallel_providers=parallel,
        provider_timeout_seconds=timeout,
        enabled=_boolean(federation.get("enabled", True), "federation.enabled"),
        synthesis_provider=synthesis,
        default_mode=mode,
        install_strategy=strategy,
        providers=configured,
    )
