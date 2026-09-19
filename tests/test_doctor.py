import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dub.config import Config
from dub.doctor import doctor
from dub.installer import install


class DoctorTests(unittest.TestCase):
    def test_project_install_reported_separately_without_auth_probe(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder).resolve()
            install("claude", project=project)
            with patch(
                "dub.doctor.detect", return_value=[{"provider": "claude", "auth": "unknown"}]
            ) as detect:
                rows = doctor(Config(), project=project)
            detect.assert_called_once_with(Config(), compatibility=True)
            self.assertTrue(rows[0]["project_skill_installed"])
            self.assertEqual(rows[0]["auth"], "unknown")
