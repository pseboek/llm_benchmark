import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.runner import apply_result_statuses


def test_apply_result_statuses_updates_plan_tasks():
    plan = [
        {"model": "model-a", "context": 8192, "category": "01 Java", "status": "PENDING_EXECUTION"},
        {"model": "model-a", "context": 8192, "category": "02 Spring Boot", "status": "PENDING_EXECUTION"},
    ]
    results = [{"model": "model-a", "context": 8192, "category": "01 Java", "status": "OK"}]

    updated = apply_result_statuses(plan, results)

    assert updated[0]["status"] == "COMPLETED"
    assert updated[1]["status"] == "FAILED"


def test_unselected_pending_tasks_remain_pending():
    plan = [
        {"model": "model-a", "context": 8192, "category": "01 Java", "status": "PENDING_EXECUTION"},
        {"model": "model-a", "context": 8192, "category": "02 Spring Boot", "status": "PENDING_EXECUTION"},
    ]

    updated = apply_result_statuses(plan, [], {("model-a", 8192, "01 Java")})

    assert updated[0]["status"] == "FAILED"
    assert updated[1]["status"] == "PENDING_EXECUTION"
