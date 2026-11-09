# ==============================================================================
# ATIVADOR OFICIAL DA SINCRONIZAÇÃO AUTOMÁTICA HORÁRIA NO WINDOWS (SA-GTI)
# Registra uma Tarefa Agendada no Windows para executar a cada 1 hora
# de forma 100% invisível em segundo plano (via pythonw.exe, sem janela preta).
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " ⏰ SP-ÁGUAS / SA-GTI — ATIVADOR DE SINCRONIZAÇÃO HORÁRIA AUTOMÁTICA" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "C:\Cockpit_GTI"
if (-not (Test-Path $baseDir)) {
    $baseDir = (Get-Location).Path
}

$scriptPython = Join-Path $baseDir "sincronizar_openproject_backend.py"
if (-not (Test-Path $scriptPython)) {
    Write-Host "[ERRO] Script $scriptPython nao encontrado." -ForegroundColor Red
    exit 1
}

# 1. Localizar executável pythonw.exe (modo sem janela) ou python.exe
$pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $pythonw) {
    $pythonw = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
}
if (-not $pythonw) {
    $pythonw = "python.exe"
}

Write-Host "[*] Interpretador Python identificado: $pythonw" -ForegroundColor Gray
Write-Host "[*] Script de Sincronizacao: $scriptPython" -ForegroundColor Gray
Write-Host ""

# 2. Criar/Atualizar Tarefa Agendada no Windows Task Scheduler
$taskName = "CockpitGTI_Sincronizacao_Horaria_OpenProject"

try {
    # Remove se já existia para recriar limpo
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null

    $action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$scriptPython`"" -WorkingDirectory $baseDir
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Sincronizacao Automatica Horaria do Cockpit GTI com o OpenProject (SP-Aguas SA-GTI)" -Force | Out-Null

    Write-Host "[OK] Tarefa Agendada '$taskName' CRIADA COM SUCESSO!" -ForegroundColor Green
    Write-Host "     • Frequência: A cada 1 hora (60 minutos) em segundo plano." -ForegroundColor Green
    Write-Host "     • Modo: Invisível (sem abrir janelas na tela)." -ForegroundColor Green
    Write-Host "     • Próxima execução programada: $(Get-Date (Get-Date).AddMinutes(1) -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Tentativa via PowerShell nativo falhou: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "[*] Tentando via utilitário schtasks.exe..." -ForegroundColor Gray
    
    $cmdSch = "schtasks /create /tn `"$taskName`" /tr `"\`"$pythonw\`" \`"$scriptPython\`"`" /sc hourly /mo 1 /ru `"$env:USERNAME`" /f"
    Invoke-Expression $cmdSch
    Write-Host "[OK] Tarefa Agendada criada via schtasks!" -ForegroundColor Green
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " [CONCLUÍDO] Automação horária ativada no Windows com sucesso!" -ForegroundColor Cyan
Write-Host " O Cockpit atualizará os cards do OpenProject automaticamente a cada 1 hora," -ForegroundColor White
Write-Host " mesmo se o navegador estiver fechado!" -ForegroundColor White
Write-Host "==============================================================================" -ForegroundColor Cyan
