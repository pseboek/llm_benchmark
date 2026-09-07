import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sources.ollama import parse_ollama_models


def test_parse_ollama_models_preserves_runtime_metadata():
    models = parse_ollama_models({
        "models": [{
            "name": "qwen2.5-coder:14b-instruct",
            "size": 8 * 1024**3,
            "digest": "abc123",
            "modified_at": "2026-09-07T10:00:00Z",
            "details": {
                "format": "gguf",
                "family": "qwen2",
                "families": ["qwen2"],
                "parameter_size": "14.8B",
                "quantization_level": "Q4_K_M",
            },
        }]
    })

    assert models == [{
        "name": "qwen2.5-coder:14b-instruct",
        "source": "ollama",
        "size_bytes": 8 * 1024**3,
        "estimated_vram_gb": 8.0,
        "digest": "abc123",
        "modified_at": "2026-09-07T10:00:00Z",
        "format": "gguf",
        "architecture": "qwen2",
        "families": ["qwen2"],
        "parameter_size": "14.8B",
        "quantization": "Q4_K_M",
    }]
