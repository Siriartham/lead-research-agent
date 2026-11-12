"""AI enrichment through an OpenAI-compatible chat-completions endpoint."""

import json
import os
from typing import Any

from openai import APIError, OpenAI
import streamlit as st
from dotenv import load_dotenv


class EnrichmentError(RuntimeError):
    """Raised when AI enrichment is unavailable or returns invalid data."""


def _get_setting(name: str, default: str = "") -> str:
    """Read configuration from environment variables or Streamlit secrets."""
    value = os.getenv(name)
    if value is not None:
        return value
    try:
        return str(st.secrets.get(name, default))
    except FileNotFoundError:
        return default


def enrich_lead(lead: dict[str, Any]) -> dict[str, Any]:
    """Create suggestions from provided data without presenting guesses as facts."""
    load_dotenv()
    api_key = _get_setting("AI_API_KEY").strip()
    if not api_key:
        raise EnrichmentError(
            "AI_API_KEY is not configured. Add it to .env locally or to the app's "
            "Streamlit Cloud secrets."
        )

    base_url = _get_setting(
        "AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
    ).rstrip("/")
    model = _get_setting("AI_MODEL").strip()
    if not model:
        raise EnrichmentError(
            "AI_MODEL is not configured in .env or Streamlit Cloud secrets."
        )

    context = {
        key: lead.get(key, "")
        for key in (
            "company_name",
            "website",
            "contact_name",
            "job_title",
            "industry",
            "location",
            "research_notes",
            "source_urls",
        )
    }
    prompt = (
        "Analyze only the supplied lead information. Do not browse the web, "
        "invent facts, or claim that information has been verified. "
        "Return a JSON object with string fields 'summary', 'industry', "
        "'location', and integer 'fit_score' from 1 to 5. Use empty strings "
        "for unknown industry/location. The fit score is a tentative assessment "
        "based only on the supplied data. Lead data:\n"
        + json.dumps(context, ensure_ascii=False)
    )

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=120.0,
            max_retries=5,
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You provide cautious, evidence-bound business lead analysis.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        result = json.loads(content)
    except (APIError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise EnrichmentError(f"AI enrichment request failed: {exc}") from exc

    if not isinstance(result, dict):
        raise EnrichmentError("AI provider returned an unexpected response.")

    score = result.get("fit_score")
    if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
        raise EnrichmentError("AI response must include fit_score as an integer from 1 to 5.")

    for field in ("summary", "industry", "location"):
        if not isinstance(result.get(field), str):
            raise EnrichmentError(f"AI response must include '{field}' as text.")
    return result
