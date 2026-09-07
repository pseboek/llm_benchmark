import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB


def test_benchmark_tasks_can_be_saved_and_completed(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    task = {"model": "model-a", "context": 8192, "category": "01 Java", "prompt_version": "v1", "status": "PENDING_EXECUTION"}
    db.save_benchmark_tasks([task])
    db.update_benchmark_task_status("model-a", 8192, "01 Java", "COMPLETED")

    tasks = db.list_benchmark_tasks()
    assert tasks[0]["status"] == "COMPLETED"
