import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from lead_agent.enrichment import _get_setting


class EnrichmentSettingsTests(unittest.TestCase):
    def test_environment_value_takes_precedence_over_streamlit_secret(self) -> None:
        with patch.dict(os.environ, {"AI_API_KEY": "environment-key"}, clear=True):
            with patch(
                "lead_agent.enrichment.st",
                SimpleNamespace(secrets={"AI_API_KEY": "cloud-key"}),
            ):
                self.assertEqual(_get_setting("AI_API_KEY"), "environment-key")

    def test_reads_streamlit_secret_when_environment_value_is_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "lead_agent.enrichment.st",
                SimpleNamespace(secrets={"AI_API_KEY": "cloud-key"}),
            ):
                self.assertEqual(_get_setting("AI_API_KEY"), "cloud-key")

    def test_uses_default_when_local_secrets_file_is_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "lead_agent.enrichment.st",
                SimpleNamespace(
                    secrets=SimpleNamespace(
                        get=Mock(side_effect=FileNotFoundError)
                    )
                ),
            ):
                self.assertEqual(_get_setting("AI_BASE_URL", "default"), "default")


if __name__ == "__main__":
    unittest.main()
