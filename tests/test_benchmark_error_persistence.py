import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB


def test_benchmark_error_is_persisted(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    db.save_benchmark_runs([{
        "model": "model-a",
        "context": 8192,
        "category": "01 Java",
        "status": "ERROR",
        "error": "request timed out",
    }])

    run = db.list_benchmark_runs()[0]
    assert run["status"] == "ERROR"
    assert run["error"] == "request timed out"
