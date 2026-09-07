import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_task_status_cli_outputs_json(tmp_path):
    result = subprocess.run(
        [sys.executable, "src/main.py", "--task-status", "--db", str(tmp_path / "scout.db")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    assert payload["total"] == 0
    assert payload["by_status"] == {}
