"""Locate the same protocol assets in a checkout or an installed wheel."""

import sys
import sysconfig
from pathlib import Path


def asset_root() -> Path:
    candidates = (
        Path(__file__).resolve().parent.parent,
        Path(sys.prefix) / "share" / "dub",
        Path(sysconfig.get_path("data")) / "share" / "dub",
        Path(sysconfig.get_path("data", scheme=sysconfig.get_preferred_scheme("user")))
        / "share"
        / "dub",
    )
    for candidate in candidates:
        if (candidate / "skills" / "do-it-up-bro" / "SKILL.md").is_file():
            return candidate
    raise FileNotFoundError("DUB protocol assets missing; reinstall the distribution")
