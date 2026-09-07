import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sources.http import request_json


class Response:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.RequestException(f"status {self.status_code}")

    def json(self):
        return self.payload


def test_request_json_adds_token_header(monkeypatch):
    calls = []
    monkeypatch.setenv("TEST_TOKEN", "secret")

    def request_get(url, **kwargs):
        calls.append(kwargs)
        return Response({"ok": True})

    assert request_json("https://example.test", token_env="TEST_TOKEN", request_get=request_get) == {"ok": True}
    assert calls[0]["headers"]["Authorization"] == "Bearer secret"


def test_request_json_retries_temporary_failures():
    attempts = []

    def request_get(url, **kwargs):
        attempts.append(url)
        if len(attempts) < 2:
            return Response({}, status_code=503)
        return Response({"ok": True})

    assert request_json("https://example.test", retries=1, request_get=request_get) == {"ok": True}
    assert len(attempts) == 2
