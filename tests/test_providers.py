"""Provider plumbing: secrets loading, model resolution, readiness prefixes."""

import json
import os
import unittest
from unittest import mock

from clippy import secrets, subagent
from clippy.brain import DEFAULT_MODEL
from clippy.session import resolve_model


class SecretsTests(unittest.TestCase):
    def test_flat_map_and_nested_env(self):
        with mock.patch.object(secrets, "SECRETS_FILE") as path:
            path.exists.return_value = True
            path.read_text.return_value = json.dumps({"MAMMOUTH_API_KEY": "sk-x", "N": 1})
            self.assertEqual(secrets.load(), {"MAMMOUTH_API_KEY": "sk-x", "N": "1"})
            path.read_text.return_value = json.dumps({"env": {"K": "v"}})
            self.assertEqual(secrets.load(), {"K": "v"})

    def test_missing_or_malformed_is_empty(self):
        with mock.patch.object(secrets, "SECRETS_FILE") as path:
            path.exists.return_value = False
            self.assertEqual(secrets.load(), {})
            path.exists.return_value = True
            path.read_text.return_value = "{not json"
            self.assertEqual(secrets.load(), {})

    def test_apply_does_not_clobber_existing(self):
        with mock.patch.object(secrets, "SECRETS_FILE") as path:
            path.exists.return_value = True
            path.read_text.return_value = json.dumps({"CLIPPY_TEST_KEY": "from-file"})
            os.environ.pop("CLIPPY_TEST_KEY", None)
            secrets.apply_to_environ()
            self.assertEqual(os.environ["CLIPPY_TEST_KEY"], "from-file")
            os.environ["CLIPPY_TEST_KEY"] = "from-env"
            secrets.apply_to_environ()
            self.assertEqual(os.environ["CLIPPY_TEST_KEY"], "from-env")
            del os.environ["CLIPPY_TEST_KEY"]


class ModelResolutionTests(unittest.TestCase):
    def test_explicit_wins(self):
        self.assertEqual(resolve_model("x/y"), "x/y")

    def test_config_model_used(self):
        with mock.patch("clippy.session.load_config", return_value={"model": "mammouth/m"}):
            self.assertEqual(resolve_model(), "mammouth/m")

    def test_falls_back_to_default(self):
        with mock.patch("clippy.session.load_config", return_value={}):
            self.assertEqual(resolve_model(), DEFAULT_MODEL)


class ReadyProvidersTests(unittest.TestCase):
    def test_config_override(self):
        with mock.patch("clippy.config.load_config", return_value={"providers": {"ready": ["mammouth"]}}):
            self.assertEqual(subagent._ready_providers(), ("mammouth",))

    def test_default_includes_mammouth(self):
        with mock.patch("clippy.config.load_config", return_value={}):
            self.assertIn("mammouth", subagent._ready_providers())


if __name__ == "__main__":
    unittest.main()
