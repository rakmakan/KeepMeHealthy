import json
from typing import Any

import httpx
import pytest

from client import WorkflowClient


@pytest.fixture(autouse=True)
def _env_api_key(monkeypatch):
    monkeypatch.setenv("WORKFLOW_API_KEY", "test-key")


class DummyResponse(httpx.Response):
    def __init__(self, status_code: int, json_data: dict[str, Any]):
        super().__init__(status_code=status_code, content=json.dumps(json_data).encode(), request=httpx.Request("POST", "https://example.com"))


def test_client_parses_response(monkeypatch):
    def fake_post(url: str, headers: dict, content: str, timeout: float) -> httpx.Response:  # type: ignore[override]
        data = {
            "data": {
                "outputs": {
                    "text": """[
                        {"url": "https://example.com", "brand": ["BrandX"], "item_name": "ItemX", "pros": [], "cons": [], "summary": "fine"}
                    ]"""
                }
            }
        }
        return DummyResponse(200, data)

    monkeypatch.setattr(httpx, "post", fake_post)
    client = WorkflowClient(timeout=2, max_retries=0)
    items = client.fetch_recommendations("oats", user="test-user")
    assert len(items) == 1
    assert items[0].brand == ["BrandX"]
    assert items[0].item_name == "ItemX"


def test_client_raises_on_missing_outputs(monkeypatch):
    def fake_post(url: str, headers: dict, content: str, timeout: float) -> httpx.Response:  # type: ignore[override]
        return DummyResponse(200, {"data": {}})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = WorkflowClient(timeout=1, max_retries=0)
    with pytest.raises(RuntimeError):
        client.fetch_recommendations("oats")
