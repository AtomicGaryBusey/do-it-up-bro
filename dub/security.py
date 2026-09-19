"""Best-effort secret minimization for artifacts (not a data-loss prevention system)."""

import os
import re

_SECRET_NAME = re.compile(
    r"token|secret|password|passwd|api_?key|cookie|credential|authorization", re.I
)
_ASSIGNMENT = re.compile(
    r"(?i)((?:[\w-]*(?:token|secret|password|passwd|api[_-]?key|cookie|credential)[\w-]*|authorization)[\"\']?\s*[=:]\s*[\"\']?)([^\s\"\',;}]+)"
)


def redact(text: str) -> str:
    for name, value in os.environ.items():
        if _SECRET_NAME.search(name) and len(value) >= 4:
            text = text.replace(value, "[REDACTED]")
    text = re.sub(r"(?i)Bearer\s+[^\s\"']+", "Bearer [REDACTED]", text)
    text = re.sub(r"\b(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{8,}", "[REDACTED]", text)
    return _ASSIGNMENT.sub(r"\1[REDACTED]", text)


def child_environment() -> dict[str, str]:
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
    return {key: value for key, value in os.environ.items() if key in allowed}
