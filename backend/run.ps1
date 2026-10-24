
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Chưa tìm thấy Python trong .venv. Hãy tạo môi trường ảo và cài requirements.txt."
}

& $Python -m uvicorn app.main:app --app-dir src --reload