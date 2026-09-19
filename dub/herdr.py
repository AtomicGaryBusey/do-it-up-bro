"""Targeted Herdr prompt transport; never assume lifecycle means goal completion."""

import os
import re
import shutil
from pathlib import Path

from dub.security import child_environment, redact
from dub.supervisor import capture


def plan(target: str, goal: str, *, campaign: bool = False, timeout_ms: int = 1800000) -> dict:
    if not re.fullmatch(r"(?:[a-z][a-z0-9_-]{0,31}|w\d+:p\d+)", target):
        raise ValueError("Herdr target must be a live agent name or pane ID such as w1:p2")
    if not goal.strip() or "\0" in goal:
        raise ValueError("Goal must be nonempty and contain no NUL")
    if type(timeout_ms) is not int or not 1 <= timeout_ms <= 86400000:
        raise ValueError("timeout-ms must be between 1 and 86400000")
    prompt = f"Do it up, Bro{' --campaign' if campaign else ''}: {goal}"
    command = [
        shutil.which("herdr") or "herdr",
        "agent",
        "prompt",
        target,
        prompt,
        "--wait",
        "--timeout",
        str(timeout_ms),
    ]
    return {
        "target": target,
        "command": [redact(item) for item in command],
        "installed": shutil.which("herdr") is not None,
        "inside_herdr": os.environ.get("HERDR_ENV") == "1",
        "completion": "Lifecycle observation only; inspect the target's result",
        "retry": "Never retry automatically; a timeout can occur after submission",
    }


def send(target: str, goal: str, *, campaign: bool = False, timeout_ms: int = 1800000) -> dict:
    preview = plan(target, goal, campaign=campaign, timeout_ms=timeout_ms)
    if not preview["installed"]:
        raise ValueError("Herdr executable not found")
    if not preview["inside_herdr"]:
        raise ValueError("Run this command from a Herdr-managed pane (HERDR_ENV=1)")
    # Build from original goal; previews/logs are redacted, but user input is sent
    # verbatim as one argument without shell interpretation.
    prompt = f"Do it up, Bro{' --campaign' if campaign else ''}: {goal}"
    command = [
        shutil.which("herdr"),
        "agent",
        "prompt",
        target,
        prompt,
        "--wait",
        "--timeout",
        str(timeout_ms),
    ]
    environment = child_environment()
    for key in (
        "HERDR_ENV",
        "HERDR_CONFIG_PATH",
        "HERDR_SESSION",
        "HERDR_SOCKET_PATH",
        "HERDR_PANE_ID",
        "HERDR_TAB_ID",
        "HERDR_WORKSPACE_ID",
    ):
        if key in os.environ:
            environment[key] = os.environ[key]
    result = capture(command, Path.cwd(), timeout_ms / 1000 + 2, environment=environment)
    return {
        **preview,
        **result,
        "goal_verified": False,
        "warning": "Stopping this client does not cancel the existing target agent",
    }
