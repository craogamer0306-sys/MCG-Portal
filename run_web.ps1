param([switch]$Reset)
if ($Reset) { if (Test-Path .venv) { Remove-Item -Recurse -Force .venv } }
python -V 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Error "Python not found. Install Python 3.11+"; exit 1 }
if (-not (Test-Path .venv)) { python -m venv .venv }
& .\.venv\Scripts\pip.exe install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env; Write-Host "Created .env from template. Fill your values." }
$port = "5173"; try { (Get-Content .env) | ForEach-Object { if ($_ -match "^PORT=(.*)$") { $port = $Matches[1] } } } catch {}
& .\.venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port $port --reload
