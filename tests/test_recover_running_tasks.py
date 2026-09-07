import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB


def test_recover_running_tasks_resets_only_running_rows(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    db.save_benchmark_tasks([
        {"model": "a", "context": 8192, "category": "01 Java", "prompt_version": "v1", "status": "RUNNING"},
        {"model": "b", "context": 8192, "category": "01 Java", "prompt_version": "v1", "status": "COMPLETED"},
    ])

    assert db.recover_running_tasks() == 1
    statuses = {item["model"]: item["status"] for item in db.list_benchmark_tasks()}
    assert statuses == {"a": "PENDING_EXECUTION", "b": "COMPLETED"}
