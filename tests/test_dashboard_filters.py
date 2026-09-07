import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import filter_dashboard_data, summarize_context_runs


def test_dashboard_filters_by_model_and_recommendation():
    data = {
        "candidates": [
            {"name": "model-a", "source": "ollama"},
            {"name": "model-b", "source": "huggingface"},
        ],
        "recommendations": [
            {"model": "model-a", "recommendation": "TEST_NOW"},
            {"model": "model-b", "recommendation": "WATCH"},
        ],
        "benchmark_runs": [],
    }

    filtered = filter_dashboard_data(data, model="model-a", recommendation="TEST_NOW")

    assert filtered["candidates"] == [{"name": "model-a", "source": "ollama"}]
    assert filtered["recommendations"] == [{"model": "model-a", "recommendation": "TEST_NOW"}]


def test_context_summary_aggregates_successful_runs():
    summary = summarize_context_runs([
        {"model": "model-a", "context": 8192, "status": "OK", "tok_per_sec": 20},
        {"model": "model-a", "context": 8192, "status": "OK", "tok_per_sec": 30},
        {"model": "model-a", "context": 16384, "status": "ERROR", "tok_per_sec": 0},
    ])

    assert summary == [{"model": "model-a", "context": 8192, "avg_tok_per_sec": 25.0, "runs": 2}]
