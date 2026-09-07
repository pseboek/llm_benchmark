import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.discovery import deduplicate_candidates, normalize_model_name


def test_normalize_model_name_removes_quirks():
    assert normalize_model_name("Qwen/Qwen2.5-Coder-14B-Instruct") == "qwen2.5-coder-14b-instruct"
    assert normalize_model_name("deepseek-r1:8b") == "deepseek-r1-8b"
    assert normalize_model_name("  Gemma3:4b  ") == "gemma3-4b"


def test_deduplicate_candidates_keeps_unique_models():
    candidates = [
        {"name": "Qwen/Qwen2.5-Coder-14B-Instruct", "source": "huggingface"},
        {"name": "qwen2.5-coder:14b-instruct", "source": "ollama"},
        {"name": "deepseek-r1:8b", "source": "ollama"},
        {"name": "DeepSeek-R1:8B", "source": "huggingface"},
    ]

    unique = deduplicate_candidates(candidates)
    assert len(unique) == 2
    assert {item["name"] for item in unique} == {"qwen2.5-coder:14b-instruct", "deepseek-r1:8b"}
