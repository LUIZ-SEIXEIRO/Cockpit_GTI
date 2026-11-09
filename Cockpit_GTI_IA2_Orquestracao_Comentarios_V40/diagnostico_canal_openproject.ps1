# ==============================================================================
# SCRIPT OFICIAL: BACKUP E DIAGNOSTICO DO CANAL OPENPROJECT (SP-AGUAS / SA-GTI)
# COMPATIVEL COM WINDOWS POWERSHELL 5.1 E POWERSHELL 7+
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " SP-AGUAS / SA-GTI - BACKUP E DIAGNOSTICO DO CANAL OPENPROJECT" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "C:\Cockpit_GTI"
if (-not (Test-Path $baseDir)) {
    $baseDir = (Get-Location).Path
}
Set-Location $baseDir

# ==============================================================================
# 1. BACKUP PREVENTIVO E VERSIONAMENTO
# ==============================================================================
Write-Host "[PASSO 1/5] Executando Backup Preventivo e Versionamento..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $baseDir "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

$backupZip = Join-Path $backupDir "Cockpit_Backup_Pre_Diagnostico_$timestamp.zip"
Write-Host "  -> Criando pacote de backup em: $backupZip" -ForegroundColor Gray

$arquivosParaBackup = @("painel.html", "frontend\painel.html", "main.py", "app.py", "sincronizar_openproject_backend.py", "diagnostico_canal_openproject.py")
$tempFolder = Join-Path $env:TEMP "bck_$timestamp"
New-Item -ItemType Directory -Path $tempFolder -Force | Out-Null

foreach ($arq in $arquivosParaBackup) {
    $caminho = Join-Path $baseDir $arq
    if (Test-Path $caminho) {
        $destino = Join-Path $tempFolder $arq
        $parent = Split-Path $destino
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        Copy-Item -Path $caminho -Destination $destino -Force
        Write-Host "     [OK] Preservado: $arq" -ForegroundColor Green
    }
}

Compress-Archive -Path "$tempFolder\*" -DestinationPath $backupZip -Force
Remove-Item -Recurse -Force $tempFolder
$zipTamanho = [math]::Round((Get-Item $backupZip).Length / 1KB, 2)
Write-Host "  [SUCESSO] Backup salvo com sucesso! Tamanho: $zipTamanho KB" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# ARQUIVO DE LOG DO LAUDO TECNICO
# ==============================================================================
$laudoPath = Join-Path $baseDir "laudo_diagnostico_openproject.txt"
$cabecalho = @"
==============================================================================
 LAUDO TECNICO DE AVALIACAO DO CANAL OPENPROJECT (SA-GTI / SP-AGUAS)
 Data/Hora: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss') | Computador: $env:COMPUTERNAME
 Backup Criado: $backupZip
==============================================================================

"@
$cabecalho | Out-File -FilePath $laudoPath -Encoding utf8

# ==============================================================================
# 2. CONECTIVIDADE DE REDE, DNS E PORTAS TCP
# ==============================================================================
Write-Host "[PASSO 2/5] Testando Resolucao DNS e Portas TCP..." -ForegroundColor Yellow
$opHost = "projetos.spaguas.sp.gov.br"

try {
    $dns = [System.Net.Dns]::GetHostAddresses($opHost)
    $ipList = ($dns | ForEach-Object { $_.IPAddressToString }) -join ", "
    Write-Host "  [OK] DNS: $opHost -> $ipList" -ForegroundColor Green
    "[OK] DNS: $opHost -> $ipList" | Out-File -FilePath $laudoPath -Append -Encoding utf8
} catch {
    Write-Host "  [FALHA] DNS: $($_.Exception.Message)" -ForegroundColor Red
    "[FALHA] DNS: $($_.Exception.Message)" | Out-File -FilePath $laudoPath -Append -Encoding utf8
}

