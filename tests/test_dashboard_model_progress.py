import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_model_progress


def test_model_progress_groups_task_status_by_model():
    progress = summarize_model_progress([
        {"model": "model-a", "status": "COMPLETED"},
        {"model": "model-a", "status": "PENDING_EXECUTION"},
        {"model": "model-b", "status": "FAILED"},
    ])

    assert progress == [
        {"model": "model-a", "completed": 1, "pending": 1, "failed": 0, "total": 2},
        {"model": "model-b", "completed": 0, "pending": 0, "failed": 1, "total": 1},
    ]
