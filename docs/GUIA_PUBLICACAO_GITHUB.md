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

### Como fazer Backup Completo dos Dados Críticos da Plataforma:

```powershell
# Script rápido PowerShell para gerar backup datado dos arquivos de configuração e estado
$dataHoje = Get-Date -Format "yyyy-MM-dd_HHmm"
$pastaDestino = "H:\Backups_Cockpit_GTI\Snapshot_$dataHoje"
New-Item -ItemType Directory -Force -Path $pastaDestino | Out-Null

# 1. Copia bases JSON, configurações do Pool de IAs e código oficial
Copy-Item "H:\Cockpit_GTI\backend\config_pool_ias.json" $pastaDestino -ErrorAction SilentlyContinue
Copy-Item "H:\Cockpit_GTI\data\*" $pastaDestino -Recurse -ErrorAction SilentlyContinue
Copy-Item "H:\Cockpit_GTI\docker-compose.yml" $pastaDestino

Write-Host "✅ Snapshot de segurança gravado em: $pastaDestino" -ForegroundColor Green
```

---

## 9. Prontuário de Comandos Rápidos (Cheat Sheet PowerShell & Docker)

| Operação Desejada | Comando Exato no PowerShell (`H:\Cockpit_GTI`) |
| :--- | :--- |
| **Subir toda a stack unificada** | `docker compose up -d` |
| **Atualizar o container após editar código** | `docker compose up -d --build --force-recreate` |
| **Ver status e portas dos 3 containers** | `docker compose ps` |
| **Parar toda a stack (sem perder dados)** | `docker compose stop` |
| **Iniciar novamente a stack parada** | `docker compose start` |
| **Ver logs do Backend Flask (:5000)** | `docker logs --tail 50 -f cockpit-gti-backend` |
| **Ver logs do Gateway New API (:3001)** | `docker logs --tail 50 -f cockpit-gti-newapi` |
| **Ver logs do Motor Ollama (:11434)** | `docker logs --tail 50 -f cockpit-gti-ollama` |
| **Testar Slot de IA via linha de comando** | `Invoke-RestMethod -Uri "http://localhost:5000/api/v1/ia/testar_slot" -Method POST -ContentType "application/json" -Body '{"slot":"principal","endpoint":"http://100.103.100.98:3001/v1","apiKey":"SUA_CHAVE","model":"qwen2.5:14b"}'` |
| **Listar modelos liberados em uma API Key** | `curl.exe -s http://100.103.100.98:3001/v1/models -H "Authorization: Bearer SUA_CHAVE"` |
