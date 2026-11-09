# ==============================================================================
# SP-AGUAS / SA-GTI - DESBLOQUEIO DE FIREWALL E DIAGNOSTICO DA IA 2
# Compativel 100% com PowerShell 5.1 e Windows 11 (ASCII Puro / Sem Erros de BOM)
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " SP-AGUAS / SA-GTI - DESBLOQUEIO DE FIREWALL E TESTE DA IA 2" -ForegroundColor Cyan
Write-Host " IA 2 (Orquestracao): llama3.2:1b @ http://10.20.40.212:3001/v1" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Identificar IPs desta maquina
Write-Host "[1/5] Identificando Enderecos IP desta maquina..." -ForegroundColor Yellow
$ipsLocais = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -ExpandProperty IPAddress
foreach ($ip in $ipsLocais) {
    if ($ip -eq "10.20.40.212") {
        Write-Host "  [OK] IP LOCAL: $ip (ESTA MAQUINA E O HOST 10.20.40.212!)" -ForegroundColor Green
    } else {
        Write-Host "  * IP Local detectado: $ip" -ForegroundColor Gray
    }
}
Write-Host ""

# 2. Configurar Regras de Entrada no Windows Defender Firewall
Write-Host "[2/5] Configurando Regras de Entrada no Windows Defender Firewall..." -ForegroundColor Yellow
$regras = @(
    @{ Nome = "Cockpit_GTI_NewAPI_3001"; Porta = "3001" },
    @{ Nome = "Cockpit_GTI_Flask_5000"; Porta = "5000" },
    @{ Nome = "Cockpit_GTI_Ollama_11434"; Porta = "11434" }
)

foreach ($r in $regras) {
    $n = $r.Nome
    $p = $r.Porta
    try {
        $cmdNetsh = "netsh advfirewall firewall add rule name=`"$n`" dir=in action=allow protocol=TCP localport=$p"
        Invoke-Expression $cmdNetsh | Out-Null
        Write-Host "  [OK] Firewall: Porta $p TCP liberada com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "  [i] Aviso ao configurar regra para porta $p" -ForegroundColor Gray
    }
}
Write-Host ""

# 3. Verificar se a porta 3001 esta escutando
Write-Host "[3/5] Verificando se algum processo escuta na Porta 3001..." -ForegroundColor Yellow
try {
    $ns = netstat -ano | findstr :3001
    if ($ns) {
        Write-Host "  [OK] Processo detectado escutando na Porta 3001:" -ForegroundColor Green
        foreach ($linha in ($ns -split "`n")) {
            if ($linha.Trim()) { Write-Host "      $linha" -ForegroundColor Green }
        }
    } else {
        Write-Host "  [X] NENHUM processo escutando na Porta 3001 nesta maquina local." -ForegroundColor Red
        Write-Host "      Se o New API estiver rodando no Notebook, execute este script tambem no Notebook." -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [i] Erro ao executar netstat" -ForegroundColor Gray
}
Write-Host ""

# 4. Testar Conexao TCP Socket na Porta 3001
Write-Host "[4/5] Testando Conectividade de Rede (Porta 3001)..." -ForegroundColor Yellow
$hostsTeste = @("10.20.40.212", "127.0.0.1")
$epAtivo = $null

foreach ($h in $hostsTeste) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect($h, 3001, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne(2000, $false)
        if ($wait -and $tcp.Connected) {
            $tcp.EndConnect($iar)
            $tcp.Close()
            Write-Host "  [OK] Conexao com $h na porta 3001: CONECTADO COM SUCESSO!" -ForegroundColor Green
            if (-not $epAtivo) { $epAtivo = "http://" + $h + ":3001/v1" }
        } else {
            $tcp.Close()
            Write-Host "  [X] Conexao com $h na porta 3001: RECUSADA OU TIMEOUT." -ForegroundColor Red
        }
    } catch {
        Write-Host "  [X] Falha ao testar $h na porta 3001" -ForegroundColor Red
    }
}
Write-Host ""

# 5. Testar Requisicao HTTP Real a IA 2 com Token Real
Write-Host "[5/5] Testando Chamada HTTP a IA 2 (llama3.2:1b)..." -ForegroundColor Yellow
$token = "sk-GxdEHwXjAPXW50uuBVeDLAEeSXdt6kJfcduffPsjBnmsRs3H"
$modelo = "llama3.2:1b"

$urlChamada = if ($epAtivo) { "$epAtivo/chat/completions" } else { "http://10.20.40.212:3001/v1/chat/completions" }
Write-Host "  [*] Testando URL: $urlChamada..." -ForegroundColor Gray

$bodyObj = @{
    model = $modelo
    messages = @(
        @{ role = "system"; content = "Voce e a IA 2 da SA-GTI SP-Aguas." },
        @{ role = "user"; content = "Responda apenas: IA 2 ONLINE E OPERACIONAL." }
    )
    temperature = 0.0
    max_tokens = 30
}
$bodyStr = $bodyObj | ConvertTo-Json -Depth 4

$iaOk = $false
try {
    $hdr = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $token"
    }
    $r = Invoke-RestMethod -Uri $urlChamada -Method Post -Body $bodyStr -Headers $hdr -TimeoutSec 12 -ErrorAction Stop
    $respTexto = $r.choices[0].message.content.Trim()
    Write-Host "  [OK] RESPOSTA RECEBIDA DA IA 2 ($modelo)!" -ForegroundColor Green
    Write-Host "      Mensagem: `"$respTexto`"" -ForegroundColor Cyan
    $iaOk = $true
} catch {
    Write-Host "  [!] Chamada HTTP retornou erro: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
if ($iaOk) {
    Write-Host " [SUCESSO TOTAL] A IA 2 ESTA OPERACIONAL E RESPONDENDO COM O TOKEN REAL!" -ForegroundColor Green
    Write-Host " Agora voce pode rodar: python sincronizar_openproject_backend.py" -ForegroundColor Green
} else {
    Write-Host " [DIAGNOSTICO]:" -ForegroundColor Yellow
    Write-Host " 1. Se a porta 3001 deu conexao recusada, verifique em qual maquina o New API esta aberto." -ForegroundColor White
    Write-Host " 2. Se o New API estiver no Notebook, execute 'ipconfig' no notebook para ver o IP real." -ForegroundColor White
    Write-Host " 3. Voce tambem pode executar: python desbloquear_e_testar_ia.py" -ForegroundColor Green
}
Write-Host "==============================================================================" -ForegroundColor Cyan
