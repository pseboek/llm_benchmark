import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import filter_dashboard_data


def test_dashboard_filters_by_source_and_hardware_tier():
    data = {
        "candidates": [
            {"name": "local", "source": "ollama", "hardware_tier": "SAFE"},
            {"name": "external", "source": "huggingface", "hardware_tier": "EXTERNAL"},
        ],
        "recommendations": [],
        "benchmark_runs": [],
        "report_snapshots": [],
        "benchmark_tasks": [],
        "source_status": [],
    }

    filtered = filter_dashboard_data(data, source="ollama", hardware_tier="SAFE")

    assert filtered["candidates"] == [{"name": "local", "source": "ollama", "hardware_tier": "SAFE"}]
