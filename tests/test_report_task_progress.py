import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import benchmark_task_progress


def test_report_task_progress_returns_counts_and_percent():
    progress = benchmark_task_progress([
        {"status": "COMPLETED"},
        {"status": "COMPLETED"},
        {"status": "PENDING_EXECUTION"},
    ])

    assert progress == {"total": 3, "completed": 2, "pending": 1, "failed": 0, "percent": 66.67}
