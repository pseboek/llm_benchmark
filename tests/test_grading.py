import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.grading import grade_response


def test_grade_response_is_transparent_and_bounded():
    result = grade_response("class Example { }\n```java\nservice\n```" * 20, "Java")

    assert 0 <= result["quality_score"] <= 100
    assert result["quality_method"] == "heuristic_v2"
    assert 0 <= result["quality_confidence"] <= 1
    assert set(result["quality_components"]) == {"completeness", "structure", "relevance"}


def test_empty_response_scores_zero():
    assert grade_response("", "Java")["quality_score"] == 0.0
