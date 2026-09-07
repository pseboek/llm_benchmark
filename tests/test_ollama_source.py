import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sources.ollama import parse_ollama_models


def test_parse_ollama_models_extracts_candidate_names():
    payload = {
        "models": [
            {"name": "qwen2.5-coder:14b-instruct"},
            {"name": "deepseek-r1:8b"},
            {"name": "gemma3:4b"},
        ]
    }

    models = parse_ollama_models(payload)

    assert models == [
        {"name": "qwen2.5-coder:14b-instruct", "source": "ollama"},
        {"name": "deepseek-r1:8b", "source": "ollama"},
        {"name": "gemma3:4b", "source": "ollama"},
    ]
