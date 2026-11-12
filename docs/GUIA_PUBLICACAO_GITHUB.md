# 🐙 Guia Oficial de DevOps, Implantação Docker Desktop, Governança Git & Ciclo de Vida no GitHub — Cockpit GTI 360°

**Manual de Operação de Infraestrutura (DevSecOps), Orquestração de Containers, Versionamento Git, Gestão de Modelos de IA e Procedimentos de Continuidade (DRP)**  
**Autarquia:** Agência de Águas do Estado de São Paulo (**SP-Águas**)  
**Unidade Gestora:** Superintendência de Administração — Gerência de Tecnologia da Informação (**SA-GTI**)  
**Responsável Técnico e Governança:** Luiz Antonio Seixeiro  
**Repositório Oficial:** [github.com/LUIZ-SEIXEIRO/Cockpit_GTI](https://github.com/LUIZ-SEIXEIRO/Cockpit_GTI)  
**Versão da Infraestrutura:** 11.0 Oficial (Stack Docker Unificada `cockpit-gti`)

---

## 📑 Sumário de DevOps & Governança

1. [Objetivo deste Guia e Público-Alvo](#1-objetivo-deste-guia-e-público-alvo)
2. [Estrutura Canônica do Repositório Oficial](#2-estrutura-canônica-do-repositório-oficial)
3. [Guia de Implantação do Zero em Nova Máquina (Clone + Docker Desktop)](#3-guia-de-implantação-do-zero-em-nova-máquina-clone--docker-desktop)
4. [Arquitetura e Operação da Stack Docker Unificada (`cockpit-gti`)](#4-arquitetura-e-operação-da-stack-docker-unificada-cockpit-gti)
5. [Gestão de Modelos Locais (Ollama `:11434`) e Canais/Tokens (New API `:3001`)](#5-gestão-de-modelos-locais-ollama-11434-e-canaistokens-new-api-3001)
6. [Fluxo de Trabalho Git, Branches, Commits Semânticos e Resolução de Conflitos](#6-fluxo-de-trabalho-git-branches-commits-semânticos-e-resolução-de-conflitos)
7. [Política de Higienização, Segurança e `.gitignore` Corporativo](#7-política-de-higienização-segurança-e-gitignore-corporativo)
8. [Plano de Continuidade de Negócios, Backup 3-2-1-1-0 e Migração de Ambiente](#8-plano-de-continuidade-de-negócios-backup-3-2-1-1-0-e-migração-de-ambiente)
9. [Prontuário de Comandos Rápidos (Cheat Sheet PowerShell & Docker)](#9-prontuário-de-comandos-rápidos-cheat-sheet-powershell--docker)
10. [Aceite, Implantação Gradual e Rollback](#10-aceite-implantação-gradual-e-rollback)

---

## 1. Objetivo deste Guia e Público-Alvo

Este documento estabelece o padrão operacional para **implantação**, **manutenção de containers Docker**, **versionamento de código no GitHub** e **gestão do ciclo de vida (DevSecOps)** da plataforma **Cockpit GTI 360°** da **SP-Águas (SA-GTI)**.

Ele foi elaborado de forma didática e passo a passo para atender:
* **Equipes de Desenvolvimento e Arquitetura (SA-GTI / DGD):** Como modificar o código-fonte (`painel.html` e `main.py`), testar localmente, reconstruir a imagem Docker e publicar atualizações na branch `main` sem conflitos;
* **Equipes de Infraestrutura, Redes e Suporte (SA-GTI / DIF):** Como administrar a stack unificada no Docker Desktop, gerenciar os volumes de 60+ GB dos modelos do Ollama, configurar o gateway New API e aplicar a política de backup 3-2-1-1-0;
* **Gestores e Auditores Técnicos:** Como verificar a rastreabilidade de releases, a integridade do código e a conformidade com a **Lei Federal nº 14.133/2021**, **LGPD** e **Súmula 269 do TCU**.

---

## 2. Estrutura Canônica do Repositório Oficial

O repositório [LUIZ-SEIXEIRO/Cockpit_GTI](https://github.com/LUIZ-SEIXEIRO/Cockpit_GTI) segue uma estrutura enxuta, higienizada e livre de arquivos temporários ou binários de banco de dados:

```text
Cockpit_GTI/
├── .dockerignore                          # Exclusão de volumes e caches no build da imagem Docker
├── .gitignore                             # Blindagem contra arquivos temporários, .zip, logs e segredos
├── Dockerfile                             # Receita oficial da imagem Python 3.11-slim do Backend (:5000)
├── docker-compose.yml                     # Orquestrador da Stack Unificada (Backend + New API + Ollama)
├── main.py                                # Servidor Backend Flask principal e Proxy REST (/api/v1/*)
├── painel.html                            # Interface SPA Mestre (4 Eixos, 15 Abas, 23 Sub-abas)
├── requirements.txt                       # Dependências Python enxutas (Flask, requests, urllib3, PyMySQL)
├── README.md                              # Cartão de visitas executivo e técnico do projeto no GitHub
├── backend/
│   ├── main.py                            # Espelho sincronizado do servidor Flask para execução modular
│   ├── config_pool_ias.json               # Parametrização persistente dos 3 Slots de IA (7B/14B/1.5B)
│   ├── sincronizar_openproject_backend.py # Conector CLI e agendador REST API v3 do OpenProject
│   └── atualizar_e_reiniciar_cockpit.py   # Utilitário de manutenção e hot-reload do backend
├── frontend/
│   └── painel.html                        # Espelho sincronizado da interface SPA para rotas estáticas
├── data/
│   ├── processos.json                     # Base estruturada dos 179 processos administrativos SEI!
│   ├── glpi_producao_cache.json           # Cache de chamados ITSM e inventário CMDB (443 PCs) do GLPI 10
│   ├── registro_execucao_agendada.json    # Trilha de auditoria das sincronizações horárias
│   └── mapa_sei_op_manual.json            # Mapeamento relacional entre Processos SEI e Work Packages OP
├── docs/
│   ├── MANUAL_DO_USUARIO.md               # Manual operacional e executivo completo (Aba por Aba)
│   ├── DOCUMENTACAO_TECNICA.md            # Arquitetura de software, DOM, APIs REST e integrações
│   └── GUIA_PUBLICACAO_GITHUB.md          # Este manual de DevOps, Docker Desktop e Governança Git
└── scripts/
    ├── iniciar_cockpit.ps1                # Script de inicialização automatizada para Windows PowerShell
    ├── iniciar_cockpit.bat                # Atalho executável de inicialização para Windows (Batch)
    ├── iniciar_cockpit.sh                 # Script de inicialização para ambientes Linux / WSL
    └── atualizar_painel_windows.ps1       # Utilitário de sincronização rápida de artefatos no Windows
```

---

## 3. Guia de Implantação do Zero em Nova Máquina (Clone + Docker Desktop)

Caso seja necessário instalar o Cockpit GTI em um novo notebook corporativo ou servidor de homologação/produção, siga os **4 passos abaixo**:

### Pré-requisitos do Ambiente:
1. **Git para Windows** instalado (`git --version`);
2. **Docker Desktop** instalado e em execução com motor **WSL2** habilitado (`docker --version`);
3. Conexão de rede local ou **Tailscale VPN** ativa (caso consuma APIs corporativas da SP-Águas).

### Passo a Passo no PowerShell:

```powershell
# 1. Acesse a unidade de disco desejada (ex: H:\ ou C:\)
Set-Location H:\

# 2. Clone o repositório oficial do GitHub
git clone https://github.com/LUIZ-SEIXEIRO/Cockpit_GTI.git H:\Cockpit_GTI

# 3. Entre na pasta do projeto
Set-Location H:\Cockpit_GTI

# 4. Crie o volume persistente do New API (necessário apenas na primeira instalação)
docker volume create new-api-data

# 5. Construa a imagem e suba toda a stack unificada em segundo plano (-d)
docker compose up -d --build

# 6. Verifique se os 3 containers estão ativos (Up)
docker compose ps
```

### Endereços de Acesso Imediato após o `docker compose up -d`:
* **🌊 Cockpit GTI 360° (Aplicação Principal):** [http://localhost:5000/](http://localhost:5000/)
* **🤖 Console de Governança New API (Tokens e Canais de IA):** [http://localhost:3001/](http://localhost:3001/)
* **🦙 Endpoint Nativo do Motor Ollama:** `http://localhost:11434/v1`

---

## 4. Arquitetura e Operação da Stack Docker Unificada (`cockpit-gti`)

Para manter o **Docker Desktop** limpo e organizado, toda a infraestrutura do projeto é agrupada sob um único projeto Compose (`name: cockpit-gti`).

### Arquivo `docker-compose.yml` Oficial Explicado:

```yaml
name: cockpit-gti

services:
  # 1. Motor de Inferência Local de Grandes Modelos de Linguagem (LLMs)
  ollama:
    image: ollama/ollama:latest
    container_name: cockpit-gti-ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - H:/spaguas/ia-multiagente/ollama_data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=24h

  # 2. Gateway OpenAI-Compatível para Governança de Chaves, Cotas e Grupos
  new-api:
    image: calciumion/new-api:latest
    container_name: cockpit-gti-newapi
    restart: unless-stopped
    ports:
      - "3001:3000"
    volumes:
      - new-api-data:/data
    depends_on:
      - ollama

  # 3. Servidor Web SPA e Proxy REST de Integração da SA-GTI
  cockpit-backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cockpit-gti-backend
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - PORT=5000
      - PYTHONUNBUFFERED=1
    depends_on:
      - new-api
      - ollama

volumes:
  new-api-data:
    external: true
```

### Por que o `cockpit-backend` utiliza `build` com `COPY . .` em vez de Volume Bind Mount no disco `H:\`?
No Windows com Docker Desktop (WSL2), unidades de disco secundárias ou externas (como `H:\`) frequentemente sofrem falhas de montagem de diretório no subsistema Linux ou não propagam alterações de arquivos em tempo real. Ao empacotar o código-fonte diretamente dentro da imagem via `Dockerfile` (`COPY . .`), garantimos que:
1. O container **`cockpit-gti-backend` nunca caia em loop de reinicialização** por falta do arquivo `main.py`;
2. A aplicação inicie em menos de 1 segundo mesmo após reiniciar o Windows;
3. Sempre que você editar o código local (`main.py` ou `painel.html`), basta executar `docker compose up -d --build` para atualizar o container em poucos segundos.

---

## 5. Gestão de Modelos Locais (Ollama `:11434`) e Canais/Tokens (New API `:3001`)

### 5.1. Como Gerenciar Modelos no Container `cockpit-gti-ollama`

Todos os modelos ficam salvos na pasta física `H:\spaguas\ia-multiagente\ollama_data`, preservando mais de 60 GB de modelos mesmo que o container seja recriado.

```powershell
# Listar todos os modelos atualmente instalados no Ollama
ollama list
# (Ou executando diretamente dentro do container):
docker exec -it cockpit-gti-ollama ollama list

# Baixar um novo modelo homologado para a SA-GTI
docker exec -it cockpit-gti-ollama ollama pull qwen2.5:14b
docker exec -it cockpit-gti-ollama ollama pull qwen2.5-coder:7b

# Remover um modelo antigo para liberar espaço em disco
docker exec -it cockpit-gti-ollama ollama rm nome-do-modelo
```

### 5.2. Checklist de Liberação de Modelos no Gateway New API (`http://localhost:3001/`)

Sempre que quiser utilizar um modelo no Cockpit GTI via New API, verifique as **3 travas de segurança** do gateway para evitar erros `HTTP 403 Forbidden` ou `HTTP 503 Service Unavailable`:

1. **Aba Canais (*Channels*):**
   * Edite o canal do **Ollama**.
   * Certifique-se de que o **Grupo** selecionado no canal inclui **`SP - ÁGUAS`** (ou o grupo ao qual seu token pertence).
   * No campo **Modelos**, digite o nome idêntico ao do `ollama list` (ex: `qwen2.5:14b` e `qwen2.5-coder:7b`) e **pressione a tecla `Enter`** após cada nome para que se transforme em uma etiqueta (*tag*) azul antes de clicar em **Salvar**.
2. **Aba Tokens (*Access Tokens*):**
   * Edite o token utilizado no Cockpit (ou crie um novo token no grupo **`SP - ÁGUAS`**).
   * Na opção de modelos permitidos, marque **Todos os Modelos** (*All Models*) ou inclua os novos modelos na lista permitida e clique em **Salvar**.
3. **Validação no Cockpit GTI (`http://localhost:5000/`):**
   * Acesse **⚙️ Configurações** ➔ **🤖 Pool de IAs**, informe o modelo e o endpoint `http://100.103.100.98:3001/v1`, clique em **⚡ Testar este Agente** (aguarde o selo **`🟢 OK`**) e clique em **💾 Salvar Configuração do Pool**.

---

## 6. Fluxo de Trabalho Git, Branches, Commits Semânticos e Resolução de Conflitos

### 6.1. Padrão Institucional de Commits Semânticos (Conventional Commits)

Para manter o histórico de versionamento claro e auditável pelo TCE-SP e pela equipe técnica, utilize os prefixos padronizados:

| Prefixo | Quando Utilizar | Exemplo Prático no Projeto |
| :--- | :--- | :--- |
| **`feat:`** | Criação de nova funcionalidade, rota de API ou sub-aba visual. | `feat(ia): adicionar rota /api/v1/ia/testar_slot e normalizacao de endpoint` |
| **`fix:`** | Correção de erro em tela, falha de conectividade ou bug de cálculo. | `fix(glpi): corrigir filtro de chamados pendentes na sub-aba operacional` |
| **`docs:`** | Criação ou expansão de manuais na pasta `docs/` ou `README.md`. | `docs: atualizar manual do usuario, documentacao tecnica e guia github v11` |
| **`chore:`** / **`build:`** | Ajustes em `Dockerfile`, `docker-compose.yml` ou `.gitignore`. | `feat(docker): unificar stack multi-ia e backend em docker-compose oficial` |
| **`refactor:`** | Melhoria de estrutura de código sem alterar o comportamento final. | `refactor(painel): organizar funcoes de troca de sub-abas do eixo 2` |

### 6.2. Rotina Padrão para Atualizar o GitHub após Alterações Locais

Sempre que alterar arquivos de código ou documentação em `H:\Cockpit_GTI`, execute esta sequência segura no PowerShell:

```powershell
Set-Location H:\Cockpit_GTI

# 1. Mantém os arquivos espelhados sincronizados (raiz <-> subpastas)
Copy-Item "main.py" "backend\main.py" -Force
Copy-Item "painel.html" "frontend\painel.html" -Force -ErrorAction SilentlyContinue

# 2. Descarta eventuais alterações automáticas em logs binários do MariaDB local
git restore volumes_docker/ -ErrorAction SilentlyContinue

# 3. Verifica quais arquivos foram modificados
git status

# 4. Adiciona os arquivos ao pacote de commit (respeitando o .gitignore)
git add Dockerfile docker-compose.yml main.py backend/ frontend/ docs/ scripts/ README.md .gitignore .dockerignore

# 5. Registra o commit descritivo
git commit -m "docs: atualizar documentacao institucional completa (Manual, Arquitetura, DevOps e README)"

# 6. Sincroniza com o GitHub e envia para a branch principal (main)
git pull origin main --rebase
git push origin main
```

### 6.3. Como Resolver Conflitos de Merge ou Arquivos Não Rastreados (`Untracked Files`)

Caso o comando `git pull` exiba um aviso informando que arquivos locais seriam sobrescritos ou haja conflito entre branches:

```powershell
# Caso arquivos de log do MariaDB impeçam o pull:
git restore volumes_docker/

# Caso queira adotar a versão mais recente da sua branch local durante um merge/cherry-pick:
git checkout --theirs .
git add -A
git -c core.editor=true commit
git push origin main
```

---

## 7. Política de Higienização, Segurança e `.gitignore` Corporativo

Um repositório governamental de excelência **nunca deve conter** backups compactados (`.zip`), scripts de rascunho (`test_*`, `temp_*`), dumps pesados de bancos de dados (`ib_logfile0`, `*.ibd`) ou credenciais privadas em texto claro.

O arquivo `.gitignore` oficial na raiz do projeto bloqueia automaticamente:
* **Arquivos Compactados e Snapshots:** `*.zip`, `*.tar.gz`, `*.rar`, `*.7z`, `*.bak`, pasta `backups/` e `recovered/`;
* **Bancos de Dados e Volumes Locais:** `volumes_docker/`, `*.ibd`, `*.frm`, `ibdata*`, `ib_logfile*`;
* **Scripts Temporários de Depuração:** `test_*`, `temp_*`, `syntax_*`, `verify_*`, `auditar_*`, `dummy_*`, `patch_*`, `laudo_*.txt`;
* **Caches Python e Ambientes Virtuais:** `__pycache__/`, `*.pyc`, `.venv/`, `env/`;
* **Variáveis de Ambiente Sensíveis:** `.env`, `.env.local`, `*.key`, `*.pem`.

---

## 8. Plano de Continuidade de Negócios, Backup 3-2-1-1-0 e Migração de Ambiente

Em alinhamento com as diretrizes de resiliência da **Divisão de Infraestrutura (SA-GTI-DIF)**, a preservação do Cockpit GTI segue a **Regra 3-2-1-1-0**:

### Política de backup e itens de recuperação:

O backup deve usar a ferramenta institucional aprovada, destino criptografado e controle de acesso. Não copie `.env`, `data/config_pool_ias.local.json` nem dados de sessão para pastas genéricas, não criptografadas ou dentro do repositório. Registre a data, o responsável, os artefatos incluídos e o resultado de uma verificação de restauração. O volume de modelos Ollama pode ultrapassar dezenas de GB; classifique-o separadamente e confirme se é recuperável por nova aquisição antes de incluí-lo em cada snapshot.

Para a implantação, trate como itens distintos: código/commit, imagem anterior do backend, `.env` e pool privado, dados operacionais em `data/` e volume `new-api-data`. A restauração de estado com credenciais ou sessão SEI exige destino restrito, criptografia e autorização do responsável pelos dados; nunca use `docker compose down -v` como procedimento de rollback.

---

## 9. Prontuário de Comandos Rápidos (Cheat Sheet PowerShell & Docker)

| Operação Desejada | Comando Exato no PowerShell (`H:\Cockpit_GTI`) |
| :--- | :--- |
| **Subir toda a stack unificada** | `docker compose up -d` |
| **Atualizar o backend com aceite e rollback preparados** | Siga todos os gates e comandos da seção 10; não atualize produção diretamente por este cheat sheet. |
| **Ver status e portas dos 3 containers** | `docker compose ps` |
| **Parar toda a stack (sem perder dados)** | `docker compose stop` |
| **Iniciar novamente a stack parada** | `docker compose start` |
| **Ver logs do Backend Flask (:5000)** | `docker logs --tail 50 -f cockpit-gti-backend` |
| **Ver logs do Gateway New API (:3001)** | `docker logs --tail 50 -f cockpit-gti-newapi` |
| **Ver logs do Motor Ollama (:11434)** | `docker logs --tail 50 -f cockpit-gti-ollama` |
| **Testar Slot de IA via linha de comando** | `$h=@{Authorization="Bearer $env:API_TOKEN"}; Invoke-RestMethod -Uri "http://localhost:5000/api/v1/ia/testar_slot" -Method POST -Headers $h -ContentType "application/json" -Body '{"slot":"principal","endpoint":"","apiKey":"","model":"llama3.2:1b"}'` (carregue `API_TOKEN` no ambiente sem exibi-lo; o backend seleciona o endpoint padrão). |
| **Listar modelos liberados em uma API Key** | `curl.exe -s http://100.103.100.98:3001/v1/models -H "Authorization: Bearer SUA_CHAVE"` |

---

## 10. Aceite, Implantação Gradual e Rollback

### 10.1. Modelo de implantação e limites atuais

A stack atual executa um único backend, com `container_name` e portas fixas (`5000`, `3001` e `11434`). Ela não implementa balanceador, divisão percentual de tráfego nem canário azul/verde no mesmo host. Portanto, a implantação gradual deve avançar por **ambientes e gates**: validação técnica, homologação isolada, piloto autorizado e janela de produção. Para manter duas versões simultâneas, use outro host/VM com dados, portas e projeto Compose isolados; não duplique o arquivo Compose atual no mesmo Docker Desktop.

A autenticação do Cockpit ainda usa um token compartilhado, sem identidade individual. O piloto não pode ser tratado como segmentação por usuário dentro da aplicação: limite-o por ambiente, rede ou mecanismo institucional já aprovado. Não habilite uso institucional da IA antes de validar inferência real no provedor/modelo aprovado com dados sintéticos e critérios de grounding.

### 10.2. Gates objetivos de aceite

Cada gate precisa de evidência registrada no chamado/change da implantação. Falha em qualquer item significa **NO-GO**; não avance para o próximo ambiente.

| Gate | Evidência mínima para aprovar |
| :--- | :--- |
| **G0 — Código e rastreabilidade** | Mudança aprovada, SHA completo do commit registrado, revisão concluída e worktree de release sem alterações não aprovadas. CI e `python -m unittest discover -v tests` aprovados. |
| **G1 — Configuração e recuperação** | `docker compose config -q` sem erro; segredos carregados por canal protegido e sem impressão no console; imagem anterior identificada e exportada; backup de estado íntegro; RTO/RPO aprovados e restauração/rollback exercitados em homologação. |
| **G2 — Homologação isolada** | Backend `healthy`, página principal HTTP 200, dependências no estado esperado, autenticação/cabeçalhos/CORS verificados e nenhuma falha inesperada nos logs ou nas sondagens por 30 minutos. |
| **G3 — Fluxos funcionais** | Suíte automatizada aprovada; leitura de pool com chaves mascaradas; chamadas GLPI/OpenProject somente de leitura; fluxo de IA com prompt sintético, se o provedor estiver disponível; escrita de integração exercitada apenas em ambiente de teste com confirmação humana. Nenhum dado pessoal ou processo real em testes. |
| **G4 — Piloto e aceite** | Grupo autorizado e janela definidos; 30 minutos de observação inicial sem reinício do backend, `unhealthy`, 5xx inesperado, exposição de segredo ou incidente P1/P2; responsável funcional, operação e segurança registram o aceite ou as exceções. |

O teste do chat não substitui a homologação do parecer: valide separadamente respostas sem contexto, bloqueio de inconsistência e indisponibilidade do provedor. Se não houver modelo/provedor acessível, registre o gate de IA como **bloqueado**, sem converter a ausência de inferência em aprovação.

### 10.3. Preparação e preservação do rollback

Execute no PowerShell a partir do clone de release. O snapshot de imagem deve ser feito **antes** do build novo; se não houver imagem anterior nem um arquivo exportado verificável, a implantação de produção não está autorizada.

```powershell
$ErrorActionPreference = "Stop"
$releaseId = (git rev-parse --short=12 HEAD).Trim()
$imagemAtual = "cockpit-gti-cockpit-backend:main"
$imagemRollback = "cockpit-gti-cockpit-backend:rollback-$releaseId"
$destinoSeguro = $env:COCKPIT_ENCRYPTED_BACKUP_ROOT

if ([string]::IsNullOrWhiteSpace($destinoSeguro)) {
    throw "Defina COCKPIT_ENCRYPTED_BACKUP_ROOT para um destino institucional criptografado e restrito."
}
docker image inspect $imagemAtual *> $null
if ($LASTEXITCODE -ne 0) { throw "Imagem anterior não encontrada; interrompa e recupere uma versão aprovada." }
docker image tag $imagemAtual $imagemRollback
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar a tag de rollback." }
New-Item -ItemType Directory -Force -Path $destinoSeguro | Out-Null
docker save --output (Join-Path $destinoSeguro "backend-$releaseId.tar") $imagemRollback
if ($LASTEXITCODE -ne 0) { throw "Falha ao exportar a imagem anterior." }
Get-FileHash (Join-Path $destinoSeguro "backend-$releaseId.tar") -Algorithm SHA256
```

Armazene o SHA-256 e o SHA do código no registro da mudança, sem incluir tokens. Faça backup dos arquivos de estado e segredos com a ferramenta institucional aprovada; valide a recuperação antes da janela. Preserve separadamente `.env`, `data/config_pool_ias.local.json`, os dados necessários de `data/` e o volume `new-api-data`. Sessões SEI e outros dados sensíveis só podem ser incluídos quando houver necessidade, autorização, criptografia e controle de acesso explícitos. A pasta de modelos Ollama não precisa ser copiada a cada release se houver procedimento validado para recuperá-la.

### 10.4. Implantação progressiva

1. **Pré-produção:** use host/VM isolado, `.env` e estado de homologação próprios. Não conecte a stack de teste a serviços de produção com credenciais reais. Execute os gates G0–G3 e registre resultados.
2. **Piloto:** aprove formalmente o grupo, o ambiente, o responsável e a janela. Como não há roteamento por usuário, conduza o piloto em ambiente isolado ou por fronteira de rede aprovada; não anuncie uma porcentagem de canário que a arquitetura não implementa. Observe os indicadores e a experiência dos usuários por pelo menos um ciclo operacional acordado.
3. **Produção:** com os gates aprovados, registre o SHA a promover, confirme backup e imagem de rollback, avise a janela e execute:

```powershell
docker compose config -q
if ($LASTEXITCODE -ne 0) { throw "Compose inválido; implantação cancelada." }

docker compose build cockpit-backend
if ($LASTEXITCODE -ne 0) { throw "Build falhou; mantenha a versão atual." }

docker compose up -d --no-deps --force-recreate cockpit-backend
if ($LASTEXITCODE -ne 0) { throw "Atualização do backend falhou; iniciar rollback." }
```

O Compose declara healthcheck HTTP do backend em `http://127.0.0.1:5000/` (intervalo de 30 s, timeout de 5 s, 3 tentativas e período inicial de 20 s). Aguarde o estado `healthy`; não considere `Up` sozinho como aceite:

```powershell
$prazo = (Get-Date).AddMinutes(3)
do {
    $health = docker inspect --format='{{.State.Health.Status}}' cockpit-gti-backend 2>$null
    if ($LASTEXITCODE -eq 0 -and $health -eq "healthy") { break }
    Start-Sleep -Seconds 5
} while ((Get-Date) -lt $prazo)

if ($health -ne "healthy") { throw "Backend não ficou healthy; iniciar rollback." }
Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:5000/" -TimeoutSec 5 | Out-Null
docker compose ps
```

Faça sondagens autenticadas sem imprimir o token e sem executar escritas em GLPI/OpenProject/SEI. Use dados sintéticos no chat. Observe reinícios, saúde, códigos HTTP e eventos operacionais sem copiar corpos ou segredos para logs externos. Aumente o público somente após aprovação do gate G4.

### 10.5. Gatilhos e execução do rollback

**Rollback imediato:** exposição de segredo/dado pessoal, corrupção de estado, escrita indevida em sistema oficial, falha P1/P2 ou regressão de segurança. **Rollback após triagem curta:** backend permanece `unhealthy`, reinicia repetidamente, página/rotas essenciais não respondem, ou há 5xx inesperado persistente por mais de 5 minutos. IA indisponível bloqueia o aceite da funcionalidade de IA; não é motivo para mascarar erro como sucesso.

1. Interrompa a divulgação/uso da nova versão e preserve os logs necessários sob controle de acesso. Não apague volumes nem reverta dados automaticamente.
2. Se a tag local não estiver disponível, recupere o arquivo verificado antes da implantação; carregue a imagem e retag a versão aprovada:

```powershell
$releaseId = "<SHA-curto-registrado>"
$imagemRollback = "cockpit-gti-cockpit-backend:rollback-$releaseId"
$imagemAtual = "cockpit-gti-cockpit-backend:main"

# Somente se a imagem não estiver no Docker local:
# docker load --input (Join-Path $env:COCKPIT_ENCRYPTED_BACKUP_ROOT "backend-$releaseId.tar")

docker image inspect $imagemRollback *> $null
if ($LASTEXITCODE -ne 0) { throw "Imagem de rollback não encontrada; manter serviço isolado e acionar recuperação." }
docker image tag $imagemRollback $imagemAtual
if ($LASTEXITCODE -ne 0) { throw "Falha ao restaurar a tag aprovada." }
docker compose up -d --no-build --no-deps --force-recreate cockpit-backend
if ($LASTEXITCODE -ne 0) { throw "Falha ao recriar o backend anterior; manter incidente aberto." }
```

3. Confirme `healthy`, HTTP 200 na página, autenticação e os fluxos de leitura essenciais. Mantenha monitoramento por 30 minutos e registre horário, causa, SHA/imagem restaurados, impacto, evidências e aprovadores.
4. Restaure arquivos/volumes apenas se houver evidência de corrupção ou incompatibilidade de dados, após aprovação do responsável e verificação do backup. Prefira correção compatível para frente quando a reversão dos dados puder causar perda.

**Proibido como atalho de rollback:** `docker compose down -v`, `docker volume prune`, apagar `data/`, sobrescrever `.env` sem snapshot ou executar `git reset --hard`/`git checkout` no ambiente operacional. O rollback da aplicação deve trocar a imagem; o estado persistente é recuperado separadamente e com autorização.

### 10.6. Registro de aceite

O registro da mudança deve conter, no mínimo: ambiente e janela; SHA completo do commit e identificação da imagem; resultados dos gates G0–G4; hash do arquivo de imagem anterior; testes funcionais executados e dados sintéticos usados; evidência de saúde e observação; incidentes/exceções; decisão **GO/NO-GO**; responsáveis funcional, técnico, segurança e operação; e, se acionado, evidência do rollback e verificação de recuperação. Uma aprovação técnica não substitui aceite funcional ou autorização de produção.
