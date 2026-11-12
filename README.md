# Lead Research Agent

An AI-assisted lead management app built with Streamlit. Store leads in SQLite and optionally generate a cautious AI summary, suggested industry/location, and fit score from research notes you provide.

The AI does not browse the web or verify claims. Review suggestions and check reliable sources before treating them as facts.

## Features

- Add, browse, search, edit, and delete leads.
- Save lead records in SQLite.
- Generate structured AI suggestions through an OpenAI-compatible chat-completions API.
- Run core lead-management features without configuring AI.

## Run locally

```powershell
cd D:\Agent_project\lead-research-agent
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

For local AI enrichment, put your provider settings in `.env`:

```dotenv
AI_API_KEY=
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
AI_MODEL=gemini-3.8-flash
```

Add your private key locally after `AI_API_KEY=`. Never commit or share the key.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) and select **Create app**.
3. Choose this repository, the `main` branch, and `app.py` as the main file.
4. In **Advanced settings → Secrets**, add your provider settings in TOML format:

   ```toml
   AI_API_KEY = "your-private-provider-key"
   AI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
   AI_MODEL = "gemini-3.8-flash"
   ```

5. Click **Deploy**. Later pushes to `main` trigger a redeployment.

Use the exact base URL and model identifier supported by your provider and account. API usage or billing limits are separate from ChatGPT subscriptions. The app allows up to 120 seconds per request and retries transient API failures up to five times; persistent provider-side errors such as 503 still require the provider to recover.

## Tests

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions runs the unit tests on pushes and pull requests to `main`.

## Important limitations

- The app has no authentication. Anyone with access to the deployed URL can use it; do not enter sensitive lead or contact information.
- Streamlit Community Cloud's local filesystem is not durable. SQLite data can be lost after restarts or redeployments. Use a hosted database with access controls before relying on saved leads.
- Only use research data you are authorized to process, and follow provider terms and applicable privacy rules.
