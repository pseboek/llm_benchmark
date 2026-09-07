import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_quality_by_context


def test_quality_by_context_aggregates_successful_runs():
    summary = summarize_quality_by_context([
        {"model": "model-a", "context": 8192, "status": "OK", "quality_score": 80},
        {"model": "model-a", "context": 8192, "status": "OK", "quality_score": 90},
        {"model": "model-a", "context": 16384, "status": "ERROR", "quality_score": 0},
    ])

    assert summary == [{
        "model": "model-a",
        "context": 8192,
        "avg_quality_score": 85.0,
        "runs": 2,
    }]
