from dataclasses import dataclass

from src.discovery import normalize_model_name

WEIGHTS = {
    "coding": 0.25, "reasoning": 0.20, "general": 0.15,
    "speed": 0.15, "vram_efficiency": 0.10, "context": 0.05,
    "tool_agent": 0.05, "freshness": 0.05,
}

@dataclass
class Candidate:
    name: str
    coding: float = 0
    reasoning: float = 0
    general: float = 0
    speed: float = 0
    vram_efficiency: float = 0
    context: float = 0
    tool_agent: float = 0
    freshness: float = 0
    vram_gb: float | None = None
    is_moe: bool = False
    active_params_b: float | None = None

def weighted_score(c: Candidate, weights: dict[str, float] | None = None) -> float:
    active_weights = weights or WEIGHTS
    return round(sum(
        max(0.0, min(100.0, getattr(c, key, 0.0))) * weight
        for key, weight in active_weights.items()
    ), 2)

def hardware_tier(vram_gb, *, is_moe=False, active_params_b=None, limits=None):
    active_limits = limits or {"safe_gb": 13, "borderline_gb": 18, "experimental_gb": 24}
    if vram_gb is None:
        return "UNKNOWN"
    if vram_gb <= active_limits["safe_gb"]:
        return "SAFE"
    if vram_gb <= active_limits["borderline_gb"]:
        return "BORDERLINE"
    if vram_gb <= active_limits["experimental_gb"]:
        return "EXPERIMENTAL"
    if is_moe and active_params_b is not None and active_params_b <= 5:
        return "SURPRISE"
    return "UNLIKELY"

def recommendation(score, tier, thresholds=None):
    if score is None:
        return "NEEDS_DATA"
    active_thresholds = thresholds or {"test_now": 85, "surprise": 80, "watch": 70}
    if score >= active_thresholds["test_now"]:
        return "TEST_NOW"
    if score >= active_thresholds["surprise"] and tier in {"BORDERLINE", "EXPERIMENTAL", "SURPRISE"}:
        return "SURPRISE_TEST"
    if score >= active_thresholds["watch"]:
        return "WATCH"
    return "IGNORE"


def rationale(score: float, tier: str, action: str, vram_gb: float | None = None) -> str:
    hardware = f"estimated VRAM {vram_gb:g} GB" if vram_gb is not None else "VRAM estimate unavailable"
    if score is None:
        return f"NEEDS_DATA: quality benchmark data is not assessed; hardware tier {tier}, {hardware}."
    return f"{action}: score {score:.2f}, hardware tier {tier}, {hardware}."


def score_candidate(candidate: dict, *, weights=None, thresholds=None, hardware_limits=None) -> dict:
    """Add score, hardware tier, and action fields to a candidate record."""
    scored = dict(candidate)
    quality_fields = set(WEIGHTS).intersection(candidate)
    has_quality_data = bool(quality_fields)
    model = Candidate(
        name=str(candidate.get("name", "unknown")),
        **{field: float(candidate.get(field, 0.0)) for field in WEIGHTS},
        vram_gb=candidate.get("vram_gb", candidate.get("estimated_vram_gb")),
        is_moe=bool(candidate.get("is_moe", False)),
        active_params_b=candidate.get("active_params_b"),
    )
    score = weighted_score(model, weights) if has_quality_data else None
    tier = hardware_tier(
        model.vram_gb,
        is_moe=model.is_moe,
        active_params_b=model.active_params_b,
        limits=hardware_limits,
    )
    if model.vram_gb is None and str(candidate.get("source", "")).lower() not in {"", "ollama", "config"}:
        tier = "EXTERNAL"
    action = recommendation(score, tier, thresholds)
    scored.update({
        "score": score,
        "hardware_tier": tier,
        "recommendation": action,
        "vram_gb": model.vram_gb,
        "rationale": rationale(score, tier, action, model.vram_gb),
        "assessment_status": "ASSESSED" if score is not None else ("METADATA_ONLY" if model.vram_gb is not None else "NEEDS_DATA"),
    })
    return scored


