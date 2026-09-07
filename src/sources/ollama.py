from __future__ import annotations

from typing import Any

import requests

OLLAMA_API_URL = "http://localhost:11434/api/tags"
OLLAMA_SHOW_URL = "http://localhost:11434/api/show"


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


def parse_ollama_details(payload: dict[str, Any]) -> dict[str, Any]:
    details = payload.get("details") or {}
    model_info = payload.get("model_info") or {}
    parsed: dict[str, Any] = {}
    if details.get("family") is not None:
        parsed["architecture"] = details["family"]
    if details.get("families") is not None:
        parsed["families"] = details["families"]
    if details.get("parameter_size") is not None:
        parsed["parameter_size"] = details["parameter_size"]
    if details.get("quantization_level") is not None:
        parsed["quantization"] = details["quantization_level"]
    parameter_count = model_info.get("general.parameter_count")
    if parameter_count is not None:
        parsed["parameters_total_b"] = round(float(parameter_count) / 1_000_000_000, 2)
    context_length = model_info.get("llama.context_length") or model_info.get("general.context_length")
    if context_length is not None:
        parsed["context_length"] = int(context_length)
    return parsed


def fetch_model_details(model: str, url: str = OLLAMA_SHOW_URL) -> dict[str, Any]:
    response = requests.post(url, json={"name": model}, timeout=30)
    response.raise_for_status()
    return parse_ollama_details(response.json())


def enrich_ollama_models(candidates: list[dict[str, Any]], details_fetcher=fetch_model_details) -> list[dict[str, Any]]:
    enriched = []
    for candidate in candidates:
        try:
            metadata = details_fetcher(candidate["name"])
        except Exception:
            metadata = {}
        enriched.append({**candidate, **metadata})
    return enriched


def list_local_candidates(url: str = OLLAMA_API_URL, enrich: bool = True) -> list[dict[str, Any]]:
    try:
        candidates = fetch_available_models(url)
        return enrich_ollama_models(candidates) if enrich else candidates
    except Exception:
        return []
