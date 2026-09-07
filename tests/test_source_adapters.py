import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import ModelScoutDB
from src.sources.artificial_analysis import parse_artificial_analysis_models
from src.sources.swebench import parse_swebench_models


def test_parse_artificial_analysis_models_extracts_names():
    payload = {
        "models": [
            {"name": "Qwen3 Coder 32B"},
            {"name": "DeepSeek V3"},
        ]
    }

    models = parse_artificial_analysis_models(payload)

    assert models == [
        {"name": "Qwen3 Coder 32B", "source": "artificial_analysis"},
        {"name": "DeepSeek V3", "source": "artificial_analysis"},
    ]


def test_parse_swebench_models_extracts_names():
    payload = [
        {
            "name": "Verified",
            "results": [
                {"model_display": "Claude 4.5 Opus", "model_org": "Anthropic"},
                {"model_display": "GPT 5.2", "model_org": "OpenAI"},
            ],
        },
        {
            "name": "Lite",
            "results": [
                {"model_display": "Claude 4.5 Opus", "model_org": "Anthropic"},
            ],
        },
    ]

    models = parse_swebench_models(payload)

    assert models == [
        {"name": "Claude 4.5 Opus", "source": "swebench"},
        {"name": "GPT 5.2", "source": "swebench"},
    ]


def test_model_scout_db_persists_candidates(tmp_path):
    db_path = tmp_path / "model_scout.db"
    db = ModelScoutDB(db_path)

    db.save_candidates([
        {"name": "qwen2.5-coder:14b-instruct", "source": "ollama"},
        {"name": "GPT-4.1", "source": "huggingface"},
    ])

    rows = db.list_candidates()
    assert [r["name"] for r in rows] == [
        "qwen2.5-coder:14b-instruct",
        "GPT-4.1",
    ]

    with sqlite3.connect(db_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        assert count == 2
