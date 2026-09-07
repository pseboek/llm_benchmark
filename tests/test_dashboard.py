import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import load_dashboard_data, summarize_runs
from src.database import ModelScoutDB


def test_dashboard_loads_history_and_summarizes_successful_runs(tmp_path):
    db_path = tmp_path / "scout.db"
    db = ModelScoutDB(db_path)
    db.save_candidates([{"name": "model-a", "source": "ollama"}])
    db.save_benchmark_runs([
        {"model": "model-a", "context": 8192, "category": "Java", "status": "OK", "tok_per_sec": 20},
        {"model": "model-a", "context": 16384, "category": "React", "status": "OK", "tok_per_sec": 30},
        {"model": "model-a", "context": 8192, "category": "SQL", "status": "ERROR", "tok_per_sec": 0},
    ])

    data = load_dashboard_data(db_path)

    assert len(data["candidates"]) == 1
    assert summarize_runs(data["benchmark_runs"]) == [
        {"model": "model-a", "avg_tok_per_sec": 25.0, "runs": 2}
    ]
