import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import benchmark_evidence_by_context


def test_benchmark_evidence_groups_by_model_and_context():
    evidence = benchmark_evidence_by_context([
        {"model": "model-a", "context": 8192, "status": "OK", "tok_per_sec": 100, "quality_score": 80},
        {"model": "model-a", "context": 8192, "status": "OK", "tok_per_sec": 120, "quality_score": 90},
        {"model": "model-a", "context": 16384, "status": "ERROR", "tok_per_sec": 0, "quality_score": 0},
    ])

    assert evidence == [{
        "model": "model-a",
        "context": 8192,
        "avg_tok_per_sec": 110.0,
        "avg_quality_score": 85.0,
        "runs": 2,
    }]
