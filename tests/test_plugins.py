import tarfile
from pathlib import Path

import pytest

from dub.plugins import export_plugin


@pytest.mark.parametrize(
    "provider,manifest", [("claude", ".claude-plugin/plugin.json"), ("grok", "plugin.json")]
)
def test_export(provider, manifest, tmp_path):
    output = tmp_path / provider
    assert export_plugin(provider, output, dry_run=True)["action"] == "export"
    assert not output.exists()
    export_plugin(provider, output)
    assert (output / manifest).is_file()
    assert (output / "skills/do-it-up-bro/references/host-adapter.md").is_file()
    if provider == "grok":
        assert (output / "agents/dub-reader.md").is_file()
        assert (output / "workflows/dub-campaign.rhai").is_file()
    (output / "user-note.txt").write_text("preserve me")
    assert export_plugin(provider, output)["action"] == "conflict"
    result = export_plugin(provider, output, force=True)
    with tarfile.open(result["backup"]) as archive:
        assert archive.extractfile(f"{provider}/user-note.txt").read() == b"preserve me"


def test_refuse_symlink_and_invalid_provider(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    with pytest.raises(ValueError, match="symlink"):
        export_plugin("claude", link / "bundle")
    with pytest.raises(ValueError, match="supports"):
        export_plugin("agy", tmp_path / "bundle")
    with pytest.raises(ValueError, match="dedicated"):
        export_plugin("claude", Path.cwd(), force=True)
