from functools import lru_cache
from typing import Any, Dict

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    workflow_endpoint: HttpUrl = Field(
        default=(
            "https://editors-elementary-displaying-employee.trycloudflare.com/"
            "v1/workflows/8b2ca1fe-6947-48c5-8347-d595077dd47e/run"
        ),
        alias="WORKFLOW_ENDPOINT",
    )
    # Allow blank by default so the app can show a friendly error instead of raising at import time.
    workflow_api_key: str = Field(default="", alias="WORKFLOW_API_KEY")
    workflow_question: str = Field(
        default="healthy {food_item} brands recommended by dietitians in Montreal Canada non-marketing sources",
        alias="WORKFLOW_QUESTION",
    )
    workflow_timeout_seconds: float = Field(default=12.0, alias="WORKFLOW_TIMEOUT_SECONDS")
    workflow_max_retries: int = Field(default=3, alias="WORKFLOW_MAX_RETRIES")
    workflow_auth_scheme: str = Field(default="Bearer", alias="WORKFLOW_AUTH_SCHEME")

    model_config = dict(
        env_prefix="",
        env_file=".env",
        extra="ignore",
    )


def _collect_streamlit_secrets() -> Dict[str, Any]:
    try:
        import streamlit as st

        secrets = st.secrets  # type: ignore[attr-defined]
        # Support both flat and [secrets] table styles.
        if "secrets" in secrets:
            return dict(secrets["secrets"])
        return dict(secrets)
    except Exception:
        return {}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    overrides = _collect_streamlit_secrets()
    return Settings(**overrides)
