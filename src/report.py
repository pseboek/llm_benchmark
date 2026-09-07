from __future__ import annotations

from datetime import date
from pathlib import Path

from src.scoring import champion_comparison, enrich_from_baseline, score_candidate
def build_report_snapshot(
    candidates: list[dict],
    scoring_config: dict | None = None,
    hardware_config: dict | None = None,
) -> dict[str, int]:
    scoring_config = scoring_config or {}
    hardware_config = hardware_config or {}
    scored = [
        score_candidate(
            candidate,
            weights=scoring_config,
            thresholds=hardware_config.get("thresholds"),
            hardware_limits=hardware_config.get("vram", {}),
        )
        for candidate in candidates
    ]
    return {
        "total_candidates": len(scored),
        "test_now": sum(item["recommendation"] == "TEST_NOW" for item in scored),
        "surprise_test": sum(item["recommendation"] == "SURPRISE_TEST" for item in scored),
        "watch": sum(item["recommendation"] == "WATCH" for item in scored),
        "needs_data": sum(item["recommendation"] == "NEEDS_DATA" for item in scored),
        "ignored": sum(item["recommendation"] == "IGNORE" for item in scored),
    }


def benchmark_task_progress(tasks: list[dict]) -> dict[str, int | float]:
    total = len(tasks)
    completed = sum(task.get("status") == "COMPLETED" for task in tasks)
    pending = sum(task.get("status") in {"PENDING_EXECUTION", "RUNNING"} for task in tasks)
    failed = sum(task.get("status") == "FAILED" for task in tasks)
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "failed": failed,
        "percent": round(completed / total * 100, 2) if total else 0.0,
    }


def benchmark_evidence_by_context(runs: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, int], list[dict]] = {}
    for run in runs:
        if run.get("status") == "OK":
            grouped.setdefault((str(run.get("model", "unknown")), int(run.get("context", 0))), []).append(run)
    evidence = []
    for (model, context), rows in sorted(grouped.items()):
        speeds = [float(row.get("tok_per_sec", 0)) for row in rows]
        qualities = [float(row["quality_score"]) for row in rows if row.get("quality_score") is not None]
        evidence.append({
            "model": model,
            "context": context,
            "avg_tok_per_sec": round(sum(speeds) / len(speeds), 2),
            "avg_quality_score": round(sum(qualities) / len(qualities), 2) if qualities else None,
            "runs": len(rows),
        })
    return evidence


