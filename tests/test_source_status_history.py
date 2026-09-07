import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_source_status
from src.database import ModelScoutDB


def test_source_status_is_persisted_and_summarized(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    status = {
        "ollama": {"status": "OK", "candidates": 13},
        "huggingface": {"status": "OK", "candidates": 1},
        "swebench": {"status": "EMPTY", "candidates": 0},
    }
    db.save_source_status(status)

    rows = db.list_source_status()
    assert summarize_source_status(rows) == [
        {"source": "huggingface", "status": "OK", "candidates": 1},
        {"source": "ollama", "status": "OK", "candidates": 13},
        {"source": "swebench", "status": "EMPTY", "candidates": 0},
    ]
