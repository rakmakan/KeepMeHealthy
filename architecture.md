Architecture & Delivery Plan
============================

Goal
----
Build a secure, well-structured Streamlit app where a user selects or types a food item, the app calls the provided workflow API, and displays a clean table of recommended brands/items to buy (with pros/cons, links, relevance). Design for scalability, maintainability, and safety.

High-Level Architecture
-----------------------
- **UI Layer (Streamlit)**: input control for food item (text + optional preset options), submit button, response table, expandable detail cards, and status/error toasts.
- **Domain/API Client**: small, testable module that wraps the workflow endpoint; handles payload shaping, retries with backoff, timeouts, and response parsing to domain models.
- **State & Caching**: Streamlit session state to avoid re-fetching identical queries; optional short-lived disk cache (e.g., `diskcache`) for scaling beyond single user/process.
- **Config & Secrets**: base config from `settings.py` using `pydantic` with environment variables; API key stored in `st.secrets` or `.env` (never hard-coded).
- **Validation Layer**: Pydantic models for request and response schemas to guard against malformed upstream data.
- **Logging & Telemetry**: structured logging to stdout (Streamlit logs) with request id; optional Sentry hook placeholder.
- **Testing**: unit tests for the client and parsing; smoke test for the app script to ensure imports and layout build.
- **Packaging & Tooling**: `pyproject.toml` with dependencies; `ruff` + `mypy` for lint/type safety; `make` targets for dev ergonomics.
- **Deployment**: ready for Streamlit Community Cloud or containerized deploy (Dockerfile). Healthcheck route via `streamlit-healthcheck` pattern (lightweight script).

Data Flow
---------
1) User enters/selects food item in Streamlit.
2) UI calls `client.fetch_recommendations(food_item)`.
3) Client builds JSON payload (Question + food_item, response_mode=blocking, user id).
4) POST to workflow endpoint with Authorization header from secrets; 10s timeout, 3 retries (expo backoff).
5) Response JSON validated into Pydantic models; errors mapped to user-friendly alerts.
6) UI renders table (brand list exploded as rows) + expandable pros/cons + source links.
7) Cached by food item + endpoint URL to reduce duplicate calls.

Security & Privacy
------------------
- Keep API key only in `st.secrets["WORKFLOW_API_KEY"]` or environment variable `WORKFLOW_API_KEY`.
- Never echo secrets to UI or logs; redact on error.
- Enforce timeouts and minimal scopes (single POST endpoint).
- Input sanitation: trim length, reject empty; limit to reasonable size to avoid abuse.
- HTTPS-only endpoint; verify certificates (requests default).
- Optional: CSRF not needed for Streamlit, but rate-limit per session (simple sleep/backoff) to avoid spam.

Scalability Considerations
--------------------------
- Stateless app; all state in client-side session/cache.
- Caching layer interchangeable (in-memory/disk/Redis) via simple interface.
- API client isolated for future async implementation (httpx) if concurrent calls needed.
- Pagination-ready table (Streamlit dataframes handle hundreds of rows; can chunk brands if large).
- Containerization enables horizontal scaling behind a reverse proxy.

Error Handling Strategy
-----------------------
- Graceful user messages for: network timeout, 4xx auth issues, 5xx upstream errors, schema validation failures, empty results.
- Log structured context: food_item, status code, elapsed, request id from response.
- Retry on network/5xx with capped exponential backoff; no retry on 4xx.

Core Files to Create
--------------------
- `app.py` — Streamlit UI, event handlers, rendering.
- `client.py` — workflow API wrapper with typed functions.
- `models.py` — Pydantic request/response models and validators.
- `settings.py` — Pydantic settings for endpoint URL, API key, timeouts, retries.
- `utils.py` — small helpers (formatting, caching keys).
- `pyproject.toml` — dependencies (streamlit, requests/httpx, pydantic, python-dotenv, diskcache, ruff, mypy, pytest).
- `Makefile` — `make dev`, `make lint`, `make test`, `make run`.
- `tests/` — unit tests for client parsing and minimal app smoke test.
- `Dockerfile` — optional container build for deployment.

Implementation Steps (short term)
---------------------------------
1) Scaffold project structure and tooling (pyproject, Makefile, .env.example, .streamlit/secrets.example).
2) Implement `settings.py`, `models.py`, `client.py` with retries, validation, and caching hook.
3) Build `app.py` UI: input, submit, loading state, table, details, error banners.
4) Add tests for client response parsing, error paths, and app import; run lint/type/test.
5) Provide run instructions (local and Streamlit Cloud) and security notes in README.

Open Questions
--------------
- Should we pre-seed a list of common food items for quick selection?
- Any rate limits/SLAs on the workflow endpoint?
- Do we need localization beyond English?
