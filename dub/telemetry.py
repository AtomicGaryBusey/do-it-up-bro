"""Validate optional provider result metadata; never infer usage or task correctness.

Contracts: Claude Agent SDK ResultMessage; Grok 1.0.34 shipped headless guide.
See docs/research/result-contracts.md. Unknown/new formats remain unknown.
"""

import json
import math
import re

from .security import redact

TOKEN_FIELDS = {
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "reasoning_tokens",
    "total_tokens",
}
MODEL_FIELDS = {
    "inputTokens",
    "outputTokens",
    "cacheReadInputTokens",
    "cacheCreationInputTokens",
    "modelCalls",
    "webSearchRequests",
}


def _number(value):
    return type(value) in (int, float) and 0 <= value <= 10**18 and math.isfinite(value)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _counts(value, fields):
    if not isinstance(value, dict):
        return {}
    return {k: v for k, v in value.items() if k in fields and type(v) is int and _number(v)}


def parse_result(provider: str, stdout: str) -> dict:
    """Return ledger-ready metadata; never retain arbitrary payloads or denial inputs."""
    result = dict(
        model_observed=None, effort_observed=None, usage_if_exposed=None, failure_reason=None
    )
    if provider not in {"claude", "grok"} or len(stdout) > 1_048_576:
        return result
    try:
        payload = json.loads(stdout, object_pairs_hook=_unique)
    except (ValueError, RecursionError):
        return result
    if not isinstance(payload, dict):
        return result
    if provider == "claude":
        if payload.get("type") != "result":
            return result
        subtype = payload.get("subtype")
        if payload.get("is_error") is True or (isinstance(subtype, str) and subtype != "success"):
            known = {
                "error_during_execution",
                "error_max_turns",
                "error_max_budget_usd",
                "error_max_structured_output_retries",
            }
            result["failure_reason"] = (
                f"Claude result: {subtype}"
                if isinstance(subtype, str) and subtype in known
                else "Claude result reported an error"
            )
        if payload.get("terminal_reason") in ("aborted_streaming", "aborted_tools"):
            result["failure_reason"] = "Claude result was aborted"
    else:
        if payload.get("type") == "error":
            result["failure_reason"] = "Grok result reported an error"
        elif not isinstance(payload.get("sessionId"), str) or not isinstance(
            payload.get("stopReason"), str
        ):
            return result
        elif payload["stopReason"] in {"max_tokens", "max_turns", "cancelled", "refusal"}:
            result["failure_reason"] = "Grok result stopped: " + payload["stopReason"]
        # Missing means no incomplete marker. Any non-false marker is suspect,
        # including malformed strings masquerading as booleans.
        if (
            payload.get("usage_is_incomplete", False) is not False
            or payload.get("cost_is_partial", False) is not False
        ):
            return result
    observed = {}
    usage = _counts(payload.get("usage"), TOKEN_FIELDS)
    if usage:
        observed["usage"] = usage
    for key in ("num_turns", "duration_ms", "duration_api_ms", "total_cost_usd_ticks"):
        value = payload.get(key)
        if type(value) is int and _number(value):
            observed[key] = value
    if _number(payload.get("total_cost_usd")):
        observed["total_cost_usd"] = payload["total_cost_usd"]
    denials = payload.get("permission_denials")
    if provider == "claude" and isinstance(denials, list):
        observed["permission_denial_count"] = len(denials)
    models = payload.get("modelUsage")
    if isinstance(models, dict) and 0 < len(models) <= 32:
        valid_models = {}
        for key, value in models.items():
            if (
                not isinstance(key, str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}", key)
                or not isinstance(value, dict)
            ):
                continue
            counts = _counts(value, MODEL_FIELDS)
            if _number(value.get("costUSD")):
                counts["costUSD"] = value["costUSD"]
            # Empty/unrecognized rows are not evidence of model execution.
            if counts:
                valid_models[key] = counts
        if valid_models:
            result["model_observed"] = redact(",".join(sorted(valid_models)))
            observed["modelUsage"] = valid_models
    if observed:
        result["usage_if_exposed"] = redact(json.dumps(observed, sort_keys=True, allow_nan=False))
    return result
