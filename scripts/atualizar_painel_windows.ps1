# =====================================================================
# ATUALIZADOR OFICIAL DO COCKPIT GTI (SA-GTI SP-ÁGUAS)
# Executa a substituição segura e abre o painel atualizado no navegador
# =====================================================================
$ErrorActionPreference = "SilentlyContinue"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " SP-AGUAS / SA-GTI -- ATUALIZADOR AUTOMATICO DO COCKPIT GTI V11" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

$possiveisCaminhos = @(
    "C:\Cockpit_GTI",
    "C:\Projetos\Cockpit_GTI",
    "$PSScriptRoot\..",
    "$PSScriptRoot"
)

$destinoOficial = "C:\Cockpit_GTI"
foreach ($caminho in $possiveisCaminhos) {
    if (Test-Path "$caminho\painel.html") {
        $destinoOficial = $caminho
        break
    }
}

Write-Host "[+] Destino identificado: $destinoOficial" -ForegroundColor Cyan

if (Test-Path "$PSScriptRoot\painel.html") {
    Copy-Item -Path "$PSScriptRoot\painel.html" -Destination "$destinoOficial\painel.html" -Force
    Write-Host "[OK] painel.html copiado com sucesso para $destinoOficial\painel.html" -ForegroundColor Green
    
    if (Test-Path "$destinoOficial\frontend") {
        Copy-Item -Path "$PSScriptRoot\painel.html" -Destination "$destinoOficial\frontend\painel.html" -Force
        Write-Host "[OK] frontend\painel.html sincronizado com sucesso!" -ForegroundColor Green
    }
}

Write-Host "`n[*] Abrindo Cockpit no navegador padrao..." -ForegroundColor Cyan
Start-Process "$destinoOficial\painel.html"
Write-Host "[CONCLUIDO] Se a aba antiga permanecer no navegador, feche-a e utilize esta nova janela." -ForegroundColor Green
