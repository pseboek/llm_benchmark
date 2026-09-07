import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.prompts import PERSONAL_PROMPTS, PROMPT_VERSION


def test_personal_prompt_catalog_is_versioned_and_complete():
    assert PROMPT_VERSION == "v1"
    assert len(PERSONAL_PROMPTS) == 10
    assert list(PERSONAL_PROMPTS)[0].startswith("01 ")
    assert list(PERSONAL_PROMPTS)[-1].startswith("10 ")
    assert all(prompt.strip() for prompt in PERSONAL_PROMPTS.values())
