import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.download_queue import build_download_plan, load_queue, write_download_plan


def test_download_plan_requires_explicit_model_approval(tmp_path):
    queue_path = tmp_path / "queue.json"
    queue_path.write_text(json.dumps([{"model": "model-a"}, {"model": "model-b"}]), encoding="utf-8")

    queue = load_queue(queue_path)
    plan = build_download_plan(queue, {"model-a"})

    assert plan[0]["status"] == "APPROVED"
    assert plan[0]["command"] == ["ollama", "pull", "model-a"]
    assert plan[1]["status"] == "PENDING_APPROVAL"

    output = write_download_plan(plan, tmp_path / "plan.json")
    assert json.loads(output.read_text(encoding="utf-8"))[1]["status"] == "PENDING_APPROVAL"
