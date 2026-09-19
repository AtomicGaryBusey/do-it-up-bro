"""Local CLI and skill diagnostics, without authentication or inference calls."""

from dub.assets import asset_root
from dub.config import Config
from dub.installer import skill_destination
from dub.providers.base import detect


def doctor(config: Config) -> list[dict]:
    root = asset_root()
    rows = detect(config)
    for row in rows:
        key = row["provider"]
        row["adapter"] = (root / "adapters" / key / "README.md").is_file()
        row["skill_installed"] = (skill_destination(key) / "SKILL.md").is_file()
    return rows
