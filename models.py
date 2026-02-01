from __future__ import annotations

import json
import re
from typing import List, Optional, Sequence

from pydantic import BaseModel, HttpUrl, ValidationError, field_validator


def _strip_code_fence(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


class RecommendationItem(BaseModel):
    url: Optional[HttpUrl]
    brand: List[str]
    item_name: str
    query: Optional[str] = None
    pros: List[str] = []
    cons: List[str] = []
    summary: Optional[str] = None
    relevant: Optional[int] = None

    @field_validator("brand", mode="before")
    @classmethod
    def _normalize_brand(cls, value: object) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []
            # Split on commas that are *not* inside parentheses to keep descriptive phrases intact.
            pieces = re.split(r",(?![^()]*\))", text)
            brands = [part.strip() for part in pieces if part.strip()]
            # If splitting produced nothing useful, fall back to the original.
            return brands or [text]
        if isinstance(value, Sequence):
            return [str(v) for v in value]
        return [str(value)]

    @field_validator("relevant", mode="before")
    @classmethod
    def _to_int(cls, value: object) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


class WorkflowOutputs(BaseModel):
    text: str

    def parsed_items(self) -> List[RecommendationItem]:
        cleaned = _strip_code_fence(self.text)
        try:
            raw = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Unable to parse workflow text as JSON: {exc}") from exc

        if not isinstance(raw, list):
            raise ValueError("Workflow text did not contain a list of items")

        items: List[RecommendationItem] = []
        for entry in raw:
            try:
                items.append(RecommendationItem.model_validate(entry))
            except ValidationError as exc:
                raise ValueError(f"Invalid item schema: {exc}") from exc
        return items


class WorkflowResponse(BaseModel):
    status: str
    outputs: WorkflowOutputs
