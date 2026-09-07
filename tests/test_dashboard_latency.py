import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_latency


def test_latency_summary_aggregates_ttft_and_prompt_speed():
    summary = summarize_latency([
        {"model": "model-a", "status": "OK", "ttft_seconds": 0.1, "prompt_tok_per_sec": 100},
        {"model": "model-a", "status": "OK", "ttft_seconds": 0.3, "prompt_tok_per_sec": 80},
        {"model": "model-a", "status": "ERROR", "ttft_seconds": 9, "prompt_tok_per_sec": 0},
    ])

    assert summary == [{
        "model": "model-a",
        "avg_ttft_seconds": 0.2,
        "avg_prompt_tok_per_sec": 90.0,
        "runs": 2,
    }]
