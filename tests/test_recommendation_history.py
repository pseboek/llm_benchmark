import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB


def test_saving_recommendation_replaces_previous_model_snapshot(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    item = {"model": "model-a", "score": 80, "hardware_tier": "SAFE", "recommendation": "WATCH"}
    db.save_recommendations([item])
    db.save_recommendations([{**item, "score": 90, "recommendation": "TEST_NOW"}])

    recommendations = db.list_recommendations()
    assert len(recommendations) == 1
    assert recommendations[0]["score"] == 90
    assert recommendations[0]["recommendation"] == "TEST_NOW"
