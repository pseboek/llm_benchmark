import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_report_history
from src.database import ModelScoutDB
from src.report import build_report_snapshot


def test_report_snapshot_counts_recommendations():
    snapshot = build_report_snapshot([
        {"name": "model-a", "coding": 100, "reasoning": 100, "general": 100, "speed": 100, "vram_efficiency": 100, "context": 100, "tool_agent": 100, "freshness": 100},
        {"name": "model-b", "source": "huggingface"},
    ])

    assert snapshot["total_candidates"] == 2
    assert snapshot["test_now"] == 1
    assert snapshot["needs_data"] == 1


def test_report_snapshots_are_persisted_and_summarized(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    db.save_report_snapshot({"total_candidates": 2, "test_now": 1, "surprise_test": 0, "watch": 0, "needs_data": 1, "ignored": 0, "output_path": "report.md"})

    history = db.list_report_snapshots()
    assert summarize_report_history(history)[0]["total_candidates"] == 2
