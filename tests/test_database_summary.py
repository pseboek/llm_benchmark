import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB


def test_database_summary_reports_table_counts(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    db.save_candidates([{"name": "model-a", "source": "ollama"}])
    db.save_recommendations([{"model": "model-a", "score": None, "hardware_tier": "SAFE", "recommendation": "NEEDS_DATA"}])

    summary = db.summary()

    assert summary["candidates"] == 1
    assert summary["recommendations"] == 1
    assert summary["benchmark_runs"] == 0
    assert summary["needs_data"] == 1
