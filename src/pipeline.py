from __future__ import annotations

from src.discovery import deduplicate_candidates
from src.sources.huggingface import list_hf_candidates
from src.sources.ollama import list_local_candidates


def discover_candidates(ollama_url: str | None = None, huggingface_limit: int = 10) -> list[dict]:
    candidates: list[dict] = []

    candidates.extend(list_local_candidates(ollama_url) if ollama_url else list_local_candidates())
    candidates.extend(list_hf_candidates(limit=huggingface_limit))

    return deduplicate_candidates(candidates)
