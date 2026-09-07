import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_source_status_cli_returns_json():
    result = subprocess.run(
        [sys.executable, "src/main.py", "--source-status", "--offline", "--hf-limit", "0"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    assert payload["ollama"]["status"] in {"OK", "EMPTY", "ERROR"}
    assert payload["huggingface"]["status"] == "DISABLED"
