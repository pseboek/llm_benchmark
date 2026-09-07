import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scoring import enrich_from_baseline, score_candidate


def test_known_baseline_model_receives_quality_profile():
    candidate = {"name": "gpt-oss:20b", "source": "ollama", "estimated_vram_gb": 15.0}
    baseline = [{"name": "gpt-oss:20b", "role": "general", "generation_tps": 140.0}]

    enriched = enrich_from_baseline(candidate, baseline)
    scored = score_candidate(enriched)

    assert enriched["speed"] > 90
    assert scored["score"] is not None
    assert scored["recommendation"] in {"TEST_NOW", "SURPRISE_TEST", "WATCH", "IGNORE"}


def test_external_candidate_without_quality_data_is_external_not_unknown():
    scored = score_candidate({"name": "org/model", "source": "huggingface"})

    assert scored["score"] is None
    assert scored["hardware_tier"] == "EXTERNAL"
    assert scored["recommendation"] == "NEEDS_DATA"
