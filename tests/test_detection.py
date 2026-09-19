import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dub.config import Config
from dub.providers.base import build_command, detect


class DetectionTests(unittest.TestCase):
    def test_antigravity_version_probe_remains_federation_gated(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "agy"
            path.write_text('#!/bin/sh\n[ "$1" = "--version" ] || exit 99\necho 1.2.7\n')
            path.chmod(0o755)
            with patch.dict(os.environ, {"PATH": folder}):
                rows = {row["provider"]: row for row in detect(Config())}
            self.assertTrue(rows["agy"]["installed"])
            self.assertEqual(rows["agy"]["version"], "1.2.7")
            self.assertFalse(rows["google"]["installed"])
            self.assertFalse(rows["agy"]["headless"])
            with self.assertRaises(ValueError):
                build_command("agy", str(path), "test")

    def test_fake_executable_versions_and_absence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "codex"
            path.write_text('#!/bin/sh\n[ "$1" = "--version" ] || exit 9\necho "fake 1.2"\n')
            path.chmod(0o755)
            with patch.dict(os.environ, {"PATH": folder}):
                rows = {row["provider"]: row for row in detect(Config())}
            self.assertEqual(rows["codex"]["version"], "fake 1.2")
            self.assertEqual(rows["codex"]["auth"], "unknown")
            self.assertFalse(rows["claude"]["installed"])

    def test_hung_version_is_unknown(self):
        with (
            patch("dub.providers.base.shutil.which", return_value="fake"),
            patch(
                "dub.providers.base.subprocess.run",
                side_effect=subprocess.TimeoutExpired("fake", 5),
            ),
        ):
            self.assertTrue(all(row["version"] == "unknown" for row in detect(Config())))

    def test_prompt_stays_one_argument_and_restrictions_hold(self):
        prompt = 'DUB work: $(touch /tmp/never) ; "quoted"\nnext'
        for key in ("codex", "claude", "grok", "kimi"):
            args = build_command(key, key, prompt)
            self.assertEqual(args[-1], prompt)
        self.assertIn("read-only", build_command("codex", "codex", prompt))
        self.assertIn("Read,Glob,Grep", build_command("claude", "claude", prompt))
        self.assertIn("mcp__*", build_command("claude", "claude", prompt))
        self.assertIn("read-only", build_command("grok", "grok", prompt))
        args = build_command("kimi", "kimi", prompt)
        policy = Path(args[args.index("--agent-file") + 1]).read_text()
        self.assertIn("  - Read", policy)
        self.assertNotIn("  - Bash", policy)

    def test_capability_gates_and_effort(self):
        with self.assertRaises(ValueError):
            build_command("google", "gemini", "test")
        with self.assertRaises(ValueError):
            build_command("kimi", "kimi", "test", effort="high")
        with self.assertRaises(ValueError):
            build_command("codex", "codex", "test", model="--bad-flag")
        self.assertIn(
            'model_reasoning_effort="ultra"',
            build_command("codex", "codex", "test", effort="ultra"),
        )
