import csv
import json
import time
import requests
from datetime import datetime
from statistics import mean

from benchmark.prompts import PERSONAL_PROMPTS, PROMPT_VERSION
from src.telemetry import capture_telemetry
from src.grading import grade_response

# ============================================================
# Configuration
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "Codestral:latest",
    "deepseek-r1:8b",
    "deepseek-coder:latest",
    "devstral-small-2:latest",
    "gemma3:4b",
    "gemma4:12B",
    "gpt-oss:20b",
    "ministral-3:14b",
    "qwen2.5-coder:14b-instruct",
    "qwen3.5:9B",
]

# Test all three context sizes
CONTEXT_SIZES = [
    8192,
    16384,
    32768,
]

# Same benchmark prompts for every model/context combination
PROMPTS = {
    "General": """
Explain the following concept clearly and concisely:
What is the difference between a process and a thread?
Give a practical example and explain when each matters.
""",

    "Java": """
Write a production-quality Java 23 example implementing a service
that loads users from a repository, validates the input, handles
missing users correctly, and returns an appropriate result.

Explain the important design decisions.
""",

    "Spring": """
You are debugging a Spring Boot application.

A service A depends on service B.
Service B depends on service A.
Spring reports a circular dependency during startup.

Explain:
1. why this happens,
2. how to diagnose it,
3. three possible solutions,
4. which solution you would recommend for production and why.
""",

    "React": """
Explain how React state updates and rendering work.

Provide a small React example that demonstrates:
- state,
- an event handler,
- a derived value,
- and how to avoid unnecessary re-renders.

Use modern React with functional components and hooks.
""",

    "Architecture": """
Design the architecture for a web application with:

- React frontend
- Spring Boot backend
- PostgreSQL
- REST API
- Docker
- GitHub Actions
- Jenkins

The application should be maintainable and scalable.

Explain the major components, communication paths,
deployment architecture, and important architectural decisions.
"""
}

# Keep the benchmark tasks versioned and shared with the personal prompt catalog.
PROMPTS = PERSONAL_PROMPTS


# ============================================================
# Ollama API
# ============================================================

def collect_stream_response(lines, started_at, clock=time.perf_counter):
    response_parts = []
    first_token_at = None
    final_data = {}

    for line in lines:
        if not line:
            continue
        data = json.loads(line)
        final_data.update(data)
        text = data.get("response", "")
        if text:
            response_parts.append(text)
            if first_token_at is None:
                first_token_at = clock()

    eval_duration = final_data.get("eval_duration", 0)
    prompt_duration = final_data.get("prompt_eval_duration", 0)
    return {
        "response": "".join(response_parts),
        "eval_count": final_data.get("eval_count", 0),
        "eval_duration_ns": eval_duration,
        "tok_per_sec": final_data.get("eval_count", 0) / (eval_duration / 1_000_000_000) if eval_duration else 0,
        "prompt_eval_count": final_data.get("prompt_eval_count", 0),
        "prompt_eval_duration_ns": prompt_duration,
        "prompt_tok_per_sec": final_data.get("prompt_eval_count", 0) / (prompt_duration / 1_000_000_000) if prompt_duration else 0,
        "total_duration_ns": final_data.get("total_duration", 0),
        "load_duration_ns": final_data.get("load_duration", 0),
        "ttft_seconds": first_token_at - started_at if first_token_at is not None else None,
    }


