"""Small SQLite run/task ledger; unknown observed metadata stays NULL."""

import sqlite3
from pathlib import Path

from .security import redact


class Ledger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                  run_id TEXT PRIMARY KEY, goal TEXT, mode TEXT, started_at TEXT,
                  ended_at TEXT, status TEXT, artifact_path TEXT);
                CREATE TABLE IF NOT EXISTS tasks (
                  task_id TEXT PRIMARY KEY, run_id TEXT, parent_task_id TEXT,
                  provider TEXT, harness TEXT, model_requested TEXT, model_observed TEXT,
                  effort_requested TEXT, effort_observed TEXT, role TEXT, task_class TEXT,
                  started_at TEXT, ended_at TEXT, status TEXT, return_code INTEGER,
                  usage_if_exposed TEXT, verification_result TEXT, failure_reason TEXT,
                  artifact_path TEXT);
            """)

    def connect(self):
        return sqlite3.connect(self.path, timeout=30)

    def record_run(self, **values):
        self._record("runs", values)

    def record_task(self, **values):
        self._record("tasks", values)

    def _record(self, table, values):
        with self.connect() as db:
            allowed = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
            if not values or not set(values) <= allowed:
                raise ValueError("Invalid ledger fields")
            cleaned = {k: redact(v) if isinstance(v, str) else v for k, v in values.items()}
            columns = ",".join(cleaned)
            marks = ",".join("?" for _ in cleaned)
            db.execute(
                f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({marks})",
                list(cleaned.values()),
            )
