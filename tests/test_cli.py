import contextlib
import io
import unittest
from unittest.mock import patch

from dub.cli import main


class CliTests(unittest.TestCase):
    def test_partial_install_reports_success_before_later_failure(self):
        rows = [{"provider": "codex", "installed": True}, {"provider": "claude", "installed": True}]
        with (
            contextlib.redirect_stdout(io.StringIO()) as output,
            patch("dub.cli.detect", return_value=rows),
            patch(
                "dub.cli.install",
                side_effect=[{"provider": "codex", "action": "copy"}, PermissionError("denied")],
            ),
        ):
            self.assertEqual(main(["install"]), 2)
        self.assertIn('"action": "copy"', output.getvalue())
        self.assertIn('"action": "error"', output.getvalue())

    def test_dry_run_and_invalid_config_exit(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(main(["herdr", "--target", "reviewer", "--dry-run", "test"]), 0)
        self.assertIn("Do it up, Bro", stdout.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--config", "/nonexistent/dub.toml", "doctor"]), 2)

    def test_conflict_and_federation_failure_exit_codes(self):
        with (
            contextlib.redirect_stdout(io.StringIO()),
            patch("dub.cli.install", return_value={"action": "conflict"}),
        ):
            self.assertEqual(main(["install", "--provider", "codex", "--dry-run"]), 1)
        with (
            contextlib.redirect_stdout(io.StringIO()),
            patch("dub.supervisor.run", return_value={"status": "failed"}),
        ):
            self.assertEqual(main(["federate", "test"]), 1)
