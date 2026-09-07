from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.runner import run_benchmark, run_benchmark_plan
from src.adaptive import adaptive_weights
from src.database import ModelScoutDB
from src.benchmark_queue import build_benchmark_queue, write_benchmark_queue
from src.benchmark_plan import build_benchmark_plan, write_benchmark_plan
from src.download_queue import build_download_plan, execute_download_plan, load_queue, write_download_plan
from src.pipeline import discover_candidates, discover_with_status
from src.report import build_report, build_report_snapshot, write_report
from src.scoring import Candidate, enrich_from_baseline, enrich_from_benchmark, hardware_tier, recommendation, score_candidate, weighted_score


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


def build_baseline_records(config):
    return [
        {
            "name": item.get("name", "unknown-model"),
            "source": "config",
            "role": item.get("role", "baseline"),
            "generation_tps": float(item.get("generation_tps", 0.0)),
            "coding": 90.0,
            "reasoning": 88.0,
            "general": 85.0,
            "speed": min(100.0, float(item.get("generation_tps", 0.0)) / 1.5),
            "vram_efficiency": 78.0,
            "context": 90.0,
            "tool_agent": 80.0,
            "freshness": 90.0,
            "vram_gb": 15.5,
        }
        for item in config.get("baseline", [])
    ]


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
    parser.add_argument("--offline", action="store_true", help="Use local Ollama only and fall back to configured baseline")
    parser.add_argument("--queue", action="store_true", help="Create a manual benchmark queue from actionable candidates")
    parser.add_argument("--max-candidates", type=int, default=5, help="Maximum candidates in the manual benchmark queue")
    parser.add_argument("--baseline-only", action="store_true", help="Build a queue or report from configured baseline data")
    parser.add_argument("--download-queue", help="Create or apply a controlled Ollama download plan from a queue JSON")
    parser.add_argument("--approve-models", nargs="*", default=[], help="Explicit model names approved for download")
    parser.add_argument("--execute-downloads", action="store_true", help="Execute approved ollama pull commands")
    parser.add_argument("--suggest-weights", action="store_true", help="Suggest scoring weights from benchmark history")
    parser.add_argument("--benchmark-plan", help="Create benchmark tasks from an approved model queue")
    parser.add_argument("--run-plan", help="Execute a previously generated benchmark plan")
    parser.add_argument("--dry-run-plan", help="Show pending benchmark tasks without executing Ollama")
    parser.add_argument("--db-summary", action="store_true", help="Show a compact SQLite data summary")
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

    if args.db_summary:
        print(json.dumps(ModelScoutDB(args.db).summary(), indent=2))
        return

    if args.suggest_weights:
        history = ModelScoutDB(args.db).list_benchmark_runs()
        suggestion = adaptive_weights(config.get("scoring", {}), history)
        output = args.output
        if output:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            Path(output).write_text(json.dumps(suggestion, indent=2), encoding="utf-8")
            print(f"Weight suggestion saved to: {output}")
        else:
            print(json.dumps(suggestion, indent=2))
        return

    if args.run_benchmark:
        results = run_benchmark(models=args.models, contexts=args.contexts)
        if results:
            ModelScoutDB(args.db).save_benchmark_runs(results)
        return

    if args.run_plan:
        plan = load_queue(args.run_plan)
        db = ModelScoutDB(args.db)
        db.save_benchmark_tasks([{**task, "status": "RUNNING"} for task in plan])
        results = run_benchmark_plan(plan)
        if results:
            db.save_benchmark_runs(results)
            for result in results:
                status = "COMPLETED" if result.get("status") == "OK" else "FAILED"
                db.update_benchmark_task_status(result["model"], result["context"], result["category"], status)
        return

    if args.dry_run_plan:
        plan = load_queue(args.dry_run_plan)
        pending = [task for task in plan if task.get("status") == "PENDING_EXECUTION"]
        print(json.dumps({
            "pending_tasks": len(pending),
            "models": sorted({task.get("model") for task in pending}),
            "contexts": sorted({task.get("context") for task in pending}),
            "categories": list(dict.fromkeys(task.get("category") for task in pending)),
        }, indent=2))
        return

    if args.discover:
        enabled_sources = {name: bool(settings.get("enabled", False)) for name, settings in config.get("sources", {}).items()}
        if args.offline:
            enabled_sources = {name: name == "ollama" for name in enabled_sources}
        candidates, source_status = discover_with_status(
            huggingface_limit=args.hf_limit,
            enabled_sources=enabled_sources,
        )
        candidates = candidates or build_baseline_records(config)
        candidates = [enrich_from_baseline(candidate, config.get("baseline", [])) for candidate in candidates]
        ModelScoutDB(args.db).save_candidates(candidates)
        ModelScoutDB(args.db).save_recommendations([score_candidate(candidate) for candidate in candidates])
        report = build_report(
            candidates,
            champions=config.get("baseline", []),
            scoring_config=config.get("scoring"),
            hardware_config={**config.get("hardware", {}), "thresholds": config.get("thresholds", {})},
            source_status=source_status,
        )
        print(report)
        return

    if args.report:
        enabled_sources = {name: bool(settings.get("enabled", False)) for name, settings in config.get("sources", {}).items()}
        if args.offline:
            enabled_sources = {name: name == "ollama" for name in enabled_sources}
        candidates, source_status = discover_with_status(
            huggingface_limit=args.hf_limit,
            enabled_sources=enabled_sources,
        )
        candidates = candidates or build_baseline_records(config)
        candidates = [enrich_from_baseline(candidate, config.get("baseline", [])) for candidate in candidates]
        db = ModelScoutDB(args.db)
        candidates = [enrich_from_benchmark(candidate, db.list_benchmark_runs()) for candidate in candidates]
        db.save_candidates(candidates)
        db.save_recommendations([score_candidate(candidate) for candidate in candidates])
        db.save_source_status(source_status)
        db.save_source_status(source_status)
        report = build_report(
            candidates,
            champions=config.get("baseline", []),
            scoring_config=config.get("scoring"),
            hardware_config={**config.get("hardware", {}), "thresholds": config.get("thresholds", {})},
            source_status=source_status,
        )
        output = args.output or str(ROOT / "reports" / f"{date.today().isoformat()}_model_scout.md")
        db.save_report_snapshot({**build_report_snapshot(candidates, config.get("scoring"), {**config.get("hardware", {}), "thresholds": config.get("thresholds", {})}), "output_path": output})
        write_report(report, output)
        print(report)
        print(f"Report saved to: {output}")
        return

    if args.queue:
        enabled_sources = {name: bool(settings.get("enabled", False)) for name, settings in config.get("sources", {}).items()}
        if args.offline:
            enabled_sources = {name: name == "ollama" for name in enabled_sources}
        candidates = [] if args.baseline_only else discover_candidates(huggingface_limit=args.hf_limit, enabled_sources=enabled_sources)
        candidates = candidates or build_baseline_records(config)
        output = args.output or str(ROOT / "reports" / "benchmark_queue.json")
        queue = build_benchmark_queue(
            candidates,
            max_candidates=args.max_candidates,
            scoring_config=config.get("scoring"),
            thresholds=config.get("thresholds"),
            hardware_limits=config.get("hardware", {}).get("vram"),
        )
        write_benchmark_queue(queue, output)
        print(json.dumps(queue, indent=2))
        print(f"Queue saved to: {output}")
        return

    if args.download_queue:
        plan = build_download_plan(load_queue(args.download_queue), set(args.approve_models))
        if args.execute_downloads:
            plan = execute_download_plan(plan)
        output = args.output or str(ROOT / "reports" / "download_plan.json")
        write_download_plan(plan, output)
        print(json.dumps(plan, indent=2))
        print(f"Download plan saved to: {output}")
        return

    if args.benchmark_plan:
        queue = load_queue(args.benchmark_plan)
        plan = build_benchmark_plan(
            queue,
            set(args.approve_models),
            args.contexts or config.get("benchmark", {}).get("contexts", [8192, 16384, 32768]),
        )
        output = args.output or str(ROOT / "reports" / "benchmark_plan.json")
        ModelScoutDB(args.db).save_benchmark_tasks(plan)
        write_benchmark_plan(plan, output)
        print(json.dumps(plan, indent=2))
        print(f"Benchmark plan saved to: {output}")
        return

    candidates = build_demo_candidates(config)
    print_summary(candidates)


if __name__ == "__main__":
    main()
