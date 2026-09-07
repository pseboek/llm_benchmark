import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import dashboard_metrics


def test_dashboard_metrics_include_needs_data_and_errors():
    metrics = dashboard_metrics(
        [{"recommendation": "NEEDS_DATA"}, {"recommendation": "TEST_NOW"}],
        [{"status": "ERROR"}, {"status": "OK"}],
    )

    assert metrics == {
        "test_now": 1,
        "watch": 0,
        "needs_data": 1,
        "errors": 1,
    }
