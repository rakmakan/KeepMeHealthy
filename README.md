# Keep Me Healthy (Streamlit)

Streamlit app that lets you enter a food item, calls a workflow API to fetch nutritionist-approved purchase suggestions in Montreal, and renders them in a clean table with pros/cons and source links.

## Quick start

1. Create a virtual environment (Python 3.10+).
2. `pip install -e ".[dev]"`  
3. Provide secrets:
   - Option A: set env vars `WORKFLOW_API_KEY` and optionally `WORKFLOW_ENDPOINT`.
   - Option B: copy `.env.example` to `.env` and fill the values.
   - Option C: for Streamlit Cloud, set `[secrets]` in `.streamlit/secrets.toml` (see example).
4. `streamlit run app.py`

## Configuration
- `WORKFLOW_ENDPOINT` (default set to the provided cloudflare URL).
- `WORKFLOW_API_KEY` (required).
- `WORKFLOW_QUESTION` (optional override of the prompt string).
- `WORKFLOW_TIMEOUT_SECONDS`, `WORKFLOW_MAX_RETRIES`.

## Tooling
- `make lint` (ruff), `make format`, `make type` (mypy), `make test` (pytest), `make run`.

## Deployment
- **Streamlit Community Cloud**
  1) Push this repo to GitHub.  
  2) In https://share.streamlit.io, create an app and select `app.py` as the entry point.  
  3) Add secrets in the Streamlit “Secrets” UI:
     ```
     WORKFLOW_API_KEY = "your_api_key_here"
     WORKFLOW_ENDPOINT = "https://editors-elementary-displaying-employee.trycloudflare.com/v1/workflows/8b2ca1fe-6947-48c5-8347-d595077dd47e/run"
     WORKFLOW_AUTH_SCHEME = "Bearer"
     ```
  4) Deploy. (Dependencies are in `requirements.txt` for Streamlit Cloud.)
- **Docker/other**: use the included `Dockerfile`, or `make run` locally.

# KeepMeHealthy
