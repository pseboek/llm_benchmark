import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_quality


def test_quality_summary_aggregates_model_categories():
    summary = summarize_quality([
        {"model": "model-a", "category": "01 Java", "status": "OK", "quality_score": 80},
        {"model": "model-a", "category": "01 Java", "status": "OK", "quality_score": 90},
        {"model": "model-a", "category": "10 General Reasoning", "status": "OK", "quality_score": 70},
        {"model": "model-a", "category": "02 Spring Boot", "status": "ERROR", "quality_score": 0},
    ])

    assert summary == [
        {"model": "model-a", "category": "01 Java", "avg_quality_score": 85.0, "runs": 2},
        {"model": "model-a", "category": "10 General Reasoning", "avg_quality_score": 70.0, "runs": 1},
    ]
