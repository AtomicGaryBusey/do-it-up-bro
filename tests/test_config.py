import tempfile
import unittest
from pathlib import Path

from dub.config import load_config


class ConfigTests(unittest.TestCase):
    def parse(self, content):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "DUB.toml"
            path.write_text(content)
            return load_config(path)

    def test_example_defaults_and_override(self):
        config = load_config("DUB.toml.example")
        self.assertEqual(config.providers["google"].command, "gemini")
        self.assertIsNone(config.providers["codex"].model)
        config = self.parse("[dub]\nmax_parallel_providers=2\n[providers.kimi]\nenabled=false\n")
        self.assertFalse(config.providers["kimi"].enabled)
        self.assertEqual(config.max_parallel_providers, 2)

    def test_invalid_and_misspelled_config(self):
        for content in (
            "[dub]\nmax_parallel_providers=true",
            "[dub]\nmax_parallel_providers=0",
            "[dub]\nprovider_timeout_seconds=nan",
            "[dub]\nprovider_timeout_seconds=-1",
            "[providers.unknown]\nenabled=true",
            "[dub]\nmax_parallel=3",
            '[providers.codex]\nenabled="yes"',
            '[install]\nstrategy="symlink"',
            'dub="not a table"',
        ):
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.parse(content)

    def test_relative_paths_are_config_relative(self):
        config = self.parse('[dub]\nrun_dir="outputs"\n[providers.codex]\ncommand="bin/fake"')
        self.assertTrue(config.run_dir.is_absolute())
        self.assertEqual(
            config.run_dir.parent, Path(config.providers["codex"].command).parent.parent
        )

    def test_explicit_missing_config_errors(self):
        with self.assertRaises(FileNotFoundError):
            load_config("/nonexistent/dub-test-config.toml")
