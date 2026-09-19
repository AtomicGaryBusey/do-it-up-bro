"""Explicitly opt in with DUB_LIVE_PROVIDER=codex pytest tests/integration -m integration.

This consumes quota. Never set this variable in the normal test environment.
"""

import os
import tempfile
from pathlib import Path

import pytest

from dub.config import Config, ProviderConfig
from dub.providers.base import PROVIDERS
from dub.supervisor import run

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.environ.get("DUB_LIVE_PROVIDER"), reason="paid CLI call requires explicit opt-in"
)
def test_single_live_provider():
    provider = os.environ["DUB_LIVE_PROVIDER"]
    assert provider in PROVIDERS and PROVIDERS[provider].headless
    with tempfile.TemporaryDirectory() as folder:
        config = Config(
            run_dir=Path(folder) / "runs",
            provider_timeout_seconds=60,
            providers={provider: ProviderConfig(command=PROVIDERS[provider].executable)},
        )
        result = run(config, "Explain why an empty list has length zero. Do not use tools.")
        assert result["status"] == "completed"
