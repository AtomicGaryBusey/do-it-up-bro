"""Install a self-contained skill bundle with recoverable explicit replacement."""

import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dub.assets import asset_root
from dub.providers.base import PROVIDERS


def skill_destination(
    provider: str, *, project: Path | None = None, home: Path | None = None
) -> Path:
    base = project if project is not None else (home or Path.home())
    if provider == "kimi" and project is None and home is None and os.environ.get("KIMI_CODE_HOME"):
        return Path(os.environ["KIMI_CODE_HOME"]).expanduser() / "skills/do-it-up-bro"
    return base / PROVIDERS[provider].skill_directory / "do-it-up-bro"


def install(
    provider: str,
    *,
    project: Path | None = None,
    home: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    root = asset_root()
    source = root / "skills/do-it-up-bro"
    adapter = root / "adapters" / provider / "README.md"
    if not adapter.is_file():
        raise FileNotFoundError(f"Missing packaged adapter: {provider}")
    destination = skill_destination(provider, project=project, home=home)
    exists = destination.exists() or destination.is_symlink()
    result = {
        "provider": provider,
        "destination": str(destination),
        "action": "replace-with-backup" if exists and force else "copy",
        "dry_run": dry_run,
        "files": sorted(
            str(path.relative_to(source)) for path in source.rglob("*") if path.is_file()
        )
        + ["references/host-adapter.md"],
    }
    # Do not follow redirected installation roots into unexpected trees.
    for parent in (destination.parent, *destination.parents):
        if parent.is_symlink():
            raise ValueError(f"Refusing symlink installation ancestor: {parent}")
    if exists and not force:
        result["action"] = "conflict"
        result["reason"] = "Already exists; --force preserves the old entry outside skill discovery"
        return result
    backup_root = destination.parent.parent / "dub-backups"
    if exists and force:
        if backup_root.is_symlink():
            raise ValueError(f"Refusing symlink backup root: {backup_root}")
        result["backup_directory"] = str(backup_root)
    if dry_run:
        return result
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".dub-install-", dir=destination.parent))
    backup = None
    try:
        shutil.copytree(source, staging, dirs_exist_ok=True)
        (staging / "references").mkdir(exist_ok=True)
        shutil.copy2(adapter, staging / "references/host-adapter.md")
        if exists:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup_root.mkdir(parents=True, exist_ok=True)
            backup = backup_root / f"do-it-up-bro-{stamp}-{uuid.uuid4().hex[:8]}"
            destination.rename(backup)
        # rename never follows a destination symlink; unexpected concurrent installs
        # are rejected by rechecking before publishing.
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"Destination appeared during installation: {destination}")
        staging.rename(destination)
        if backup:
            result["backup"] = str(backup)
        return result
    except BaseException:
        if backup and not destination.exists() and not destination.is_symlink():
            backup.rename(destination)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
