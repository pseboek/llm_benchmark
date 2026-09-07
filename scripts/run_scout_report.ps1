$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }
$reportPath = Join-Path $projectRoot ("reports\{0}_model_scout.md" -f (Get-Date -Format "yyyy-MM-dd"))
$dbPath = Join-Path $projectRoot "data\model_scout.db"

Push-Location $projectRoot
try {
    # Live discovery: queries Ollama, Hugging Face and (best-effort)
    # Artificial Analysis and SWE-bench. Broken/misconfigured sources report
    # ERROR in the report's Source Status section instead of aborting the run.
    # Starts no downloads and no local model benchmark.
    & $python "src\main.py" --report --hf-limit 15 --db $dbPath --output $reportPath
    if ($LASTEXITCODE -ne 0) {
        throw "Model Scout report failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
