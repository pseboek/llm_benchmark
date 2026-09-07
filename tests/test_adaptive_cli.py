import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_suggest_weights_cli_writes_json(tmp_path):
    output = tmp_path / "weights.json"
    result = subprocess.run(
        [sys.executable, "src/main.py", "--suggest-weights", "--db", str(tmp_path / "scout.db"), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Weight suggestion saved" in result.stdout
    assert json.loads(output.read_text(encoding="utf-8"))["speed"] == 0.15
