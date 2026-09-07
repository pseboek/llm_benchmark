from __future__ import annotations

from src.discovery import deduplicate_candidates
from src.sources.artificial_analysis import list_artificial_analysis_candidates
from src.sources.huggingface import list_hf_candidates
from src.sources.lmarena import list_lmarena_candidates
from src.sources.ollama import list_local_candidates
from src.sources.swebench import list_swebench_candidates


def discover_candidates(
    ollama_url: str | None = None,
    huggingface_limit: int = 10,
    enabled_sources: dict[str, bool] | None = None,
) -> list[dict]:
    enabled = enabled_sources or {
        "ollama": True,
        "huggingface": True,
        "lmarena": True,
        "artificial_analysis": True,
        "swebench": True,
    }
    loaders = {
        "ollama": lambda: list_local_candidates(ollama_url) if ollama_url else list_local_candidates(),
        "huggingface": lambda: list_hf_candidates(limit=huggingface_limit),
        "lmarena": list_lmarena_candidates,
        "artificial_analysis": list_artificial_analysis_candidates,
        "swebench": list_swebench_candidates,
    }
    candidates: list[dict] = []
    for source, loader in loaders.items():
        if not enabled.get(source, True):
            continue
        try:
            candidates.extend(loader())
        except Exception:
            # A broken/misconfigured source must not abort discovery for the others.
            continue

    return deduplicate_candidates(candidates)


def discover_with_status(
    ollama_url: str | None = None,
    huggingface_limit: int = 10,
    enabled_sources: dict[str, bool] | None = None,
) -> tuple[list[dict], dict[str, dict]]:
    enabled = enabled_sources or {
        "ollama": True,
        "huggingface": True,
        "lmarena": True,
        "artificial_analysis": True,
        "swebench": True,
    }
    loaders = {
        "ollama": lambda: list_local_candidates(ollama_url) if ollama_url else list_local_candidates(),
        "huggingface": lambda: list_hf_candidates(limit=huggingface_limit),
        "lmarena": list_lmarena_candidates,
        "artificial_analysis": list_artificial_analysis_candidates,
        "swebench": list_swebench_candidates,
    }
    candidates: list[dict] = []
    status: dict[str, dict] = {}
    for source, loader in loaders.items():
        if not enabled.get(source, True):
            status[source] = {"status": "DISABLED", "candidates": 0}
            continue
        try:
            found = loader()
            candidates.extend(found)
            status[source] = {"status": "OK" if found else "EMPTY", "candidates": len(found)}
        except Exception as error:
            status[source] = {"status": "ERROR", "candidates": 0, "error": str(error)}
    return deduplicate_candidates(candidates), status
