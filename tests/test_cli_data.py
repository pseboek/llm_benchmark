import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.main import build_baseline_records


def test_baseline_records_provide_offline_report_candidates():
    records = build_baseline_records({
        "baseline": [
            {"name": "model-a", "role": "coding", "generation_tps": 100},
        ]
    })

    assert records[0]["name"] == "model-a"
    assert records[0]["source"] == "config"
    assert records[0]["generation_tps"] == 100.0
    assert records[0]["speed"] == 100.0 / 1.5
