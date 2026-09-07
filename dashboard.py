from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

MISSING_VALUE = "Not available"

def load_dashboard_data(db_path: str | Path = "data/model_scout.db") -> dict[str, list[dict]]:
    path = Path(db_path)
    if not path.exists():
        return {"candidates": [], "benchmark_runs": [], "recommendations": [], "report_snapshots": [], "benchmark_tasks": [], "source_status": []}

    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        data = {}
        for table in ("candidates", "benchmark_runs", "recommendations", "report_snapshots", "benchmark_tasks", "source_status"):
            rows = connection.execute(f"SELECT * FROM {table} ORDER BY id ASC").fetchall()
            data[table] = [dict(row) for row in rows]
    return data


def summarize_runs(runs: list[dict]) -> list[dict]:
    grouped: dict[str, list[float]] = {}
    for run in runs:
        if run.get("status") != "OK":
            continue
        grouped.setdefault(str(run.get("model", "unknown")), []).append(float(run.get("tok_per_sec", 0)))

    return [
        {"model": model, "avg_tok_per_sec": round(sum(values) / len(values), 2), "runs": len(values)}
        for model, values in sorted(grouped.items())
    ]


def summarize_context_runs(runs: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, int], list[float]] = {}
    for run in runs:
        if run.get("status") != "OK":
            continue
        key = (str(run.get("model", "unknown")), int(run.get("context", 0)))
        grouped.setdefault(key, []).append(float(run.get("tok_per_sec", 0)))
    return [
        {"model": model, "context": context, "avg_tok_per_sec": round(sum(values) / len(values), 2), "runs": len(values)}
        for (model, context), values in sorted(grouped.items())
    ]


