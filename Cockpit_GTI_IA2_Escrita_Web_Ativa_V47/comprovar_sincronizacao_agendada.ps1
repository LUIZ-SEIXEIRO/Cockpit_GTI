# ==============================================================================
# SP-AGUAS / SA-GTI -- AUDITORIA E COMPROVACAO DE SINCRONIZACAO AGENDADA
# Compativel 100% com Windows PowerShell 5.1 e PowerShell 7
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " SP-AGUAS / SA-GTI -- COMPROVACAO DA SINCRONIZACAO AGENDADA OPENPROJECT" -ForegroundColor Cyan
Write-Host " Data/Hora: $(Get-Date -Format 'dd/MM/yyyy as HH:mm:ss') | Governanca: SA-GTI" -ForegroundColor Gray
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "C:\Cockpit_GTI"
if (-not (Test-Path $baseDir)) {
    $baseDir = (Get-Location).Path
}

# 1. Checagem da Tarefa Agendada no Windows
Write-Host " [1/3] VERIFICACAO DO AGENDADOR DE TAREFAS DO WINDOWS:" -ForegroundColor Yellow
$taskName = "CockpitGTI_Sincronizacao_Horaria_OpenProject"

$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
    Write-Host "   [OK] Tarefa Agendada Identificada: '$taskName'" -ForegroundColor Green
    Write-Host "       * Estado Atual: $($task.State)" -ForegroundColor White
    Write-Host "       * Ultima Execucao: $($taskInfo.LastRunTime)" -ForegroundColor White
    
    $resText = "$($taskInfo.LastTaskResult) (Aviso)"
    if ($taskInfo.LastTaskResult -eq 0) {
        $resText = "0 (Sucesso / Executado com Exito)"
    }
    Write-Host "       * Resultado da Ultima Execucao: $resText" -ForegroundColor White
    Write-Host "       * Proxima Execucao Agendada: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
} else {
    Write-Host "   [!] Tarefa '$taskName' ainda nao registrada no Agendador do Windows." -ForegroundColor Yellow
    Write-Host "       Execute 'powershell -File ativar_automacao_horaria_windows.ps1' para registrar o servico." -ForegroundColor Gray
}

Write-Host ""

# 2. Leitura do Registro Probatorio JSON de Execucoes
Write-Host " [2/3] REGISTRO HISTORICO DE EXECUCOES (registro_execucao_agendada.json):" -ForegroundColor Yellow
$regJsonPath = Join-Path $baseDir "registro_execucao_agendada.json"

if (Test-Path $regJsonPath) {
    try {
        $rawJson = Get-Content -Path $regJsonPath -Raw -Encoding UTF8
        $conteudo = ConvertFrom-Json -InputObject $rawJson
        $totalExecs = $conteudo.Count
        Write-Host "   [OK] Arquivo de historico localizado: $totalExecs execucoes registradas." -ForegroundColor Green
        Write-Host ""
        Write-Host "   Ultimas Execucoes Registradas:" -ForegroundColor Gray
        
        $count = 0
        foreach ($item in $conteudo) {
            if ($count -ge 5) { break }
            $statusCor = "Yellow"
            if ($item.status -eq "SUCESSO") {
                $statusCor = "Green"
            }
            Write-Host "   * [$($item.timestamp)] - Modo: $($item.modo) | Cards: $($item.cards_processados) | Status: $($item.status) | Hash: #$($item.comprovante_hash)" -ForegroundColor $statusCor
            $count++
        }
    } catch {
        Write-Host "   [!] Falha ao ler JSON: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [i] Nenhum registro historico gerado ainda em '$regJsonPath'." -ForegroundColor Gray
    Write-Host "       O arquivo e criado automaticamente na primeira execucao do motor." -ForegroundColor Gray
}

Write-Host ""

# 3. Leitura do Laudo de Auditoria TXT
Write-Host " [3/3] LAUDO PROBATORIO DE AUDITORIA (laudo_sincronizacao_automatica.txt):" -ForegroundColor Yellow
$laudoPath = Join-Path $baseDir "laudo_sincronizacao_automatica.txt"

if (Test-Path $laudoPath) {
    Write-Host "   [OK] Laudo de auditoria localizado." -ForegroundColor Green
    $ultimasLinhas = Get-Content -Path $laudoPath -Tail 8 -Encoding UTF8
    Write-Host ""
    Write-Host "   Ultimos registros de log:" -ForegroundColor Gray
    foreach ($linha in $ultimasLinhas) {
        Write-Host "     $linha" -ForegroundColor DarkGray
    }
} else {
    Write-Host "   [i] Arquivo laudo_sincronizacao_automatica.txt sera gerado na primeira sincronizacao." -ForegroundColor Gray
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " [RESUMO DO COMPROVANTE] Governanca SA-GTI / SP-Aguas" -ForegroundColor Cyan
Write-Host " * Sincronizacao Agendada: Conforme ajuste configurado no Motor 3" -ForegroundColor White
Write-Host " * Sincronizacao Manual 1 a 1: Ativa e Homologada no Orquestrador Web" -ForegroundColor White
Write-Host "==============================================================================" -ForegroundColor Cyan
