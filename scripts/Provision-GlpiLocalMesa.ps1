#Requires -Version 7.0
<#
.SYNOPSIS
    Provisiona no GLPI LOCAL (http://localhost:8088) o projeto "Cockpit GTI — Mesa de Trabalho"
    e, opcionalmente, tarefas de projeto listadas em um arquivo JSON.

.DESCRIPTION
    - Somente GLPI local: a URL e fixa e nao e configuravel. Nunca usa variaveis de producao e nunca le o arquivo de ambiente.
    - Autenticacao: OAuth2 "password" grant (recomendado para scripts em html/resources/api_doc.MD,
      "Authentication"/"Password Grant"), endpoint POST /api.php/token, escopo "api".
      Segredos sao pedidos com Read-Host -AsSecureString e nunca impressos.
    - Padrao = PREVIEW (somente GET, e o POST do token). Nada e criado sem -Apply
      e sem confirmacao digitada pelo operador.
    - Idempotente: projeto de mesmo nome na entidade informada nao e duplicado; tarefas de mesmo
      nome no projeto sao ignoradas. Mais de um projeto igual interrompe a execucao.

.PARAMETER EntityId
    ID numerico de uma entidade EXISTENTE no GLPI local (nao e inventado; e verificado por GET).

.PARAMETER TasksFile
    JSON opcional: array de objetos {"name": "...", "comment": "..."}; "name" obrigatorio.

.PARAMETER Apply
    Executa as criacoes (POST) apos confirmacao explicita. Sem -Apply apenas pre-visualiza.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateRange(0, [int]::MaxValue)][int]$EntityId,
    [string]$TasksFile,
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:GlpiLocalOrigin = 'http://localhost:8088'
$script:TokenUrl = "$script:GlpiLocalOrigin/api.php/token"
$script:ApiBase = "$script:GlpiLocalOrigin/api.php/v2"
$script:ProjectName = 'Cockpit GTI — Mesa de Trabalho'
$script:TimeoutSec = 30
$script:KnownSecrets = [System.Collections.Generic.List[string]]::new()

function Assert-GlpiLocalUrl {
    param([Parameter(Mandatory)][string]$Url)
    $uri = $null
    if (-not [Uri]::TryCreate($Url, [UriKind]::Absolute, [ref]$uri) -or
        $uri.Scheme -ne 'http' -or $uri.Host -ne 'localhost' -or $uri.Port -ne 8088 -or
        $uri.UserInfo -or -not ($uri.AbsolutePath -like '/api.php/*')) {
        throw 'URL recusada: somente http://localhost:8088/api.php/ (GLPI local) e permitido.'
    }
}

function Remove-GlpiSecret {
    param([AllowNull()][string]$Text)
    if ([string]::IsNullOrEmpty($Text)) { return '' }
    foreach ($s in $script:KnownSecrets) {
        if ($s) { $Text = $Text.Replace($s, '[REDACTED]') }
    }
    $Text = $Text -replace '(?i)bearer\s+[A-Za-z0-9\-\._~\+/]+=*', '[REDACTED]'
    return $Text -replace '(?i)(access_token|client_secret|password|refresh_token)"?\s*[:=]\s*"?[^"&,\s}]+', '$1=[REDACTED]'
}

