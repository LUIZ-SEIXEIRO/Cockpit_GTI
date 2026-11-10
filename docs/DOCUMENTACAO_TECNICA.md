# ⚙️ Documentação Técnica, Arquitetura de Software & Engenharia de Integrações — Cockpit GTI 360°

**Especificações de Engenharia de Software, Módulos Frontend/Backend, Stack Docker Unificada, Protocolos de Integração (SEI!, OpenProject v3, GLPI 10) e Orquestração Multi-IA**  
**Autarquia:** Agência de Águas do Estado de São Paulo (**SP-Águas**)  
**Unidade Gestora:** Superintendência de Administração — Gerência de Tecnologia da Informação (**SA-GTI**)  
**Divisões Técnicas:** Divisão de Infraestrutura (**DIF**) & Divisão de Governança Digital e Sistemas (**DGD**)  
**Repositório Oficial:** [github.com/LUIZ-SEIXEIRO/Cockpit_GTI](https://github.com/LUIZ-SEIXEIRO/Cockpit_GTI)  
**Versão da Arquitetura:** 11.0 Oficial (Stack Docker Unificada)

---

## 📑 Sumário Técnico

1. [Visão Geral da Arquitetura e Princípios de Engenharia](#1-visão-geral-da-arquitetura-e-princípios-de-engenharia)
2. [Topologia da Stack Docker Unificada (`cockpit-gti`)](#2-topologia-da-stack-docker-unificada-cockpit-gti)
3. [Arquitetura do Frontend SPA (`painel.html`) e Mapeamento DOM](#3-arquitetura-do-frontend-spa-painelhtml-e-mapeamento-dom)
4. [Mapeamento Técnico Completo dos 4 Eixos, 15 Abas e 23 Sub-abas](#4-mapeamento-técnico-completo-dos-4-eixos-15-abas-e-23-sub-abas)
5. [Arquitetura do Backend Flask (`main.py`) e Referência da API REST (`/api/v1/`)](#5-arquitetura-do-backend-flask-mainpy-e-referência-da-api-rest-apiv1)
6. [Engenharia do Pool Multi-IA (New API `:3001` + Ollama `:11434`)](#6-engenharia-do-pool-multi-ia-new-api-3001--ollama-11434)
7. [Engenharia de Integração Bidirecional com OpenProject 14 (API v3)](#7-engenharia-de-integração-bidirecional-com-openproject-14-api-v3)
8. [Conector GLPI 10 (ITSM Tickets & CMDB de Ativos)](#8-conector-glpi-10-itsm-tickets--cmdb-de-ativos)
9. [Motor ETL SEI!, Cálculo de Aging Líquido e Regra Jurídica dos "Poréns"](#9-motor-etl-sei-cálculo-de-aging-líquido-e-regra-jurídica-dos-poréns)
10. [Segurança da Informação, RBAC, LGPD e Conformidade (Súmula 269 TCU)](#10-segurança-da-informação-rbac-lgpd-e-conformidade-súmula-269-tcu)
11. [Procedimentos de Operação, Diagnóstico (Troubleshooting) e Manutenção](#11-procedimentos-de-operação-diagnóstico-troubleshooting-e-manutenção)

---

## 1. Visão Geral da Arquitetura e Princípios de Engenharia

O **Cockpit GTI 360°** foi concebido sob os princípios de **alta disponibilidade local**, **zero dependência de pacotes externos vulneráveis**, **soberania de dados públicos** e **desacoplamento por microsserviços containerizados**.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO (CLIENTE / NAVEGADOR WEB)                     │
│  [ painel.html ] Single-Page Application (HTML5 + CSS3 Glassmorphism + Vanilla JS ES6+) │
│  • 4 Eixos Mestres | 15 Abas | 23 Sub-abas | Motor RBAC Dinâmico | Persistência Híbrida │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │ HTTP / JSON (Porta :5000)
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                     STACK DOCKER UNIFICADA: PROJETO "cockpit-gti"                       │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Container: cockpit-gti-backend (Python 3.11-slim / Flask :5000)                │  │
│  │    • Servidor Web SPA, Proxy CORS, Normalizador de Endpoints IA & Orquestrador    │  │
│  │    • Rotas REST: /api/v1/telemetria | /ia/pool | /ia/testar_slot | /ia/chat       │  │
│  │                  /openproject/sync_card | /openproject/sync_batch | /glpi/tickets │  │
│  └──────────────────┬───────────────────────────────────────────────┬────────────────┘  │
│                     │ (Porta :3001 / :3000)                         │                   │
│                     ▼                                               │                   │
│  ┌──────────────────────────────────────────┐                       │                   │
│  │ 2. Container: cockpit-gti-newapi (:3001) │                       │                   │
│  │    • Imagem: calciumion/new-api:latest   │                       │                   │
│  │    • Gestão de Tokens (sk-...), Canais,  │                       │                   │
│  │      Grupos (SP - ÁGUAS) e Rate Limit    │                       │                   │
│  │    • Volume: new-api-data (/data)        │                       │                   │
│  └──────────────────┬───────────────────────┘                       │                   │
│                     │ (Porta :11434)                                │                   │
│                     ▼                                               ▼                   │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 3. Container: cockpit-gti-ollama (:11434)                                         │  │
│  │    • Imagem: ollama/ollama:latest | Keep-Alive: 24h                               │  │
│  │    • Volume Persistente: H:/spaguas/ia-multiagente/ollama_data -> /root/.ollama   │  │
│  │    • Modelos Locais: qwen2.5:14b, qwen2.5-coder:7b, qwen2.5-coder:1.5b,           │  │
│  │                      llama3.2:1b, deepseek-r1:14b, qwen2.5:32b                    │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────────────┬───────────────────┘
                      │ HTTPS / REST API v3                           │ HTTPS / REST API
                      ▼                                               ▼
┌───────────────────────────────────────────┐   ┌─────────────────────────────────────────┐
│     SERVIDOR OPENPROJECT 14 SP-ÁGUAS      │   │       SERVIDOR GLPI 10 SP-ÁGUAS         │
│  • 500 Work Packages / 29 Projetos        │   │  • Fila ITSM de Chamados Técnicos       │
│  • Leitura e Escrita Controlada c/ Trava  │   │  • Inventário CMDB (443 PCs, 436 Monit) │
└───────────────────────────────────────────┘   └─────────────────────────────────────────┘
```

### Decisões Arquiteturais Chave:
1. **Frontend em Vanilla JavaScript ES6+ (Zero Node/NPM Runtime Dependency):**
   * Toda a lógica de interface reside em um único artefato autocontido (`painel.html` / `frontend/painel.html`). Isso elimina falhas de compilação de *bundlers* (Webpack/Vite), evita vulnerabilidades em árvores de pacotes `node_modules` (em conformidade com as práticas de DevSecOps e **Súmula 269 do TCU**) e garante carregamento instantâneo (< 100ms).
2. **Backend Proxy Leve em Python 3.11 + Flask (`main.py`):**
   * Atua simultaneamente como servidor da aplicação web na porta `5000` e como *API Gateway / Reverse Proxy* para o **New API**, **Ollama**, **OpenProject** e **GLPI**, eliminando bloqueios de *Cross-Origin Resource Sharing (CORS)* no navegador.
3. **Normalização Automática de Rede Container-Host:**
   * Como processos dentro de um container Docker enxergam `localhost` como o próprio container isolado, o backend inclui a função `normalizar_endpoint_ia()`, que converte automaticamente chamadas `localhost:3001` ou `127.0.0.1:3001` para o IP da interface de rede/Tailscale (`100.103.100.98:3001`) e assegura o sufixo `/v1` exigido pelo protocolo OpenAI.

---

## 2. Topologia da Stack Docker Unificada (`cockpit-gti`)

A infraestrutura de execução local em notebooks ou servidores Windows/Linux (via **Docker Desktop / WSL2**) é orquestrada por um único arquivo `docker-compose.yml` na raiz do projeto, agrupando os 3 serviços sob o namespace **`cockpit-gti`**:

### Especificação dos Serviços (`docker-compose.yml`):

| Serviço Docker | Nome do Container | Imagem Base | Portas (`Host:Container`) | Volumes de Persistência | Função Técnica |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **`ollama`** | `cockpit-gti-ollama` | `ollama/ollama:latest` | `11434:11434` | `H:/spaguas/ia-multiagente/ollama_data:/root/.ollama` | Servidor de inferência de LLMs locais com `OLLAMA_KEEP_ALIVE=24h` para evitar recarregamento de pesos na memória RAM/VRAM. |
| **`new-api`** | `cockpit-gti-newapi` | `calciumion/new-api:latest` | `3001:3000` | `new-api-data:/data` (*external volume*) | Gateway centralizador OpenAI-compatível. Gerencia chaves (`sk-...`), permissões de modelos por grupo (`SP - ÁGUAS`) e logs de consumo. |
| **`cockpit-backend`** | `cockpit-gti-backend` | Build local (`Dockerfile` / `python:3.11-slim`) | `5000:5000` | Código copiado na imagem + `config_pool_ias.json` | Servidor Flask principal, provedor do `painel.html`, motor de telemetria e proxy para IA, OpenProject e GLPI. |

### Estrutura do `Dockerfile` (`cockpit-backend`):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
ENV PORT=5000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT []
CMD ["python", "main.py"]
```
> **Nota de Engenharia (Compatibilidade com Drives Externos / `H:\` no Windows):** O `Dockerfile` copia integralmente o código-fonte para dentro da imagem (`COPY . .`) em vez de depender exclusivamente de *bind mounts* (`volumes: - .:/app`) da raiz do disco `H:\`, prevenindo o problema clássico do WSL2 onde unidades secundárias do Windows não notificam eventos *inotify* ou montam diretórios vazios.

---

## 3. Arquitetura do Frontend SPA (`painel.html`) e Mapeamento DOM

O arquivo `painel.html` é estruturado de forma modularizada em camadas bem definidas:

1. **Camada de Design System (CSS3 Variáveis & Glassmorphism):**
   * Suporte nativo a **Dual-Theme** (Dark Mode executivo padrão `#0b0f19` com cartões translúcidos `backdrop-filter: blur(12px)` e modo claro de alto contraste, comutáveis via `window.alternarTemaCockpitV11()`).
   * Paleta semântica institucional SP-Águas: Azul Governança (`#0544cf` / `#38bdf8`), Verde Conformidade (`#10b981`), Amarelo Atenção (`#f59e0b`), Laranja Saneamento (`#ea580c`) e Vermelho Intervenção (`#ef4444`).
2. **Camada de Estado Global em Memória (JavaScript State):**
   * `window.PROCESSOS`: Array estruturado contendo os 179 processos administrativos do SEI!, enriquecido com metadados de *aging*, *bucket*, diretoria, responsável e condição de "Porém".
   * `window.PORTFOLIO_OP`: Array com os 500 pacotes de trabalho (*Work Packages*) dos 29 projetos do OpenProject.
   * `window.CHAMADOS_GLPI_REAIS` / `window.TICKETS_GLPI`: Fila de chamados técnicos sincronizados do GLPI 10.
   * `window.POOL_TRES_IAS`: Objeto JSON sincronizado com `localStorage` (`cockpit_pool_3_ias_v11`) e com o backend (`/api/v1/ia/pool`), armazenando endpoints, chaves, modelos e prompts dos 3 slots de IA.
3. **Motor de Roteamento de Abas (`window.switchTab`):**
   * Controla a exibição instantânea dos containers `<div id="view-..." class="tab-view">` e alterna automaticamente a visibilidade das 3 barras superiores de sub-abas (`#barra-subabas-eixo1`, `#barra-subabas-eixo2` e `#barra-subabas-eixo3`).

---

## 4. Mapeamento Técnico Completo dos 4 Eixos, 15 Abas e 23 Sub-abas

A tabela abaixo serve como guia de referência para desenvolvedores e sustentação, relacionando cada tela visível pelo usuário ao seu respectivo **ID de Container DOM**, **Função JavaScript Controladora** e **Fonte de Dados**:

### 4.1. EIXO 1 — Cockpit de Gestão à Vista (`#barra-subabas-eixo1`)

| Aba / Sub-aba na Interface | Container DOM (`id`) | Função JS de Ativação / Filtro | Fonte de Dados / Integração | Objetivo Funcional |
| :--- | :--- | :--- | :--- | :--- |
| **1.1. 📂 Acervo SEI (360°)** | `#view-dashboards` | `switchTab('dashboards')` | `window.PROCESSOS` (`processos.json`) | Container mestre dos dashboards executivos do SEI. |
| ├─ *Visão Consolidada 360°* | `#subview-dash-consolidado` | `alternarModoDashboard('consolidado')` | 179 processos (Todos) | KPIs dos 4 faróis, volumetria por bucket e gráficos ApexCharts. |
| ├─ *Esteira de Contratação* | `#subview-dash-esteira` | `alternarModoDashboard('esteira')` | Recorte de 55 processos licitatórios | Monitoramento das fases da Lei Federal nº 14.133/2021. |
| ├─ *Rotina Operacional* | `#subview-dash-rotina` | `alternarModoDashboard('rotina')` | Recorte de 93 processos contínuos | Controle de atestes mensais, faturas SIAFEM/DMO e ofícios. |
| ├─ *Portfólio Estratégico* | `#subview-dash-portfolio` | `alternarModoDashboard('portfolio')` | Recorte de 31 processos PDTIC | Cruzamento entre processos SEI e metas do PDTIC 2027–2030. |
| ├─ *Faróis & Gargalos* | `#subview-dash-farois` | `alternarModoDashboard('farois')` + `filtrarModoFarol()` | 87 processos em atenção | Análise de *aging* por servidor e separação Custódia vs. Poréns. |
| └─ *Relatório Executivo* | Modal / View de Impressão | `alternarModoDashboard('relatorio')` | Agregação em tempo real | Geração de relatório executivo formatado em A4 para Diretoria. |
| **1.2. 🏗️ Portfólio OpenProject** | `#view-portfolio_openproject` | `switchTab('portfolio_openproject')` | `window.PORTFOLIO_OP` + API v3 | Gestão integrada dos 500 Work Packages e 29 projetos. |
| ├─ *Todos os Projetos (500)* | `#subview-op-todos` | `filtrarModoRapidoOP('todos')` | 500 Work Packages | Grade paginada com filtros por projeto, tipo, status e autor. |
| ├─ *SA-GTI: Tracks & Projetos* | `#subview-op-sagti` | `filtrarModoRapidoOP('sagti')` | 97 Work Packages da SA-GTI | Isolamento da Track 1 (Operação) e Track 2 (Novas Contratações). |
| ├─ *PDTIC 2027–2030 & KPIs* | `#subview-op-pdtic` | `filtrarModoRapidoOP('pdtic')` | 35 Iniciativas / 8 KPIs | Monitoramento dos 5 Eixos Estratégicos (E1 a E5) do PDTIC. |
| └─ *Relatório OpenProject* | Sub-view Relatório OP | `alternarSubAbaOpenProject('relatorio')` | Agregação do Portfólio | Emissão de dossiê gerencial de projetos e marcos (*milestones*). |
| **1.3. 🎫 Atendimento GLPI 10** | `#view-gestao_glpi` | `switchTab('gestao_glpi')` | `/api/v1/glpi/tickets` + Cache | Central unificada de Helpdesk ITSM e inventário CMDB. |
| ├─ *Fila Operacional (ITSM)* | `#subview-glpi-operacional` | `alternarSubAbaGlpi('operacional')` | `glpi_producao_cache.json` | Monitoramento de chamados não solucionados, SLAs e técnicos. |
| ├─ *Parque de Ativos (CMDB)* | `#subview-glpi-ativos` | `alternarSubAbaGlpi('ativos')` | Inventário CMDB GLPI 10 | Painel de 443 PCs, 436 Monitores, 30 Impressoras e 8.9K Softwares. |
| └─ *Relatório Gerencial GLPI* | `#subview-glpi-relatorio` | `alternarSubAbaGlpi('relatorio')` | Indicadores consolidados | Boletim estatístico de atendimento para fiscalização contratual. |
| **1.4. ⚖️ Auditoria TCE-SP** | `#view-auditoria` | `switchTab('auditoria')` | Matriz GRC + Súmula 269 | Painel de conformidade legal (88.5%), Riscos R01–R12 e IMR. |

---

### 4.2. EIXO 2 — Mesa de Trabalho, SEI & Inteligência Artificial (`#barra-subabas-eixo2`)

| Aba / Sub-aba na Interface | Container DOM (`id`) | Função JS de Ativação / Filtro | Fonte de Dados / Integração | Objetivo Funcional |
| :--- | :--- | :--- | :--- | :--- |
| **2.1. 🖥️ Mesa de Trabalho** | `#view-mesa_trabalho` | `switchTab('mesa_trabalho')` | Filtro por usuário logado | Cockpit individual de produção diária e mural da coordenação. |
| ├─ *Pílula: Minha Custódia* | `#tbody-meus-processos` | `alternarModoMesa('custodia')` | `window.PROCESSOS` (por nome) | Lista processos sob responsabilidade direta do servidor logado. |
| ├─ *Pílula: Fixados (⭐)* | `#tbody-meus-processos` | `alternarModoMesa('fixados')` | `localStorage` (`fixados_sei`) | Watchlist de processos prioritários marcados com estrela. |
| ├─ *Pílula: Pacotes OP* | `#tbody-meus-processos` | `alternarModoMesa('openproject')` | `window.PORTFOLIO_OP` | Lista pacotes do OpenProject atribuídos ao usuário na mesma grade. |
| └─ *Pílula: Chamados GLPI* | `#tbody-meus-processos` | `alternarModoMesa('glpi')` | `window.CHAMADOS_GLPI_REAIS` | Lista tickets do GLPI pertinentes à divisão do usuário. |
| **2.2. 📂 Acervo SEI (179)** | `#view-consulta` | `switchTab('consulta')` | `window.PROCESSOS` | Pesquisa avançada com 9 filtros combinados e exportação CSV. |
| **2.3. 🤖 Assistente IA** | `#view-esteira_ia` | `switchTab('esteira_ia')` | `/api/v1/ia/chat` (New API) | Copiloto executivo, atalhos DFD/ETP/TR e escrita no OpenProject. |
| **2.4. 📚 Cadernos & Toolkits** | `#view-cadernos` | `switchTab('cadernos')` | Repositório de 29 modelos | Biblioteca de minutas da Lei 14.133/2021, catálogos UST e normas. |
| **2.5. 📊 Matrizes RACI** | `#view-matriz_raci` | `switchTab('matriz_raci')` | `localStorage` + JSON RACI | Gestão de papéis (*Responsible, Accountable, Consulted, Informed*). |
| **2.6. 📑 Relatórios & Sprints** | `#view-relatorios_sprints` | `switchTab('relatorios_sprints')` | Acervo de Atas e Sprints | Histórico de atas de Daily e relatórios de Sprint com edição/PDF. |
| **2.7. 🗂️ Drive Contexto IA** | `#view-drive_contexto_ia` | `switchTab('drive_contexto_ia')` | Base RAG de PDFs locais | Gestão de documentos PDF que enriquecem o contexto das IAs. |

---

### 4.3. EIXO 3 — War Room & Rituais Ágeis (`#barra-subabas-eixo3`)

| Aba / Sub-aba na Interface | Container DOM (`id`) | Função JS de Ativação / Filtro | Fonte de Dados / Integração | Objetivo Funcional |
| :--- | :--- | :--- | :--- | :--- |
| **3.1. 👥 War Room: Daily** | `#view-daily_warroom` | `switchTab('daily_warroom')` | Pauta SEI + OP + GLPI | Condução da Daily Scrum de 15m com cronômetro, post-its e ata PDF. |
| ├─ *Pauta: Processos SEI* | Painel de Pauta Daily | `alternarAbaPautaDaily('sei')` | `window.PROCESSOS` | Seleção de processos críticos do SEI para debate na Daily. |
| ├─ *Pauta: OpenProject* | Painel de Pauta Daily | `alternarAbaPautaDaily('op')` | `window.PORTFOLIO_OP` | Seleção de Work Packages da Sprint atual para alinhamento. |
| └─ *Pauta: Chamados GLPI* | Painel de Pauta Daily | `alternarAbaPautaDaily('glpi')` | `window.CHAMADOS_GLPI_REAIS` | Seleção de incidentes urgentes do GLPI para força-tarefa. |
| **3.2. 🏃 Gestão Ágil (Kanban)** | `#view-gestao_agil` | `switchTab('gestao_agil')` | Sprints + OpenProject API | Quadro Kanban *drag-and-drop* com controle de WIP e sincronização. |

---

### 4.4. EIXO 4 — Configurações & Governança Técnica (`#view-configuracoes`)

| Sub-aba de Configuração | Container DOM (`id`) | Função JS de Ativação | Fonte de Dados / Persistência | Objetivo Funcional |
| :--- | :--- | :--- | :--- | :--- |
| **4.1. 👥 Usuários & Perfis** | `#subview-cfg-usuarios` | `alternarSubConfig('usuarios')` | `data/usuarios_cockpit.json` | CRUD de usuários e habilitação de múltiplos perfis de acesso. |
| **4.2. 🛡️ Perfis & RBAC** | `#subview-cfg-rbac` | `alternarSubConfig('rbac')` | Matriz de Permissões RBAC | Configuração granular de visibilidade e travas por perfil. |
| **4.3. ⚖️ Parâmetros & Aging** | `#subview-cfg-parametros` | `alternarSubConfig('parametros')` | `config/regras_governanca_sei.json` | Ajuste de dias de corte dos faróis SEI, regra dos Poréns e Sprints. |
| **4.4. 🔌 Conectores (11 Motores)** | `#subview-cfg-conectores` | `alternarSubConfig('conectores')` | `/api/v1/telemetria` | Monitoramento dos 11 motores de busca e tokens de API. |
| ├─ *Matriz de Conectores* | Sub-aba Matriz | `alternarSubAbaConectores('matriz')` | Status TCP/HTTP em tempo real | Tabela dos 11 conectores com botões de teste e varredura. |
| └─ *Configurações de Tokens* | Sub-aba Config | `alternarSubAbaConectores('configuracoes')` | `openproject_token.txt` / Local | Cadastro de tokens e agendamento horário de sincronização. |
| **4.5. 🤖 Pool das 3 IAs** | `#subview-cfg-agentes` | `alternarSubConfig('agentes')` | `/api/v1/ia/pool` & `/testar_slot` | Parametrização de modelos, endpoints, chaves `sk-...` e teste de ping. |
| **4.6. 💾 Backup & DRP** | `#subview-cfg-backup` | `alternarSubConfig('backup')` | Regra Canônica 3-2-1-1-0 | Exportação e restauração de snapshots completos de estado. |
| **4.7. 📖 Documentação Oficial** | `#subview-cfg-documentacao` | `alternarSubConfig('documentacao')` | `docs/*.md` + HTML Embutido | Consulta integrada ao Manual do Usuário, Doc Técnica e GitHub. |

---

## 5. Arquitetura do Backend Flask (`main.py`) e Referência da API REST (`/api/v1/`)

O servidor backend (`main.py` na raiz e espelhado em `backend/main.py`) é construído sobre **Flask** e executa na porta TCP **`5000`**. Todos os endpoints possuem cabeçalhos CORS habilitados (`Access-Control-Allow-Origin: *`) e tratamento resiliente de exceções (retornando payloads JSON padronizados).

### Catálogo Completo de Endpoints REST:

#### 5.1. `GET /` | `GET /painel` | `GET /frontend/painel.html`
* **Descrição:** Localiza dinamicamente o arquivo `painel.html` (verificando a raiz do projeto, pasta `frontend/` ou diretórios `C:\Cockpit_GTI` e `H:\Cockpit_GTI`) e entrega a interface SPA completa ao navegador.

#### 5.2. `GET /api/v1/telemetria`
* **Descrição:** Realiza *socket probing* TCP assíncrono (timeout de 800ms por porta) para verificar a disponibilidade real dos 5 pilares de infraestrutura.
* **Exemplo de Resposta (`200 OK`):**
  ```json
  {
    "mariadb": false,
    "ollama": true,
    "glpi": true,
    "openproject": true,
    "newapi": true
  }
  ```

#### 5.3. `GET /api/v1/ia/pool` e `POST /api/v1/ia/pool`
* **Descrição:** Lê (`GET`) ou grava (`POST`) o arquivo `config_pool_ias.json`, persistindo em disco as configurações dos 3 slots de IA (modelos, endpoints, API keys, temperatura, limite de tokens e prompts).

#### 5.4. `POST /api/v1/ia/testar_slot`
* **Descrição:** Endpoint dedicado ao botão **`⚡ Testar este Agente`** da interface. Recebe as credenciais de um slot específico, aplica a função `normalizar_endpoint_ia()` (garantindo o sufixo `/v1` e convertendo `localhost:3001` para `100.103.100.98:3001` quando em container), dispara uma requisição `POST /v1/chat/completions` com um payload mínimo (`"content": "ping"`, `"max_tokens": 10`) e mede a latência exata em milissegundos.
* **Payload de Entrada:**
  ```json
  {
    "slot": "principal",
    "endpoint": "http://100.103.100.98:3001/v1",
    "apiKey": "sk-...",
    "model": "qwen2.5:14b"
  }
  ```
* **Resposta de Sucesso (`200 OK`):**
  ```json
  {
    "sucesso": true,
    "status": "sucesso",
    "codigo": 200,
    "codigoHttp": 200,
    "latenciaMs": 142,
    "latencia_ms": 142,
    "mensagem": "Slot qwen2.5:14b ativo (142ms)!"
  }
  ```

#### 5.5. `POST /api/v1/ia/chat`
* **Descrição:** Roteia conversas completas, análises de processos SEI e geração de minutas para o slot de IA solicitado (`principal`, `orquestracao` ou `microservicos`), lendo automaticamente as credenciais salvas em `config_pool_ias.json` ou aceitando parâmetros em tempo de execução.

#### 5.6. `POST /api/v1/openproject/sync_card` e `POST /api/v1/openproject/sync_batch`
* **Descrição:** Endpoints de integração para sincronização individual de um cartão (`card_id` + `comentario` / dossiê) ou sincronização em lote de múltiplos *Work Packages* com o OpenProject.

#### 5.7. `GET /api/v1/openproject/historico_agendado_v2`
* **Descrição:** Retorna o histórico auditável de execuções do agendador automático (`registro_execucao_agendada.json`).

#### 5.8. `GET /api/v1/glpi/tickets`
* **Descrição:** Retorna o espelho atualizado de chamados técnicos do GLPI 10 a partir do cache estruturado de produção (`glpi_producao_cache.json`).

---

## 6. Engenharia do Pool Multi-IA (New API `:3001` + Ollama `:11434`)

A arquitetura de Inteligência Artificial do Cockpit GTI separa o **Gerenciamento de Acesso/Governança (New API)** do **Motor de Inferência Bruta (Ollama)**.

### 6.1. Papéis dos Componentes na Stack de IA:
1. **Ollama (`cockpit-gti-ollama` na porta `11434`):**
   * Gerencia os arquivos de pesos dos modelos quantizados (GGUF) armazenados em `H:/spaguas/ia-multiagente/ollama_data`.
   * Modelos instalados e homologados no ambiente:
     * `qwen2.5:14b` (9.0 GB) — Raciocínio executivo denso e redação formal em português;
     * `qwen2.5-coder:7b` (4.7 GB) — Estruturação de dossiês técnicos, JSON, Markdown e análise normativa;
     * `qwen2.5:7b` (4.7 GB) — Equilíbrio entre velocidade e qualidade textual;
     * `deepseek-r1:14b` (9.0 GB) / `deepseek-r1:7b` (4.7 GB) — Modelos *reasoning* (cadeia de pensamento) para pareceres jurídicos/técnicos complexos;
     * `qwen2.5-coder:1.5b` (986 MB) e `llama3.2:1b` (1.3 GB) — Modelos ultraleves para triagem instantânea e baixa utilização de RAM.
2. **New API (`cockpit-gti-newapi` na porta `3001`):**
   * Atua como proxy de autenticação e governança na frente do Ollama.
   * **Regra de Ouro de Configuração no New API:**
     * Para que um modelo baixado no Ollama não retorne `HTTP 403 Forbidden` ou `HTTP 503 Service Unavailable (model_not_found)`, o modelo **deve estar cadastrado como etiqueta (*tag*) dentro do Canal (Channel) associado ao grupo `SP - ÁGUAS`** e o **Token (`sk-...`) deve estar vinculado ao grupo `SP - ÁGUAS` com permissão para os modelos**.

---

## 7. Engenharia de Integração Bidirecional com OpenProject 14 (API v3)

O módulo `sincronizar_openproject_backend.py` (presente em `backend/`) implementa o cliente REST oficial para o **OpenProject API v3** (`https://projetos.spaguas.sp.gov.br/api/v3`).

### Mecanismo Técnico de Atualização de Work Packages:
1. **Autenticação HTTP Basic:**
   * O OpenProject utiliza a string literal `apikey` como usuário e o token de 64 caracteres (lido de `openproject_token.txt`) como senha, codificados em Base64:
     `Authorization: Basic base64("apikey:<TOKEN>")`.
2. **Controle de Concorrência Otimista (`lockVersion`):**
   * O OpenProject rejeita qualquer requisição `PATCH` que não informe a versão exata do registro atual (`HTTP 409 Conflict`).
   * Por isso, o conector executa sempre um ciclo de **2 etapas**:
     * **Etapa A (`GET /api/v3/work_packages/{id}`):** Extrai o inteiro `lockVersion` atual e os metadados existentes do cartão.
     * **Etapa B (`PATCH /api/v3/work_packages/{id}`):** Envia o novo corpo Markdown em `description.raw` acompanhado do `lockVersion` recém-obtido.
3. **Registro Auditável na Timeline (`POST /api/v3/work_packages/{id}/activities`):**
   * Além de enriquecer a descrição principal do pacote com o Dossiê Técnico homologado pela IA 2, o script publica um comentário datado na aba *Activity* do cartão, garantindo trilha de auditoria completa de quem realizou a sincronização e quando.

---

## 8. Conector GLPI 10 (ITSM Tickets & CMDB de Ativos)

O script `sincronizar_glpi_oficial.py` gerencia a comunicação com o servidor **GLPI 10 da SP-Águas** em modo estritamente seguro (**Read-Only**), preservando a integridade da base de produção de suporte.

* **Fluxo de Autenticação GLPI REST:**
  1. Chama `GET /apirest.php/initSession` enviando `App-Token` e `Authorization: user_token <token>` para obter o `session_token` temporário.
  2. Consulta `GET /apirest.php/Ticket` com parâmetros de filtro para extrair chamados não encerrados (Status 1 a 4: *Novo*, *Em atendimento - atribuído*, *Em atendimento - planejado* e *Pendente*).
  3. Consulta os endpoints de ativos (`Computer`, `Monitor`, `Printer`, `NetworkEquipment`, `Software`) para consolidar os quantitativos do CMDB.
  4. Grava o resultado higienizado em `glpi_producao_cache.json` e encerra a sessão com `GET /apirest.php/killSession`.

---

## 9. Motor ETL SEI!, Cálculo de Aging Líquido e Regra Jurídica dos "Poréns"

A base processual da SA-GTI (`processos.json` / `etl_sei_pdf.py`) classifica automaticamente os **179 processos administrativos** nos **18 Buckets Canônicos (A-001 a A-018)** e aplica o algoritmo de apuração de prazos da autarquia:

### Fórmula do Aging Líquido:
$$\text{Aging Líquido (Dias)} = \text{Aging Bruto Total} - \sum \text{Dias em Suspensão Externa ("Poréns")}$$

* **O que ativa a flag de "Porém" (Suspensão Externa):**
  * Processos aguardando parecer jurídico na Consultoria Jurídica (**CJ**);
  * Processos aguardando cotação de mercado, carta de exclusividade ou assinatura de fornecedor externo;
  * Processos aguardando deliberação de Diretoria Colegiada, Secretaria ou órgãos externos (PRODESP, CESP, ANA, TCE-SP).
* Enquanto o processo permanece sob condição de "Porém", ele é sinalizado com o badge laranja `⏸️ Com Porém` na interface e seu tempo de espera externa não penaliza o indicador de **Eficiência Líquida Individual** do analista da SA-GTI.

---

## 10. Segurança da Informação, RBAC, LGPD e Conformidade (Súmula 269 TCU)

1. **Conformidade com a LGPD (Lei nº 13.709/2018):**
   * Como toda a inferência de Inteligência Artificial ocorre localmente através dos containers `cockpit-gti-newapi` e `cockpit-gti-ollama`, textos de processos administrativos, nomes de servidores, minutas contratuais e pareceres **permanecem 100% dentro da infraestrutura controlada pelo gestor**, sem compartilhamento com serviços de IA públicos externos.
2. **Trava Humana de Escrita (*Human-in-the-Loop*):**
   * Nenhuma IA possui permissão para alterar status ou sobrescrever descrições no OpenProject de forma autônoma a partir do chat. Toda ação mutável exige a validação visual do texto pelo servidor e o acionamento manual do botão de confirmação.
3. **Aderência à Lei Federal nº 14.133/2021 e Súmula 269 do TCU:**
   * Os prompts de sistema das IAs (Slot #1 e Slot #2) e os 29 Cadernos Técnicos embutem nativamente a exigência de métricas objetivas (UST/Pontos de Função), vedação à caracterização de subordinação direta de terceirizados e obrigatoriedade de Matriz de Riscos e IMR.

---

## 11. Procedimentos de Operação, Diagnóstico (Troubleshooting) e Manutenção

### 11.1. Comandos Diários de Operação da Stack Unificada (PowerShell)

```powershell
# Entrar no diretório oficial do projeto
Set-Location H:\Cockpit_GTI

# Verificar o status dos 3 containers da stack unificada
docker compose ps

# Visualizar os logs em tempo real do backend Flask
docker logs -f --tail 50 cockpit-gti-backend

# Reiniciar toda a stack rapidamente
docker compose restart

# Reconstruir a imagem do backend após alterações no main.py ou painel.html
docker compose up -d --build cockpit-backend
```

### 11.2. Tabela de Diagnóstico Rápido (Troubleshooting)

| Sintoma Observado | Causa Raiz Provável | Solução Técnica Imediata |
| :--- | :--- | :--- |
| **`🔴 Falha (HTTP 404)` ao testar Agente IA** | O container `cockpit-gti-backend` estava rodando uma imagem antiga sem a rota `/api/v1/ia/testar_slot`, ou o endpoint estava sem `/v1`. | Execute `docker compose up -d --build --force-recreate` e defina o endpoint como `http://100.103.100.98:3001/v1`. |
| **`🔴 Falha (HTTP 403: Forbidden)` ou `503 model_not_found`** | O modelo digitado no Cockpit não está vinculado ao Canal do grupo `SP - ÁGUAS` ou não está liberado no Token dentro do New API (`:3001`). | Acesse `http://localhost:3001/`, vá em **Canais** ➔ adicione a tag do modelo com `Enter` no grupo `SP - ÁGUAS`, e em **Tokens** habilite **Todos os Modelos**. |
| **Alterações em arquivos no disco `H:\` não refletem no container** | Limitação do Docker Desktop / WSL2 ao monitorar alterações em *bind mounts* de unidades externas (`H:\`). | O projeto utiliza `COPY . .` no `Dockerfile`. Sempre que alterar `main.py` ou `painel.html`, rode `docker compose up -d --build`. |
| **Erro no `git pull` por arquivos do MariaDB (`aria_log` / `ib_buffer_pool`)** | Arquivos binários de runtime do banco local sofreram modificação em disco. | Execute `git restore volumes_docker/` antes de realizar o `git pull` ou `git checkout`. |
