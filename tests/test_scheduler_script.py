from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_scheduler_script_uses_repository_relative_paths():
    script = (ROOT / "scripts" / "run_scout_report.ps1").read_text(encoding="utf-8")

    assert "$PSScriptRoot" in script
    assert "--report" in script
    assert "--hf-limit" in script
    assert "C:\\Users" not in script
