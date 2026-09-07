import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scoring import champion_comparison, benchmark_profile


def test_benchmark_profile_and_champion_comparison_use_real_runs():
    runs = [
        {"model": "challenger", "status": "OK", "tok_per_sec": 120, "quality_score": 90},
        {"model": "champion", "status": "OK", "tok_per_sec": 100, "quality_score": 80},
    ]

    profile = benchmark_profile("challenger", runs)
    comparison = champion_comparison(
        {"name": "challenger", "coding": 90},
        [{"name": "champion", "coding": 80}],
        benchmark_runs=runs,
    )

    assert profile == {"model": "challenger", "avg_tok_per_sec": 120.0, "avg_quality_score": 90.0, "runs": 1}
    assert comparison["speed_delta"] == 20.0
    assert comparison["quality_delta"] == 10.0
    assert comparison["advantage"] == "challenger"
