from __future__ import annotations

from src.discovery import deduplicate_candidates
from src.sources.artificial_analysis import list_artificial_analysis_candidates
from src.sources.huggingface import list_hf_candidates
from src.sources.lmarena import list_lmarena_candidates
from src.sources.ollama import list_local_candidates
from src.sources.swebench import list_swebench_candidates


def discover_candidates(ollama_url: str | None = None, huggingface_limit: int = 10) -> list[dict]:
    candidates: list[dict] = []

    candidates.extend(list_local_candidates(ollama_url) if ollama_url else list_local_candidates())
    candidates.extend(list_hf_candidates(limit=huggingface_limit))
    candidates.extend(list_lmarena_candidates())
    candidates.extend(list_artificial_analysis_candidates())
    candidates.extend(list_swebench_candidates())

    return deduplicate_candidates(candidates)
