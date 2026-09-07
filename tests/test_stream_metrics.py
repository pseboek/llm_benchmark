import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ollama_benchmark import collect_stream_response


def test_collect_stream_response_tracks_first_token_and_final_metrics():
    events = [
        json.dumps({"response": "Hello", "done": False}).encode(),
        json.dumps({
            "response": " world",
            "done": True,
            "eval_count": 4,
            "eval_duration": 2_000_000_000,
            "prompt_eval_count": 8,
            "prompt_eval_duration": 1_000_000_000,
        }).encode(),
    ]

    result = collect_stream_response(events, started_at=0.0, clock=lambda: 0.25)

    assert result["response"] == "Hello world"
    assert result["ttft_seconds"] == 0.25
    assert result["eval_count"] == 4
    assert result["tok_per_sec"] == 2.0
    assert result["prompt_tok_per_sec"] == 8.0
