from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "ollama_benchmark.py"


def load_ollama_benchmark_module():
    spec = importlib.util.spec_from_file_location("ollama_benchmark", BENCHMARK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load benchmark module from {BENCHMARK_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_benchmark(models=None, contexts=None):
    module = load_ollama_benchmark_module()

    if models is not None:
        module.MODELS = models

    if contexts is not None:
        module.CONTEXT_SIZES = contexts

    module.run_benchmark()


def main():
    parser = argparse.ArgumentParser(description="Run the local Ollama benchmark")
    parser.add_argument("--models", nargs="*", help="Specific model names to benchmark")
    parser.add_argument("--contexts", nargs="*", type=int, help="Context sizes to benchmark, e.g. 8192 16384 32768")
    parser.add_argument("--list-models", action="store_true", help="Print the configured benchmark models")
    args = parser.parse_args()

    if args.list_models:
        module = load_ollama_benchmark_module()
        print("Configured benchmark models:")
        for model in module.MODELS:
            print(f"- {model}")
        return

    run_benchmark(models=args.models, contexts=args.contexts)


if __name__ == "__main__":
    main()
