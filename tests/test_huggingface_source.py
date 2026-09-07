import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sources.huggingface import parse_huggingface_models


def test_parse_huggingface_models_extracts_candidate_names():
    payload = [
        {"id": "Qwen/Qwen2.5-Coder-14B-Instruct"},
        {"id": "deepseek-ai/DeepSeek-R1"},
        {"id": "google/gemma-3-4b-it"},
    ]

    models = parse_huggingface_models(payload)

    assert models == [
        {"name": "Qwen/Qwen2.5-Coder-14B-Instruct", "source": "huggingface"},
        {"name": "deepseek-ai/DeepSeek-R1", "source": "huggingface"},
        {"name": "google/gemma-3-4b-it", "source": "huggingface"},
    ]
