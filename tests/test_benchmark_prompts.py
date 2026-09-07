import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.runner import load_ollama_benchmark_module


def test_benchmark_uses_versioned_personal_prompt_catalog():
    module = load_ollama_benchmark_module()

    assert module.PROMPT_VERSION == "v1"
    assert len(module.PROMPTS) == 10
    assert "01 Java" in module.PROMPTS
    assert "10 General Reasoning" in module.PROMPTS
