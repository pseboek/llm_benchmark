from __future__ import annotations

from typing import Any

import requests

HUGGINGFACE_API_URL = "https://huggingface.co/api/models"


def fetch_huggingface_models(limit: int = 10, search: str | None = None) -> list[dict[str, Any]]:
    params = {"limit": limit, "sort": "downloads"}
    if search:
        params["search"] = search

    response = requests.get(HUGGINGFACE_API_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return parse_huggingface_models(payload)


def parse_huggingface_models(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        raw_models = payload.get("models") or payload.get("items") or []
    else:
        raw_models = payload or []

    parsed: list[dict[str, Any]] = []
    for model in raw_models:
        model_id = model.get("id") or model.get("model_id") or model.get("name")
        if not model_id:
            continue
        parsed.append({
            "name": model_id,
            "source": "huggingface",
        })

    return parsed


def list_hf_candidates(limit: int = 10, search: str | None = None) -> list[dict[str, Any]]:
    try:
        return fetch_huggingface_models(limit=limit, search=search)
    except Exception:
        return []