def benchmark_profile(model: str, runs: list[dict]) -> dict | None:
    successful = [run for run in runs if run.get("model") == model and run.get("status") == "OK"]
    if not successful:
        return None
    speeds = [float(run.get("tok_per_sec", 0)) for run in successful]
    qualities = [float(run["quality_score"]) for run in successful if run.get("quality_score") is not None]
    return {
        "model": model,
        "avg_tok_per_sec": round(sum(speeds) / len(speeds), 2),
        "avg_quality_score": round(sum(qualities) / len(qualities), 2) if qualities else None,
        "runs": len(successful),
    }


def enrich_from_baseline(candidate: dict, baseline: list[dict]) -> dict:
    candidate_key = normalize_model_name(str(candidate.get("name", "")))
    for item in baseline:
        if normalize_model_name(str(item.get("name", ""))) != candidate_key:
            continue
        speed = min(100.0, float(item.get("generation_tps", 0.0)) / 1.5)
        enriched = dict(candidate)
        enriched.update({
            "role": item.get("role", "baseline"),
            "coding": 90.0,
            "reasoning": 88.0,
            "general": 85.0,
            "speed": speed,
            "vram_efficiency": 78.0,
            "context": 90.0,
            "tool_agent": 80.0,
            "freshness": 90.0,
        })
        return enriched
    return candidate


def enrich_from_benchmark(candidate: dict, runs: list[dict]) -> dict:
    model_runs = [
        run for run in runs
        if run.get("model") == candidate.get("name") and run.get("status") == "OK"
    ]
    quality_runs = [run for run in model_runs if run.get("quality_score") is not None]
    if not model_runs:
        return candidate

    enriched = dict(candidate)
    speeds = [float(run.get("tok_per_sec", 0)) for run in model_runs]
    enriched["speed"] = round(sum(speeds) / len(speeds), 2)
    coding_categories = ("Java", "Spring", "React", "TypeScript", "SQL", "Debugging", "Architecture", "MCP", "RAG")
    coding_scores = [
        float(run["quality_score"])
        for run in quality_runs
        if any(category in str(run.get("category", "")) for category in coding_categories)
    ]
    reasoning_scores = [
        float(run["quality_score"])
        for run in quality_runs
        if "Reasoning" in str(run.get("category", ""))
    ]
    if coding_scores:
        enriched["coding"] = round(sum(coding_scores) / len(coding_scores), 2)
    if reasoning_scores:
        enriched["reasoning"] = round(sum(reasoning_scores) / len(reasoning_scores), 2)
    return enriched


def champion_comparison(candidate: dict, champions: list[dict], *, weights=None, thresholds=None, hardware_limits=None, benchmark_runs=None) -> dict:
    scored_candidate = score_candidate(
        candidate,
        weights=weights,
        thresholds=thresholds,
        hardware_limits=hardware_limits,
    )
    if not champions:
        return {"candidate": candidate.get("name", "unknown"), "champion": None, "delta": None, "advantage": "unknown"}

    scored_champions = [
        score_candidate(
            champion,
            weights=weights,
            thresholds=thresholds,
            hardware_limits=hardware_limits,
        )
        for champion in champions
    ]
    champion = max(scored_champions, key=lambda item: item["score"] if item["score"] is not None else -1)
    candidate_profile = benchmark_profile(scored_candidate["name"], benchmark_runs or [])
    champion_profile = benchmark_profile(champion["name"], benchmark_runs or [])
    speed_delta = None
    quality_delta = None
    if candidate_profile and champion_profile:
        speed_delta = round(candidate_profile["avg_tok_per_sec"] - champion_profile["avg_tok_per_sec"], 2)
        if candidate_profile["avg_quality_score"] is not None and champion_profile["avg_quality_score"] is not None:
            quality_delta = round(candidate_profile["avg_quality_score"] - champion_profile["avg_quality_score"], 2)
    if scored_candidate["score"] is None or champion["score"] is None:
        return {
            "candidate": scored_candidate["name"],
            "champion": champion["name"],
            "delta": None,
            "speed_delta": speed_delta,
            "quality_delta": quality_delta,
            "advantage": "needs_data",
        }
    delta = round(scored_candidate["score"] - champion["score"], 2)
    return {
        "candidate": scored_candidate["name"],
        "champion": champion["name"],
        "delta": delta,
        "speed_delta": speed_delta,
        "quality_delta": quality_delta,
        "advantage": "challenger" if delta > 0 else "champion",
    }
