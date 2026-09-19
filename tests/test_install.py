import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
            for provider in ("codex", "claude", "google", "grok", "kimi", "agy"):
                result = install(provider, project=project)
                self.assertTrue(Path(result["destination"]).is_relative_to(project))
                if provider == "agy":
                    self.assertEqual(result["action"], "already-installed")

    def test_relocated_provider_roots_and_project_precedence(self):
        for provider, variable in (
            ("kimi", "KIMI_CODE_HOME"),
            ("grok", "GROK_HOME"),
            ("claude", "CLAUDE_CONFIG_DIR"),
        ):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as folder:
                root = Path(folder).resolve()
                with patch.dict(os.environ, {variable: str(root / "relocated")}):
                    self.assertEqual(
                        skill_destination(provider), root / "relocated/skills/do-it-up-bro"
                    )
                    self.assertTrue(
                        skill_destination(provider, project=root / "project").is_relative_to(
                            root / "project"
                        )
                    )

    def test_shared_project_bundle_keeps_both_adapters_and_refuses_user_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            first = install("agy", project=root)
            target = Path(first["destination"])
            self.assertEqual(install("codex", project=root)["action"], "already-installed")
            for host in ("codex", "agy"):
                self.assertTrue((target / f"references/{host}-host-adapter.md").is_file())
            (target / "user-note.txt").write_text("keep")
            self.assertEqual(install("codex", project=root)["action"], "conflict")

    def test_antigravity_personal_and_project_locations_are_distinct(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder).resolve()
            personal = install("agy", home=home)
            self.assertEqual(
                Path(personal["destination"]), home / ".gemini/antigravity-cli/skills/do-it-up-bro"
            )
            adapter = Path(personal["destination"]) / "references/host-adapter.md"
            self.assertIn("# Google Antigravity CLI adapter", adapter.read_text())
            project = install("agy", project=home / "project")
            self.assertEqual(
                Path(project["destination"]), home / "project/.agents/skills/do-it-up-bro"
            )
            self.assertFalse((home / ".gemini/skills").exists())

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
