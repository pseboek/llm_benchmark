import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.telemetry import aggregate_gpu_rows, parse_nvidia_smi_csv, parse_nvidia_smi_rows, summarize_telemetry_samples


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


def test_aggregate_gpu_rows_combines_multiple_devices():
    metrics = aggregate_gpu_rows(parse_nvidia_smi_rows("60, 4000, 16000\n80, 6000, 16000"))

    assert metrics == {
        "gpu_count": 2,
        "gpu_utilization_percent": 70.0,
        "gpu_utilization_peak_percent": 80.0,
        "gpu_memory_used_mb": 10000.0,
        "gpu_memory_total_mb": 32000.0,
        "gpu_memory_utilization_percent": 31.25,
    }


def test_summarize_telemetry_samples_returns_deltas_and_peaks():
    summary = summarize_telemetry_samples(
        {"gpu_utilization_percent": 20, "gpu_memory_used_mb": 1000, "ram_used_mb": 4000, "cpu_percent": 10},
        {"gpu_utilization_percent": 80, "gpu_memory_used_mb": 3000, "ram_used_mb": 5000, "cpu_percent": 40},
    )

    assert summary["gpu_utilization_percent_delta"] == 60.0
    assert summary["gpu_utilization_percent_peak"] == 80.0
    assert summary["gpu_memory_used_mb_peak"] == 3000.0
    assert summary["ram_used_mb_delta"] == 1000.0
    assert summary["cpu_percent_peak"] == 40.0
