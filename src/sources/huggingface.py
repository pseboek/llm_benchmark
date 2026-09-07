from __future__ import annotations

from typing import Any

import requests

from src.sources.http import endpoint_from_env, request_json

HUGGINGFACE_API_URL = "https://huggingface.co/api/models"


def fetch_huggingface_models(limit: int = 10, search: str | None = None) -> list[dict[str, Any]]:
    params = {"limit": limit, "sort": "downloads"}
    if search:
        params["search"] = search

    payload = request_json(
        endpoint_from_env("HUGGINGFACE_API_URL", HUGGINGFACE_API_URL),
        params=params,
        token_env="HUGGINGFACE_TOKEN",
    )
    return parse_huggingface_models(payload)


def parse_huggingface_models(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        raw_models = payload.get("models") or payload.get("items") or []
    else:
        raw_models = payload or []

    parsed: list[dict[str, Any]] = []
    generative_tags = {"text-generation", "text2text-generation", "conversational"}
    for model in raw_models:
        model_id = model.get("id") or model.get("model_id") or model.get("name")
        if not model_id:
            continue
        pipeline_tag = model.get("pipeline_tag")
        if pipeline_tag and pipeline_tag not in generative_tags:
            continue
        parsed.append({
            "name": model_id,
            "source": "huggingface",
            **({"pipeline_tag": pipeline_tag} if pipeline_tag else {}),
        })

    return parsed


def list_hf_candidates(limit: int = 10, search: str | None = None) -> list[dict[str, Any]]:
    try:
        return fetch_huggingface_models(limit=limit, search=search)
    except Exception:
        return []