def summarize_telemetry(runs: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for run in runs:
        if run.get("status") == "OK":
            grouped.setdefault(str(run.get("model", "unknown")), []).append(run)

    def average(runs_for_model: list[dict], field: str) -> float | None:
        values = [float(run[field]) for run in runs_for_model if run.get(field) is not None]
        return round(sum(values) / len(values), 2) if values else None

    return [
        {
            "model": model,
            "avg_gpu_percent": average(model_runs, "gpu_utilization_percent"),
            "peak_gpu_memory_mb": max(
                [float(run["gpu_memory_used_mb"]) for run in model_runs if run.get("gpu_memory_used_mb") is not None],
                default=None,
            ),
            "avg_ram_mb": average(model_runs, "ram_used_mb"),
            "avg_cpu_percent": average(model_runs, "cpu_percent"),
            "runs": len(model_runs),
        }
        for model, model_runs in sorted(grouped.items())
    ]


def summarize_report_history(snapshots: list[dict]) -> list[dict]:
    return [
        {
            "created_at": snapshot.get("created_at", MISSING_VALUE),
            "total_candidates": snapshot.get("total_candidates", 0),
            "test_now": snapshot.get("test_now", 0),
            "surprise_test": snapshot.get("surprise_test", 0),
            "watch": snapshot.get("watch", 0),
            "needs_data": snapshot.get("needs_data", 0),
            "ignored": snapshot.get("ignored", 0),
        }
        for snapshot in snapshots
    ]


def summarize_quality(runs: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[float]] = {}
    for run in runs:
        if run.get("status") != "OK" or run.get("quality_score") is None:
            continue
        key = (str(run.get("model", "unknown")), str(run.get("category", "unknown")))
        grouped.setdefault(key, []).append(float(run["quality_score"]))
    return [
        {"model": model, "category": category, "avg_quality_score": round(sum(values) / len(values), 2), "runs": len(values)}
        for (model, category), values in sorted(grouped.items())
    ]


def summarize_source_status(rows: list[dict]) -> list[dict]:
    latest: dict[str, dict] = {}
    for row in rows:
        latest[str(row.get("source", "unknown"))] = row
    return [
        {"source": source, "status": row.get("status", MISSING_VALUE), "candidates": row.get("candidates", 0)}
        for source, row in sorted(latest.items())
    ]


def filter_dashboard_data(
    data: dict[str, list[dict]],
    *,
    model: str | None = None,
    recommendation: str | None = None,
    source: str | None = None,
    hardware_tier: str | None = None,
) -> dict[str, list[dict]]:
    filtered = {key: list(value) for key, value in data.items()}
    if model:
        filtered["candidates"] = [item for item in filtered["candidates"] if item.get("name") == model]
        filtered["recommendations"] = [item for item in filtered["recommendations"] if item.get("model") == model]
        filtered["benchmark_runs"] = [item for item in filtered["benchmark_runs"] if item.get("model") == model]
    if recommendation:
        filtered["recommendations"] = [
            item for item in filtered["recommendations"] if item.get("recommendation") == recommendation
        ]
    if source:
        filtered["candidates"] = [item for item in filtered["candidates"] if item.get("source") == source]
    if hardware_tier:
        filtered["candidates"] = [item for item in filtered["candidates"] if item.get("hardware_tier") == hardware_tier]
    return filtered


def display_rows(rows: list[dict]) -> list[dict]:
    """Create display copies without replacing missing values in stored data."""
    return [
        {key: MISSING_VALUE if value is None else value for key, value in row.items()}
        for row in rows
    ]


def show_table(st, title: str, rows: list[dict], empty_message: str) -> None:
    st.subheader(title)
    if rows:
        st.dataframe(display_rows(rows), use_container_width=True, hide_index=True)
    else:
        st.info(empty_message)


def render_dashboard(db_path: str | Path) -> None:
    import streamlit as st

    data = load_dashboard_data(db_path)
    st.set_page_config(page_title="LLM Model Scout", layout="wide")
    st.title("LLM Model Scout")
    st.caption(f"History: {db_path}")

    model_options = ["All"] + sorted({str(item.get("name")) for item in data["candidates"]})
    selected_model = st.selectbox("Model", model_options)
    recommendation_options = ["All"] + sorted({str(item.get("recommendation")) for item in data["recommendations"]})
    selected_recommendation = st.selectbox("Recommendation", recommendation_options)
    source_options = ["All"] + sorted({str(item.get("source")) for item in data["candidates"]})
    selected_source = st.selectbox("Source", source_options)
    tier_options = ["All"] + sorted({str(item.get("hardware_tier")) for item in data["candidates"] if item.get("hardware_tier")})
    selected_tier = st.selectbox("Hardware tier", tier_options)
    data = filter_dashboard_data(
        data,
        model=None if selected_model == "All" else selected_model,
        recommendation=None if selected_recommendation == "All" else selected_recommendation,
        source=None if selected_source == "All" else selected_source,
        hardware_tier=None if selected_tier == "All" else selected_tier,
    )

    candidates = data["candidates"]
    recommendations = data["recommendations"]
    runs = data["benchmark_runs"]
    test_now = sum(item.get("recommendation") == "TEST_NOW" for item in recommendations)
    watch = sum(item.get("recommendation") == "WATCH" for item in recommendations)

    first, second, third, fourth = st.columns(4)
    first.metric("Candidates", len(candidates))
    second.metric("Benchmark runs", len(runs))
    third.metric("Test now", test_now)
    fourth.metric("Watchlist", watch)

    show_table(st, "Recommendations", recommendations, "No recommendations match the selected filters.")
    show_table(st, "Benchmark throughput", summarize_runs(runs), "No successful benchmark runs are stored yet.")
    show_table(st, "Quality by category", summarize_quality(runs), "Quality scores appear after a benchmark plan has run.")
    show_table(st, "Throughput by context", summarize_context_runs(runs), "Context throughput appears after a successful benchmark run.")
    show_table(st, "Hardware telemetry", summarize_telemetry(runs), "Hardware telemetry appears after a successful benchmark run.")
    show_table(st, "Report history", summarize_report_history(data["report_snapshots"]), "Report history appears after the next report run.")
    show_table(st, "Benchmark task status", data["benchmark_tasks"], "Benchmark tasks appear after an approved plan is created.")
    show_table(st, "Source status", summarize_source_status(data["source_status"]), "Source status appears after the next discovery run.")
    show_table(st, "Discovered candidates", candidates, "No candidates were discovered for the selected filters.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LLM Model Scout dashboard")
    parser.add_argument("--db", default="data/model_scout.db", help="SQLite history database path")
    args = parser.parse_args()
    render_dashboard(args.db)


if __name__ == "__main__":
    main()
