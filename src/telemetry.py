from __future__ import annotations

import shutil
import subprocess
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


def capture_telemetry() -> dict[str, Any]:
    telemetry: dict[str, Any] = {
        "gpu_utilization_percent": None,
        "gpu_memory_used_mb": None,
        "gpu_memory_total_mb": None,
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
            telemetry.update(parse_nvidia_smi_csv(result.stdout.splitlines()[0]))
        except (OSError, subprocess.SubprocessError, IndexError):
            pass

    try:
        import psutil
        telemetry["ram_used_mb"] = round(psutil.virtual_memory().used / 1024**2, 2)
        telemetry["cpu_percent"] = psutil.cpu_percent(interval=None)
    except (ImportError, OSError):
        pass
    return telemetry
