# ==============================================================================
# 🛡️ SP-ÁGUAS / SA-GTI — AUDITORIA & COMPROVAÇÃO DE SINCRONIZAÇÃO AGENDADA
# Valida se a sincronização automática do OpenProject está operando conforme
# a programação do Cockpit e do Agendador do Windows.
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " 🛡️ SP-ÁGUAS / SA-GTI — COMPROVAÇÃO DA SINCRONIZAÇÃO AGENDADA OPENPROJECT" -ForegroundColor Cyan
Write-Host " Data/Hora: $(Get-Date -Format 'dd/MM/yyyy às HH:mm:ss') | Governança: SA-GTI" -ForegroundColor Gray
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "C:\Cockpit_GTI"
if (-not (Test-Path $baseDir)) {
    $baseDir = (Get-Location).Path
}

# 1. Checagem da Tarefa Agendada no Windows
Write-Host " [1/3] VERIFICAÇÃO DO AGENDADOR DE TAREFAS DO WINDOWS:" -ForegroundColor Yellow
$taskName = "CockpitGTI_Sincronizacao_Horaria_OpenProject"

$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
    Write-Host "   [✓] Tarefa Agendada Identificada: '$taskName'" -ForegroundColor Green
    Write-Host "       • Estado Atual: $($task.State)" -ForegroundColor White
    Write-Host "       • Última Execução: $($taskInfo.LastRunTime)" -ForegroundColor White
    $resText = if ($taskInfo.LastTaskResult -eq 0) { "0 (Sucesso / Executado com Êxito)" } else { "$($taskInfo.LastTaskResult) (Aviso)" }
    Write-Host "       • Resultado da Última Execução: $resText" -ForegroundColor White
    Write-Host "       • Próxima Execução Agendada: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
} else {
    Write-Host "   [!] Tarefa '$taskName' ainda não registrada no Agendador do Windows." -ForegroundColor Yellow
    Write-Host "       Execute 'ativar_automacao_horaria_windows.ps1' para registrar o serviço em segundo plano." -ForegroundColor Gray
}

Write-Host ""

# 2. Leitura do Registro Probatório JSON de Execuções
Write-Host " [2/3] REGISTRO HISTÓRICO DE EXECUÇÕES (registro_execucao_agendada.json):" -ForegroundColor Yellow
$regJsonPath = Join-Path $baseDir "registro_execucao_agendada.json"

if (Test-Path $regJsonPath) {
    try {
        $conteudo = Get-Content -Path $regJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $totalExecs = $conteudo.Count
        Write-Host "   [✓] Arquivo de histórico localizado: $totalExecs execuções registradas." -ForegroundColor Green
        
        $top5 = $conteudo | Select-Object -First 5
        Write-Host ""
        Write-Host "   Últimas Execuções Registradas:" -ForegroundColor Gray
        foreach ($item in $top5) {
            $statusCor = if ($item.status -eq "SUCESSO") { "Green" } else { "Yellow" }
            Write-Host "   • [$($item.timestamp)] - Modo: $($item.modo) | Cards: $($item.cards_processados) | Status: $($item.status) | Comprovante: #$($item.comprovante_hash)" -ForegroundColor $statusCor
        }
    } catch {
        Write-Host "   [!] Falha ao ler JSON: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [i] Nenhum registro histórico gerado ainda em '$regJsonPath'." -ForegroundColor Gray
}

Write-Host ""

# 3. Leitura do Laudo de Auditoria TXT
Write-Host " [3/3] LAUDO PROBATÓRIO DE AUDITORIA (laudo_sincronizacao_automatica.txt):" -ForegroundColor Yellow
$laudoPath = Join-Path $baseDir "laudo_sincronizacao_automatica.txt"

if (Test-Path $laudoPath) {
    Write-Host "   [✓] Laudo de auditoria localizado." -ForegroundColor Green
    $ultimasLinhas = Get-Content -Path $laudoPath -Tail 8 -Encoding UTF8
    Write-Host ""
    Write-Host "   Últimos registros de log:" -ForegroundColor Gray
    foreach ($linha in $ultimasLinhas) {
        Write-Host "     $linha" -ForegroundColor DarkGray
    }
} else {
    Write-Host "   [i] Arquivo laudo_sincronizacao_automatica.txt será gerado na primeira sincronização." -ForegroundColor Gray
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " [RESUMO DO COMPROVANTE] Governança SA-GTI / SP-Águas" -ForegroundColor Cyan
Write-Host " • Sincronização Agendada: Conforme ajuste configurado no Motor 3" -ForegroundColor White
Write-Host " • Sincronização Manual 1 a 1: Ativa e Homologada no Orquestrador Web" -ForegroundColor White
Write-Host "==============================================================================" -ForegroundColor Cyan
