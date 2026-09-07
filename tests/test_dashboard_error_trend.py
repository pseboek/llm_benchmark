import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_error_trend


def test_error_trend_groups_failed_runs_by_model_and_category():
    trend = summarize_error_trend([
        {"model": "model-a", "category": "01 Java", "status": "ERROR"},
        {"model": "model-a", "category": "01 Java", "status": "ERROR"},
        {"model": "model-a", "category": "02 Spring Boot", "status": "OK"},
    ])

    assert trend == [{"model": "model-a", "category": "01 Java", "errors": 2}]
