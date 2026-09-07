from __future__ import annotations

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
        candidate = {
            "name": name,
            "source": "ollama",
        }
        details = model.get("details") or {}
        if model.get("size") is not None:
            candidate["size_bytes"] = int(model["size"])
            candidate["estimated_vram_gb"] = round(model["size"] / 1024**3, 2)
        for target, source in {
            "format": "format",
            "parameter_size": "parameter_size",
            "quantization": "quantization_level",
        }.items():
            if details.get(source) is not None:
                candidate[target] = details[source]
        for field in ("digest", "modified_at"):
            if model.get(field) is not None:
                candidate[field] = model[field]
        if details.get("family") is not None:
            candidate["architecture"] = details["family"]
        if details.get("families") is not None:
            candidate["families"] = details["families"]
        parsed.append(candidate)

    return parsed


def list_local_candidates(url: str = OLLAMA_API_URL) -> list[dict[str, Any]]:
    try:
        return fetch_available_models(url)
    except Exception:
        return []
