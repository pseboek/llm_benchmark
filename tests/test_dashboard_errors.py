import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_errors


def test_error_summary_exposes_failed_benchmark_details():
    errors = summarize_errors([
        {"model": "model-a", "context": 8192, "category": "01 Java", "status": "ERROR", "error": "request timed out"},
        {"model": "model-a", "context": 16384, "category": "02 Spring Boot", "status": "OK", "error": None},
    ])

    assert errors == [{
        "model": "model-a",
        "context": 8192,
        "category": "01 Java",
        "error": "request timed out",
    }]
