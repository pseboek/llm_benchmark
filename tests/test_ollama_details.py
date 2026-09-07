import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sources.ollama import enrich_ollama_models, parse_ollama_details


def test_parse_ollama_details_extracts_model_metadata():
    details = parse_ollama_details({
        "details": {
            "family": "qwen2",
            "families": ["qwen2"],
            "parameter_size": "14.8B",
            "quantization_level": "Q4_K_M",
        },
        "model_info": {"general.parameter_count": 14_800_000_000},
    })

    assert details["architecture"] == "qwen2"
    assert details["parameter_size"] == "14.8B"
    assert details["quantization"] == "Q4_K_M"
    assert details["parameters_total_b"] == 14.8


def test_enrich_ollama_models_keeps_candidates_when_details_fail():
    candidates = [{"name": "model-a", "source": "ollama"}]

    enriched = enrich_ollama_models(candidates, lambda _: (_ for _ in ()).throw(RuntimeError("offline")))

    assert enriched == candidates