def build_report(
    candidates: list[dict],
    champions: list[dict] | None = None,
    scoring_config: dict | None = None,
    hardware_config: dict | None = None,
    source_status: dict[str, dict] | None = None,
    benchmark_runs: list[dict] | None = None,
    benchmark_tasks: list[dict] | None = None,
) -> str:
    scoring_config = scoring_config or {}
    hardware_limits = (hardware_config or {}).get("vram", {})
    thresholds = (hardware_config or {}).get("thresholds")
    candidates = [enrich_from_baseline(candidate, champions or []) for candidate in candidates]
    scored = [
        score_candidate(
            candidate,
            weights=scoring_config,
            thresholds=thresholds,
            hardware_limits=hardware_limits,
        )
        for candidate in candidates
    ]
    groups = {
        "TEST_NOW": "Test Now",
        "SURPRISE_TEST": "Surprise Candidates",
        "WATCH": "Watchlist",
        "NEEDS_DATA": "Needs Data",
        "IGNORE": "Ignored",
    }
    lines = [
        "# Model Scout Report",
        "",
        f"- Generated: {date.today().isoformat()}",
        f"- Total candidates: {len(scored)}",
        f"- {len(scored)} candidates",
        "- Sources: ollama, huggingface, lmarena, artificial_analysis, swebench",
        "",
        "## Executive Summary",
    ]
    if benchmark_runs is not None:
        lines.append("- Benchmark evidence: available")
    if benchmark_tasks is not None:
        progress = benchmark_task_progress(benchmark_tasks)
        lines.append(
            f"- Benchmark progress: {progress['completed']}/{progress['total']} "
            f"completed ({progress['percent']:.2f}%), pending={progress['pending']}, failed={progress['failed']}"
        )
    for action, title in groups.items():
        lines.append(f"- {title}: {sum(item['recommendation'] == action for item in scored)}")
    source_names = ("ollama", "huggingface", "lmarena", "artificial_analysis", "swebench")
    source_counts = {source: sum(item.get("source") == source for item in candidates) for source in source_names}
    lines.extend(["", "## Source Coverage"])
    lines.extend(f"- {source}: {source_counts[source]}" for source in source_names)
    if source_status:
        lines.extend(["", "## Source Status"])
        for source in source_names:
            item = source_status.get(source, {"status": "UNKNOWN"})
            detail = f", error={item['error']}" if item.get("error") else ""
            lines.append(f"- {source}: {item.get('status', 'UNKNOWN')}{detail}")
    lines.extend(["", "## Recommendations"])
    for action, title in groups.items():
        lines.extend(["", f"### {title}"])
        matching = [item for item in scored if item["recommendation"] == action]
        if not matching:
            lines.append("- None")
            continue
        for candidate in sorted(matching, key=lambda item: item["score"] or -1, reverse=True):
            score_text = f"{candidate['score']:.2f}" if candidate["score"] is not None else "not assessed"
            lines.append(
                f"- {candidate.get('name', 'unknown')} "
                f"(score={score_text}, tier={candidate['hardware_tier']}, "
                f"source={candidate.get('source', 'unknown')}, "
                f"VRAM={candidate.get('vram_gb', 'unknown')} GB) "
                f"Reason: {candidate['rationale']}"
            )
    lines.extend(["", "## Candidates"])

    for candidate in scored:
        name = candidate.get("name", "unknown")
        source = candidate.get("source", "unknown")
        score_text = f"{candidate['score']:.2f}" if candidate["score"] is not None else "not assessed"
        lines.append(
            f"- {name} ({source}, {candidate['hardware_tier']}, {score_text}, "
            f"VRAM={candidate.get('vram_gb', 'unknown')} GB)"
        )

    if benchmark_runs is not None:
        evidence: dict[str, list[dict]] = {}
        for run in benchmark_runs:
            if run.get("status") == "OK":
                evidence.setdefault(str(run.get("model", "unknown")), []).append(run)
        lines.extend(["", "## Benchmark Evidence"])
        if not evidence:
            lines.append("- No successful benchmark runs available.")
        for model, runs in sorted(evidence.items()):
            speeds = [float(run.get("tok_per_sec", 0)) for run in runs]
            qualities = [float(run["quality_score"]) for run in runs if run.get("quality_score") is not None]
            quality_text = f"{sum(qualities) / len(qualities):.2f} quality" if qualities else "quality not assessed"
            lines.append(
                f"- {model}: {sum(speeds) / len(speeds):.2f} tok/s, {quality_text}, runs={len(runs)}"
            )
        lines.extend(["", "### By Context"])
        for item in benchmark_evidence_by_context(benchmark_runs):
            quality_text = f"{item['avg_quality_score']:.2f} quality" if item["avg_quality_score"] is not None else "quality not assessed"
            lines.append(
                f"- {item['model']} @ {item['context']}: {item['avg_tok_per_sec']:.2f} tok/s, {quality_text}, runs={item['runs']}"
            )

    if champions is not None:
        lines.extend(["", "## Champion Comparison"])
        for candidate in scored:
            comparison = champion_comparison(
                candidate,
                champions,
                weights=scoring_config,
                thresholds=thresholds,
                hardware_limits=hardware_limits,
            )
            if comparison["champion"] is None:
                lines.append(f"- {comparison['candidate']}: no champion configured")
            else:
                delta_text = f"{comparison['delta']:+.2f}" if comparison["delta"] is not None else "not assessed"
                lines.append(
                    f"- {comparison['candidate']} vs {comparison['champion']}: "
                    f"delta={delta_text} ({comparison['advantage']})"
                )

    return "\n".join(lines)


def write_report(report: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return path
