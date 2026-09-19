import subprocess
import unittest
from unittest.mock import patch

from dub.config import Config
from dub.providers.base import REQUIRED_HELP, build_command, detect, probe_compatibility


class CompatibilityTests(unittest.TestCase):
    def test_required_help_contracts(self):
        for key, tokens in REQUIRED_HELP.items():
            with self.subTest(provider=key):
                result = subprocess.CompletedProcess([], 0, "\n".join(tokens), "")
                with patch("dub.providers.base.subprocess.run", return_value=result) as run:
                    self.assertTrue(probe_compatibility(key, key)["compatible"])
                    self.assertIn("--help", run.call_args.args[0])
                    self.assertNotIn("-p", run.call_args.args[0])
                for missing in tokens:
                    result.stdout = "\n".join(t for t in tokens if t != missing)
                    with patch("dub.providers.base.subprocess.run", return_value=result):
                        probe = probe_compatibility(key, key)
                        self.assertFalse(probe["compatible"])
                        self.assertIn(missing, probe["reason"])

    def test_probe_errors_fail_closed(self):
        for error in (OSError("bad"), subprocess.TimeoutExpired("test", 5), UnicodeError()):
            with patch("dub.providers.base.subprocess.run", side_effect=error):
                self.assertFalse(probe_compatibility("kimi", "kimi")["compatible"])
        with patch(
            "dub.providers.base.subprocess.run",
            return_value=subprocess.CompletedProcess([], 1, "", ""),
        ):
            self.assertFalse(probe_compatibility("claude", "claude")["compatible"])

    def test_dry_detection_does_not_probe(self):
        with (
            patch("dub.providers.base.shutil.which", return_value="fake"),
            patch("dub.providers.base.subprocess.run") as run,
        ):
            rows = detect(Config(), versions=False)
        run.assert_not_called()
        self.assertEqual(rows[0]["compatibility"], "unchecked")

    def test_legacy_kimi_incompatible(self):
        legacy = subprocess.CompletedProcess([], 0, "--prompt --output-format text", "")
        with (
            patch("dub.providers.base.shutil.which", return_value="fake"),
            patch("dub.providers.base.subprocess.run", return_value=legacy),
        ):
            rows = {r["provider"]: r for r in detect(Config(), versions=False, compatibility=True)}
        self.assertEqual(rows["kimi"]["compatibility"], "incompatible")
        self.assertIn("--agent-file", rows["kimi"]["compatibility_reason"])

    def test_worker_restrictions_and_effort(self):
        claude = build_command("claude", "claude", "goal")
        for flag in (
            "--restricted",
            "--strict-mcp-config",
            "--permission-prompts",
            "--no-session-persistence",
            "--disable-slash-commands",
        ):
            self.assertIn(flag, claude)
        self.assertNotIn("--bare", claude)
        with self.assertRaises(ValueError):
            build_command("claude", "claude", "goal", effort="ultracode")
        grok = build_command("grok", "grok", "goal", prompt_file="/tmp/prompt.txt")
        self.assertEqual(grok[-2:], ["--prompt-file", "/tmp/prompt.txt"])
        self.assertNotIn("goal", grok)
        for flag in ("--tools", "--no-subagents", "--disable-web-search", "--max-turns", "--agent"):
            self.assertIn(flag, grok)
        with self.assertRaises(ValueError):
            build_command("grok", "grok", "goal", effort="unlimited")
        with self.assertRaises(ValueError):
            build_command("grok", "grok", "goal", prompt_file="--bad")

    def test_federation_does_not_advertise_native_orchestration(self):
        rows = detect(Config(), versions=False)
        for row in rows:
            self.assertNotIn("subagents", row["federation_capabilities"])
            self.assertNotIn("workflows", row["federation_capabilities"])
