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
- Works on Streamlit Community Cloud: push repo, set secrets, click deploy.
- Docker-ready; add a simple `Dockerfile` if deploying to another platform.

# KeepMeHealthy
