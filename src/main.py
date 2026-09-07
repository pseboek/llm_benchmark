from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.runner import run_benchmark
from database import ModelScoutDB
from pipeline import discover_candidates
from report import build_report, write_report
from scoring import Candidate, hardware_tier, recommendation, weighted_score


def load_config():
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_demo_candidates(config):
    baseline = config.get("baseline", [])
    candidates = []

    for item in baseline:
        candidates.append(
            Candidate(
                name=item.get("name", "unknown-model"),
                coding=90,
                reasoning=88,
                general=85,
                speed=min(100.0, float(item.get("generation_tps", 0.0)) / 1.5),
                vram_efficiency=78,
                context=90,
                tool_agent=80,
                freshness=90,
                vram_gb=15.5,
                is_moe=item.get("name", "").lower().endswith("moe") or False,
                active_params_b=4,
            )
        )

    return candidates


def print_summary(candidates):
    for candidate in candidates:
        score = weighted_score(candidate)
        tier = hardware_tier(
            candidate.vram_gb,
            is_moe=candidate.is_moe,
            active_params_b=candidate.active_params_b,
        )
        print(f"{candidate.name:32} score={score:>6.2f} tier={tier:<11} action={recommendation(score, tier)}")


def parse_args():
    parser = argparse.ArgumentParser(description="LLM Model Scout")
    parser.add_argument("--list-models", action="store_true", help="Display the configured benchmark models")
    parser.add_argument("--run-benchmark", action="store_true", help="Execute the local Ollama benchmark")
    parser.add_argument("--discover", action="store_true", help="Discover and deduplicate Ollama and Hugging Face candidates")
    parser.add_argument("--report", action="store_true", help="Generate a markdown-style candidate report")
    parser.add_argument("--models", nargs="*", help="Restrict benchmark to specific model names")
    parser.add_argument("--contexts", nargs="*", type=int, help="Context sizes to use for the benchmark")
    parser.add_argument("--hf-limit", type=int, default=10, help="Maximum number of Hugging Face models to inspect")
    parser.add_argument("--db", default=str(ROOT / "data" / "model_scout.db"), help="SQLite history database path")
    parser.add_argument("--output", help="Report output path; defaults to reports/YYYY-MM-DD_model_scout.md")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config()

    if args.list_models:
        benchmark_models = config.get("baseline", [])
        print("Configured benchmark models:")
        for item in benchmark_models:
            print(f"- {item.get('name')}")
        return

    if args.run_benchmark:
        results = run_benchmark(models=args.models, contexts=args.contexts)
        if results:
            ModelScoutDB(args.db).save_benchmark_runs(results)
        return

    if args.discover:
        candidates = discover_candidates(
            huggingface_limit=args.hf_limit,
            enabled_sources={name: bool(settings.get("enabled", False)) for name, settings in config.get("sources", {}).items()},
        )
        ModelScoutDB(args.db).save_candidates(candidates)
        report = build_report(candidates, champions=config.get("baseline", []))
        print(report)
        return

    if args.report:
        candidates = discover_candidates(
            huggingface_limit=args.hf_limit,
            enabled_sources={name: bool(settings.get("enabled", False)) for name, settings in config.get("sources", {}).items()},
        )
        db = ModelScoutDB(args.db)
        db.save_candidates(candidates)
        report = build_report(candidates, champions=config.get("baseline", []))
        output = args.output or str(ROOT / "reports" / f"{date.today().isoformat()}_model_scout.md")
        write_report(report, output)
        print(report)
        print(f"Report saved to: {output}")
        return

    candidates = build_demo_candidates(config)
    print_summary(candidates)


if __name__ == "__main__":
    main()
