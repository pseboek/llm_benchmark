import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB


def test_database_summary_counts_benchmark_errors(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    db.save_benchmark_runs([{
        "model": "model-a",
        "context": 8192,
        "category": "01 Java",
        "status": "ERROR",
        "error": "timeout",
    }])

    assert db.summary()["benchmark_errors"] == 1
