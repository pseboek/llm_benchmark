import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.runner import plan_dimensions


def test_plan_dimensions_ignores_completed_tasks():
    models, contexts, categories = plan_dimensions([
        {"model": "model-a", "context": 8192, "category": "01 Java", "status": "PENDING_EXECUTION"},
        {"model": "model-b", "context": 16384, "category": "02 Spring Boot", "status": "COMPLETED"},
    ])

    assert models == ["model-a"]
    assert contexts == [8192]
    assert categories == ["01 Java"]
