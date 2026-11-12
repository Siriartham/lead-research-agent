<<<<<<< HEAD
# AI-Powered Lead Research & Enrichment Agent

A Streamlit app for organizing business leads and generating cautious AI suggestions from research information you provide.

## Features

- Add, browse, search, edit, and delete leads.
- Store lead records in SQLite.
- Optionally generate an AI summary and suggested industry, location, and fit score.
- Keep AI configuration optional; lead management works without an API key.

The AI does not browse the web or verify claims. Supply accurate research notes and source links yourself. Do not enter sensitive personal data. Before adding automated research, choose compliant and authorized data providers and respect their terms and applicable privacy rules.

## Deploy online with Streamlit Community Cloud

### 1. Put the project on GitHub

Create a GitHub repository for this project, then open PowerShell in the project folder:

```powershell
cd D:\Agent_project\lead-research-agent
git init
git add .
git status --short
```

Check the status before committing: `.env`, `.streamlit/secrets.toml`, and `leads.db` must not be listed. The `.gitignore` excludes these files. If everything looks right:

```powershell
git commit -m "Initial lead research agent"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/lead-research-agent.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username and use the repository URL you created. If Git is already initialized or `origin` is already configured, do not repeat those setup commands; update the existing remote if needed.

**Never put an API key in source code, README, or GitHub.** If a key was ever committed or shared, revoke it with the provider and create a replacement.

### 2. Create the Streamlit app

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) and connect the GitHub account that can access your repository.
2. Select **Create app**.
3. Choose your repository, the `main` branch, and `app.py` as the main file.
4. Open **Advanced settings** before deploying and add the secrets below.
5. Click **Deploy**. When deployment finishes, Streamlit gives you an internet-accessible app URL.

### 3. Add AI settings securely

Paste this TOML in the app's **Secrets** field in Advanced settings (or later in the deployed app's settings). Replace the API key placeholder with your own secret key:

```toml
AI_API_KEY = "your-secret-api-key"
AI_BASE_URL = "https://api.openai.com/v1"
AI_MODEL = "gpt-4o-mini"
```

The model name must be available to your API account. API billing and usage limits are separate from a ChatGPT subscription. A `429` response means the provider refused the request due to a rate or usage limit; deploying the app does not resolve that provider-side issue. The app allows up to 120 seconds per request and retries transient API failures up to five times; persistent provider outages still need to be resolved by the provider.

### 4. Check the deployed app

Open the URL Streamlit provides, add a non-sensitive test lead, and try enrichment if API access is configured. If you change project files later, push the changes to GitHub; Streamlit Community Cloud will redeploy the app.

## Important before sharing or using real leads

- This app currently has **no login or per-user access control**. Anyone who can access its URL can interact with it. Do not use it to store private or sensitive lead/contact information.
- The app uses a local SQLite database. Streamlit Community Cloud's app filesystem is not durable storage, so leads may be lost after a restart or redeployment. Use a hosted database with appropriate access controls before relying on saved data.
- Review AI suggestions and verify them from reliable sources before treating them as facts.

## Run locally (optional)

For development or testing on your computer:

```powershell
cd D:\Agent_project\lead-research-agent
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

For local AI enrichment, configure `AI_API_KEY`, `AI_BASE_URL`, and `AI_MODEL` in `.env`. Keep `.env` private; it is excluded from Git.

## Run tests

```powershell
python -m unittest discover -s tests -v
```
=======
# lead-research-agent
>>>>>>> origin/main
