import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import ollama_benchmark


def test_generate_uses_configured_request_timeout(monkeypatch):
    captured = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": "ok", "eval_count": 1, "eval_duration": 1_000_000_000}

    def post(url, **kwargs):
        captured.update(kwargs)
        return Response()

    monkeypatch.setattr(ollama_benchmark.requests, "post", post)
    ollama_benchmark.REQUEST_TIMEOUT_SECONDS = 42

    ollama_benchmark.generate("model", "prompt", 8192)

    assert captured["timeout"] == 42
