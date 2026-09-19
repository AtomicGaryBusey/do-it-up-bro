"""Best-effort secret minimization for artifacts (not a data-loss prevention system)."""

import json
import os
import re
from pathlib import Path

PROVIDER_HOME_VARIABLES = {
    "claude": "CLAUDE_CONFIG_DIR",
    "grok": "GROK_HOME",
    "kimi": "KIMI_CODE_HOME",
}

_SECRET_NAME = re.compile(
    r"token|secret|password|passwd|api_?key|cookie|credential|authorization", re.I
)
_ASSIGNMENT = re.compile(
    r"(?i)((?:[\w-]*(?:token|secret|password|passwd|api[_-]?key|cookie|credential)[\w-]*|authorization)[\"\']?\s*[=:]\s*[\"\']?)([^\s\"\',;}]+)"
)


def _redact_text(text: str) -> str:
    for name, value in os.environ.items():
        if _SECRET_NAME.search(name) and len(value) >= 4:
            text = text.replace(value, "[REDACTED]")
    text = re.sub(r"(?i)Bearer\s+[^\s\"']+", "Bearer [REDACTED]", text)
    text = re.sub(r"\b(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{8,}", "[REDACTED]", text)
    return _ASSIGNMENT.sub(r"\1[REDACTED]", text)


_NUMERIC_METRICS = {
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "reasoning_tokens",
    "total_tokens",
    "inputTokens",
    "outputTokens",
    "cacheReadInputTokens",
    "cacheCreationInputTokens",
    "maxOutputTokens",
}


def redact(text: str) -> str:
    """Preserve JSON types; token-count metrics are not authentication tokens."""

    def clean(value, field=""):
        if _SECRET_NAME.search(field):
            if field not in _NUMERIC_METRICS or type(value) not in (int, float):
                return "[REDACTED]"
        if isinstance(value, str):
            # Ledger JSON can itself be a string inside result.json. Preserve its
            # typed counters too, while still redacting nested credential fields.
            return redact(value)
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, dict):
            return {_redact_text(key): clean(item, key) for key, item in value.items()}
        return value

    try:
        value = json.loads(text)
        if isinstance(value, (dict, list)):
            return json.dumps(clean(value), ensure_ascii=False)
    except (ValueError, RecursionError):
        pass
    return _redact_text(text)


def child_environment(provider: str | None = None) -> dict[str, str]:
    """Keep normal home-based CLI login, but do not forward API keys or arbitrary env."""
    allowed = {
        "HOME",
        "PATH",
        "USER",
        "LOGNAME",
        "LANG",
        "LC_ALL",
        "TERM",
        "TMPDIR",
        "SYSTEMROOT",
        "WINDIR",
        "APPDATA",
        "LOCALAPPDATA",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_CACHE_HOME",
    }
    result = {key: value for key, value in os.environ.items() if key in allowed}
    variable = PROVIDER_HOME_VARIABLES.get(provider)
    if variable and os.environ.get(variable):
        # Resolve before changing cwd to the isolated worker directory. Forward
        # only this provider's location, never arbitrary configuration or keys.
        result[variable] = str(Path(os.environ[variable]).expanduser().absolute())
    return result
