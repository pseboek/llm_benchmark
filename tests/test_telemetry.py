import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.telemetry import parse_nvidia_smi_csv


def test_parse_nvidia_smi_csv_returns_gpu_metrics():
    metrics = parse_nvidia_smi_csv("73, 4096, 16384")

    assert metrics == {
        "gpu_utilization_percent": 73.0,
        "gpu_memory_used_mb": 4096.0,
        "gpu_memory_total_mb": 16384.0,
    }


def test_parse_nvidia_smi_csv_handles_unavailable_values():
    metrics = parse_nvidia_smi_csv("N/A, N/A, N/A")

    assert metrics["gpu_utilization_percent"] is None
    assert metrics["gpu_memory_used_mb"] is None
