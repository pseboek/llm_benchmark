from __future__ import annotations

import re
from typing import Iterable


def normalize_model_name(name: str) -> str:
    normalized = (name or "").strip().lower()

    if "/" in normalized:
        parts = [part for part in normalized.split("/") if part]
        if len(parts) >= 2:
            normalized = parts[-1]

    normalized = normalized.replace("_", "-")
    normalized = normalized.replace(":", "-")
    normalized = re.sub(r"[^a-z0-9.\-]", "", normalized)
    normalized = re.sub(r"-+", "-", normalized)
    normalized = normalized.strip("-")
    return normalized


def _prefer_candidate(existing: dict, candidate: dict) -> dict:
    existing_source = str(existing.get("source", "")).lower()
    candidate_source = str(candidate.get("source", "")).lower()

    if candidate_source == "ollama" and existing_source != "ollama":
        return candidate
    if existing_source == "ollama" and candidate_source != "ollama":
        return existing

    existing_name = str(existing.get("name", "")).strip()
    candidate_name = str(candidate.get("name", "")).strip()
    if len(candidate_name) < len(existing_name):
        return candidate
    return existing


def deduplicate_candidates(candidates: Iterable[dict]) -> list[dict]:
    by_key: dict[str, dict] = {}
    for candidate in candidates:
        raw_name = str(candidate.get("name", "")).strip()
        if not raw_name:
            continue

        key = normalize_model_name(raw_name)
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = candidate
        else:
            by_key[key] = _prefer_candidate(existing, candidate)

    return list(by_key.values())
