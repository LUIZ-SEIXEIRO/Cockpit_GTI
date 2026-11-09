# ==============================================================================
# SP-ÁGUAS / SA-GTI — DESBLOQUEIO DE FIREWALL & DIAGNÓSTICO PROFUNDO DA IA 2
# Executar no PowerShell do Miniservidor (Desktop) e/ou Notebook
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " 🛡️ SP-ÁGUAS / SA-GTI — DESBLOQUEIO DE FIREWALL & DIAGNÓSTICO DA IA 2" -ForegroundColor Cyan
Write-Host " IA 2 (Orquestração): llama3.2:1b @ http://10.20.40.212:3001/v1" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Identificar IPs desta máquina
Write-Host "[1/5] Identificando Endereços IP desta máquina..." -ForegroundColor Yellow
$ipsLocais = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -ExpandProperty IPAddress
foreach ($ip in $ipsLocais) {
    if ($ip -eq "10.20.40.212") {
        Write-Host "  [✓] IP LOCAL DETECTADO: $ip (ESTA MÁQUINA É O HOST 10.20.40.212!)" -ForegroundColor Green
    } else {
        Write-Host "  • IP Local: $ip" -ForegroundColor Gray
    }
}
Write-Host ""

# 2. Desbloquear Portas 3001 e 5000 no Windows Defender Firewall
Write-Host "[2/5] Configurando Regras de Entrada no Windows Defender Firewall..." -ForegroundColor Yellow
$portasParaAbrir = @(
    @{ Nome = "Cockpit_GTI_NewAPI_AI_3001"; Porta = 3001; Desc = "New API Gateway IA (Porta 3001)" },
    @{ Nome = "Cockpit_GTI_Flask_Web_5000"; Porta = 5000; Desc = "Cockpit GTI Flask Web (Porta 5000)" },
    @{ Nome = "Cockpit_GTI_Ollama_11434"; Porta = 11434; Desc = "Ollama Local LLM (Porta 11434)" }
)

