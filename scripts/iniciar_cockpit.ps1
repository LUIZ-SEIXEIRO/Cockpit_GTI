# ==============================================================================
# SP-ÁGUAS / SA-GTI -- INICIALIZADOR POWERSHELL DO COCKPIT GTI (V11)
# ==============================================================================
$ErrorActionPreference = "SilentlyContinue"
$projectRoot = "C:\Cockpit_GTI"
if (-not (Test-Path $projectRoot)) {
    $projectRoot = Split-Path -Parent $PSScriptRoot
}
Set-Location $projectRoot

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " SP-AGUAS / SA-GTI -- INICIALIZADOR DO COCKPIT GTI V11 (HTTP :5000)" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Cyan

# 1. Libera a porta 5000 caso haja algum processo Python anterior pendente
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Localiza e inicia o main.py
$mainFile = "main.py"
if (-not (Test-Path "$projectRoot\main.py")) {
    $mainFile = "backend\main.py"
}

Write-Host "[*] Iniciando Servidor Flask Oficial (:5000)..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList $mainFile -WindowStyle Hidden

Start-Sleep -Seconds 2

# 3. Abre no navegador via servidor web HTTP
Write-Host "[*] Abrindo Cockpit GTI em http://localhost:5000/..." -ForegroundColor Cyan
Start-Process "http://localhost:5000/"

Write-Host "[OK] Cockpit GTI em execucao via HTTP (http://localhost:5000/)!" -ForegroundColor Green
