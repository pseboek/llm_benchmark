from __future__ import annotations

import json
from typing import Any

import requests

OLLAMA_API_URL = "http://localhost:11434/api/tags"


def fetch_available_models(url: str = OLLAMA_API_URL) -> list[dict[str, Any]]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    payload = response.json()
    return parse_ollama_models(payload)


def parse_ollama_models(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_models = payload.get("models", [])
    parsed: list[dict[str, Any]] = []

    for model in raw_models:
        name = model.get("name")
        if not name:
            continue
        parsed.append({
            "name": name,
            "source": "ollama",
        })

    return parsed


def list_local_candidates(url: str = OLLAMA_API_URL) -> list[dict[str, Any]]:
    try:
        return fetch_available_models(url)
    except Exception:
        return []