def generate(model, prompt, num_ctx, measure_ttft=False):
    """
    Execute one Ollama generation with a specific context size.
    """

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": measure_ttft,
        "options": {
            "num_ctx": num_ctx,
            "temperature": 0.0,
        }
    }

    start = time.perf_counter()

    response = requests.post(OLLAMA_URL, json=payload, timeout=600, stream=measure_ttft)

    response.raise_for_status()

    if measure_ttft:
        data = collect_stream_response(response.iter_lines(), start)
        data["elapsed"] = time.perf_counter() - start
        return data

    elapsed = time.perf_counter() - start

    data = response.json()

    # Ollama reports generation duration in nanoseconds
    eval_duration = data.get("eval_duration", 0)
    eval_count = data.get("eval_count", 0)

    if eval_duration:
        tok_per_sec = eval_count / (eval_duration / 1_000_000_000)
    else:
        tok_per_sec = 0

    return {
        "response": data.get("response", ""),
        "eval_count": eval_count,
        "eval_duration_ns": eval_duration,
        "tok_per_sec": tok_per_sec,
        "total_duration_ns": data.get("total_duration", 0),
        "load_duration_ns": data.get("load_duration", 0),
        "prompt_eval_count": data.get("prompt_eval_count", 0),
        "prompt_eval_duration_ns": data.get(
            "prompt_eval_duration", 0
        ),
        "prompt_tok_per_sec": (
            data.get("prompt_eval_count", 0)
            / (data.get("prompt_eval_duration", 0) / 1_000_000_000)
            if data.get("prompt_eval_duration")
            else 0
        ),
        "ttft_seconds": None,
        "elapsed": elapsed,
    }


# ============================================================
# Benchmark
# ============================================================

def run_benchmark():

    results = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_runs = (
        len(MODELS)
        * len(CONTEXT_SIZES)
        * len(PROMPTS)
    )

    current_run = 0

    print()
    print("=" * 80)
    print("OLLAMA LLM BENCHMARK")
    print("=" * 80)
    print(f"Models:          {len(MODELS)}")
    print(f"Context sizes:   {CONTEXT_SIZES}")
    print(f"Prompts/model:   {len(PROMPTS)}")
    print(f"Total runs:      {total_runs}")
    print("=" * 80)
    print()

    for model in MODELS:

        for num_ctx in CONTEXT_SIZES:

            print()
            print("-" * 80)
            print(f"MODEL:   {model}")
            print(f"CONTEXT: {num_ctx}")
            print("-" * 80)

            # ------------------------------------------------
            # Important:
            # Wait briefly between context-size changes.
            # Ollama will unload/reload if necessary.
            # ------------------------------------------------

            for category, prompt in PROMPTS.items():

                current_run += 1

                print(
                    f"[{current_run}/{total_runs}] "
                    f"{model:<30} "
                    f"{num_ctx:>5} "
                    f"{category:<12}",
                    end=" ",
                    flush=True
                )

                try:
                    result = generate(
                        model=model,
                        prompt=prompt,
                        num_ctx=num_ctx,
                        measure_ttft=True,
                    )
                    telemetry_after = capture_telemetry()

                    print(
                        f"{result['tok_per_sec']:>7.2f} tok/s"
                    )

                    results.append({
                        "timestamp": timestamp,
                        "model": model,
                        "context": num_ctx,
                        "category": category,
                        "prompt_version": PROMPT_VERSION,
                        "status": "OK",

                        "tokens": result["eval_count"],
                        "generation_seconds":
                            result["eval_duration_ns"]
                            / 1_000_000_000,

                        "tok_per_sec":
                            result["tok_per_sec"],

                        "prompt_tokens":
                            result["prompt_eval_count"],

                        "prompt_seconds":
                            result["prompt_eval_duration_ns"]
                            / 1_000_000_000,

                        "prompt_tok_per_sec": result["prompt_tok_per_sec"],
                        "ttft_seconds": result["ttft_seconds"],
                        **telemetry_after,

                        "load_seconds":
                            result["load_duration_ns"]
                            / 1_000_000_000,

                        "total_seconds":
                            result["total_duration_ns"]
                            / 1_000_000_000,

                        "response":
                            result["response"]
                        , **grade_response(result["response"], category)
                    })

                except Exception as e:

                    print(f"ERROR: {e}")

                    results.append({
                        "timestamp": timestamp,
                        "model": model,
                        "context": num_ctx,
                        "category": category,
                        "prompt_version": PROMPT_VERSION,
                        "status": "ERROR",
                        "tokens": 0,
                        "generation_seconds": 0,
                        "tok_per_sec": 0,
                        "prompt_tokens": 0,
                        "prompt_seconds": 0,
                        "prompt_tok_per_sec": 0,
                        "ttft_seconds": None,
                        "gpu_utilization_percent": None,
                        "gpu_memory_used_mb": None,
                        "gpu_memory_total_mb": None,
                        "ram_used_mb": None,
                        "cpu_percent": None,
                        "load_seconds": 0,
                        "total_seconds": 0,
                        "response": "",
                        "quality_score": 0.0,
                        "quality_method": "heuristic_v1",
                        "error": str(e)
                    })


    # ========================================================
    # Save detailed results
    # ========================================================

    filename = (
        "ollama_benchmark_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".csv"
    )

    fieldnames = [
        "timestamp",
        "model",
        "context",
        "category",
        "prompt_version",
        "status",
        "tokens",
        "generation_seconds",
        "tok_per_sec",
        "prompt_tokens",
        "prompt_seconds",
        "prompt_tok_per_sec",
        "ttft_seconds",
        "gpu_utilization_percent",
        "gpu_memory_used_mb",
        "gpu_memory_total_mb",
        "ram_used_mb",
        "cpu_percent",
        "load_seconds",
        "total_seconds",
        "response",
        "error"
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 80)
    print(f"Results saved to: {filename}")
    print("=" * 80)

    print_summary(results)
    return results


