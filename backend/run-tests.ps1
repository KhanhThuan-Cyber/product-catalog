
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Chưa tìm thấy Python trong .venv."
}

$env:PYTHONPATH = Join-Path $PSScriptRoot "src"

& $Python -m pytest tests -v

exit $LASTEXITCODE
