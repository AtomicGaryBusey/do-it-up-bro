import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from dub.config import Config, ProviderConfig
from dub.supervisor import capture, plan, run


class SupervisorTests(unittest.TestCase):
    def test_cancellation_cleans_children_and_finalizes_ledger(self):
        cancellation = threading.Event()
        timer = threading.Timer(0.15, cancellation.set)
        with tempfile.TemporaryDirectory() as directory:
            started = time.monotonic()
            timer.start()
            try:
                with patch(
                    "dub.supervisor.build_command",
                    return_value=[sys.executable, "-c", "import time;time.sleep(30)"],
                ):
                    result = run(self.config(directory), "test", cancellation=cancellation)
            finally:
                timer.cancel()
            self.assertLess(time.monotonic() - started, 3)
            self.assertEqual(result["status"], "interrupted")
            self.assertTrue(all(row["status"] == "interrupted" for row in result["results"]))
            with sqlite3.connect(Path(result["run_dir"]) / "ledger.sqlite3") as db:
                self.assertEqual(db.execute("SELECT status FROM runs").fetchone()[0], "interrupted")

    def test_keyboard_interrupt_signals_worker_cancellation(self):
        from concurrent.futures import Future

        original = Future.result
        called = False

        def interrupt_once(future, *args, **kwargs):
            nonlocal called
            if not called:
                called = True
                raise KeyboardInterrupt
            return original(future, *args, **kwargs)

        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(Future, "result", interrupt_once),
                patch(
                    "dub.supervisor.build_command",
                    return_value=[sys.executable, "-c", "import time;time.sleep(30)"],
                ),
            ):
                result = run(self.config(directory), "test")
            self.assertEqual(result["status"], "interrupted")

    def test_capture_streams_and_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            result = capture(
                [
                    sys.executable,
                    "-c",
                    "import sys;print('out');print('err',file=sys.stderr);sys.exit(3)",
                ],
                directory,
                5,
            )
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["return_code"], 3)
            self.assertEqual(result["stdout"], "out\n")
            self.assertEqual(result["stderr"], "err\n")

    def test_timeout_and_output_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            result = capture([sys.executable, "-c", "import time;time.sleep(10)"], directory, 0.1)
            self.assertEqual(result["status"], "timeout")
            result = capture([sys.executable, "-c", "print('x'*2000000)"], directory, 5)
            self.assertEqual(result["status"], "output_limit")
            self.assertEqual(result["stdout"], "")

    def test_descendant_holding_pipe_does_not_hang(self):
        with tempfile.TemporaryDirectory() as directory:
            started = time.monotonic()
            result = capture(
                [
                    sys.executable,
                    "-c",
                    "import subprocess,sys;subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)'])",
                ],
                directory,
                0.2,
            )
            self.assertEqual(result["status"], "timeout")
            self.assertLess(time.monotonic() - started, 3)

    def config(self, directory):
        return Config(
            run_dir=Path(directory) / "runs",
            max_parallel_providers=2,
            providers={key: ProviderConfig(command=sys.executable) for key in ("codex", "claude")},
        )

    def test_dry_plan_no_writes_or_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "dub.supervisor.subprocess.Popen", side_effect=AssertionError("must not launch")
            ):
                result = plan(self.config(directory), "test")
            self.assertEqual(len(result["assignments"]), 2)
            self.assertFalse((Path(directory) / "runs").exists())

    def test_partial_failure_artifacts_ledger_and_parallelism(self):
        def command(provider, executable, prompt, **kwargs):
            code = "import time;time.sleep(.3);print('api_key=do-not-persist');"
            if provider == "claude":
                code += "raise SystemExit(4)"
            return [executable, "-c", code]

        with tempfile.TemporaryDirectory() as directory:
            started = time.monotonic()
            with patch("dub.supervisor.build_command", side_effect=command):
                result = run(self.config(directory), "Analyze api_key=goal-secret")
            self.assertLess(time.monotonic() - started, 1.5)
            self.assertEqual(result["status"], "partial")
            run_dir = Path(result["run_dir"])
            self.assertTrue((run_dir / "SYNTHESIS.md").exists())
            with sqlite3.connect(run_dir / "ledger.sqlite3") as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0], 2)
            for path in run_dir.rglob("*"):
                if path.is_file():
                    self.assertNotIn(b"do-not-persist", path.read_bytes())
                    self.assertNotIn(b"goal-secret", path.read_bytes())

    def test_launches_independent_providers_concurrently(self):
        barrier = threading.Barrier(2, timeout=3)

        def fake_capture(*args):
            barrier.wait()
            return {
                "status": "completed",
                "failure_reason": None,
                "return_code": 0,
                "stdout": "ok",
                "stderr": "",
            }

        with tempfile.TemporaryDirectory() as directory:
            with patch("dub.supervisor.capture", side_effect=fake_capture):
                result = run(self.config(directory), "test")
            self.assertEqual(result["status"], "completed")
