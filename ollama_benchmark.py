import csv
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from statistics import mean

from benchmark.prompts import PERSONAL_PROMPTS, PROMPT_VERSION
from src.telemetry import capture_telemetry, summarize_telemetry_samples
from src.grading import grade_response

# ============================================================
# Configuration
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
REQUEST_TIMEOUT_SECONDS = 600
# Hard cap on generated tokens: bounds worst-case generation time even if a
# model loops/repeats and never emits a natural stop token.
NUM_PREDICT = 2048
RESULTS_DIR = Path(".")

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

def collect_stream_response(lines, started_at, clock=time.perf_counter, deadline_seconds=None, response=None):
    response_parts = []
    first_token_at = None
    final_data = {}

    for line in lines:
        if deadline_seconds is not None and clock() - started_at > deadline_seconds:
            if response is not None:
                response.close()
            raise TimeoutError(
                f"Streaming generation exceeded {deadline_seconds}s wall-clock deadline "
                "(model likely stuck in a repetition loop)"
            )
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


def result_path(output_dir, timestamp):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"ollama_benchmark_{timestamp}.csv"


def get_gpu_cpu_split(model):
    """Query `ollama ps` for the GPU/CPU memory split of the resident model."""
    try:
        response = requests.get("http://localhost:11434/api/ps", timeout=10)
        response.raise_for_status()
        loaded = response.json().get("models", [])
    except Exception:
        return None

    for entry in loaded:
        name = entry.get("name") or entry.get("model")
        if name != model:
            continue
        size = entry.get("size") or 0
        size_vram = entry.get("size_vram") or 0
        if not size:
            return None
        gpu_percent = round(size_vram / size * 100, 1)
        return {"gpu_percent": gpu_percent, "cpu_percent": round(100 - gpu_percent, 1)}

    return None


def print_block_summary(model, tok_per_sec_values, telemetry, load_seconds_values=None):
    """Print avg/min/max tok/s, GPU/CPU split, nvidia-smi and model load time for one context block."""
    print("-" * 80)

    if tok_per_sec_values:
        print(
            f"BLOCK SUMMARY: avg {mean(tok_per_sec_values):.2f} tok/s | "
            f"min {min(tok_per_sec_values):.2f} tok/s | "
            f"max {max(tok_per_sec_values):.2f} tok/s"
        )
    else:
        print("BLOCK SUMMARY: no successful runs")

    split = get_gpu_cpu_split(model)
    if split:
        print(
            f"GPU/CPU SPLIT:  {split['gpu_percent']:.1f}% GPU / "
            f"{split['cpu_percent']:.1f}% CPU (ollama ps)"
        )
    else:
        print("GPU/CPU SPLIT:  n/a (model not resident / ollama ps unavailable)")

    if telemetry and telemetry.get("gpu_utilization_percent") is not None:
        print(
            f"NVIDIA-SMI:     GPU util {telemetry['gpu_utilization_percent']:.1f}% | "
            f"VRAM {telemetry.get('gpu_memory_used_mb') or 0:.0f}/"
            f"{telemetry.get('gpu_memory_total_mb') or 0:.0f} MB"
        )
    else:
        print("NVIDIA-SMI:     n/a")

    # Ollama only reports a non-zero load_duration on the request that
    # actually (re)loaded the model into VRAM/RAM for this context size.
    load_seconds = max(load_seconds_values, default=0) if load_seconds_values else 0
    print(f"MODEL LOAD TIME: {load_seconds:.2f}s")

    print("-" * 80)


