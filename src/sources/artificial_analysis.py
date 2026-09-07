from __future__ import annotations

from typing import Any

import requests

ARTIFICIAL_ANALYSIS_API_URL = "https://artificialanalysis.ai/api/models"


def fetch_artificial_analysis_models(url: str = ARTIFICIAL_ANALYSIS_API_URL) -> list[dict[str, Any]]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return parse_artificial_analysis_models(payload)


def parse_artificial_analysis_models(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        raw_models = payload.get("models") or payload.get("items") or []
    else:
        raw_models = payload or []

    parsed: list[dict[str, Any]] = []
    for model in raw_models:
        name = model.get("name") or model.get("model") or model.get("id")
        if not name:
            continue
        parsed.append({"name": name, "source": "artificial_analysis"})
    return parsed


def list_artificial_analysis_candidates(url: str = ARTIFICIAL_ANALYSIS_API_URL) -> list[dict[str, Any]]:
    try:
        return fetch_artificial_analysis_models(url)
    except Exception:
        return []