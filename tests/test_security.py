import os
import unittest
from pathlib import Path
from unittest.mock import patch

from dub.security import PROVIDER_HOME_VARIABLES, child_environment


class EnvironmentTests(unittest.TestCase):
    def test_only_current_provider_location_survives(self):
        values = {value: "relative config" for value in PROVIDER_HOME_VARIABLES.values()}
        values.update(ANTHROPIC_API_KEY="secret", XAI_API_KEY="secret", KIMI_API_KEY="secret")
        with patch.dict(os.environ, values):
            for provider, expected in PROVIDER_HOME_VARIABLES.items():
                env = child_environment(provider)
                self.assertEqual(env[expected], str(Path("relative config").absolute()))
                self.assertEqual(set(env) & set(values), {expected})
            self.assertFalse(set(child_environment()) & set(values))
