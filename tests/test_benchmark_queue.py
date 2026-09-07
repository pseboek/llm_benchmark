import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.benchmark_queue import build_benchmark_queue, write_benchmark_queue


def test_queue_only_contains_actionable_candidates_and_respects_limit(tmp_path):
    candidates = [
        {"name": "ignore", "coding": 10},
        {"name": "test-a", "coding": 100, "reasoning": 100, "general": 100, "speed": 100, "vram_efficiency": 100, "context": 100, "tool_agent": 100, "freshness": 100},
        {"name": "test-b", "coding": 99, "reasoning": 99, "general": 99, "speed": 99, "vram_efficiency": 99, "context": 99, "tool_agent": 99, "freshness": 99},
    ]

    queue = build_benchmark_queue(candidates, max_candidates=1)
    assert len(queue) == 1
    assert queue[0]["model"] == "test-a"
    assert queue[0]["status"] == "PENDING_REVIEW"

    output = write_benchmark_queue(queue, tmp_path / "queue.json")
    assert json.loads(output.read_text(encoding="utf-8"))[0]["model"] == "test-a"
