from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


class ModelScoutDB:
    def __init__(self, db_path: str | Path = "data/model_scout.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    source TEXT NOT NULL DEFAULT 'unknown',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS benchmark_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    context INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    tok_per_sec REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    score REAL NOT NULL,
                    hardware_tier TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save_candidates(self, candidates: Iterable[dict]) -> list[dict]:
        saved: list[dict] = []
        with self._connect() as connection:
            for candidate in candidates:
                name = str(candidate.get("name", "")).strip()
                if not name:
                    continue
                source = str(candidate.get("source", "unknown")).strip() or "unknown"
                connection.execute(
                    "INSERT OR IGNORE INTO candidates (name, source) VALUES (?, ?)",
                    (name, source),
                )
                saved.append({"name": name, "source": source})
        return saved

    def list_candidates(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name, source FROM candidates ORDER BY id ASC"
            ).fetchall()
        return [{"name": name, "source": source} for name, source in rows]

    def save_benchmark_runs(self, runs: Iterable[dict]) -> None:
        with self._connect() as connection:
            connection.executemany(
                "INSERT INTO benchmark_runs (model, context, category, status, tok_per_sec) VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        str(run.get("model", "unknown")),
                        int(run.get("context", 0)),
                        str(run.get("category", "unknown")),
                        str(run.get("status", "UNKNOWN")),
                        float(run.get("tok_per_sec", 0.0)),
                    )
                    for run in runs
                ],
            )

    def list_benchmark_runs(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT model, context, category, status, tok_per_sec FROM benchmark_runs ORDER BY id ASC"
            ).fetchall()
        return [
            {"model": model, "context": context, "category": category, "status": status, "tok_per_sec": tok_per_sec}
            for model, context, category, status, tok_per_sec in rows
        ]

    def save_recommendations(self, recommendations: Iterable[dict]) -> None:
        with self._connect() as connection:
            connection.executemany(
                "INSERT INTO recommendations (model, score, hardware_tier, recommendation) VALUES (?, ?, ?, ?)",
                [
                    (
                        str(item.get("model", item.get("name", "unknown"))),
                        float(item.get("score", 0.0)),
                        str(item.get("hardware_tier", "UNKNOWN")),
                        str(item.get("recommendation", "IGNORE")),
                    )
                    for item in recommendations
                ],
            )

    def list_recommendations(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT model, score, hardware_tier, recommendation FROM recommendations ORDER BY id ASC"
            ).fetchall()
        return [
            {"model": model, "score": score, "hardware_tier": tier, "recommendation": action}
            for model, score, tier, action in rows
        ]