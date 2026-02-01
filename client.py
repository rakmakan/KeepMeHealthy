from __future__ import annotations

import json
import logging
import time
from typing import List

import httpx
from httpx import HTTPStatusError, RequestError

from models import RecommendationItem, WorkflowOutputs
from settings import get_settings

logger = logging.getLogger(__name__)


class WorkflowClient:
    def __init__(self, *, timeout: float | None = None, max_retries: int | None = None) -> None:
        self.settings = get_settings()
        self.timeout = timeout or self.settings.workflow_timeout_seconds
        self.max_retries = max_retries or self.settings.workflow_max_retries

    def _headers(self) -> dict[str, str]:
        key = self.settings.workflow_api_key
        if self.settings.workflow_auth_scheme:
            prefix = f"{self.settings.workflow_auth_scheme} "
            if not key.lower().startswith(prefix.lower()):
                key = prefix + key
        return {
            "Content-Type": "application/json",
            "Authorization": key,
        }

    def _payload(self, food_item: str, user: str) -> dict:
        return {
            "inputs": {
                "Question": self.settings.workflow_question,
                "food_item": food_item,
            },
            "response_mode": "blocking",
            "user": user,
        }

    def fetch_recommendations(
        self, food_item: str, user: str = "streamlit-user"
    ) -> List[RecommendationItem]:
        if not food_item or not food_item.strip():
            raise ValueError("food_item must be provided")

        attempt = 0
        last_error: Exception | None = None
        while attempt <= self.max_retries:
            try:
                response = httpx.post(
                    str(self.settings.workflow_endpoint),
                    headers=self._headers(),
                    content=json.dumps(self._payload(food_item.strip(), user)),
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                # Response shape: { "data": { "outputs": { "text": "<json>" }, ... } }
                outputs_raw = data.get("data", {}).get("outputs")
                if not outputs_raw or "text" not in outputs_raw:
                    raise ValueError("Unexpected response shape: missing outputs.text")
                outputs = WorkflowOutputs.model_validate(outputs_raw)
                return outputs.parsed_items()
            except (RequestError, HTTPStatusError, ValueError) as exc:
                last_error = exc
                attempt += 1
                if isinstance(exc, HTTPStatusError) and exc.response.status_code < 500:
                    break
                if attempt > self.max_retries:
                    break
                backoff = min(2**attempt, 8)
                logger.warning("Request failed (attempt %s): %s; retrying in %ss", attempt, exc, backoff)
                time.sleep(backoff)

        raise RuntimeError(f"Failed to fetch recommendations: {last_error}") from last_error


def get_client() -> WorkflowClient:
    return WorkflowClient()
