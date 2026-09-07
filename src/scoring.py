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

def weighted_score(c: Candidate) -> float:
    return round(sum(
        max(0.0, min(100.0, getattr(c, key))) * weight
        for key, weight in WEIGHTS.items()
    ), 2)

def hardware_tier(vram_gb, *, is_moe=False, active_params_b=None):
    if vram_gb is None:
        return "UNKNOWN"
    if vram_gb <= 13:
        return "SAFE"
    if vram_gb <= 18:
        return "BORDERLINE"
    if vram_gb <= 24:
        return "EXPERIMENTAL"
    if is_moe and active_params_b is not None and active_params_b <= 5:
        return "SURPRISE"
    return "UNLIKELY"

def recommendation(score, tier):
    if score >= 85:
        return "TEST_NOW"
    if score >= 80 and tier in {"BORDERLINE", "EXPERIMENTAL", "SURPRISE"}:
        return "SURPRISE_TEST"
    if score >= 70:
        return "WATCH"
    return "IGNORE"


def score_candidate(candidate: dict) -> dict:
    """Add score, hardware tier, and action fields to a candidate record."""
    scored = dict(candidate)
    model = Candidate(
        name=str(candidate.get("name", "unknown")),
        **{field: float(candidate.get(field, 50.0)) for field in WEIGHTS},
        vram_gb=candidate.get("vram_gb"),
        is_moe=bool(candidate.get("is_moe", False)),
        active_params_b=candidate.get("active_params_b"),
    )
    score = weighted_score(model)
    tier = hardware_tier(
        model.vram_gb,
        is_moe=model.is_moe,
        active_params_b=model.active_params_b,
    )
    scored.update({
        "score": score,
        "hardware_tier": tier,
        "recommendation": recommendation(score, tier),
    })
    return scored
