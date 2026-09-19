import tempfile
import unittest
from pathlib import Path

from dub.installer import install, skill_destination


class InstallTests(unittest.TestCase):
    def test_dry_run_copy_conflict_and_recoverable_force(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder).resolve()
            preview = install("codex", home=home, dry_run=True)
            self.assertEqual(preview["action"], "copy")
            self.assertEqual(list(home.iterdir()), [])
            result = install("codex", home=home)
            target = Path(result["destination"])
            self.assertTrue((target / "references/host-adapter.md").is_file())
            (target / "user-notes.md").write_text("preserve me")
            self.assertEqual(install("codex", home=home)["action"], "conflict")
            result = install("codex", home=home, force=True)
            backup = Path(result["backup"])
            self.assertEqual((backup / "user-notes.md").read_text(), "preserve me")
            self.assertFalse(backup.is_relative_to(target.parent))
            self.assertFalse((target / "user-notes.md").exists())

    def test_all_provider_project_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder).resolve()
            for provider in ("codex", "claude", "google", "grok", "kimi"):
                result = install(provider, project=project)
                self.assertTrue(Path(result["destination"]).is_relative_to(project))

    def test_symlink_target_preserved_and_ancestor_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder).resolve()
            original = home / "original"
            original.mkdir()
            (original / "user.txt").write_text("safe")
            target = skill_destination("codex", home=home)
            target.parent.mkdir(parents=True)
            target.symlink_to(original, target_is_directory=True)
            self.assertEqual(install("codex", home=home)["action"], "conflict")
            result = install("codex", home=home, force=True)
            self.assertTrue(Path(result["backup"]).is_symlink())
            self.assertEqual((original / "user.txt").read_text(), "safe")
            (home / ".claude").symlink_to(original, target_is_directory=True)
            with self.assertRaises(ValueError):
                install("claude", home=home, dry_run=True)
