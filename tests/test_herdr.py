import os
import unittest
from unittest.mock import patch

from dub.herdr import plan, send


class HerdrTests(unittest.TestCase):
    def test_plan_never_sends_and_goal_is_one_argument(self):
        goal = 'Review "x"; $(touch /tmp/never)'
        with patch("dub.herdr.capture", side_effect=AssertionError("no send")):
            result = plan("w1:p2", goal, campaign=True)
        self.assertEqual(result["command"][4], "Do it up, Bro --campaign: " + goal)

    def test_explicit_target_and_managed_context_required(self):
        for target in ("", "--current", "wrong target", "../agent"):
            with self.assertRaises(ValueError):
                plan(target, "test")
        with (
            patch.dict(os.environ, {"HERDR_ENV": "0"}),
            patch("dub.herdr.shutil.which", return_value="herdr"),
        ):
            with self.assertRaises(ValueError):
                send("reviewer", "test")

    def test_session_preserved_timeout_not_retried(self):
        with (
            patch.dict(
                os.environ,
                {
                    "HERDR_ENV": "1",
                    "HERDR_SOCKET_PATH": "/tmp/specific.sock",
                    "API_KEY": "test-secret",
                },
            ),
            patch("dub.herdr.shutil.which", return_value="herdr"),
            patch(
                "dub.herdr.capture", return_value={"status": "timeout", "return_code": 1}
            ) as capture,
        ):
            result = send("reviewer", "test", timeout_ms=1234)
        self.assertEqual(result["status"], "timeout")
        self.assertFalse(result["goal_verified"])
        capture.assert_called_once()
        self.assertEqual(
            capture.call_args.kwargs["environment"]["HERDR_SOCKET_PATH"], "/tmp/specific.sock"
        )
        self.assertNotIn("API_KEY", capture.call_args.kwargs["environment"])
