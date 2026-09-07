import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scoring import enrich_from_benchmark, score_candidate


def test_benchmark_runs_enrich_candidate_quality_and_speed():
    candidate = {"name": "model-a", "source": "ollama", "estimated_vram_gb": 8}
    runs = [
        {"model": "model-a", "category": "01 Java", "status": "OK", "quality_score": 90, "tok_per_sec": 40},
        {"model": "model-a", "category": "10 General Reasoning", "status": "OK", "quality_score": 80, "tok_per_sec": 40},
    ]

    enriched = enrich_from_benchmark(candidate, runs)
    scored = score_candidate(enriched)

    assert enriched["coding"] == 90
    assert enriched["reasoning"] == 80
    assert enriched["speed"] == 40
    assert scored["score"] is not None
