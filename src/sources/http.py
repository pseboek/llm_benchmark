from __future__ import annotations

import os
import time
from typing import Any, Callable

import requests
from dotenv import load_dotenv

load_dotenv()


def request_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    token_env: str | None = None,
    timeout: int = 30,
    retries: int = 2,
    request_get: Callable[..., Any] = requests.get,
) -> Any:
    headers = {"Accept": "application/json"}
    token = os.getenv(token_env) if token_env else None
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = request_get(url, params=params, headers=headers, timeout=timeout)
            if response.status_code == 429 or response.status_code >= 500:
                response.raise_for_status()
                raise requests.RequestException(f"temporary HTTP status {response.status_code}")
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as error:
            last_error = error
            if attempt < retries:
                time.sleep(0.25 * (attempt + 1))

    raise last_error or requests.RequestException(f"request failed: {url}")
