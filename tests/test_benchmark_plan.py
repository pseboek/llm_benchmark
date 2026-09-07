import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.benchmark_plan import build_benchmark_plan, write_benchmark_plan


def test_approved_models_expand_into_versioned_benchmark_tasks(tmp_path):
    plan = build_benchmark_plan(
        [{"model": "model-a"}, {"model": "model-b"}],
        {"model-a"},
        [8192, 16384],
    )

    assert len(plan) == 20
    assert {item["model"] for item in plan} == {"model-a"}
    assert {item["context"] for item in plan} == {8192, 16384}
    assert {item["prompt_version"] for item in plan} == {"v1"}
    assert {item["status"] for item in plan} == {"PENDING_EXECUTION"}

    output = write_benchmark_plan(plan, tmp_path / "benchmark_plan.json")
    assert output.exists()
