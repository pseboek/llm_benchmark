import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.runner import reset_failed_tasks


def test_reset_failed_tasks_preserves_completed_tasks():
    plan = [
        {"model": "a", "context": 8192, "category": "01 Java", "status": "FAILED"},
        {"model": "b", "context": 8192, "category": "01 Java", "status": "COMPLETED"},
    ]

    updated = reset_failed_tasks(plan)

    assert updated[0]["status"] == "PENDING_EXECUTION"
    assert updated[1]["status"] == "COMPLETED"
