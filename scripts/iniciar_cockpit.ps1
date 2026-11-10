# ==============================================================================
# SP-ÁGUAS / SA-GTI -- INICIALIZADOR POWERSHELL DO COCKPIT GTI (V11)
# ==============================================================================
$ErrorActionPreference = "SilentlyContinue"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " SP-AGUAS / SA-GTI -- INICIALIZADOR DO COCKPIT GTI V11" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Cyan

if (Test-Path "$projectRoot\requirements.txt") {
    Write-Host "[*] Verificando dependencias Python..." -ForegroundColor Cyan
    python -m pip install -r "$projectRoot\requirements.txt" --quiet --disable-pip-version-check
}

Write-Host "[*] Iniciando Backend Flask (:5000)..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "backend\main.py" -WindowStyle Hidden

Start-Sleep -Seconds 2

Write-Host "[*] Abrindo Cockpit GTI no navegador..." -ForegroundColor Cyan
Start-Process "$projectRoot\painel.html"

Write-Host "[OK] Cockpit GTI em execucao com sucesso!" -ForegroundColor Green
