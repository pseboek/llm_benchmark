from pathlib import Path
import yaml
from scoring import Candidate, weighted_score, hardware_tier, recommendation

ROOT = Path(__file__).resolve().parents[1]

def load_config():
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    load_config()

    # Skeleton candidate. Replace with the five real source adapters.
    candidates = [
        Candidate(
            name="example-candidate",
            coding=90, reasoning=88, general=85, speed=80,
            vram_efficiency=75, context=95, tool_agent=90,
            freshness=100, vram_gb=15.5, is_moe=True,
            active_params_b=4
        )
    ]

    for c in candidates:
        score = weighted_score(c)
        tier = hardware_tier(
            c.vram_gb, is_moe=c.is_moe,
            active_params_b=c.active_params_b
        )
        print(c.name, score, tier, recommendation(score, tier))

if __name__ == "__main__":
    main()
