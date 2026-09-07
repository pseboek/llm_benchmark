import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB


def test_task_status_summary_counts_lifecycle_states(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    db.save_benchmark_tasks([
        {"model": "a", "context": 8192, "category": "01 Java", "prompt_version": "v1", "status": "COMPLETED"},
        {"model": "b", "context": 8192, "category": "01 Java", "prompt_version": "v1", "status": "FAILED"},
    ])

    assert db.benchmark_task_summary() == {"total": 2, "by_status": {"COMPLETED": 1, "FAILED": 1}}
