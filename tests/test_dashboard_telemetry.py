import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard import summarize_telemetry


def test_telemetry_summary_aggregates_available_metrics():
    summary = summarize_telemetry([
        {"model": "model-a", "status": "OK", "gpu_utilization_percent": 60, "gpu_memory_used_mb": 4000, "ram_used_mb": 8000, "cpu_percent": 20},
        {"model": "model-a", "status": "OK", "gpu_utilization_percent": 80, "gpu_memory_used_mb": 6000, "ram_used_mb": 10000, "cpu_percent": 40},
        {"model": "model-a", "status": "ERROR", "gpu_utilization_percent": 100},
    ])

    assert summary == [{
        "model": "model-a",
        "avg_gpu_percent": 70.0,
        "peak_gpu_memory_mb": 6000.0,
        "avg_ram_mb": 9000.0,
        "avg_cpu_percent": 30.0,
        "runs": 2,
    }]