def unload_loaded_models():
    """Evict any models still resident in VRAM from a previous run/session.

    Ollama keeps a model loaded for OLLAMA_KEEP_ALIVE (default 5 min) after
    its last use. On a tight-VRAM GPU a leftover model from an interrupted
    run can leave too little free memory for the next model to load,
    causing the very first request of a fresh run to hang or crash.
    """
    try:
        response = requests.get("http://localhost:11434/api/ps", timeout=10)
        response.raise_for_status()
        loaded = response.json().get("models", [])
    except Exception as e:
        print(f"WARNING: could not query loaded models: {e}")
        return

    for entry in loaded:
        model_name = entry.get("name") or entry.get("model")
        if not model_name:
            continue
        try:
            requests.post(
                OLLAMA_URL,
                json={"model": model_name, "keep_alive": 0},
                timeout=30,
            )
            print(f"Unloaded stale model from VRAM: {model_name}")
        except Exception as e:
            print(f"WARNING: could not unload {model_name}: {e}")


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
            "num_predict": NUM_PREDICT,
        }
    }

    start = time.perf_counter()

    response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT_SECONDS, stream=measure_ttft)

    response.raise_for_status()

    if measure_ttft:
        data = collect_stream_response(
            response.iter_lines(),
            start,
            deadline_seconds=REQUEST_TIMEOUT_SECONDS,
            response=response,
        )
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

    unload_loaded_models()

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

        # Ensure the previous model has been evicted before loading a new
        # one; on tight-VRAM GPUs, two resident models can exceed capacity.
        unload_loaded_models()

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

            block_tok_per_sec = []
            block_telemetry = None
            block_load_seconds = []

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
                    telemetry_before = capture_telemetry()
                    result = generate(
                        model=model,
                        prompt=prompt,
                        num_ctx=num_ctx,
                        measure_ttft=True,
                    )
                    telemetry_after = capture_telemetry()
                    telemetry_run = {
                        **telemetry_after,
                        **summarize_telemetry_samples(telemetry_before, telemetry_after),
                        "telemetry_duration_seconds": result["elapsed"],
                    }

                    print(
                        f"{result['tok_per_sec']:>7.2f} tok/s"
                    )

                    block_tok_per_sec.append(result["tok_per_sec"])
                    block_telemetry = telemetry_after
                    block_load_seconds.append(result["load_duration_ns"] / 1_000_000_000)

                    graded = grade_response(result["response"], category)
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
                        **telemetry_run,

                        "load_seconds":
                            result["load_duration_ns"]
                            / 1_000_000_000,

                        "total_seconds":
                            result["total_duration_ns"]
                            / 1_000_000_000,

                        "response": result["response"],
                        "quality_score": graded["quality_score"],
                        "quality_method": graded["quality_method"],
                        "quality_confidence": graded["quality_confidence"],
                        "quality_components": json.dumps(graded["quality_components"]),
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
                        "telemetry_captured_at": None,
                        "tokens": 0,
                        "generation_seconds": 0,
                        "tok_per_sec": 0,
                        "prompt_tokens": 0,
                        "prompt_seconds": 0,
                        "prompt_tok_per_sec": 0,
                        "ttft_seconds": None,
                        "gpu_count": None,
                        "gpu_utilization_percent": None,
                        "gpu_utilization_peak_percent": None,
                        "gpu_memory_used_mb": None,
                        "gpu_memory_total_mb": None,
                        "gpu_memory_utilization_percent": None,
                        "ram_used_mb": None,
                        "cpu_percent": None,
                        "telemetry_duration_seconds": None,
                        "gpu_utilization_percent_delta": None,
                        "gpu_utilization_percent_peak": None,
                        "gpu_memory_used_mb_delta": None,
                        "gpu_memory_used_mb_peak": None,
                        "ram_used_mb_delta": None,
                        "ram_used_mb_peak": None,
                        "cpu_percent_delta": None,
                        "cpu_percent_peak": None,
                        "load_seconds": 0,
                        "total_seconds": 0,
                        "response": "",
                        "quality_score": 0.0,
                        "quality_method": "heuristic_v2",
                        "quality_confidence": 0.0,
                        "quality_components": "{}",
                        "error": str(e)
                    })

            print_block_summary(model, block_tok_per_sec, block_telemetry, block_load_seconds)

    # ========================================================
    # Save detailed results
    # ========================================================

    filename = result_path(RESULTS_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))

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
        "telemetry_captured_at",
        "telemetry_duration_seconds",
        "gpu_count",
        "gpu_utilization_percent",
        "gpu_utilization_peak_percent",
        "gpu_utilization_percent_delta",
        "gpu_utilization_percent_peak",
        "gpu_memory_used_mb",
        "gpu_memory_total_mb",
        "gpu_memory_utilization_percent",
        "gpu_memory_used_mb_delta",
        "gpu_memory_used_mb_peak",
        "ram_used_mb",
        "ram_used_mb_delta",
        "ram_used_mb_peak",
        "cpu_percent",
        "cpu_percent_delta",
        "cpu_percent_peak",
        "quality_score",
        "quality_method",
        "quality_confidence",
        "quality_components",
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

