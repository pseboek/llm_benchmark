import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scoring import Candidate, hardware_tier, recommendation, score_candidate, weighted_score


def test_custom_weights_change_candidate_score():
    candidate = {"name": "model", "coding": 100, "reasoning": 0}

    assert weighted_score(
        Candidate(name="model", coding=100, reasoning=0),
        weights={"coding": 1.0, "reasoning": 0.0},
    ) == 100.0


def test_custom_thresholds_and_hardware_limits_are_used():
    assert recommendation(75, "SAFE", {"test_now": 75, "surprise": 70, "watch": 60}) == "TEST_NOW"
    assert hardware_tier(10, limits={"safe_gb": 8, "borderline_gb": 12, "experimental_gb": 20}) == "BORDERLINE"


def test_score_candidate_accepts_configuration():
    scored = score_candidate(
        {"name": "model", "coding": 100, "vram_gb": 10},
        weights={"coding": 1.0},
        thresholds={"test_now": 90, "surprise": 80, "watch": 70},
        hardware_limits={"safe_gb": 8, "borderline_gb": 12, "experimental_gb": 20},
    )

    assert scored["score"] == 100.0
    assert scored["recommendation"] == "TEST_NOW"
    assert scored["hardware_tier"] == "BORDERLINE"
