import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sources.huggingface import parse_huggingface_models


def test_huggingface_parser_filters_non_generative_pipeline_tags():
    models = parse_huggingface_models([
        {"id": "org/text-model", "pipeline_tag": "text-generation"},
        {"id": "org/embedding-model", "pipeline_tag": "feature-extraction"},
        {"id": "org/legacy-model"},
    ])

    assert [item["name"] for item in models] == ["org/text-model", "org/legacy-model"]
