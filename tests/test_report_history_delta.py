import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_report_history


def test_report_history_includes_deltas_from_previous_snapshot():
    summary = summarize_report_history([
        {"created_at": "2026-09-06", "total_candidates": 10, "test_now": 1, "surprise_test": 0, "watch": 2, "needs_data": 7, "ignored": 0},
        {"created_at": "2026-09-07", "total_candidates": 12, "test_now": 2, "surprise_test": 1, "watch": 3, "needs_data": 6, "ignored": 0},
    ])

    assert summary[0]["test_now_delta"] == 0
    assert summary[1]["test_now_delta"] == 1
    assert summary[1]["needs_data_delta"] == -1
