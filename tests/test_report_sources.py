import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import build_report


def test_report_shows_source_coverage_and_empty_sources():
    report = build_report([
        {"name": "local-model", "source": "ollama", "coding": 90},
        {"name": "external-model", "source": "huggingface"},
    ])

    assert "## Source Coverage" in report
    assert "ollama: 1" in report
    assert "huggingface: 1" in report
    assert "lmarena: 0" in report
    assert "artificial_analysis: 0" in report
    assert "swebench: 0" in report
