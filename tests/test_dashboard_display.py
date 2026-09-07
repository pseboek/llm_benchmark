import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import display_rows


def test_display_rows_replaces_missing_values_without_mutating_source():
    rows = [{"model": "model-a", "score": None, "hardware_tier": "EXTERNAL"}]

    displayed = display_rows(rows)

    assert displayed == [{"model": "model-a", "score": "Not available", "hardware_tier": "EXTERNAL"}]
    assert rows[0]["score"] is None
