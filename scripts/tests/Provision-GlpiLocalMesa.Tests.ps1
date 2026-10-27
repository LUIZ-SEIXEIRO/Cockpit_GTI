BeforeAll {
    $script:Script = Join-Path $PSScriptRoot '..' 'Provision-GlpiLocalMesa.ps1'
    . $script:Script -EntityId 1
    function New-Resp($code, $obj = $null, $headers = @{}) {
        [pscustomobject]@{ StatusCode = $code; Content = ($obj ? ($obj | ConvertTo-Json -Depth 8 -Compress) : ''); Headers = $headers }
    }
}

Describe 'URL fixa' {
    It 'aceita somente localhost:8088/api.php' {
        { Assert-GlpiLocalUrl 'http://localhost:8088/api.php/v2/Project' } | Should -Not -Throw
    }
    It 'recusa hosts nao locais, outras portas, https e credenciais na URL' -ForEach @(
        'http://glpi.exemplo.gov.br/api.php/v2', 'http://127.0.0.1:8088/api.php/v2', 'http://localhost:80/api.php/v2',
        'https://localhost:8088/api.php/v2', 'http://user:pw@localhost:8088/api.php/v2', 'http://localhost:8088/apirest.php',
        'http://localhost:8088.evil.com/api.php/v2') {
        { Assert-GlpiLocalUrl $_ } | Should -Throw
    }
    It 'nao expoe parametro de URL nem le GLPI_PROD_* / .env' {
        (Get-Command $script:Script).Parameters.Keys | Should -Not -Contain 'BaseUrl'
        $src = Get-Content $script:Script -Raw
        $src | Should -Not -Match 'GLPI_PROD'
        $src | Should -Not -Match '\.env'
    }
}

Describe 'Sanitizacao' {
    It 'remove segredos conhecidos e tokens Bearer' {
        $script:KnownSecrets.Add('s3gredo-xyz')
        $t = Remove-GlpiSecret 'erro s3gredo-xyz Authorization: ****** "access_token":"zzz"'
        $t | Should -Not -Match 's3gredo-xyz|abc\.def|zzz'
    }
}

Describe 'Arquivo de tarefas' {
    BeforeEach { $script:f = Join-Path $TestDrive 't.json' }
    It 'le tarefas validas' {
        '[{"name":"A","comment":"x"},{"name":"B"}]' | Set-Content $script:f
        (Read-GlpiTasksFile $script:f).Count | Should -Be 2
    }
    It 'recusa JSON invalido, vazio, sem nome, campo extra e duplicado' -ForEach @(
        '{bad', '[]', '[{"comment":"x"}]', '[{"name":"A","id":5}]', '[{"name":"A"},{"name":"A"}]') {
        $_ | Set-Content $script:f
        { Read-GlpiTasksFile $script:f } | Should -Throw
    }
}

Describe 'Provisionamento' {
    BeforeEach {
        $script:calls = [System.Collections.Generic.List[object]]::new()
        $script:projects = @()
        Mock Invoke-GlpiHttp {
            $script:calls.Add("$Method $Url")
            if ($Method -eq 'POST') { return New-Resp 201 @{ id = 77 } }
            if ($Url -like '*/Administration/Entity/*') { return New-Resp 200 @{ id = 5 } }
            if ($Url -like '*/Project/Task*' -and $Method -eq 'GET') { return New-Resp 200 @(@{ name = 'A' }) }
            if ($Url -like '*/Project?*') { return New-Resp 200 $script:projects }
            New-Resp 404
        }
    }
    It 'preview nao faz POST nem pede confirmacao' {
        Mock Read-Host { throw 'nao deveria perguntar' }
        $r = Invoke-GlpiMesaProvisioning -EntityId 5 -Token 't'
        $r.Mode | Should -Be 'Preview'
        $script:calls | Where-Object { $_ -like 'POST*' } | Should -BeNullOrEmpty
    }
    It 'Apply sem confirmacao correta nao cria nada' {
        Mock Read-Host { 'nao' }
        { Invoke-GlpiMesaProvisioning -EntityId 5 -Token 't' -Apply } | Should -Throw
        $script:calls | Where-Object { $_ -like 'POST*' } | Should -BeNullOrEmpty
    }
    It 'Apply confirmado cria projeto e somente tarefas novas' {
        Mock Read-Host { if ($Prompt -like '*entidade*') { '5' } else { 'CONFIRMAR' } }
        $f = Join-Path $TestDrive 't2.json'
        '[{"name":"A"},{"name":"B"}]' | Set-Content $f
        $script:projects = @()
        $r = Invoke-GlpiMesaProvisioning -EntityId 5 -Token 't' -Apply -TasksFile $f
        $r.ProjectCreated | Should -BeTrue
        $r.TasksCreated | Should -Be 2
    }
    It 'idempotente: projeto existente na entidade nao e duplicado' {
        Mock Read-Host { if ($Prompt -like '*entidade*') { '5' } else { 'CONFIRMAR' } }
        $script:projects = @(@{ id = 9; name = $script:ProjectName; entity = @{ id = 5 } })
        $r = Invoke-GlpiMesaProvisioning -EntityId 5 -Token 't' -Apply
        $r.ProjectCreated | Should -BeFalse
        $r.ProjectId | Should -Be 9
        $script:calls | Where-Object { $_ -like 'POST*' } | Should -BeNullOrEmpty
    }
    It 'projetos duplicados interrompem a execucao' {
        $script:projects = @(@{ id = 9; name = $script:ProjectName; entity = @{ id = 5 } },
            @{ id = 10; name = $script:ProjectName; entity = @{ id = 5 } })
        { Invoke-GlpiMesaProvisioning -EntityId 5 -Token 't' -Apply } | Should -Throw '*Conflito*'
    }
    It 'erro HTTP nao vaza corpo da resposta' {
        Mock Invoke-GlpiHttp { New-Resp 500 @{ detail = 'dados-pessoais' } }
        $e = { Invoke-GlpiApi -Method GET -Path '/Project' -Token 'tok' } | Should -Throw -PassThru
        $e.Exception.Message | Should -Not -Match 'dados-pessoais'
    }
}

Describe 'Token' {
    It 'usa password grant e nao imprime segredos' {
        Mock Invoke-GlpiHttp { New-Resp 200 @{ access_token = 'TOK123'; token_type = 'Bearer' } }
        $sec = ConvertTo-SecureString 'segredo-a' -AsPlainText -Force
        $out = Get-GlpiAccessToken -ClientId 'c' -ClientSecret $sec -Username 'u' -Password $sec 6>&1 | Out-String
        $out | Should -Not -Match 'segredo-a'
        Should -Invoke Invoke-GlpiHttp -ParameterFilter { $Url -eq 'http://localhost:8088/api.php/token' -and $Body.grant_type -eq 'password' }
    }
    It 'falha sem expor o corpo quando recusado' {
        Mock Invoke-GlpiHttp { New-Resp 401 @{ error = 'x' } }
        $sec = ConvertTo-SecureString 'a' -AsPlainText -Force
        { Get-GlpiAccessToken -ClientId 'c' -ClientSecret $sec -Username 'u' -Password $sec } | Should -Throw '*HTTP 401*'
    }
}
