from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def load_queue(queue_path: str | Path) -> list[dict]:
    payload = json.loads(Path(queue_path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Queue must contain a JSON array")
    return payload


def build_download_plan(queue: list[dict], approved_models: set[str] | None = None) -> list[dict]:
    approved = approved_models or set()
    plan = []
    for item in queue:
        model = str(item.get("model", "")).strip()
        if not model:
            continue
        plan.append({
            "model": model,
            "command": ["ollama", "pull", model],
            "status": "APPROVED" if model in approved else "PENDING_APPROVAL",
        })
    return plan


def execute_download_plan(plan: list[dict]) -> list[dict]:
    if shutil.which("ollama") is None:
        raise RuntimeError("ollama executable was not found on PATH")

    results = []
    for item in plan:
        if item["status"] != "APPROVED":
            results.append({**item, "status": "SKIPPED"})
            continue
        completed = subprocess.run(item["command"], check=False, text=True)
        results.append({**item, "status": "DOWNLOADED" if completed.returncode == 0 else "FAILED", "returncode": completed.returncode})
    return results


def write_download_plan(plan: list[dict], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return path
