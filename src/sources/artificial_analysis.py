from __future__ import annotations

import os
import re
from typing import Any

import requests

from src.sources.http import endpoint_from_env, request_json

ARTIFICIAL_ANALYSIS_API_URL = "https://artificialanalysis.ai/api/models"
ARTIFICIAL_ANALYSIS_HOMEPAGE_URL = "https://artificialanalysis.ai/"

# Slugs under /models/ on the homepage that are navigation pages, not models.
_NON_MODEL_SLUGS = {"capabilities", "recommend", "releases"}
_MODEL_LINK_PATTERN = re.compile(r'href="/models/([a-z0-9\-]+)"')


def fetch_artificial_analysis_models(url: str = ARTIFICIAL_ANALYSIS_API_URL) -> list[dict[str, Any]]:
    if os.getenv("ARTIFICIAL_ANALYSIS_API_KEY"):
        payload = request_json(url, token_env="ARTIFICIAL_ANALYSIS_API_KEY", token_required=True)
        return parse_artificial_analysis_models(payload)
    # No API key configured: fall back to scraping the small set of models
    # featured in the homepage highlights carousel (server-rendered HTML,
    # no key required). This is only a partial view of the full leaderboard.
    return scrape_artificial_analysis_homepage()


def scrape_artificial_analysis_homepage(url: str = ARTIFICIAL_ANALYSIS_HOMEPAGE_URL) -> list[dict[str, Any]]:
    response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    slugs = dict.fromkeys(_MODEL_LINK_PATTERN.findall(response.text))
    parsed: list[dict[str, Any]] = []
    for slug in slugs:
        if slug in _NON_MODEL_SLUGS:
            continue
        parsed.append({"name": slug.replace("-", " ").title(), "source": "artificial_analysis"})
    return parsed


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


def list_artificial_analysis_candidates(url: str | None = None) -> list[dict[str, Any]]:
    return fetch_artificial_analysis_models(url or endpoint_from_env("ARTIFICIAL_ANALYSIS_API_URL", ARTIFICIAL_ANALYSIS_API_URL))