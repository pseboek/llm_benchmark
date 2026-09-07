import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import ollama_benchmark


def test_benchmark_result_path_uses_configured_directory(tmp_path):
    path = ollama_benchmark.result_path(tmp_path, "20260907_120000")

    assert path == tmp_path / "ollama_benchmark_20260907_120000.csv"
