from __future__ import annotations

import json
from pathlib import Path

from src.scoring import score_candidate


def build_benchmark_queue(
    candidates: list[dict],
    max_candidates: int = 5,
    *,
    scoring_config: dict | None = None,
    thresholds: dict | None = None,
    hardware_limits: dict | None = None,
) -> list[dict]:
    scored = [
        score_candidate(
            candidate,
            weights=scoring_config,
            thresholds=thresholds,
            hardware_limits=hardware_limits,
        )
        for candidate in candidates
    ]
    selected = [
        candidate
        for candidate in scored
        if candidate["recommendation"] in {"TEST_NOW", "SURPRISE_TEST"}
    ]
    selected.sort(key=lambda candidate: candidate["score"], reverse=True)
    return [
        {
            "model": candidate["name"],
            "source": candidate.get("source", "unknown"),
            "score": candidate["score"],
            "hardware_tier": candidate["hardware_tier"],
            "recommendation": candidate["recommendation"],
            "status": "PENDING_REVIEW",
        }
        for candidate in selected[:max_candidates]
    ]


def write_benchmark_queue(queue: list[dict], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    return path
