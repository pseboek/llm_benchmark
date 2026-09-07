from __future__ import annotations

from typing import Any

import requests

from src.sources.http import endpoint_from_env, request_json

SWEBENCH_API_URL = "https://api.swebench.com/benchmarks"


def fetch_swebench_models(url: str = SWEBENCH_API_URL) -> list[dict[str, Any]]:
    payload = request_json(url)
    return parse_swebench_models(payload)


def parse_swebench_models(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        raw_models = payload.get("tasks") or payload.get("items") or payload.get("benchmarks") or []
    else:
        raw_models = payload or []

    parsed: list[dict[str, Any]] = []
    for item in raw_models:
        name = item.get("repo") or item.get("name") or item.get("model") or item.get("id")
        if not name:
            continue
        parsed.append({"name": name, "source": "swebench"})
    return parsed


def list_swebench_candidates(url: str | None = None) -> list[dict[str, Any]]:
    try:
        return fetch_swebench_models(url or endpoint_from_env("SWEBENCH_API_URL", SWEBENCH_API_URL))
    except Exception:
        return []