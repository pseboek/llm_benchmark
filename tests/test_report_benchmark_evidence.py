import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import build_report


def test_report_includes_benchmark_evidence():
    report = build_report(
        [{"name": "model-a", "source": "ollama", "coding": 90}],
        benchmark_runs=[
            {"model": "model-a", "status": "OK", "tok_per_sec": 100, "quality_score": 80},
            {"model": "model-a", "status": "ERROR", "tok_per_sec": 0, "quality_score": 0},
        ],
    )

    assert "## Benchmark Evidence" in report
    assert "model-a" in report
    assert "100.00 tok/s" in report
    assert "80.00 quality" in report
    assert "runs=1" in report
