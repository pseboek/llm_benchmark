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

    assert records == [{
        "name": "model-a",
        "source": "config",
        "role": "coding",
        "generation_tps": 100.0,
    }]
