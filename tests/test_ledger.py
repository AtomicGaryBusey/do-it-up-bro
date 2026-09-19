import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dub.ledger import Ledger
from dub.security import child_environment, redact


class LedgerTests(unittest.TestCase):
    def test_unknown_metadata_and_redaction(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "ledger.db")
            ledger.record_task(task_id="t", run_id="r", provider="fake", status="completed")
            with ledger.connect() as db:
                self.assertEqual(
                    db.execute(
                        "SELECT model_observed,effort_observed,usage_if_exposed FROM tasks"
                    ).fetchone(),
                    (None, None, None),
                )
            with self.assertRaises(ValueError):
                ledger.record_task(**{"invalid); DROP TABLE tasks;": "bad"})

    def test_secret_environment_excluded_and_output_redacted(self):
        with patch.dict("os.environ", {"MY_API_KEY": "supersecret123", "HOME": "/safe/home"}):
            self.assertNotIn("MY_API_KEY", child_environment())
            self.assertEqual(child_environment()["HOME"], "/safe/home")
            self.assertNotIn("supersecret123", redact("text supersecret123"))
        self.assertNotIn("abc123", redact("api_key=abc123"))
        self.assertNotIn("abc123", redact("Authorization: Bearer abc123"))
        self.assertNotIn("abc123", redact('{"api_key": "abc123"}'))