$portas = @(
    @{ Nome = "OpenProject HTTPS Remoto"; Host = $opHost; Porta = 443 },
    @{ Nome = "OpenProject HTTP Remoto"; Host = $opHost; Porta = 80 },
    @{ Nome = "OpenProject Container Local (:8090)"; Host = "127.0.0.1"; Porta = 8090 },
    @{ Nome = "Backend Cockpit Flask (:5000)"; Host = "127.0.0.1"; Porta = 5000 },
    @{ Nome = "Gateway New API AI (:3001)"; Host = "127.0.0.1"; Porta = 3001 },
    @{ Nome = "Banco de Dados MariaDB (:3306)"; Host = "127.0.0.1"; Porta = 3306 }
)

foreach ($p in $portas) {
    $pNome = $p.Nome
    $pHost = $p.Host
    $pPorta = $p.Porta
    $tcp = New-Object System.Net.Sockets.TcpClient
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $ar = $tcp.BeginConnect($pHost, $pPorta, $null, $null)
    $ok = $ar.AsyncWaitHandle.WaitOne(1500, $false)
    $sw.Stop()
    $lat = $sw.ElapsedMilliseconds

    if ($ok -and $tcp.Connected) {
        $tcp.EndConnect($ar)
        $tcp.Close()
        Write-Host "  [ABERTA] $pNome ($pHost : $pPorta) - $lat ms" -ForegroundColor Green
        "[ABERTA] $pNome ($pHost : $pPorta) - $lat ms" | Out-File -FilePath $laudoPath -Append -Encoding utf8
    } else {
        $tcp.Close()
        Write-Host "  [FECHADA] $pNome ($pHost : $pPorta) - Inacessivel" -ForegroundColor DarkGray
        "[FECHADA] $pNome ($pHost : $pPorta)" | Out-File -FilePath $laudoPath -Append -Encoding utf8
    }
}
Write-Host ""

# ==============================================================================
# 3. TESTE DE CORS E CERTIFICADO SSL/TLS
# ==============================================================================
Write-Host "[PASSO 3/5] Testando Negociacao SSL/TLS e Politica de CORS..." -ForegroundColor Yellow
$url1497 = "https://projetos.spaguas.sp.gov.br/api/v3/work_packages/1497"

