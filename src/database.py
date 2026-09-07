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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS report_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_candidates INTEGER NOT NULL,
                    test_now INTEGER NOT NULL,
                    surprise_test INTEGER NOT NULL,
                    watch INTEGER NOT NULL,
                    needs_data INTEGER NOT NULL,
                    ignored INTEGER NOT NULL,
                    output_path TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._ensure_column(connection, "benchmark_runs", "prompt_version", "TEXT NOT NULL DEFAULT 'unknown'")
            self._ensure_column(connection, "benchmark_runs", "prompt_tok_per_sec", "REAL NOT NULL DEFAULT 0")
            self._ensure_column(connection, "benchmark_runs", "ttft_seconds", "REAL")
            for column in (
                "gpu_utilization_percent",
                "gpu_memory_used_mb",
                "gpu_memory_total_mb",
                "ram_used_mb",
                "cpu_percent",
            ):
                self._ensure_column(connection, "benchmark_runs", column, "REAL")
            self._ensure_column(connection, "candidates", "parameter_size", "TEXT")
            self._ensure_column(connection, "candidates", "quantization", "TEXT")
            self._ensure_column(connection, "candidates", "architecture", "TEXT")
            self._ensure_column(connection, "candidates", "estimated_vram_gb", "REAL")
            self._ensure_column(connection, "candidates", "parameters_total_b", "REAL")
            self._ensure_column(connection, "candidates", "context_length", "INTEGER")
            self._migrate_nullable_recommendation_score(connection)

    @staticmethod
    def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
        columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
        if column not in columns:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    @staticmethod
    def _migrate_nullable_recommendation_score(connection: sqlite3.Connection) -> None:
        columns = connection.execute("PRAGMA table_info(recommendations)").fetchall()
        score_column = next((column for column in columns if column[1] == "score"), None)
        if score_column is None or score_column[3] == 0:
            return
        connection.execute("ALTER TABLE recommendations RENAME TO recommendations_legacy")
        connection.execute(
            """
            CREATE TABLE recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                score REAL,
                hardware_tier TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            INSERT INTO recommendations (model, score, hardware_tier, recommendation, created_at)
            SELECT model, score, hardware_tier, recommendation, created_at
            FROM recommendations_legacy
            """
        )
        connection.execute("DROP TABLE recommendations_legacy")

    def save_candidates(self, candidates: Iterable[dict]) -> list[dict]:
        saved: list[dict] = []
        with self._connect() as connection:
            for candidate in candidates:
                name = str(candidate.get("name", "")).strip()
                if not name:
                    continue
                source = str(candidate.get("source", "unknown")).strip() or "unknown"
                connection.execute(
                    """
                    INSERT INTO candidates
                        (name, source, parameter_size, quantization, architecture, estimated_vram_gb, parameters_total_b, context_length)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        source = excluded.source,
                        parameter_size = COALESCE(excluded.parameter_size, candidates.parameter_size),
                        quantization = COALESCE(excluded.quantization, candidates.quantization),
                        architecture = COALESCE(excluded.architecture, candidates.architecture),
                        estimated_vram_gb = COALESCE(excluded.estimated_vram_gb, candidates.estimated_vram_gb),
                        parameters_total_b = COALESCE(excluded.parameters_total_b, candidates.parameters_total_b),
                        context_length = COALESCE(excluded.context_length, candidates.context_length)
                    """,
                    (
                        name,
                        source,
                        candidate.get("parameter_size"),
                        candidate.get("quantization"),
                        candidate.get("architecture"),
                        candidate.get("estimated_vram_gb"),
                        candidate.get("parameters_total_b"),
                        candidate.get("context_length"),
                    ),
                )
                saved.append(dict(candidate, name=name, source=source))
        return saved

    def list_candidates(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name, source, parameter_size, quantization, architecture, estimated_vram_gb, parameters_total_b, context_length FROM candidates ORDER BY id ASC"
            ).fetchall()
        candidates = []
        for name, source, parameter_size, quantization, architecture, estimated_vram_gb, parameters_total_b, context_length in rows:
            candidate = {"name": name, "source": source}
            for key, value in {
                "parameter_size": parameter_size,
                "quantization": quantization,
                "architecture": architecture,
                "estimated_vram_gb": estimated_vram_gb,
                "parameters_total_b": parameters_total_b,
                "context_length": context_length,
            }.items():
                if value is not None:
                    candidate[key] = value
            candidates.append(candidate)
        return candidates

    def save_benchmark_runs(self, runs: Iterable[dict]) -> None:
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO benchmark_runs
                    (model, context, category, status, tok_per_sec, prompt_version,
                     prompt_tok_per_sec, ttft_seconds, gpu_utilization_percent,
                     gpu_memory_used_mb, gpu_memory_total_mb, ram_used_mb, cpu_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        str(run.get("model", "unknown")),
                        int(run.get("context", 0)),
                        str(run.get("category", "unknown")),
                        str(run.get("status", "UNKNOWN")),
                        float(run.get("tok_per_sec", 0.0)),
                        str(run.get("prompt_version", "unknown")),
                        float(run.get("prompt_tok_per_sec", 0.0)),
                        run.get("ttft_seconds"),
                        run.get("gpu_utilization_percent"),
                        run.get("gpu_memory_used_mb"),
                        run.get("gpu_memory_total_mb"),
                        run.get("ram_used_mb"),
                        run.get("cpu_percent"),
                    )
                    for run in runs
                ],
            )

    def list_benchmark_runs(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT model, context, category, status, tok_per_sec, prompt_version, prompt_tok_per_sec, ttft_seconds, gpu_utilization_percent, gpu_memory_used_mb, gpu_memory_total_mb, ram_used_mb, cpu_percent FROM benchmark_runs ORDER BY id ASC"
            ).fetchall()
        return [
            {
                "model": model, "context": context, "category": category,
                "status": status, "tok_per_sec": tok_per_sec,
                "prompt_version": prompt_version, "prompt_tok_per_sec": prompt_tok_per_sec,
                "ttft_seconds": ttft_seconds,
                "gpu_utilization_percent": gpu_utilization_percent,
                "gpu_memory_used_mb": gpu_memory_used_mb,
                "gpu_memory_total_mb": gpu_memory_total_mb,
                "ram_used_mb": ram_used_mb,
                "cpu_percent": cpu_percent,
            }
            for model, context, category, status, tok_per_sec, prompt_version,
            prompt_tok_per_sec, ttft_seconds, gpu_utilization_percent,
            gpu_memory_used_mb, gpu_memory_total_mb, ram_used_mb, cpu_percent in rows
        ]

    def save_recommendations(self, recommendations: Iterable[dict]) -> None:
        with self._connect() as connection:
            for item in recommendations:
                model = str(item.get("model", item.get("name", "unknown")))
                connection.execute("DELETE FROM recommendations WHERE model = ?", (model,))
                connection.execute(
                    "INSERT INTO recommendations (model, score, hardware_tier, recommendation) VALUES (?, ?, ?, ?)",
                    (
                        model,
                        item.get("score"),
                        str(item.get("hardware_tier", "UNKNOWN")),
                        str(item.get("recommendation", "IGNORE")),
                    ),
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

    def save_report_snapshot(self, snapshot: dict) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO report_snapshots
                    (total_candidates, test_now, surprise_test, watch, needs_data, ignored, output_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    int(snapshot.get("total_candidates", 0)),
                    int(snapshot.get("test_now", 0)),
                    int(snapshot.get("surprise_test", 0)),
                    int(snapshot.get("watch", 0)),
                    int(snapshot.get("needs_data", 0)),
                    int(snapshot.get("ignored", 0)),
                    snapshot.get("output_path"),
                ),
            )

    def list_report_snapshots(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT created_at, total_candidates, test_now, surprise_test, watch, needs_data, ignored, output_path FROM report_snapshots ORDER BY id ASC"
            ).fetchall()
        return [
            {
                "created_at": created_at,
                "total_candidates": total_candidates,
                "test_now": test_now,
                "surprise_test": surprise_test,
                "watch": watch,
                "needs_data": needs_data,
                "ignored": ignored,
                "output_path": output_path,
            }
            for created_at, total_candidates, test_now, surprise_test, watch, needs_data, ignored, output_path in rows
        ]