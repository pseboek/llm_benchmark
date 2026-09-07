import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_task_progress


def test_task_progress_reports_counts_and_percentages():
    progress = summarize_task_progress([
        {"status": "COMPLETED"},
        {"status": "COMPLETED"},
        {"status": "PENDING_EXECUTION"},
        {"status": "FAILED"},
    ])

    assert progress == [
        {"status": "COMPLETED", "tasks": 2, "percent": 50.0},
        {"status": "FAILED", "tasks": 1, "percent": 25.0},
        {"status": "PENDING_EXECUTION", "tasks": 1, "percent": 25.0},
    ]
