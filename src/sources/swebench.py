from __future__ import annotations

import json
import re
from typing import Any

import requests

from src.sources.http import endpoint_from_env

SWEBENCH_API_URL = "https://www.swebench.com/index.html"

# The official leaderboard page has no JSON API, but it embeds the full
# leaderboard dataset as a <script type="application/json"> tag, which is a
# stable, real data source we can parse without executing any JavaScript.
_LEADERBOARD_SCRIPT_PATTERN = re.compile(
    r'<script[^>]*id="leaderboard-data"[^>]*>(.*?)</script>', re.DOTALL
)


def fetch_swebench_models(url: str = SWEBENCH_API_URL) -> list[dict[str, Any]]:
    response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    match = _LEADERBOARD_SCRIPT_PATTERN.search(response.text)
    if not match:
        raise ValueError("swebench.com leaderboard data script not found; page layout may have changed")

    payload = json.loads(match.group(1))
    return parse_swebench_models(payload)


def parse_swebench_models(payload: Any) -> list[dict[str, Any]]:
    sections = payload if isinstance(payload, list) else [payload]

    seen: set[str] = set()
    parsed: list[dict[str, Any]] = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        for result in section.get("results") or []:
            name = result.get("model_display") or result.get("name") or result.get("model")
            if not name or name in seen:
                continue
            seen.add(name)
            parsed.append({"name": name, "source": "swebench"})
    return parsed


def list_swebench_candidates(url: str | None = None) -> list[dict[str, Any]]:
    return fetch_swebench_models(url or endpoint_from_env("SWEBENCH_API_URL", SWEBENCH_API_URL))