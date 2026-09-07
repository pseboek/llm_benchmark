from __future__ import annotations

from collections import defaultdict


def adaptive_weights(base_weights: dict[str, float], benchmark_runs: list[dict]) -> dict[str, float]:
    """Adjust weights from observed throughput while preserving total weight.

    Speed receives a small bonus only when historical runs show meaningful
    differences between models. The adjustment is returned for review and is
    never written to configuration automatically.
    """
    weights = {name: float(value) for name, value in base_weights.items()}
    if "speed" not in weights:
        return weights

    by_model: dict[str, list[float]] = defaultdict(list)
    for run in benchmark_runs:
        if run.get("status") == "OK":
            by_model[str(run.get("model", "unknown"))].append(float(run.get("tok_per_sec", 0)))

    averages = [sum(values) / len(values) for values in by_model.values() if values]
    if len(averages) < 2 or min(averages) <= 0:
        return weights

    spread = (max(averages) - min(averages)) / min(averages)
    bonus = min(0.05, max(0.0, spread * 0.02))
    donor = "general" if "general" in weights else max(weights, key=weights.get)
    transferable = min(bonus, weights[donor])
    weights["speed"] += transferable
    weights[donor] -= transferable
    return {name: round(value, 6) for name, value in weights.items()}
