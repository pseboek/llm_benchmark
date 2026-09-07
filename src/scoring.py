from dataclasses import dataclass

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
    return f"{action}: score {score:.2f}, hardware tier {tier}, {hardware}."


def score_candidate(candidate: dict, *, weights=None, thresholds=None, hardware_limits=None) -> dict:
    """Add score, hardware tier, and action fields to a candidate record."""
    scored = dict(candidate)
    model = Candidate(
        name=str(candidate.get("name", "unknown")),
        **{field: float(candidate.get(field, 50.0)) for field in WEIGHTS},
        vram_gb=candidate.get("vram_gb"),
        is_moe=bool(candidate.get("is_moe", False)),
        active_params_b=candidate.get("active_params_b"),
    )
    score = weighted_score(model, weights)
    tier = hardware_tier(
        model.vram_gb,
        is_moe=model.is_moe,
        active_params_b=model.active_params_b,
        limits=hardware_limits,
    )
    action = recommendation(score, tier, thresholds)
    scored.update({
        "score": score,
        "hardware_tier": tier,
        "recommendation": action,
        "rationale": rationale(score, tier, action, model.vram_gb),
    })
    return scored


def champion_comparison(candidate: dict, champions: list[dict], *, weights=None, thresholds=None, hardware_limits=None) -> dict:
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
    champion = max(scored_champions, key=lambda item: item["score"])
    delta = round(scored_candidate["score"] - champion["score"], 2)
    return {
        "candidate": scored_candidate["name"],
        "champion": champion["name"],
        "delta": delta,
        "advantage": "challenger" if delta > 0 else "champion",
    }
