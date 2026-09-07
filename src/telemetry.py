from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any


def parse_nvidia_smi_csv(output: str) -> dict[str, float | None]:
    values = [part.strip() for part in output.strip().split(",")]
    if len(values) < 3:
        return {"gpu_utilization_percent": None, "gpu_memory_used_mb": None, "gpu_memory_total_mb": None}

    def number(value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            return None

    return {
        "gpu_utilization_percent": number(values[0]),
        "gpu_memory_used_mb": number(values[1]),
        "gpu_memory_total_mb": number(values[2]),
    }


def parse_nvidia_smi_rows(output: str) -> list[dict[str, float | None]]:
    return [parse_nvidia_smi_csv(line) for line in output.splitlines() if line.strip()]


def _average(values: list[float | None]) -> float | None:
    available = [value for value in values if value is not None]
    return round(sum(available) / len(available), 2) if available else None


def aggregate_gpu_rows(rows: list[dict[str, float | None]]) -> dict[str, Any]:
    utilizations = [row["gpu_utilization_percent"] for row in rows]
    used = [row["gpu_memory_used_mb"] for row in rows]
    total = [row["gpu_memory_total_mb"] for row in rows]
    used_total = sum(value for value in used if value is not None)
    memory_total = sum(value for value in total if value is not None)
    return {
        "gpu_count": len(rows),
        "gpu_utilization_percent": _average(utilizations),
        "gpu_utilization_peak_percent": max((value for value in utilizations if value is not None), default=None),
        "gpu_memory_used_mb": round(used_total, 2) if used else None,
        "gpu_memory_total_mb": round(memory_total, 2) if total else None,
        "gpu_memory_utilization_percent": round(used_total / memory_total * 100, 2) if memory_total else None,
    }


def summarize_telemetry_samples(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for field in ("gpu_utilization_percent", "gpu_memory_used_mb", "ram_used_mb", "cpu_percent"):
        start = before.get(field)
        end = after.get(field)
        if start is not None and end is not None:
            metrics[f"{field}_delta"] = round(float(end) - float(start), 2)
            metrics[f"{field}_peak"] = round(max(float(start), float(end)), 2)
    for key, value in after.items():
        if key not in metrics:
            metrics[key] = value
    return metrics


def capture_telemetry() -> dict[str, Any]:
    telemetry: dict[str, Any] = {
        "telemetry_captured_at": datetime.now(timezone.utc).isoformat(),
        "gpu_count": 0,
        "gpu_utilization_percent": None,
        "gpu_utilization_peak_percent": None,
        "gpu_memory_used_mb": None,
        "gpu_memory_total_mb": None,
        "gpu_memory_utilization_percent": None,
        "ram_used_mb": None,
        "cpu_percent": None,
    }
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi:
        try:
            result = subprocess.run(
                [nvidia_smi, "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            telemetry.update(aggregate_gpu_rows(parse_nvidia_smi_rows(result.stdout)))
        except (OSError, subprocess.SubprocessError):
            pass

    try:
        import psutil
        telemetry["ram_used_mb"] = round(psutil.virtual_memory().used / 1024**2, 2)
        telemetry["cpu_percent"] = psutil.cpu_percent(interval=None)
    except (ImportError, OSError):
        pass
    return telemetry
