import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import build_report
from src.scoring import score_candidate


def test_scoring_adds_actionable_rationale():
    scored = score_candidate({"name": "model", "coding": 95, "vram_gb": 12})

    assert "rationale" in scored
    assert "SAFE" in scored["rationale"]
    assert "score" in scored["rationale"]


def test_report_includes_vram_and_rationale():
    report = build_report([{"name": "model", "source": "ollama", "vram_gb": 12, "coding": 95}])

    assert "VRAM=12 GB" in report
    assert "Reason:" in report
