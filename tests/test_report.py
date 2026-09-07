import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import build_report


def test_build_report_contains_summary_and_candidates():
    candidates = [
        {"name": "qwen2.5-coder:14b-instruct", "source": "ollama"},
        {"name": "Qwen/Qwen2.5-Coder-14B-Instruct", "source": "huggingface"},
    ]

    report = build_report(candidates)

    assert "# Model Scout Report" in report
    assert "2 candidates" in report
    assert "qwen2.5-coder:14b-instruct" in report
    assert "Qwen/Qwen2.5-Coder-14B-Instruct" in report
