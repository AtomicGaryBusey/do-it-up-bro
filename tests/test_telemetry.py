"""Synthetic provider envelopes; these tests never invoke a vendor/model."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dub.ledger import Ledger
from dub.security import redact
from dub.supervisor import capture
from dub.telemetry import parse_result


def claude_result(**extra):
    return dict(type="result", subtype="success", is_error=False, **extra)


def grok_result(**extra):
    return dict(sessionId="synthetic-session", stopReason="end_turn", **extra)


class TelemetryTests(unittest.TestCase):
    def test_success_metadata_is_valid_json_with_numeric_tokens(self):
        for provider, payload in (
            ("claude", claude_result(usage={"input_tokens": 8, "output_tokens": 2})),
            ("grok", grok_result(usage={"input_tokens": 8, "output_tokens": 2})),
        ):
            with self.subTest(provider=provider):
                parsed = parse_result(provider, json.dumps(payload))
                self.assertEqual(json.loads(parsed["usage_if_exposed"])["usage"], payload["usage"])
                self.assertIsNone(parsed["effort_observed"])

    def test_models_are_observed_only_with_recognized_metrics(self):
        payload = claude_result(
            modelUsage={
                "model-b": {"costUSD": 0, "inputTokens": 2},
                "model-a": {"outputTokens": 1},
                "unsupported": {"something": 9},
                "invalid model": {"inputTokens": 2},
            }
        )
        parsed = parse_result("claude", json.dumps(payload))
        self.assertEqual(parsed["model_observed"], "model-a,model-b")
        usage = json.loads(parsed["usage_if_exposed"])
        self.assertEqual(set(usage["modelUsage"]), {"model-a", "model-b"})

    def test_untrusted_denial_inputs_never_enter_metadata(self):
        payload = claude_result(
            permission_denials=[
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "do-not-copy-me"},
                }
            ],
            result="also-do-not-copy",
            session_id="private-session",
        )
        parsed = parse_result("claude", json.dumps(payload))
        self.assertEqual(json.loads(parsed["usage_if_exposed"]), {"permission_denial_count": 1})
        self.assertNotIn("do-not-copy", str(parsed))
        self.assertNotIn("private-session", str(parsed))

    def test_incomplete_grok_metadata_is_unknown(self):
        for field in ("usage_is_incomplete", "cost_is_partial"):
            for marker in (True, "false", 0, None):
                with self.subTest(field=field, marker=marker):
                    payload = grok_result(
                        usage={"input_tokens": 1}, modelUsage={"grok": {"inputTokens": 1}}
                    )
                    payload[field] = marker
                    parsed = parse_result("grok", json.dumps(payload))
                    self.assertIsNone(parsed["usage_if_exposed"])
                    self.assertIsNone(parsed["model_observed"])

    def test_malformed_and_unrecognized_payloads_remain_unknown(self):
        payloads = [
            "",
            "not-json",
            "[]",
            "null",
            '{"type":"result","type":"result"}',
            "[" * 1100 + "]" * 1100,
            "x" * 1_048_577,
        ]
        for provider in ("claude", "grok", "kimi"):
            for payload in payloads:
                with self.subTest(provider=provider, prefix=payload[:20]):
                    result = parse_result(provider, payload)
                    self.assertIsNone(result["model_observed"])
                    self.assertIsNone(result["usage_if_exposed"])

    def test_invalid_numeric_fields_are_not_retained(self):
        payload = claude_result(
            usage={"input_tokens": True, "output_tokens": -1, "total_tokens": 10**30},
            total_cost_usd=float("nan"),
            num_turns="2",
        )
        self.assertIsNone(parse_result("claude", json.dumps(payload))["usage_if_exposed"])

    def test_error_metadata_does_not_override_failure_or_invent_cost(self):
        payload = {"type": "error", "message": "private diagnostic", "usage_is_incomplete": True}
        parsed = parse_result("grok", json.dumps(payload))
        self.assertEqual(parsed["failure_reason"], "Grok result reported an error")
        self.assertIsNone(parsed["usage_if_exposed"])
        payload = claude_result()
        payload["is_error"] = True
        self.assertIsNotNone(parse_result("claude", json.dumps(payload))["failure_reason"])

    def test_success_label_does_not_hide_aborted_claude_turn(self):
        for reason in ("aborted_streaming", "aborted_tools"):
            result = parse_result("claude", json.dumps(claude_result(terminal_reason=reason)))
            self.assertIsNotNone(result["failure_reason"])

    @unittest.skipUnless(os.name == "posix", "capture uses POSIX process groups")
    def test_exit_zero_error_envelope_is_failed(self):
        payload = dict(
            type="result",
            subtype="error_max_turns",
            is_error=True,
            permission_denials=[{"tool_input": {"secret": "hidden-value"}}],
        )
        with tempfile.TemporaryDirectory() as folder:
            captured = capture(
                [sys.executable, "-c", "print(" + repr(json.dumps(payload)) + ")"],
                folder,
                5,
                provider="claude",
            )
        self.assertEqual(captured["return_code"], 0)
        self.assertEqual(captured["status"], "failed")
        self.assertIn("error_max_turns", captured["failure_reason"])
        self.assertNotIn("hidden-value", captured["stdout"])
        self.assertEqual(json.loads(captured["usage_if_exposed"]), {"permission_denial_count": 1})

    @unittest.skipUnless(os.name == "posix", "capture uses POSIX process groups")
    def test_failure_subtype_cannot_leak_environment_secret(self):
        secret = "distinctlowercasesecret"
        payload = dict(type="result", subtype=secret, is_error=True)
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.dict(os.environ, {"TEST_API_KEY": secret}),
        ):
            result = capture(
                [sys.executable, "-c", "print(" + repr(json.dumps(payload)) + ")"],
                folder,
                5,
                provider="claude",
            )
        self.assertNotIn(secret, str(result))

    @unittest.skipUnless(os.name == "posix", "capture uses POSIX process groups")
    def test_capture_limit_discards_observed_metadata(self):
        payload = json.dumps(claude_result(usage={"input_tokens": 10}))
        with tempfile.TemporaryDirectory() as folder:
            captured = capture(
                [
                    sys.executable,
                    "-c",
                    "import sys; print(" + repr(payload) + "); sys.stderr.write('x'*1100000)",
                ],
                folder,
                5,
                provider="claude",
            )
        self.assertEqual(captured["status"], "output_limit")
        self.assertEqual(captured["stdout"], "")
        self.assertEqual(captured["stderr"], "")
        self.assertIsNone(captured["usage_if_exposed"])
        self.assertIsNone(captured["model_observed"])

    def test_validated_metadata_survives_ledger_serialization(self):
        parsed = parse_result("claude", json.dumps(claude_result(usage={"input_tokens": 42})))
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder) / "ledger.sqlite3")
            ledger.record_task(task_id="synthetic", provider="claude", **parsed)
            with ledger.connect() as db:
                row = db.execute("SELECT usage_if_exposed, effort_observed FROM tasks").fetchone()
        self.assertEqual(json.loads(row[0]), {"usage": {"input_tokens": 42}})
        self.assertIsNone(row[1])
        artifact = json.loads(redact(json.dumps({"usage_if_exposed": row[0]})))
        self.assertEqual(json.loads(artifact["usage_if_exposed"]), {"usage": {"input_tokens": 42}})
