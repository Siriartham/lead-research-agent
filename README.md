# Lead Research Agent 🔎

An AI-assisted lead management app built with Streamlit. Organize business leads in a
SQLite database and generate **cautious, evidence-bound AI enrichment** — a summary,
suggested industry/location, and a 1–5 fit score — from research notes you supply.

The AI never browses the web or invents facts: it analyzes only the information you
provide, and every suggestion is clearly framed as tentative until you verify it.

## Features

- **Full lead CRUD** — add, browse, search, edit, and delete leads from a clean Streamlit UI
- **AI enrichment** — one click generates a summary, suggested industry/location, and fit
  score via any OpenAI-compatible chat-completions API
- **Structured output** — the model is constrained to JSON (`response_format`), and every
  field is validated before it is saved
- **Optional AI** — lead management works without any API key; the app degrades gracefully
- **Safe by design** — secrets stay in `.env` / Streamlit Cloud secrets, never in code

## Tech Stack

| Layer      | Choice                                                        |
| ---------- | ------------------------------------------------------------- |
| UI         | Streamlit                                                     |
| Database   | SQLite (parameterized queries)                                |
| AI         | OpenAI-compatible chat-completions API (any provider/model)   |
| Config     | `python-dotenv` locally, Streamlit secrets in the cloud       |
| Testing    | `unittest` (database CRUD + enrichment settings)              |

## How It Works

```
app.py                    Streamlit UI: forms, search, detail view, enrich/edit/delete
lead_agent/
├── database.py           SQLite schema + CRUD with input validation
└── enrichment.py         Builds a constrained prompt, calls the LLM, validates the
                          JSON response (fit_score must be an int 1–5, fields must be
                          strings) before anything is stored
tests/                    Unit tests for persistence and enrichment settings
```

The enrichment prompt explicitly instructs the model to analyze only the supplied
data, never to claim verification, and to return empty strings for unknown fields —
a simple guardrail pattern against hallucinated lead data.

## Quick Start (local)

```bash
git clone https://github.com/Siriartham/lead-research-agent.git
cd lead-research-agent

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env             # then fill in your settings
streamlit run app.py
```

### Configuration (`.env` or Streamlit secrets)

```toml
AI_API_KEY = "your-secret-api-key"
AI_BASE_URL = "https://api.openai.com/v1"   # any OpenAI-compatible endpoint
AI_MODEL = "gpt-4o-mini"
```

**Never commit an API key.** `.env`, `leads.db`, and `.streamlit/secrets.toml` are
gitignored; if a key is ever exposed, revoke it immediately.

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub and sign in at [share.streamlit.io](https://share.streamlit.io/).
2. **Create app** → pick this repo, the `main` branch, `app.py` as the entry point.
3. In **Advanced settings → Secrets**, paste the TOML block above with your real key.
4. Deploy and open the URL Streamlit provides.

Any later push to `main` automatically redeploys.

## Run Tests

```bash
python -m unittest discover -s tests -v
```

## Limitations & Responsible Use

- **No authentication** — anyone with the URL can use the app. Don't store private or
  sensitive contact data in a public deployment.
- **SQLite on Streamlit Cloud is not durable** — data can be lost on restart. Use a
  hosted database with access controls before relying on saved leads.
- **AI output is unverified** — summaries and fit scores are tentative suggestions based
  only on the notes you supply. Verify against reliable sources before acting, and only
  use research data you are authorized to use (respect provider terms and privacy rules).

## Roadmap

- [ ] Hosted database (Postgres) instead of local SQLite
- [ ] Login / per-user access control
- [ ] Bulk CSV import & export
- [ ] Optional live web-research step behind compliant, authorized data providers

## License

MIT
