import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sources.http import endpoint_from_env, request_json


def test_endpoint_from_env_prefers_configured_url(monkeypatch):
    monkeypatch.setenv("TEST_SOURCE_URL", "https://configured.test/api")

    assert endpoint_from_env("TEST_SOURCE_URL", "https://default.test") == "https://configured.test/api"


def test_request_json_requires_token_when_configured(monkeypatch):
    monkeypatch.delenv("MISSING_TOKEN", raising=False)

    try:
        request_json("https://example.test", token_env="MISSING_TOKEN", token_required=True, retries=0)
    except RuntimeError as error:
        assert "MISSING_TOKEN" in str(error)
    else:
        raise AssertionError("Missing required token did not fail")
