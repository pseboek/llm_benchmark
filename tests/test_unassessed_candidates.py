import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import build_report
from src.scoring import score_candidate


def test_ollama_metadata_is_used_for_hardware_tier_without_fake_quality_score():
    scored = score_candidate({
        "name": "model-a",
        "source": "ollama",
        "estimated_vram_gb": 8.46,
        "parameter_size": "13.9B",
    })

    assert scored["score"] is None
    assert scored["hardware_tier"] == "SAFE"
    assert scored["recommendation"] == "NEEDS_DATA"
    assert "quality benchmark" in scored["rationale"]


def test_report_labels_unassessed_candidates_explicitly():
    report = build_report([{"name": "model-a", "source": "huggingface"}])

    assert "NEEDS_DATA" in report
    assert "not assessed" in report
    assert "50.00" not in report
