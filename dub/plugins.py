"""Export self-contained native plugins without installing or registering them."""

import json
import shutil
import tarfile
import tempfile
import uuid
from pathlib import Path

from dub.assets import asset_root


def export_plugin(provider: str, output: Path, dry_run: bool = False, force: bool = False) -> dict:
    """Build a host-specific plugin; replacements preserve a non-discoverable archive."""
    if provider not in {"claude", "grok"}:
        raise ValueError("Plugin export supports claude and grok only")
    output = Path(output).expanduser().absolute()
    if output == Path(output.anchor) or output == Path.home() or output == Path.cwd():
        raise ValueError("Plugin output must be a dedicated bundle directory")
    for parent in output.parents:
        if parent.is_symlink():
            raise ValueError(f"Refusing symlink plugin ancestor: {parent}")
    if output.is_symlink():
        raise ValueError("Refusing symlink plugin destination")
    exists = output.exists()
    if exists and not output.is_dir():
        raise ValueError("Plugin destination must be a directory")
    root = asset_root()
    source = root / "skills/do-it-up-bro"
    files = {
        "skills/do-it-up-bro/" + str(p.relative_to(source)): p
        for p in source.rglob("*")
        if p.is_file()
    }
    files["skills/do-it-up-bro/references/host-adapter.md"] = (
        root / "adapters" / provider / "README.md"
    )
    if provider == "grok":
        files["agents/dub-reader.md"] = root / "adapters/grok/readonly-agent.md"
        files["workflows/dub-campaign.rhai"] = root / "adapters/grok/do-it-up-bro.rhai"
    for path in files.values():
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Invalid plugin source: {path}")
    manifest_path = ".claude-plugin/plugin.json" if provider == "claude" else "plugin.json"
    result = {
        "provider": provider,
        "destination": str(output),
        "dry_run": dry_run,
        "action": "conflict" if exists and not force else "export",
        "files": sorted([*files, manifest_path]),
    }
    if exists and not force:
        result["reason"] = "Already exists; --force preserves a tar.gz backup"
        return result
    if dry_run:
        result["action"] = "replace-with-backup" if exists else "export"
        return result
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".dub-plugin-", dir=output.parent))
    recovery = None
    try:
        bundle = staging / "bundle"
        bundle.mkdir()
        for name, src in files.items():
            dest = bundle / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        manifest = bundle / manifest_path
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                {
                    "name": "do-it-up-bro",
                    "version": "0.1.0",
                    "description": "Native DUB orchestration skill and host adapter",
                    "author": {"name": "AtomicGaryBusey"},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        if exists:
            backup = output.parent / f"{output.name}.dub-backup-{uuid.uuid4().hex}.tar.gz"
            # An archive is not a discovered plugin directory. Do not dereference links.
            with tarfile.open(backup, "x:gz", dereference=False) as archive:
                archive.add(output, arcname=output.name, recursive=True)
            recovery = staging / "previous"
            output.rename(recovery)
            result.update(action="replace-with-backup", backup=str(backup))
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Plugin destination appeared: {output}")
        bundle.rename(output)
        return result
    except BaseException:
        if recovery is not None and recovery.exists() and not output.exists():
            recovery.rename(output)
        raise
    finally:
        shutil.rmtree(staging)