function ConvertFrom-SecureStringPlain {
    param([Parameter(Mandatory)][securestring]$Secure)
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
    try { return [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
    finally { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

# Unica funcao que faz I/O de rede (ponto de mock nos testes). Nunca segue redirecionamentos.
function Invoke-GlpiHttp {
    param(
        [Parameter(Mandatory)][ValidateSet('GET', 'POST')][string]$Method,
        [Parameter(Mandatory)][string]$Url,
        [hashtable]$Headers = @{},
        $Body,
        [string]$ContentType
    )
    Assert-GlpiLocalUrl -Url $Url
    $params = @{
        Method                = $Method
        Uri                   = $Url
        Headers               = $Headers
        MaximumRedirection    = 0
        TimeoutSec            = $script:TimeoutSec
        SkipHttpErrorCheck    = $true
        SkipCertificateCheck  = $false
    }
    if ($null -ne $Body) { $params.Body = $Body }
    if ($ContentType) { $params.ContentType = $ContentType }
    $r = Invoke-WebRequest @params
    $headersOut = @{}
    foreach ($k in $r.Headers.Keys) { $headersOut[$k] = ($r.Headers[$k] -join ',') }
    [pscustomobject]@{ StatusCode = [int]$r.StatusCode; Content = [string]$r.Content; Headers = $headersOut }
}

function Invoke-GlpiApi {
    param(
        [Parameter(Mandatory)][ValidateSet('GET', 'POST')][string]$Method,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Token,
        [hashtable]$Body
    )
    $args2 = @{
        Method  = $Method
        Url     = "$script:ApiBase$Path"
        Headers = @{ Authorization = ('Bearer ' + $Token); Accept = 'application/json' }
    }
    if ($Body) {
        $args2.Body = ($Body | ConvertTo-Json -Depth 5 -Compress)
        $args2.ContentType = 'application/json'
    }
    $resp = Invoke-GlpiHttp @args2
    Write-Host ("HTTP {0} {1} -> {2}" -f $Method, ($Path -replace '\?.*$', ''), $resp.StatusCode)
    if ($resp.StatusCode -lt 200 -or $resp.StatusCode -ge 300) {
        throw ("Falha na API do GLPI local (HTTP {0}) em {1} {2}." -f $resp.StatusCode, $Method, ($Path -replace '\?.*$', ''))
    }
    $parsed = $null
    if ($resp.Content) { try { $parsed = $resp.Content | ConvertFrom-Json -Depth 20 } catch { $parsed = $null } }
    [pscustomobject]@{ Status = $resp.StatusCode; Data = $parsed; Headers = $resp.Headers }
}

function Get-GlpiAccessToken {
    param(
        [Parameter(Mandatory)][string]$ClientId,
        [Parameter(Mandatory)][securestring]$ClientSecret,
        [Parameter(Mandatory)][string]$Username,
        [Parameter(Mandatory)][securestring]$Password
    )
    $secret = ConvertFrom-SecureStringPlain $ClientSecret
    $pass = ConvertFrom-SecureStringPlain $Password
    $script:KnownSecrets.Add($secret); $script:KnownSecrets.Add($pass)
    $form = @{ grant_type = 'password'; client_id = $ClientId; client_secret = $secret
               username = $Username; password = $pass; scope = 'api' }
    $resp = Invoke-GlpiHttp -Method POST -Url $script:TokenUrl -Body $form -ContentType 'application/x-www-form-urlencoded'
    Write-Host "HTTP POST /api.php/token -> $($resp.StatusCode)"
    if ($resp.StatusCode -ne 200) { throw "Autenticacao OAuth recusada (HTTP $($resp.StatusCode))." }
    $json = $resp.Content | ConvertFrom-Json
    if (-not $json.access_token) { throw 'Resposta OAuth sem access_token.' }
    $script:KnownSecrets.Add([string]$json.access_token)
    return [string]$json.access_token
}

function Read-GlpiTasksFile {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw 'Arquivo de tarefas nao encontrado.' }
    try { $items = Get-Content -LiteralPath $Path -Raw -Encoding utf8 | ConvertFrom-Json -NoEnumerate }
    catch { throw 'Arquivo de tarefas nao e JSON valido.' }
    if ($items -isnot [array] -or $items.Count -eq 0) { throw 'Arquivo de tarefas deve ser um array JSON nao vazio.' }
    $seen = @{}
    $out = foreach ($i in $items) {
        $name = if ($i -is [pscustomobject]) { $i.PSObject.Properties['name']?.Value } else { $null }
        if ($name -isnot [string] -or [string]::IsNullOrWhiteSpace($name) -or $name.Length -gt 255) {
            throw 'Cada tarefa precisa de "name" (texto nao vazio, ate 255 caracteres).'
        }
        $comment = $i.PSObject.Properties['comment']?.Value
        if ($null -ne $comment -and $comment -isnot [string]) { throw '"comment" deve ser texto.' }
        $extra = @($i.PSObject.Properties.Name | Where-Object { $_ -notin 'name', 'comment' })
        if ($extra.Count) { throw 'Campos nao suportados no arquivo de tarefas (use apenas name e comment).' }
        if ($seen.ContainsKey($name.Trim())) { throw 'Nomes de tarefa duplicados no arquivo.' }
        $seen[$name.Trim()] = $true
        [pscustomobject]@{ name = $name.Trim(); comment = $comment }
    }
    return @($out)
}

function Get-ItemsFromResponse {
    param($Data)
    if ($null -eq $Data) { return @() }
    return @($Data)
}

function Find-GlpiProject {
    param([string]$Token, [int]$EntityId)
    $filter = [Uri]::EscapeDataString("name==`"$script:ProjectName`"")
    $r = Invoke-GlpiApi -Method GET -Path "/Project?filter=$filter&limit=100" -Token $Token
    # Comparacao exata local (o filtro do servidor nao e a unica barreira)
    return @(Get-ItemsFromResponse $r.Data | Where-Object {
            $_.name -ceq $script:ProjectName -and $_.entity -and [int]$_.entity.id -eq $EntityId -and -not $_.PSObject.Properties['is_deleted']?.Value })
}

function Find-GlpiProjectTaskNames {
    param([string]$Token, [int]$ProjectId)
    $filter = [Uri]::EscapeDataString("project.id==$ProjectId")
    $r = Invoke-GlpiApi -Method GET -Path "/Project/Task?filter=$filter&limit=500" -Token $Token
    return @(Get-ItemsFromResponse $r.Data | ForEach-Object { [string]$_.name })
}

function Confirm-GlpiOperator {
    param([Parameter(Mandatory)][string]$Expected, [Parameter(Mandatory)][string]$Prompt)
    $answer = Read-Host $Prompt
    return ($answer -ceq $Expected)
}

function Get-CreatedId {
    param($Response)
    if ($Response.Data -and $Response.Data.PSObject.Properties['id']) { return [int]$Response.Data.id }
    $loc = $Response.Headers['Location']
    if ($loc -and $loc -match '/(\d+)/?$') { return [int]$Matches[1] }
    throw 'Criacao sem ID identificavel na resposta; verifique manualmente no GLPI local.'
}

function Invoke-GlpiMesaProvisioning {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][int]$EntityId,
        [string]$TasksFile,
        [switch]$Apply,
        [Parameter(Mandatory)][string]$Token
    )
    $tasks = @()
    if ($TasksFile) { $tasks = Read-GlpiTasksFile -Path $TasksFile }

    # Entidade deve existir; so o ID e exibido.
    Invoke-GlpiApi -Method GET -Path "/Administration/Entity/$EntityId" -Token $Token | Out-Null
    Write-Host "Entidade ${EntityId}: encontrada."

    $existing = @(Find-GlpiProject -Token $Token -EntityId $EntityId)
    if ($existing.Count -gt 1) {
        throw "Conflito: $($existing.Count) projetos com o mesmo nome na entidade $EntityId (IDs: $((($existing | ForEach-Object id) -join ', '))). Resolva manualmente."
    }
    $projectId = $null
    $createProject = $false
    if ($existing.Count -eq 1) {
        $projectId = [int]$existing[0].id
        Write-Host "Projeto ja existe (ID $projectId); nao sera duplicado."
    } else {
        $createProject = $true
        Write-Host 'Projeto nao existe; seria criado.'
    }

    $pendingTasks = @()
    if ($tasks.Count) {
        $known = if ($projectId) { @(Find-GlpiProjectTaskNames -Token $Token -ProjectId $projectId) } else { @() }
        $pendingTasks = @($tasks | Where-Object { $_.name -cnotin $known })
        Write-Host "Tarefas no arquivo: $($tasks.Count); novas: $($pendingTasks.Count); ja existentes: $($tasks.Count - $pendingTasks.Count)."
    }

    $summary = [ordered]@{ Mode = 'Preview'; ProjectId = $projectId; ProjectCreated = $false; TasksCreated = 0 }
    $nothing = (-not $createProject) -and $pendingTasks.Count -eq 0
    if (-not $Apply) {
        Write-Host 'PREVIEW: nenhuma alteracao feita. Use -Apply para criar apos confirmacao.'
        return [pscustomobject]$summary
    }
    if ($nothing) {
        Write-Host 'Nada a criar.'
        $summary.Mode = 'Apply'
        return [pscustomobject]$summary
    }

    Write-Host "Sera criado: projeto=$([int]$createProject), tarefas=$($pendingTasks.Count), entidade=$EntityId (GLPI local)."
    if (-not (Confirm-GlpiOperator -Expected ([string]$EntityId) -Prompt "Digite o ID da entidade ($EntityId) para confirmar")) {
        throw 'Confirmacao da entidade nao confere. Nada foi criado.'
    }
    if (-not (Confirm-GlpiOperator -Expected 'CONFIRMAR' -Prompt 'Digite CONFIRMAR para executar as criacoes no GLPI local')) {
        throw 'Operacao cancelada pelo operador. Nada foi criado.'
    }

    $summary.Mode = 'Apply'
    if ($createProject) {
        $r = Invoke-GlpiApi -Method POST -Path '/Project' -Token $Token -Body @{
            name = $script:ProjectName; entity = @{ id = $EntityId } }
        $projectId = Get-CreatedId $r
        $summary.ProjectId = $projectId
        $summary.ProjectCreated = $true
        Write-Host "Projeto criado (ID $projectId)."
    }
    foreach ($t in $pendingTasks) {
        $body = @{ name = $t.name; project = @{ id = $projectId } }
        if ($t.comment) { $body.comment = $t.comment }
        $r = Invoke-GlpiApi -Method POST -Path '/Project/Task' -Token $Token -Body $body
        $summary.TasksCreated++
        Write-Host "Tarefa criada (ID $(Get-CreatedId $r))."
    }
    return [pscustomobject]$summary
}

# Execucao principal (nao roda quando o arquivo e carregado por dot-source, ex.: Pester)
if ($MyInvocation.InvocationName -ne '.') {
    try {
        Assert-GlpiLocalUrl -Url $script:TokenUrl
        Assert-GlpiLocalUrl -Url $script:ApiBase
        Write-Host 'Destino fixo: GLPI LOCAL http://localhost:8088 (producao nunca e usada).'
        $clientId = Read-Host 'OAuth client_id (cliente do GLPI local)'
        $clientSecret = Read-Host 'OAuth client_secret' -AsSecureString
        $username = Read-Host 'Usuario da conta tecnica (permissoes minimas)'
        $password = Read-Host 'Senha da conta tecnica' -AsSecureString
        if (-not $clientId -or -not $username -or $clientSecret.Length -eq 0 -or $password.Length -eq 0) {
            throw 'Configuracao ausente: client_id, client_secret, usuario e senha sao obrigatorios.'
        }
        $token = Get-GlpiAccessToken -ClientId $clientId -ClientSecret $clientSecret -Username $username -Password $password
        $result = Invoke-GlpiMesaProvisioning -EntityId $EntityId -TasksFile $TasksFile -Apply:$Apply -Token $token
        $result | Format-List
    } catch {
        [Console]::Error.WriteLine((Remove-GlpiSecret ([string]$_.Exception.Message)))
        exit 1
    }
}
