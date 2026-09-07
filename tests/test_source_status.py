import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import discover_with_status


def test_discovery_status_reports_empty_source_and_candidate_counts(monkeypatch):
    monkeypatch.setattr("src.pipeline.list_local_candidates", lambda: [{"name": "local", "source": "ollama"}])
    monkeypatch.setattr("src.pipeline.list_hf_candidates", lambda limit=10: [])
    monkeypatch.setattr("src.pipeline.list_artificial_analysis_candidates", lambda: [])
    monkeypatch.setattr("src.pipeline.list_swebench_candidates", lambda: [])

    candidates, status = discover_with_status()

    assert candidates == [{"name": "local", "source": "ollama"}]
    assert status["ollama"]["candidates"] == 1
    assert status["huggingface"]["candidates"] == 0
    assert status["swebench"]["status"] == "EMPTY"
