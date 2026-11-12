import os
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from lead_agent.enrichment import _get_setting, enrich_lead


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

    def test_enrichment_uses_configured_timeout_and_retries(self) -> None:
        result_data = {
            "summary": "Potential fintech lead.",
            "industry": "Fintech",
            "location": "Hyderabad",
            "fit_score": 4,
        }
        response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps(result_data))
                )
            ]
        )
        client = Mock()
        client.chat.completions.create.return_value = response
        with patch.dict(
            os.environ,
            {
                "AI_API_KEY": "test-key",
                "AI_BASE_URL": "https://example.test/v1/",
                "AI_MODEL": "test-model",
            },
            clear=True,
        ):
            with patch("lead_agent.enrichment.load_dotenv"):
                with patch("lead_agent.enrichment.OpenAI", return_value=client) as openai:
                    result = enrich_lead({"company_name": "Example"})

        self.assertEqual(result, result_data)
        openai.assert_called_once_with(
            api_key="test-key",
            base_url="https://example.test/v1",
            timeout=120.0,
            max_retries=5,
        )


if __name__ == "__main__":
    unittest.main()
