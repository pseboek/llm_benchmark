from __future__ import annotations

import json
from pathlib import Path

from benchmark.prompts import PERSONAL_PROMPTS, PROMPT_VERSION


def build_benchmark_plan(
    queue: list[dict],
    approved_models: set[str],
    contexts: list[int],
) -> list[dict]:
    plan = []
    for item in queue:
        model = str(item.get("model", "")).strip()
        if not model or model not in approved_models:
            continue
        for context in contexts:
            for category in PERSONAL_PROMPTS:
                plan.append({
                    "model": model,
                    "context": context,
                    "category": category,
                    "prompt_version": PROMPT_VERSION,
                    "status": "PENDING_EXECUTION",
                })
    return plan


def write_benchmark_plan(plan: list[dict], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return path
