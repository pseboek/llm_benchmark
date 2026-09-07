from __future__ import annotations

from datetime import date
from pathlib import Path

from src.scoring import champion_comparison, score_candidate


def build_report(
    candidates: list[dict],
    champions: list[dict] | None = None,
    scoring_config: dict | None = None,
    hardware_config: dict | None = None,
) -> str:
    scoring_config = scoring_config or {}
    hardware_limits = (hardware_config or {}).get("vram", {})
    thresholds = (hardware_config or {}).get("thresholds")
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
    for action, title in groups.items():
        lines.append(f"- {title}: {sum(item['recommendation'] == action for item in scored)}")
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