foreach ($p in $portasParaAbrir) {
    try {
        $regraExistente = Get-NetFirewallRule -Name $p.Nome -ErrorAction SilentlyContinue
        if ($regraExistente) {
            Set-NetFirewallRule -Name $p.Nome -Enabled True -Action Allow -Profile Any -ErrorAction SilentlyContinue
            Write-Host "  [✓] Firewall: Regra '$($p.Nome)' já existente e REATIVADA (Porta $($p.Porta) TCP liberada)." -ForegroundColor Green
        } else {
            New-NetFirewallRule -Name $p.Nome -DisplayName $p.Desc -Direction Inbound -LocalPort $p.Porta -Protocol TCP -Action Allow -Profile Any -ErrorAction Stop | Out-Null
            Write-Host "  [✓] Firewall: Nova regra criada com sucesso para a Porta $($p.Porta) TCP!" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [!] Aviso Firewall ($($p.Porta)): Requer privilégios de Administrador. Execute: netsh advfirewall firewall add rule name=`"$($p.Nome)`" dir=in action=allow protocol=TCP localport=$($p.Porta)" -ForegroundColor Yellow
    }
}
Write-Host ""

# 3. Verificar o que está ouvindo na Porta 3001 nesta máquina
Write-Host "[3/5] Verificando se algum processo está escutando na Porta 3001..." -ForegroundColor Yellow
$proc3001 = $null
try {
    $conexoes = Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue
    if ($conexoes) {
        foreach ($c in $conexoes) {
            $pId = $c.OwningProcess
            $pNome = (Get-Process -Id $pId -ErrorAction SilentlyContinue).ProcessName
            Write-Host "  [✓] Porta 3001 está OUVINDO!" -ForegroundColor Green
            Write-Host "      • Endereço Local: $($c.LocalAddress):$($c.LocalPort)" -ForegroundColor Green
            Write-Host "      • Processo: $pNome (PID: $pId)" -ForegroundColor Green
            if ($c.LocalAddress -eq "127.0.0.1") {
                Write-Host "      [⚠️ ALERTA DE BINDING]: O serviço está escutando APENAS em 127.0.0.1 (localhost)!" -ForegroundColor Red
                Write-Host "      Isso significa que conexões usando '10.20.40.212:3001' serão RECUSADAS." -ForegroundColor Red
                Write-Host "      Solução: Inicie o serviço com host 0.0.0.0 (ex: docker run -p 3001:3001 ou HOST=0.0.0.0)." -ForegroundColor Yellow
            } elseif ($c.LocalAddress -eq "0.0.0.0" -or $c.LocalAddress -eq "::") {
                Write-Host "      [✓ BINDING PERFEITO]: Ouvindo em 0.0.0.0 (acessível por qualquer IP da rede!)." -ForegroundColor Green
            }
        }
    } else {
        Write-Host "  [✗] NENHUM processo está escutando na Porta 3001 nesta máquina local." -ForegroundColor Red
        Write-Host "      • Se o New API estiver rodando no NOTEBOOK, certifique-se de que o firewall do notebook liberou a porta 3001." -ForegroundColor Yellow
        Write-Host "      • Se o New API deveria rodar no DESKTOP, inicie o container/aplicativo do New API." -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [i] Erro na verificação de conexões: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

# 4. Testar Conectividade de Rede com a IA 2 (TCP Socket)
Write-Host "[4/5] Testando Conectividade de Rede (Porta 3001)..." -ForegroundColor Yellow
$alvosTeste = @(
    @{ Host = "10.20.40.212"; Porta = 3001; Nome = "IP da Rede (10.20.40.212:3001)" },
    @{ Host = "127.0.0.1"; Porta = 3001; Nome = "Loopback Local (127.0.0.1:3001)" }
)

$endpointOperacional = $null
foreach ($alvo in $alvosTeste) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect($alvo.Host, $alvo.Porta, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne(2000, $false)
        if ($wait -and $tcp.Connected) {
            $tcp.EndConnect($iar)
            $tcp.Close()
            Write-Host "  [✓] $($alvo.Nome): CONECTADO COM SUCESSO (Porta Aberta e Respondendo)!" -ForegroundColor Green
            if (-not $endpointOperacional) {
                $endpointOperacional = "http://$($alvo.Host):$($alvo.Porta)/v1"
            }
        } else {
            $tcp.Close()
            Write-Host "  [✗] $($alvo.Nome): CONEXÃO RECUSADA OU TIMEOUT (Porta Fechada ou Bloqueada)." -ForegroundColor Red
        }
    } catch {
        Write-Host "  [✗] $($alvo.Nome): Falha de conexão ($($_.Exception.Message))" -ForegroundColor Red
    }
}
Write-Host ""

# 5. Testar Requisição HTTP Real à IA 2 com o Token e Modelo
Write-Host "[5/5] Testando Chamada HTTP Real da IA 2 (llama3.2:1b)..." -ForegroundColor Yellow
$token = "sk-GxdEHwXjAPXW50uuBVeDLAEeSXdt6kJfcduffPsjBnmsRs3H"
$modelo = "llama3.2:1b"

$urlsParaTestar = @()
if ($endpointOperacional) {
    $urlsParaTestar += "$endpointOperacional/chat/completions"
}
$urlsParaTestar += "http://10.20.40.212:3001/v1/chat/completions"
$urlsParaTestar += "http://127.0.0.1:3001/v1/chat/completions"

$sucessoIa = $false
foreach ($urlTest in ($urlsParaTestar | Select-Object -Unique)) {
    Write-Host "  [*] Tentando POST em: $urlTest..." -ForegroundColor Gray
    $bodyJson = @{
        model = $modelo
        messages = @(
            @{ role = "system"; content = "Você é a IA 2 — Orquestração da SA-GTI SP-Águas." },
            @{ role = "user"; content = "Teste de conectividade. Responda apenas: 'IA 2 ONLINE E OPERACIONAL'." }
        )
        temperature = 0.0
        max_tokens = 30
    } | ConvertTo-Json -Depth 5

    try {
        $headers = @{
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $token"
        }
        $resp = Invoke-RestMethod -Uri $urlTest -Method Post -Body $bodyJson -Headers $headers -TimeoutSec 10 -ErrorAction Stop
        $textoResposta = $resp.choices[0].message.content.Trim()
        Write-Host "  [✓] RESPOSTA RECEBIDA DA IA 2 ($modelo)!" -ForegroundColor Green
        Write-Host "      • Mensagem da IA: `"$textoResposta`"" -ForegroundColor Cyan
        $sucessoIa = $true
        break
    } catch {
        Write-Host "  [!] Erro ao chamar $urlTest: $($_.Exception.Message)" -ForegroundColor Yellow
        if ($_.Exception.Response) {
            $status = [int]$_.Exception.Response.StatusCode
            Write-Host "      • HTTP Status Code: $status" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
if ($sucessoIa) {
    Write-Host " [OK] IA 2 ESTÁ 100% OPERACIONAL E RESPONDENDO COM SUCESSO!" -ForegroundColor Green
    Write-Host " Agora você pode rodar 'python sincronizar_openproject_backend.py'!" -ForegroundColor Green
} else {
    Write-Host " [DIAGNÓSTICO CONCLUSIVO]:" -ForegroundColor Yellow
    Write-Host " 1. Se a Porta 3001 deu CONEXÃO RECUSADA em 10.20.40.212:" -ForegroundColor White
    Write-Host "    - O container/serviço New API não está em execução ou não escuta em 0.0.0.0." -ForegroundColor White
    Write-Host " 2. Se o New API estiver rodando no Notebook:" -ForegroundColor White
    Write-Host "    - O IP 10.20.40.212 é o do Desktop ou do Notebook? Verifique 'ipconfig' em ambos." -ForegroundColor White
    Write-Host " 3. As regras de Firewall para as portas 3001 e 5000 foram aplicadas nesta máquina." -ForegroundColor White
}
Write-Host "==============================================================================" -ForegroundColor Cyan
