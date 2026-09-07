import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB
from src.report import build_report, write_report
from src.scoring import score_candidate


def test_score_candidate_returns_recommendation_and_hardware_tier():
    scored = score_candidate({
        "name": "qwen3-coder:30b",
        "source": "ollama",
        "vram_gb": 20,
        "is_moe": True,
        "active_params_b": 3,
        "coding": 95,
        "reasoning": 90,
    })

    assert scored["score"] > 0
    assert scored["hardware_tier"] == "EXPERIMENTAL"
    assert scored["recommendation"] in {"TEST_NOW", "SURPRISE_TEST", "WATCH", "IGNORE"}


def test_report_groups_recommendations_and_can_be_written(tmp_path):
    report = build_report([
        {"name": "qwen3-coder:30b", "source": "ollama", "coding": 95, "reasoning": 90},
        {"name": "tiny-model", "source": "huggingface"},
    ])

    assert "## Test Now" in report
    assert "## Watchlist" in report
    assert "qwen3-coder:30b" in report

    output = write_report(report, tmp_path / "scout.md")
    assert output.exists()
    assert output.read_text(encoding="utf-8") == report


def test_database_stores_benchmark_runs_and_recommendations(tmp_path):
    db = ModelScoutDB(tmp_path / "scout.db")
    db.save_benchmark_runs([
        {"model": "qwen3-coder:30b", "context": 8192, "category": "Java", "status": "OK", "tok_per_sec": 42.5, "prompt_version": "v1", "prompt_tok_per_sec": 12.5},
    ])
    db.save_recommendations([
        {"model": "qwen3-coder:30b", "score": 86.0, "hardware_tier": "SAFE", "recommendation": "TEST_NOW"},
    ])

    assert db.list_benchmark_runs()[0]["tok_per_sec"] == 42.5
    assert db.list_benchmark_runs()[0]["prompt_version"] == "v1"
    assert db.list_benchmark_runs()[0]["prompt_tok_per_sec"] == 12.5
    assert db.list_recommendations()[0]["recommendation"] == "TEST_NOW"
