from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def load_dashboard_data(db_path: str | Path = "data/model_scout.db") -> dict[str, list[dict]]:
    path = Path(db_path)
    if not path.exists():
        return {"candidates": [], "benchmark_runs": [], "recommendations": []}

    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        data = {}
        for table in ("candidates", "benchmark_runs", "recommendations"):
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


def render_dashboard(db_path: str | Path) -> None:
    import streamlit as st

    data = load_dashboard_data(db_path)
    st.set_page_config(page_title="LLM Model Scout", layout="wide")
    st.title("LLM Model Scout")
    st.caption(f"History: {db_path}")

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

    st.subheader("Recommendations")
    st.dataframe(recommendations, use_container_width=True, hide_index=True)

    st.subheader("Benchmark throughput")
    st.dataframe(summarize_runs(runs), use_container_width=True, hide_index=True)

    st.subheader("Discovered candidates")
    st.dataframe(candidates, use_container_width=True, hide_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LLM Model Scout dashboard")
    parser.add_argument("--db", default="data/model_scout.db", help="SQLite history database path")
    args = parser.parse_args()
    render_dashboard(args.db)


if __name__ == "__main__":
    main()