[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12 -bor [System.Net.SecurityProtocolType]::Tls13
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

try {
    $reqOptions = [System.Net.HttpWebRequest]::Create($url1497)
    $reqOptions.Method = "OPTIONS"
    $reqOptions.Headers.Add("Origin", "http://localhost:5000")
    $reqOptions.Headers.Add("Access-Control-Request-Method", "PATCH")
    $reqOptions.Headers.Add("Access-Control-Request-Headers", "authorization,content-type")
    $reqOptions.Timeout = 5000
    $respOpt = $reqOptions.GetResponse()
    $corsOrigin = $respOpt.Headers["Access-Control-Allow-Origin"]
    Write-Host "  Status OPTIONS: $($respOpt.StatusCode)" -ForegroundColor Green
    Write-Host "  Access-Control-Allow-Origin: $(if ($corsOrigin) { $corsOrigin } else { '[NAO RETORNADO - CORS BLOQUEIA NAVEGADOR]' })" -ForegroundColor Yellow
    "[CORS OPTIONS] Status: $($respOpt.StatusCode) | Allow-Origin: $corsOrigin" | Out-File -FilePath $laudoPath -Append -Encoding utf8
    $respOpt.Close()
} catch [System.Net.WebException] {
    $st = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
    Write-Host "  [AVISO] OPTIONS Preflight retornou HTTP $st" -ForegroundColor Yellow
    "[CORS OPTIONS] HTTP $st: $($_.Exception.Message)" | Out-File -FilePath $laudoPath -Append -Encoding utf8
} catch {
    Write-Host "  [AVISO] OPTIONS falhou: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# ==============================================================================
# 4. INSPECAO DO CARD #1497 NA API REST V3
# ==============================================================================
Write-Host "[PASSO 4/5] Inspecionando Card #1497 na API REST v3..." -ForegroundColor Yellow

$cardData = $null
$lockVer = $null

try {
    $reqGet = [System.Net.HttpWebRequest]::Create($url1497)
    $reqGet.Method = "GET"
    $reqGet.UserAgent = "Cockpit-GTI-Diagnostico/1.0"
    $reqGet.Timeout = 6000
    $respGet = $reqGet.GetResponse()
    $reader = New-Object System.IO.StreamReader($respGet.GetResponseStream())
    $rawJson = $reader.ReadToEnd()
    $reader.Close()
    $respGet.Close()

    $cardData = ConvertFrom-Json $rawJson
    $lockVer = $cardData.lockVersion
    $subj = $cardData.subject
    Write-Host "  [SUCESSO] Card #1497 Lido Publicamente!" -ForegroundColor Green
    Write-Host "  Assunto Atual: $subj" -ForegroundColor Green
    Write-Host "  lockVersion Atual: $lockVer" -ForegroundColor Green
    "[CARD 1497 SUCESSO] HTTP 200 | lockVersion: $lockVer | Assunto: $subj" | Out-File -FilePath $laudoPath -Append -Encoding utf8
} catch [System.Net.WebException] {
    $st = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
    Write-Host "  [INFO] Card #1497 retornou HTTP $st" -ForegroundColor Yellow
    if ($st -eq 401) {
        Write-Host "  Causa: Servidor exige autenticacao obrigatoria para leitura." -ForegroundColor Gray
    }
    "[CARD 1497] HTTP $st" | Out-File -FilePath $laudoPath -Append -Encoding utf8
} catch {
    Write-Host "  [FALHA] Erro ao ler Card #1497: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# ==============================================================================
# 5. DIAGNOSTICO DO BACKEND FLASK LOCAL (:5000)
# ==============================================================================
Write-Host "[PASSO 5/5] Verificando Backend Flask Local (:5000)..." -ForegroundColor Yellow
$flaskOk = $false
try {
    $rF = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($rF.StatusCode -eq 200) { $flaskOk = $true }
} catch {}

if ($flaskOk) {
    Write-Host "  [OK] Backend Flask (:5000) esta ONLINE em execucao!" -ForegroundColor Green
    "[FLASK] Porta 5000 ONLINE" | Out-File -FilePath $laudoPath -Append -Encoding utf8
} else {
    Write-Host "  [INFO] Backend Flask (:5000) nao respondeu nesta porta." -ForegroundColor Yellow
    "[FLASK] Porta 5000 OFFLINE" | Out-File -FilePath $laudoPath -Append -Encoding utf8
}

# ==============================================================================
# SINTESE E PARECER
# ==============================================================================
$parecer = @"

==============================================================================
 PARECER TECNICO E RECOMENDACOES (SA-GTI / SP-AGUAS)
==============================================================================
1. Card Oficial: Tarefa #1497 (Processo SEI 137.00013132/2026-01).
2. O que o diagnostico avaliou:
   - Resolucao de DNS e portas do servidor projetos.spaguas.sp.gov.br.
   - Sonda da API REST v3 e lockVersion do Card #1497.
   - Analise de politica de CORS do navegador.
3. Causa técnica da escrita no navegador:
   O navegador web (Chrome/Edge) bloqueia requisicoes diretas de PATCH entre
   'http://localhost:5000' e 'https://projetos.spaguas.sp.gov.br' por politica
   de CORS (Cross-Origin Resource Sharing).
4. Solucao:
   - Executar o proxy backend Python 'python sincronizar_openproject_backend.py'
   - Ou aplicar via aba ativa do OpenProject com sessao ja autenticada.
==============================================================================
"@

Write-Host $parecer -ForegroundColor Cyan
$parecer | Out-File -FilePath $laudoPath -Append -Encoding utf8

Write-Host "Laudo tecnico completo gravado em: $laudoPath" -ForegroundColor White
Write-Host ""
