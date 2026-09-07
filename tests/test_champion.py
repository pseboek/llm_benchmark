import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import build_report
from src.scoring import champion_comparison


def test_champion_comparison_reports_expected_advantage():
    result = champion_comparison(
        {"name": "challenger", "coding": 95, "reasoning": 90},
        [{"name": "champion", "coding": 80, "reasoning": 80}],
    )

    assert result["champion"] == "champion"
    assert result["delta"] > 0
    assert result["advantage"] == "challenger"


def test_report_includes_champion_comparison():
    report = build_report(
        [{"name": "challenger", "coding": 95, "reasoning": 90}],
        champions=[{"name": "champion", "coding": 80, "reasoning": 80}],
    )

    assert "## Champion Comparison" in report
    assert "challenger vs champion" in report
