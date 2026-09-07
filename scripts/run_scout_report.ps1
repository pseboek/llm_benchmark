$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }
$reportPath = Join-Path $projectRoot ("reports\{0}_model_scout.md" -f (Get-Date -Format "yyyy-MM-dd"))
$dbPath = Join-Path $projectRoot "data\model_scout.db"

Push-Location $projectRoot
try {
    & $python "src\main.py" --report --offline --db $dbPath --output $reportPath
    if ($LASTEXITCODE -ne 0) {
        throw "Model Scout report failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
