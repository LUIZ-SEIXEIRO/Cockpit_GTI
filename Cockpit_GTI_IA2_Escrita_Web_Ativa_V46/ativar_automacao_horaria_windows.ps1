# ==============================================================================
# ATIVADOR OFICIAL DA SINCRONIZAÇÃO AUTOMÁTICA AGENDADA NO WINDOWS (SA-GTI)
# Registra uma Tarefa Agendada no Windows conforme a parametrização do Cockpit
# de forma 100% invisível em segundo plano (via pythonw.exe, sem janela preta).
# ==============================================================================

param (
    [string]$Frequencia = "Horaria" # "Horaria" ou "Diaria03"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " ⏰ SP-ÁGUAS / SA-GTI — ATIVADOR DE SINCRONIZAÇÃO AGENDADA (MOTOR 3)" -ForegroundColor Cyan
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

Write-Host "[*] Interpretador Python: $pythonw" -ForegroundColor Gray
Write-Host "[*] Script de Sincronizacao: $scriptPython" -ForegroundColor Gray
Write-Host ""

# 2. Criar/Atualizar Tarefa Agendada no Windows Task Scheduler
$taskName = "CockpitGTI_Sincronizacao_Horaria_OpenProject"

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null

    $action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$scriptPython`"" -WorkingDirectory $baseDir

    if ($Frequencia -eq "Diaria03") {
        $trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
        $descFreq = "Diário às 03:00 em segundo plano"
    } else {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)
        $descFreq = "A cada 1 hora em segundo plano"
    }

    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Sincronizacao Automatica do Cockpit GTI com OpenProject 14 (SP-Aguas SA-GTI)" -Force | Out-Null

    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "[OK] Tarefa Agendada '$taskName' ATIVADA COM SUCESSO!" -ForegroundColor Green
    Write-Host "     • Frequência: $descFreq" -ForegroundColor Green
    Write-Host "     • Modo: Invisível em segundo plano (pythonw.exe)" -ForegroundColor Green
    Write-Host "     • Próxima execução prevista: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
} catch {
    Write-Host "[AVISO] Tentativa via PowerShell falhou, tentando schtasks: $($_.Exception.Message)" -ForegroundColor Yellow
    $cmdSch = "schtasks /create /tn `"$taskName`" /tr `"\`"$pythonw\`" \`"$scriptPython\`"`" /sc hourly /mo 1 /ru `"$env:USERNAME`" /f"
    Invoke-Expression $cmdSch
    Write-Host "[OK] Tarefa Agendada criada via schtasks!" -ForegroundColor Green
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " [CONCLUÍDO] Automação agendada ativa no Windows!" -ForegroundColor Cyan
Write-Host " O Cockpit atualizará o OpenProject de forma autônoma conforme o agendamento." -ForegroundColor White
Write-Host " Para auditar e comprovar a qualquer momento, execute:" -ForegroundColor White
Write-Host " powershell -File comprovar_sincronizacao_agendada.ps1" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Cyan
