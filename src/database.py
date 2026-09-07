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