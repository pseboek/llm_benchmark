from __future__ import annotations

from typing import Any

import requests

LMARENA_API_URL = "https://lmarena.ai/leaderboard"


def fetch_lmarena_models(url: str = LMARENA_API_URL) -> list[dict[str, Any]]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return parse_lmarena_models(payload)


def parse_lmarena_models(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        raw_models = payload.get("leaderboard") or payload.get("models") or payload.get("items") or []
    else:
        raw_models = payload or []

    parsed: list[dict[str, Any]] = []
    for model in raw_models:
        name = model.get("name") or model.get("model") or model.get("id")
        if not name:
            continue
        parsed.append({"name": name, "source": "lmarena"})
    return parsed


def list_lmarena_candidates(url: str = LMARENA_API_URL) -> list[dict[str, Any]]:
    try:
        return fetch_lmarena_models(url)
    except Exception:
        return []