# ============================================================
# Summary
# ============================================================

def print_summary(results):

    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)

    # --------------------------------------------------------
    # Model + context
    # --------------------------------------------------------

    combinations = {}

    for result in results:

        if result["status"] != "OK":
            continue

        key = (
            result["model"],
            result["context"]
        )

        combinations.setdefault(key, [])

        combinations[key].append(
            result["tok_per_sec"]
        )

    print()

    print(
        f"{'Model':<32}"
        f"{'Context':>10}"
        f"{'Avg tok/s':>14}"
        f"{'Min':>12}"
        f"{'Max':>12}"
        f"{'Runs':>8}"
    )

    print("-" * 100)

    for (model, context), values in combinations.items():

        print(
            f"{model:<32}"
            f"{context:>10}"
            f"{mean(values):>14.2f}"
            f"{min(values):>12.2f}"
            f"{max(values):>12.2f}"
            f"{len(values):>8}"
        )

    # --------------------------------------------------------
    # Context comparison per model
    # --------------------------------------------------------

    print()
    print("=" * 100)
    print("CONTEXT COMPARISON")
    print("=" * 100)

    model_context = {}

    for result in results:

        if result["status"] != "OK":
            continue

        key = (
            result["model"],
            result["context"]
        )

        model_context.setdefault(key, [])

        model_context[key].append(
            result["tok_per_sec"]
        )

    models = sorted(
        set(model for model, _ in model_context)
    )

    print()

    print(
        f"{'Model':<32}"
        f"{'8K':>12}"
        f"{'16K':>12}"
        f"{'32K':>12}"
        f"{'32K vs 8K':>14}"
    )

    print("-" * 90)

    for model in models:

        values = {}

        for context in CONTEXT_SIZES:

            key = (model, context)

            if key in model_context:
                values[context] = mean(
                    model_context[key]
                )

        v8 = values.get(8192)
        v16 = values.get(16384)
        v32 = values.get(32768)

        if v8 and v32:

            degradation = (
                (v32 / v8) - 1
            ) * 100

            degradation_text = (
                f"{degradation:+.1f}%"
            )

        else:

            degradation_text = "n/a"

        print(
            f"{model:<32}"
            f"{v8 if v8 else 0:>12.2f}"
            f"{v16 if v16 else 0:>12.2f}"
            f"{v32 if v32 else 0:>12.2f}"
            f"{degradation_text:>14}"
        )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    run_benchmark()

