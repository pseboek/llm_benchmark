import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.adaptive import adaptive_weights


def test_adaptive_weights_rewards_speed_when_history_differs():
    base = {"coding": 0.25, "general": 0.15, "speed": 0.15}
    runs = [
        {"model": "fast", "status": "OK", "tok_per_sec": 100},
        {"model": "slow", "status": "OK", "tok_per_sec": 50},
    ]

    adjusted = adaptive_weights(base, runs)

    assert adjusted["speed"] > base["speed"]
    assert adjusted["general"] < base["general"]
    assert sum(adjusted.values()) == sum(base.values())


def test_adaptive_weights_is_stable_without_comparable_history():
    base = {"general": 0.15, "speed": 0.15}

    assert adaptive_weights(base, [{"model": "only", "status": "OK", "tok_per_sec": 50}]) == base
