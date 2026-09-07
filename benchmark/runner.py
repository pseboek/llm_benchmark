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

    return module.run_benchmark()


def plan_dimensions(plan):
    pending = [item for item in plan if item.get("status") == "PENDING_EXECUTION"]
    models = sorted({item["model"] for item in pending if item.get("model")})
    contexts = sorted({int(item["context"]) for item in pending if item.get("context")})
    categories = list(dict.fromkeys(item["category"] for item in pending if item.get("category")))
    return models, contexts, categories


def apply_result_statuses(plan, results, attempted_tasks=None):
    attempted = attempted_tasks or {
        (item.get("model"), item.get("context"), item.get("category"))
        for item in plan
    }
    result_status = {
        (item.get("model"), item.get("context"), item.get("category")): "COMPLETED" if item.get("status") == "OK" else "FAILED"
        for item in results
    }
    updated = []
    for task in plan:
        key = (task.get("model"), task.get("context"), task.get("category"))
        fallback = "FAILED" if key in attempted and task.get("status") == "PENDING_EXECUTION" else task.get("status", "PENDING_EXECUTION")
        updated.append({**task, "status": result_status.get(key, fallback)})
    return updated


def reset_failed_tasks(plan):
    return [
        {**task, "status": "PENDING_EXECUTION" if task.get("status") == "FAILED" else task.get("status", "PENDING_EXECUTION")}
        for task in plan
    ]


def run_benchmark_plan(plan):
    module = load_ollama_benchmark_module()
    models, contexts, categories = plan_dimensions(plan)
    module.MODELS = models
    module.CONTEXT_SIZES = contexts
    module.PROMPTS = {category: module.PROMPTS[category] for category in categories if category in module.PROMPTS}
    return module.run_benchmark()


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
