"""Local CLI and skill diagnostics, without authentication or inference calls."""

from pathlib import Path

from dub.assets import asset_root
from dub.config import Config
from dub.installer import skill_destination
from dub.providers.base import detect


def doctor(config: Config, *, project: Path | None = None) -> list[dict]:
    root = asset_root()
    rows = detect(config, compatibility=True)
    for row in rows:
        key = row["provider"]
        row["adapter"] = (root / "adapters" / key / "README.md").is_file()
        row["skill_installed"] = (skill_destination(key) / "SKILL.md").is_file()
        row["project_skill_installed"] = (
            (skill_destination(key, project=project) / "SKILL.md").is_file()
            if project is not None
            else None
        )
    return rows
