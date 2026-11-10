# 🌊 Cockpit GTI — Plataforma Executiva de Governança, Processos SEI & Orquestração Multi-IA (v11.0)

[![Release](https://img.shields.io/badge/Release-v11.0.0--Oficial-0284c7.svg)](https://github.com/luizseixeiro/cockpit-gti-spaguas)
[![SP-Águas](https://img.shields.io/badge/Autarquia-SP--%C3%81guas-01a75f.svg)](https://www.spaguas.sp.gov.br/)
[![Unidade](https://img.shields.io/badge/Unidade-SA--GTI-002d5a.svg)](https://github.com/luizseixeiro/cockpit-gti-spaguas)
[![Conformidade](https://img.shields.io/badge/Conformidade-Lei%2014.133%20%7C%20S%C3%BAmula%20269%20TCU-f59e0b.svg)](https://github.com/luizseixeiro/cockpit-gti-spaguas)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%20:5000-000000.svg)](https://flask.palletsprojects.com/)

> **Repositório Oficial:** [https://github.com/luizseixeiro/cockpit-gti-spaguas](https://github.com/luizseixeiro/cockpit-gti-spaguas)  
> **Central de Comando Executivo, Operação Administrativa, Instrução Processual (Lei nº 14.133/2021) e Prestação de Contas da Superintendência de Tecnologia da Informação (SA-GTI), projetada como plataforma corporativa escalável para todas as Diretorias da Agência de Águas do Estado de São Paulo (SP-Águas).**


## 📋 Sumário

 1. [Visão Geral e Propósito Institucional](#-1-visão-geral-e-propósito-institucional)

 2. [Arquitetura Geral do Sistema (v11.0)](#-2-arquitetura-geral-do-sistema-v110)

 3. [Design System: Glassmorphism SaaS Dual-Theme (Dark & Light)](#-3-design-system-glassmorphism-saas-dual-theme-dark--light)

 4. [Navegação Enxuta: Sidebar Unificada & As 4 Visões Mestras](#-4-navegação-enxuta-sidebar-unificada--as-4-visões-mestras)

 5. [Segurança: Tela de Login & Controle de Acesso Escalonado (RBAC)](#-5-segurança-tela-de-login--controle-de-acesso-escalonado-rbac)

 6. [Stack de Inteligência Artificial: Pipeline de 3 Agentes + RAG Híbrido](#-6-stack-de-inteligência-artificial-pipeline-de-3-agentes--rag-híbrido)

 7. [Hub de Conectores Editáveis: 6 Motores Internos & 5 Motores Externos](#-7-hub-de-conectores-editáveis-6-motores-internos--5-motores-externos)

 8. [Modelagem de Dados e Esquema SQL (DDL MariaDB `:3306`)](#-8-modelagem-de-dados-e-esquema-sql-ddl-mariadb-3306)

 9. [Catálogo Completo de Endpoints da API REST (Backend `:5000`)](#-9-catálogo-completo-de-endpoints-da-api-rest-backend-5000)

10. [Especificação Técnica do Protocolo entre as 3 IAs & Microsserviços](#-10-especificação-técnica-do-protocolo-entre-as-3-ias--microsserviços)

11. [Regras de Negócio Canônicas: Regra dos "Poréns", 18 Buckets & Toolkits A4](#-11-regras-de-negócio-canônicas-regra-dos-poréns-18-buckets--toolkits-a4)

12. [Estrutura de Diretórios, Variáveis de Ambiente (`.env`), Portas e Operação DRP](#-12-estrutura-de-diretórios-variáveis-de-ambiente-env-portas-e-operação-drp)

## 🏛️ 1. Visão Geral e Propósito Institucional

O **Cockpit GTI** nasceu na **Superintendência de Tecnologia da Informação (SA-GTI)** — abrangendo as divisões de Infraestrutura (**DIF**), Governança e Dados (**DGD**) e Gestão de Contratos — com o objetivo de eliminar a fragmentação informacional entre múltiplos sistemas administrativos e técnicos.

Mais do que um painel de indicadores, o Cockpit consolida-se em três pilares estratégicos:

1. **Painel Executivo de Gestão à Vista (Command Center 360°):** Monitoramento contínuo, visual e sem fricção de processos, projetos, chamados e conformidade regulatória.

2. **Estação de Trabalho Administrativa assistida por IA (Mesa de Trabalho):** Central única onde o gestor e o analista consultam o acervo do **SEI-SP**, higienizam relatórios oficiais em PDF (Manual v7.1), pesquisam em motores externos oficiais (**DOE-SP**, **PNCP**, **TCE-SP**) e redigem artefatos da **Lei Federal nº 14.133/2021** (DFD, ETP, TR, Matriz de Riscos, IMR e Pareceres Técnicos) com suporte de um pipeline hierárquico de 3 Agentes de IA.

3. **Sala de Reuniões e Prestação de Contas à Diretoria:** Condução de rituais ágeis (Daily Scrum de 15 min e Sprint Planning), controle de impedimentos jurídicos/externos (*"Poréns"*) e emissão em 1 clique de **Atas Administrativas e Dossiês Executivos em PDF A4** no padrão visual oficial das três ondas da SP-Águas.

### Escopo Corporativo Multidiretoria (SP-Águas)

Embora concebido como piloto na **SA-GTI**, o sistema suporta nativamente o recorte de dados e permissões para todas as unidades da autarquia:

* 💻 **`[SA-GTI]`** Superintendência de Tecnologia da Informação (Piloto Master)

* 🏛️ **`[SA]`** Diretoria / Superintendência Administrativa (GLCC, GRH, GFN, GPA)

* 🛡️ **`[SH]`** Diretoria de Segurança Hídrica (GMH, GPE, Escola das Águas)

* 🌊 **`[SD]`** Diretoria de Unidades Descentralizadas (Bacias Hidrográficas / UGRHIs)

* ⚖️ **`[SR]`** Diretoria de Regulação (Agenda Regulatória e Outorgas)

* 🔍 **`[SF]`** Diretoria de Fiscalização (PROFISC e Monitoramento)

* 🏢 **`[Gabinete]`** Presidência, Conselho Diretor, Ouvidoria e Consultoria Jurídica (CJ)

## 🏗️ 2. Arquitetura Geral do Sistema (v11.0)

O diagrama abaixo representa a arquitetura de ponta a ponta da plataforma, integrando autenticação escalonada, interface em 4 Visões Mestras, banco de dados relacional + vetorial, conectores multissistêmicos e o pipeline de 3 IAs gerenciado pela **New API**:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              CAMADA DE APRESENTAÇÃO (FRONTEND WEB v11.0)                               │
│         Design System: Glassmorphism SaaS Dual-Theme (🌙 Dark Space #090D16 / ☀️ Light #F2F6FC)        │
├────────────────────────┬───────────────────────────────────────────────────────────────────────────────┤
│ 🔐 TELA DE LOGIN RBAC  │ 🧭 SIDEBAR UNIFICADA (ESQUERDA) + 4 VISÕES MESTRAS (100% ÁREA ÚTIL SEM BANNER)│
│ • E-mail/Matrícula     │   [1] 📺 EIXO 1: Gestão à Vista 360° (Informativo Puro + Auditoria TCE/TCU)   │
│ • Senha (Hash Bcrypt)  │   [2] 💼 EIXO 2: Mesa de Trabalho Única (SEI + IA + Toolkits A4 + Buscadores) │
│ • 4 Níveis de Acesso   │   [3] 🤝 EIXO 3: Sala de Reuniões & Diretoria (War Room 15m + Kanban + Ata A4)│
│ • Escopo por Diretoria │   [4] ⚙️ EIXO 4: Configurações (11 Conectores + Pipeline 3 IAs + Motor RAG)   │
└───────────┬────────────┴───────────────────────────────────────┬───────────────────────────────────────┘
            │                                                    │ REST API / JSON (HTTPS / Local)
            ▼                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA DE APLICAÇÃO, ORQUESTRAÇÃO & RAG (BACKEND)                            │
│                         Servidor Python (Flask :5000 / FastAPI :8000) + Workers                        │
├───────────────────────────────┬────────────────────────────────┬───────────────────────────────────────┤
│ 🛡️ Auth & RBAC Middleware     │ 🔎 Motor RAG Híbrido           │ ⚙️ Gerenciador de Conectores & ETL    │
│ • Validação de Sessão/Token   │ • SQL Query Builder (MariaDB)  │ • Parser SEI PDF v7.1 (UPSERT)        │
│ • Filtro por Diretoria/Nível  │ • Vector Index (Embeddings)    │ • Cálculo de Aging Líquido ("Poréns") │
│ • Auditoria de Ações          │ • Top-K + Threshold Config     │ • Scheduler de Varreduras Externas    │
└───────────────┬───────────────┴────────────────┬───────────────┴───────────────────┬───────────────────┘
                │                                │                                   │
                ▼                                ▼                                   ▼
┌───────────────────────────────┐ ┌──────────────────────────────────┐ ┌─────────────────────────────────┐
│ 🗄️ CAMADA DE DADOS (SSOT)     │ │ 🧠 GATEWAY MULTI-IA: NEW API     │ │ 🔌 BARRAMENTO DE CONECTORES     │
│ MariaDB 10.11 (:3306 glpidb)  │ │ Porta :3001/v1 (Cloud + Ollama)  │ │ (6 Internos + 5 Externos)       │
├───────────────────────────────┤ ├──────────────────────────────────┤ ├─────────────────────────────────┤
│ • processos_sei (197 reais)   │ │ 1. 🧠 IA 1 (Principal Multimodal)│ │ INTERNOS:                       │
│ • op_pacotes (500 corporativos│ │    Interpretação + Consulta RAG  │ │ • OpenProject 14 (:8090 / Prod) │
│   e 97 pacotes SA-GTI A-018)  │ │              │                   │ │ • GLPI 10 (:8088 Read-Only)     │
│ • glpi_tickets (13 reais)     │ │              ▼                   │ │ • SEI-SP / Zabbix NOC           │
│ • feed_publicacoes_externas   │ │ 2. 🧭 IA 2 (Orquestradora)       │ │ EXTERNOS (Ingestão RAG/SQL):    │
│ • usuarios_cockpit (RBAC)     │ │    Gera Log de Tarefas JSON DAG  │ │ • 📰 DOE-SP (Diário Oficial)    │
│ • cfg_conectores_motores      │ │              │                   │ │ • 🛒 PNCP (UASG 262101 / PCA)   │
│ • rag_embeddings_index        │ │              ▼                   │ │ • 🌊 Portal SP-Águas            │
│   (Delib. 21/2026 + PCA 1,51bi│ │ 3. ⚡ IA 3 (Microsserviços)      │ │ • ⚖️ TCE-SP & Súmula 269 TCU    │
│   + Lei 14.133 + Súmula 269)  │ │    Execução Determinística (T=0) │ │ • 💧 SIGRH / SOE / ANA / CETESB │
└───────────────────────────────┘ └──────────────────────────────────┘ └─────────────────────────────────┘

```

## 🎨 3. Design System: Glassmorphism SaaS Dual-Theme (Dark & Light)

A interface web foi projetada sob o conceito **Glassmorphism SaaS / Dashboard Moderno**, garantindo estética executiva de alto contraste, profundidade tridimensional e transição instantânea entre os modos **Escuro (Default)** e **Claro**:

| Propriedade Estética | 🌙 Modo Escuro (Dark Mode — Default) | ☀️ Modo Claro (Light Mode) | 
| ----- | ----- | ----- | 
| **Fundo Principal (`body`, `#main`)** | Cinza espacial profundo / grafite (`#090D16`) | Branco gelo / azul sutil (`#F2F6FC`) | 
| **Aurora Backdrop Glow** | Esferas de luz difusa em Azul Royal (`rgba(5,68,207,0.25)`), Roxo (`rgba(124,58,237,0.22)`) e Ciano (`rgba(14,165,233,0.18)`) | Gradientes suaves e translúcidos em tons pastel da marca (`rgba(5,68,207,0.08)`) | 
| **Superfície dos Cards de Vidro** | `rgba(15, 23, 42, 0.68)` + `backdrop-filter: blur(18px)` | `rgba(255, 255, 255, 0.72)` + `backdrop-filter: blur(18px)` | 
| **Bordas Especulares (`1px`)** | `1px solid rgba(255, 255, 255, 0.12)` | `1px solid rgba(203, 213, 225, 0.75)` | 
| **Tipografia Primária / Secundária** | `#FFFFFF` (Branco puro) / `#94A3B8` (Cinza claro) | `#1A1A1A` (Grafite escuro) / `#475569` (Cinza médio) | 
| **Cor de Destaque (CTAs / Ativos)** | Gradiente vibrante `#4F46E5` ➔ `#2563EB` | Idêntico (`#4F46E5` ➔ `#2563EB`) | 
| **Semáforos de Criticidade** | 🔴 `#F87171` • 🟠 `#FB923C` • 🟡 `#FACC15` • 🟢 `#4ADE80` | 🔴 `#DC2626` • 🟠 `#EA580C` • 🟡 `#CA8A04` • 🟢 `#16A34A` | 

## 🧭 4. Navegação Enxuta: Sidebar Unificada & As 4 Visões Mestras

Para eliminar a poluição visual das antigas 15 abas independentes e do banner superior que ocupava 25% da tela, a versão **v11.0** adota **duas diretrizes estruturais**:

1. **Fim do Banner Principal (`.page-banner`) e do Cabeçalho Horizontal (`#topbar`):** Todos os controles globais (Logo SP-Águas, Busca Global `Ctrl+K`, Usuário Logado, Seletor de Diretoria, Telemetria `11/11 Online`, Comutador `🌙/☀️` e Logout) foram incorporados verticalmente na **Sidebar Esquerda**, liberando 100% da área direita para os cards.

2. **Apenas 4 Visões Mestras (1 por Eixo):**

### 📺 Eixo 1 — Gestão à Vista (Dashboard 360° Informativo & Conformidade)

* **Conceito:** Painel executivo **100% informativo, direto e sem interação complexa**, estilo monitor de sala de situação / TV de diretoria.

* **4 Quadrantes Visuais:**

  1. **Pulso Processual SEI:** Acervo Total (197 processos), 4 Semáforos de Criticidade e proporção Custódia Interna vs. Suspensões Externas (*"Poréns"*).

  2. **Pulso de Projetos & Estratégia:** Portfólio OpenProject (500 pacotes corporativos / 97 Tracks SA-GTI), avanço das 35 iniciativas do PDTIC 2027-2030 e execução orçamentária do PCA (R\$ 1,51 bilhão).

  3. **Pulso Operacional ITSM (GLPI 10):** Saúde da fila real (13 chamados ativos), cumprimento de SLA e disponibilidade de links/infraestrutura.

  4. **Pulso de Conformidade & Auditoria (TCE-SP & Súmula 269 TCU):** Índice de conformidade contratual (88.5%), métricas PF/UST, apuração de IMR/SIAFEM, regra de backup imutável 3-2-1-1-0 (WORM) e matriz de riscos ISO/IEC 27001.

### 💼 Eixo 2 — Mesa de Trabalho Única (O Hub Operacional onde Tudo Acontece)

* **Conceito:** Em vez de separar *Acervo SEI*, *Mesa de Trabalho*, *Processos Fixados*, *Assistente IA* e *Cadernos A4* em abas distintas, **tudo parte da Mesa de Trabalho**.

* **Grade Operacional Central:** Permite alternar em 1 clique entre `📌 Minha Custódia`, `⭐ Processos Fixados`, `📂 Acervo Completo SEI (197)` e `📦 Pacotes OpenProject (97)`, com o botão de **`📥 Upload PDF SEI (Manual v7.1)`** integrado no topo da tabela.

* **Módulos / Gavetas Contextuais (Acionados sem sair da Mesa):**

  * **🧠 Gaveta do Pipeline de 3 IAs & RAG Regimental:** Abre na lateral direita para analisar o processo selecionado, responder dúvidas sobre a Deliberação nº 21/2026 ou disparar tarefas automatizadas.

  * **📄 Gaveta de Toolkits & Modelos A4 (Lei 14.133/2021):** Abre sobre o processo selecionado já pré-preenchida com número SEI, objeto e responsável para gerar e imprimir **DFD, ETP, TR, Matriz de Riscos, IMR e Parecer Técnico de 3 páginas** com o logo oficial da SP-Águas.

  * **🌐 Gaveta de Motores de Busca Externos:** Pesquisa unificada em **DOE-SP, PNCP, Portal SP-Águas, TCE-SP e SIGRH/SOE** diretamente de dentro da Mesa.

### 🤝 Eixo 3 — Sala de Reuniões Administrativas & Prestação de Contas à Diretoria

* **Conceito:** Ambiente focado na condução de reuniões executivas, rituais ágeis (Daily de 15 min) e geração de atas formais.

* **Recursos Integrados:** Cronômetro regressivo de 15 minutos, quadro de pauta / Kanban da Sprint ativa (22 status oficiais), mural rápido de Deliberações e Impedimentos (*"Poréns"*) e botão de 1 clique para **`🖨️ Emitir Ata Administrativa & Dossiê de Prestação de Contas em PDF A4`**.

### ⚙️ Eixo 4 — Central de Configurações (Simplificada e 100% Parametrizável)

* **Conceito:** Exclusiva para administradores, organizada em 4 blocos limpos para controle total dos **11 Conectores (Internos e Externos)**, do **Pipeline das 3 IAs na New API**, do **Motor RAG** e da **Gestão de Usuários/Backups**.

## 🔐 5. Segurança: Tela de Login & Controle de Acesso Escalonado (RBAC)

Cada usuário autentica-se na **Tela de Login Institucional (`#view-login-gate`)** com credenciais validadas na tabela `usuarios_cockpit` do MariaDB (`:3306`), recebendo acesso escalonado conforme seu **Nível Funcional** e sua **Diretoria de Lotação**:

| Nível RBAC | Perfil Institucional | Escopo de Dados | Visões e Ações Permitidas | 
| ----- | ----- | ----- | ----- | 
| **👑 Nível 1** | **Super-Admin** *(Luiz Seixeiro / Governança Master)* | Global (`Toda a SP-Águas`) | Acesso irrestrito às **4 Visões Mestras**. Único perfil habilitado a configurar Conectores, API Keys da New API, parâmetros do RAG, usuários e Backups DRP no **Eixo 4**. | 
| **👔 Nível 2** | **Gestor Executivo** *(Diretores, Superintendentes e Gerentes)* | Sua Diretoria ou Consolidado | Acesso ao **Eixo 1 (Gestão à Vista)**, **Eixo 2 (Mesa de Trabalho da sua Diretoria)** e **Eixo 3 (Sala de Reuniões e emissão de Atas A4)**. **Eixo 4 oculto.** | 
| **💻 Nível 3** | **Analista Técnico** *(Equipes DIF/DGD e Fiscais de Contrato)* | Sua Unidade e Processos sob Custódia | Acesso ao **Eixo 1**, operação na **Mesa de Trabalho (Eixo 2)** (Upload PDF v7.1, Pipeline IA e Toolkits A4 nos seus processos) e Daily no **Eixo 3**. **Eixo 4 oculto.** | 
| **🏛️ Nível 4** | **Demandante / Consulta** *(Unidades Descentralizadas e Bacias)* | Estritamente suas Demandas | Acesso somente leitura (*Read-Only*) ao **Eixo 1** da sua unidade e consulta de status dos seus processos na **Mesa de Trabalho (Eixo 2)**. **Eixos 3 e 4 ocultos.** | 

## 🧠 6. Stack de Inteligência Artificial: Pipeline de 3 Agentes + RAG Híbrido

O Cockpit GTI implementa uma esteira multiagente profissional acolhida e gerenciada pelo gateway **New API (`:3001/v1`)**, permitindo combinar modelos em nuvem e modelos locais (**Ollama `:11434`**):

```
[Demanda do Usuário: Chat / PDF do SEI / Planilha / Imagem]
      │
      ▼
[1. 🧠 IA 1 — AGENTE PRINCIPAL (Multimodal, Alto Contexto & RAG Híbrido)]
   • Consulta o MariaDB (SQL) + Base Vetorial (Deliberação 21/2026, PCA R$ 1,51 bi, Lei 14.133).
   • Interpreta a necessidade, responde dúvidas complexas e gera o [Diagnóstico Contextual].
      │
      ▼
[2. 🧭 IA 2 — AGENTE DE ORQUESTRAÇÃO (Planejador de Tarefas / DAG)]
   • Recebe o diagnóstico da IA 1 e orquestra um [Log Estruturado de Tarefas em JSON]
     definindo a sequência exata de ações para a IA 3.
      │
      ▼
[3. ⚡ IA 3 — AGENTE DE MICROSSERVIÇOS (Executor Determinístico • Temp 0.05)]
   • Executa o Log de Tarefas com precisão: queries SQL/UPSERT, extração PDF v7.1,
     preenchimento de Toolkits A4 (DFD, ETP, TR, Parecer Técnico, Ata) e atualização da Mesa.

```

### Modelos Recomendados por Camada (Configuráveis pelo Frontend)

| Camada | Função | Modelo Cloud Recomendado (New API) | Modelo Local Recomendado (Ollama) | Temperatura | 
| ----- | ----- | ----- | ----- | ----- | 
| **🧠 IA 1 (Principal)** | Multimodal, alto contexto e síntese **RAG** ampla no banco de dados | `gemini-2.5-pro` *(ou `gpt-4o`)* | `mistral-nemo:12b` + `llama3.2-vision:11b` | `0.25` | 
| **🧭 IA 2 (Orquestração)** | Raciocínio lógico e geração do **Log de Tarefas (`JSON DAG`)** | `gemini-2.5-flash-thinking` *(ou `deepseek-reasoner`)* | `deepseek-r1:14b` *(16k–32k ctx)* | `0.10` | 
| **⚡ IA 3 (Microsserviços)** | Execução determinística do Log de Tarefas (SQL, A4, Tags) | `gemini-2.5-flash` *(ou `gpt-4o-mini`)* | `qwen2.5-coder:14b` + `qwen2.5-coder:3b` | `0.05` | 
| **🔎 Motor RAG** | Embeddings semânticos e indexação vetorial | `text-embedding-004` | `nomic-embed-text` *(768 dims)* | — | 

## 🔌 7. Hub de Conectores Editáveis: 6 Motores Internos & 5 Motores Externos

Na visão **`⚙️ 4. Configurações`**, todos os conectores internos e externos possuem parâmetros editáveis pela interface web (URL, Token/API Key, Filtros/UASG, Frequência do Cron, Toggle ON/OFF, Indexação no RAG, botão `🔌 Testar Handshake` e botão `⚡ Sincronizar Agora`), além de suporte **CRUD para adicionar novos motores**:

### 7.1 Motores Internos (6 Conectores)

1. **🗄️ MariaDB 10.11 (`:3306 / glpidb`):** Banco relacional oficial (SSOT) com fallback automático para cache JSON local quando em operação offline.

2. **📂 Barramento SEI-SP & Extrator PDF v7.1:** Parametrização da unidade (`110036935`), regras de regex v7.1 e cálculo de Aging Líquido com expurgo automático de suspensões externas (*"Poréns"*).

3. **📋 OpenProject 14 PMIS (`:8090` / Produção):** Leitura dos **500 pacotes corporativos** da SP-Águas e canal bidirecional com **trava de escopo estrita na SA-GTI** (97 pacotes nos 18 Buckets `A-001` a `A-018`).

4. **🎫 GLPI 10 ITSM (`:8088` / Produção):** Conector **estritamente Read-Only (Somente Leitura)** monitorando os **13 chamados reais pendentes (`id < 1500`)** e ativos do CMDB.

5. **📡 Zabbix NOC & Telemetria (DMO/WAN):** Monitoramento de disponibilidade de links SD-WAN/Intragov e estações hidrológicas.

6. **🧠 Gateway New API (`:3001`) + Ollama (`:11434`):** Gerenciamento centralizado de chaves, descoberta automática de modelos (`GET /v1/models`) e hiperparâmetros do **RAG** (`Top-K`, `Threshold`, `Chunk Size`).

### 7.2 Motores de Busca Externos Oficiais (5 Conectores + CRUD)

 7. **📰 Diário Oficial do Estado de São Paulo (DOE-SP):** Varredura automatizada de publicações da SP-Águas/DAEE/SA-GTI, portarias e extratos contratuais.

 8. **🛒 Portal Nacional de Contratações Públicas (PNCP — UASG `262101`):** Conciliação automática de editais, atas e contratos com o **PCA 2027 (R\$ 1,51 bi)** e os 55 processos da Lei 14.133.

 9. **🌊 Portal Institucional SP-Águas (`spaguas.sp.gov.br`):** Coleta de Deliberações do Conselho Diretor, normativos internos e Agenda Regulatória para o RAG.

10. **⚖️ Jurisprudência TCE-SP / TCU / AUDESP:** Monitoramento de acórdãos, Súmula 269 TCU e regras de fiscalização contratual (IMR/SIAFEM).

11. **💧 Barramento Hídrico (SIGRH / SOE / ANA / CETESB):** Interoperabilidade com dados de outorgas e bacias hidrográficas (UGRHIs).

## 🗄️ 8. Modelagem de Dados e Esquema SQL (DDL MariaDB `:3306`)

Todas as tabelas operacionais do Cockpit GTI residem no schema `glpidb` do servidor **MariaDB 10.11 (`:3306`)**, utilizando charset `utf8mb4_unicode_ci` e operações idempotentes (`INSERT ... ON DUPLICATE KEY UPDATE`).

```
-- ============================================================================
-- 1. TABELA DE AUTENTICAÇÃO E CONTROLE DE ACESSO ESCALONADO (RBAC)
-- ============================================================================
CREATE TABLE IF NOT EXISTS usuarios_cockpit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    matricula VARCHAR(40) UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    nivel_rbac ENUM('SUPER_ADMIN', 'GESTOR', 'ANALISTA', 'DEMANDANTE') NOT NULL DEFAULT 'ANALISTA',
    diretoria_escopo VARCHAR(40) NOT NULL DEFAULT 'spaguas-sa-gti', -- Ex: todas, spaguas-sa-gti, spaguas-sh, etc.
    unidade_divisao VARCHAR(80) DEFAULT 'SA-GTI',
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    ultimo_login DATETIME NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. TABELA MESTRA DE PROCESSOS DO SEI-SP (197 PROCESSOS REAIS)
-- ============================================================================
CREATE TABLE IF NOT EXISTS processos_sei (
    id_processo VARCHAR(40) PRIMARY KEY,            -- Ex: 137.00013843/2025-97
    especificacao TEXT NOT NULL,
    tipo_processo VARCHAR(120),
    diretoria_macro VARCHAR(40) DEFAULT 'spaguas-sa-gti',
    eixo_gestao ENUM('ESTEIRA', 'ROTINA', 'PORTFOLIO') NOT NULL DEFAULT 'ROTINA',
    bucket_canonico VARCHAR(120) NOT NULL,          -- A-001 a A-018
    status_kanban VARCHAR(80) NOT NULL,             -- 22 Status Oficiais
    responsavel_tecnico VARCHAR(120),
    data_abertura DATE,
    data_ultima_movimentacao DATE,
    dias_aging_bruto INT DEFAULT 0,
    dias_suspensao_porens INT DEFAULT 0,            -- Dias na CJ/Bacias/Fornecedor Externo
    dias_aging_liquido INT GENERATED ALWAYS AS (GREATEST(0, dias_aging_bruto - dias_suspensao_porens)) STORED,
    motivo_porem VARCHAR(255) NULL,
    farol_criticidade ENUM('VERMELHO', 'LARANJA', 'AMARELO', 'VERDE') NOT NULL DEFAULT 'VERDE',
    fixado_watchlist TINYINT(1) DEFAULT 0,
    id_pacote_openproject INT NULL,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_eixo_farol (eixo_gestao, farol_criticidade),
    INDEX idx_responsavel (responsavel_tecnico),
    INDEX idx_bucket (bucket_canonico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. TABELA DE CONFIGURAÇÃO DOS 11 CONECTORES (INTERNOS E EXTERNOS)
-- ============================================================================
CREATE TABLE IF NOT EXISTS cfg_conectores_motores (
    id_conector VARCHAR(50) PRIMARY KEY,            -- Ex: conn_mariadb, conn_doe_sp, conn_pncp
    nome_exibicao VARCHAR(120) NOT NULL,
    categoria ENUM('INTERNO', 'EXTERNO', 'IA_GATEWAY') NOT NULL,
    protocolo VARCHAR(40) NOT NULL,                 -- REST_API, SQL, SCRAPER, JSON_RPC
    endpoint_url VARCHAR(500) NOT NULL,
    auth_token_encrypted TEXT NULL,
    parametros_filtro_json JSON NULL,               -- Ex: {"uasg": "262101", "keywords": ["SP-Águas", "SA-GTI"]}
    frequencia_cron VARCHAR(40) DEFAULT '30m',
    timeout_ms INT DEFAULT 10000,
    somente_leitura TINYINT(1) DEFAULT 1,
    indexar_no_rag TINYINT(1) DEFAULT 1,
    ativo TINYINT(1) DEFAULT 1,
    ultimo_status ENUM('ONLINE', 'DEGRADADO', 'OFFLINE', 'FALLBACK_LOCAL') DEFAULT 'ONLINE',
    ultima_sincronizacao DATETIME NULL,
    total_registros_coletados INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. TABELA DE PUBLICAÇÕES DOS MOTORES DE BUSCA EXTERNOS (DOE, PNCP, TCE, SIGRH)
-- ============================================================================
CREATE TABLE IF NOT EXISTS feed_publicacoes_externas (
    id_publicacao BIGINT AUTO_INCREMENT PRIMARY KEY,
    hash_unico CHAR(64) NOT NULL UNIQUE,            -- SHA-256 (fonte + url + data + titulo) para UPSERT
    fonte_motor VARCHAR(40) NOT NULL,               -- DOE-SP, PNCP, PORTAL_SPAGUAS, TCE-SP, SIGRH
    data_publicacao DATE NOT NULL,
    titulo VARCHAR(300) NOT NULL,
    resumo_conteudo TEXT,
    url_oficial VARCHAR(600) NOT NULL,
    id_processo_sei_vinculado VARCHAR(40) NULL,
    indexado_rag TINYINT(1) DEFAULT 0,
    coletado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_fonte_data (fonte_motor, data_publicacao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. ÍNDICE VETORIAL DO MOTOR RAG HÍBRIDO & LOG DE AUDITORIA DO PIPELINE 3 IAs
-- ============================================================================
CREATE TABLE IF NOT EXISTS rag_embeddings_index (
    id_chunk BIGINT AUTO_INCREMENT PRIMARY KEY,
    origem_fonte VARCHAR(60) NOT NULL,              -- REGIMENTO_21_2026, PCA_2027, LEI_14133, SEI, FEED_EXTERNO
    referencia_id VARCHAR(100) NOT NULL,            -- Ex: Art_42, SEI_137.00013843, PCA_ITEM_12
    texto_chunk TEXT NOT NULL,
    vetor_embedding JSON NOT NULL,                  -- Array float[768] gerado por nomic-embed-text / text-embedding-004
    metadados_json JSON NULL,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_origem (origem_fonte, referencia_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ia_pipeline_logs (
    id_execucao VARCHAR(50) PRIMARY KEY,            -- Ex: ORCH-20261103-0001
    usuario_id INT NOT NULL,
    prompt_original TEXT NOT NULL,
    ia1_modelo VARCHAR(80),
    ia1_diagnostico_rag JSON,
    ia2_modelo VARCHAR(80),
    ia2_task_log_dag JSON,
    ia3_modelo VARCHAR(80),
    ia3_resultados_execucao JSON,
    latencia_total_ms INT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

```

## 🌐 9. Catálogo Completo de Endpoints da API REST (Backend `:5000`)

O servidor backend (`main.py`) expõe uma API RESTful estruturada por domínio, validando o token de sessão RBAC em todas as rotas protegidas:

### 9.1 Autenticação e Gestão de Usuários (`Auth & RBAC`)

| Método | Rota | Nível Mínimo | Descrição Técnica | 
| ----- | ----- | ----- | ----- | 
| `POST` | `/api/auth/login` | Público | Autentica `email` + `senha`, valida hash `bcrypt` em `usuarios_cockpit` e retorna JWT + perfil + escopo de diretoria. | 
| `POST` | `/api/auth/logout` | Autenticado | Invalida a sessão ativa e registra o evento no log de auditoria. | 
| `GET` | `/api/auth/me` | Autenticado | Retorna os dados do usuário logado, seu nível RBAC (1 a 4) e as visões habilitadas na Sidebar. | 
| `GET/POST` | `/api/usuarios` | `SUPER_ADMIN` | Lista, cria, edita nível RBAC/diretoria ou bloqueia usuários do Cockpit. | 

### 9.2 Operação: Processos SEI, OpenProject, GLPI e Sala de Reuniões

| Método | Rota | Nível Mínimo | Descrição Técnica | 
| ----- | ----- | ----- | ----- | 
| `GET` | `/api/gestao-vista/resumo` | `DEMANDANTE` | Retorna os 4 quadrantes consolidados do **Eixo 1 (Gestão à Vista)** filtrados pelo escopo da diretoria. | 
| `GET` | `/api/mesa/demandas` | `DEMANDANTE` | Retorna os processos SEI, Fixados ⭐ e pacotes OpenProject para a grade central da **Mesa de Trabalho (Eixo 2)**. | 
| `POST` | `/api/sei/upload-v71` | `ANALISTA` | Recebe PDF oficial do SEI, executa o parser v7.1, aplica a Regra dos *"Poréns"* e faz UPSERT em `processos_sei`. | 
| `POST` | `/api/mesa/fixar/<id_sei>` | `ANALISTA` | Alterna o marcador de estrela (⭐ Watchlist) de um processo SEI. | 
| `POST` | `/api/toolkits/render-a4` | `ANALISTA` | Preenche qualquer um dos 15 modelos da Lei 14.133 com os dados do processo e retorna o HTML/PDF A4 institucional. | 
| `POST` | `/api/warroom/ata-pdf` | `GESTOR` | Compila a pauta deliberada, os post-its de impedimentos e participantes em uma **Ata Administrativa A4 em PDF**. | 

### 9.3 Pipeline das 3 IAs (New API `:3001`), Motor RAG e Conectores (`Eixo 4`)

| Método | Rota | Nível Mínimo | Descrição Técnica | 
| ----- | ----- | ----- | ----- | 
| `POST` | `/api/ia/pipeline` | `ANALISTA` | Executa o ciclo completo: **Busca RAG ➔ IA 1 (Principal) ➔ IA 2 (Orquestradora DAG) ➔ IA 3 (Microsserviços)** via New API (`:3001`). | 
| `GET` | `/api/ia/models-sync` | `SUPER_ADMIN` | Consulta `GET /v1/models` na New API (`:3001`) e retorna todos os modelos Cloud e Ollama disponíveis para os dropdowns. | 
| `GET/POST` | `/api/config/ia-rag` | `SUPER_ADMIN` | Lê ou atualiza modelos, API Keys, temperaturas da IA 1/2/3 e parâmetros do RAG (`Top-K`, `Threshold`, `Chunk Size`, fontes). | 
| `POST` | `/api/rag/reindex` | `SUPER_ADMIN` | Recalcula os embeddings (`nomic-embed-text`) de todas as fontes marcadas e atualiza a tabela `rag_embeddings_index`. | 
| `GET/PUT` | `/api/conectores` | `SUPER_ADMIN` | Lista, edita ou cadastra conectores na tabela `cfg_conectores_motores` (6 internos + 5 externos + novos CRUD). | 
| `POST` | `/api/conectores/<id>/sync` | `SUPER_ADMIN` | Testa handshake HTTP/SQL e força a coleta/sincronização imediata do conector selecionado. | 
| `POST` | `/api/drp/snapshot` | `SUPER_ADMIN` | Compacta o diretório do projeto + dump SQL do MariaDB gerando um ponto de restauração `.zip` versionado. | 

## 🤖 10. Especificação Técnica do Protocolo entre as 3 IAs & Microsserviços

A comunicação interna entre os 3 Agentes gerenciados pela **New API (`:3001/v1`)** obedece a um contrato JSON determinístico:

### 10.1 Estágio 1 — Saída Estruturada da `🧠 IA 1 (Principal Multimodal & RAG)`

Quando a IA 1 analisa o pedido do usuário junto aos anexos e aos trechos recuperados pelo **Motor RAG**, ela produz:

```
{
  "resposta_usuario_markdown": "O Processo SEI **137.00013843/2025-97** refere-se à contratação de serviços de nuvem (IaaS/PaaS), enquadrado no Bucket **A-018** e previsto no **Item 14 do PCA 2027**. Conforme o Art. 42 da Deliberação nº 21/2026 e o Art. 18 da Lei 14.133/2021, elaborei o plano de instrução do ETP abaixo.",
  "fontes_rag_citadas": [
    "MariaDB:processos_sei#137.00013843/2025-97",
    "Deliberacao_21_2026:Art_42",
    "PCA_2027:Item_14_Nuvem_IaaS"
  ],
  "requer_orquestracao_ia2": true,
  "intent_payload": {
    "acao_macro": "INSTRUIR_ARTEFATO_LEI_14133",
    "id_processo_sei": "137.00013843/2025-97",
    "tipo_artefato": "ETP",
    "diretoria": "spaguas-sa-gti",
    "responsavel": "Luiz Seixeiro"
  }
}

```

### 10.2 Estágio 2 — Log de Tarefas (`TaskExecutionLog`) Gerado pela `🧭 IA 2 (Orquestradora)`

A IA 2 recebe o `intent_payload` da IA 1 e gera o grafo acíclico direcionado (DAG) de tarefas para a IA 3:

```
{
  "orchestration_id": "ORCH-20261103-0042",
  "tasks_for_ia3": [
    {
      "step": 1,
      "microservice_code": "MS_SQL_FETCH_DOSSIE",
      "description": "Recuperar histórico completo e pacotes OpenProject vinculados ao SEI 137.00013843/2025-97",
      "params": { "id_sei": "137.00013843/2025-97" }
    },
    {
      "step": 2,
      "microservice_code": "MS_SEARCH_PNCP_BENCHMARK",
      "description": "Consultar atas e contratações similares no feed PNCP (UASG 262101)",
      "params": { "termo": "IaaS PaaS Nuvem", "ano": 2026 }
    },
    {
      "step": 3,
      "microservice_code": "MS_GENERATE_TOOLKIT_A4",
      "description": "Preencher minuta técnica do Estudo Técnico Preliminar (ETP - Lei 14.133) em padrão A4 SP-Águas",
      "params": { "template_id": "TK_02_ETP", "incluir_sumula_269": true }
    },
    {
      "step": 4,
      "microservice_code": "MS_MESA_UPDATE_STATUS",
      "description": "Atualizar status do processo na Mesa de Trabalho e registrar log de auditoria",
      "params": { "novo_status_kanban": "📄 Elaboração de ETP / Riscos" }
    }
  ]
}

```

### 10.3 Estágio 3 — Catálogo de Microsserviços Determinísticos da `⚡ IA 3`

A IA 3 (`Temperature: 0.05`) possui permissão estrita para invocar apenas os microsserviços homologados no catálogo interno:

1. **`MS_SQL_FETCH_DOSSIE`:** Consulta parametrizada read-only em `processos_sei`, `op_pacotes` e `glpi_tickets`.

2. **`MS_SEI_PDF_PARSER_V71`:** Extração estruturada e higienização UPSERT de relatórios PDF do SEI.

3. **`MS_CALC_AGING_PORENS`:** Recálculo determinístico de Aging Líquido descontando suspensões jurídicas/externas.

4. **`MS_CLASSIFY_BUCKET_A18`:** Enquadramento automático nos 18 Buckets Canônicos (`A-001` a `A-018`).

5. **`MS_GENERATE_TOOLKIT_A4`:** Compilação HTML/CSS A4 dos 15 artefatos da Lei 14.133/2021 com o logo das três ondas da SP-Águas.

6. **`MS_CALC_GLOSA_IMR`:** Cálculo matemático de faixas de desconto do Instrumento de Medição de Resultados (IMR) para liquidação no SIAFEM.

7. **`MS_SEARCH_EXTERNAL_FEEDS`:** Busca filtrada na tabela `feed_publicacoes_externas` (DOE-SP, PNCP, TCE-SP, SIGRH).

8. **`MS_GENERATE_ATA_WARROOM`:** Formatação de Ata de Reunião Administrativa A4 a partir da pauta e mural do Eixo 3.

## ⚖️ 11. Regras de Negócio Canônicas: Regra dos "Poréns", 18 Buckets & Toolkits A4

### 11.1 Regra Jurídica dos "Poréns" e Cálculo de Aging Líquido

Para evitar distorções nos indicadores da equipe técnica da SA-GTI, o Cockpit diferencia o **Aging Bruto** do **Aging Líquido**:

$$
\text{Aging}_{\text{Líquido}} = \max\left(0,\; \text{Dias}_{\text{Corridos desde Abertura/Última Entrega}} - \sum \text{Dias}_{\text{Custódia Externa (Poréns)}}\right)
$$

* **Custódia Externa ("Poréns"):** Períodos em que o processo aguarda parecer da Consultoria Jurídica (**CJ**), deliberação do Conselho Diretor (**CD**), manifestação de Diretorias de Bacia ou resposta de fornecedor externo.

* **Faixas Padrão de Semáforo (Configuráveis no Eixo 4):**

  * 🟢 **Fluxo Normal:** $\le 30$ dias líquidos

  * 🟡 **Monitoramento Ativo:** $31$ a $60$ dias líquidos

  * 🟠 **Saneamento Prioritário:** $61$ a $90$ dias líquidos

  * 🔴 **Intervenção Imediata:** $> 90$ dias líquidos sem movimentação interna

### 11.2 Os 18 Buckets Canônicos da SA-GTI (`A-001` a `A-018`)

Todos os 197 processos do SEI e os 97 pacotes de TIC do OpenProject são classificados nos 18 Buckets oficiais:

* **Rotina Operacional & Sustentação (`A-001` a `A-010`):** `A-001` Atestes e Medições Mensais (PRODESP/Links), `A-002` Faturas de Concessionárias e Telefonia, `A-003` Gestão de Licenças e Subscrições, `A-004` Licenciamento e Outorgas Digitais, `A-005` Segurança da Informação e Backup WORM, `A-006` Infraestrutura Local, CPD e Redes, `A-007` Sustentação de Sistemas Legados (SOE/SIBH), `A-008` Governança de Dados e LGPD, `A-009` Atendimento a Auditorias e Ouvidoria, `A-010` Suporte Interno N2/N3 e Ativos (GLPI/SAM).

* **Esteira de Contratações — Lei 14.133/2021 (`A-011` a `A-015`):** `A-011` Elaboração de DFD, ETP e Matriz de Riscos, `A-012` Elaboração de Termo de Referência (TR) e Catálogo PF/UST, `A-013` Pesquisa de Preços e Conciliação PNCP/BEC, `A-014` Mapeamento de Processos BPMN 2.0, `A-015` Fiscalização Contratual, TRP, TRD e Glosas IMR.

* **Portfólio Estratégico & Transformação (`A-016` a `A-018`):** `A-016` Governança de TIC, PDTIC 2027-2030 e Inovação (IA), `A-017` Modernização de Sistemas e Infraestrutura (Sede e Regionais), `A-018` Otimização, Desmembramento de Contratos e FinOps (Tracks 1 e 2).

### 11.3 Catálogo dos 15 Toolkits & Modelos A4 (Lei 14.133/2021) Acoplados à Mesa de Trabalho

 1. **TK-01:** Documento de Formalização de Demanda (**DFD**) alinhado ao PCA 2027.

 2. **TK-02:** Estudo Técnico Preliminar (**ETP**) com análise de viabilidade e TCO.

 3. **TK-03:** Termo de Referência (**TR**) para Serviços de TIC (Súmula 269 TCU — PF/UST).

 4. **TK-04:** Termo de Referência (**TR**) para Aquisição de Ativos/Licenças (IaaS/PaaS/SaaS).

 5. **TK-05:** Matriz de Alocação de Riscos Contratuais (Lei 14.133, Art. 22 e 103).

 6. **TK-06:** Instrumento de Medição de Resultados (**IMR**) com tabela progressiva de glosas.

 7. **TK-07:** Parecer Técnico Conclusivo em 3 Páginas A4 (Modelo Canônico com **Tripla Validação**: Legal, Técnica e Orçamentária).

 8. **TK-08:** Termo de Recebimento Provisório (**TRP**) para instrução no SEI.

 9. **TK-09:** Termo de Recebimento Definitivo (**TRD**) e autorização de liquidação SIAFEM.

10. **TK-10:** Mapa Comparativo de Pesquisa de Preços (PNCP / Painel de Preços / Contratos Similares).

11. **TK-11:** Ordem de Serviço / Abertura de Sprint para Fábrica de Software (PF/UST).

12. **TK-12:** Laudo Técnico de Teste de Restauração de Backup Imutável (Regra 3-2-1-1-0).

13. **TK-13:** Notificação Técnica de Descumprimento de SLA / Glosa Contratual.

14. **TK-14:** Dossiê Executivo de Prestação de Contas para o Conselho Diretor.

15. **TK-15:** Ata de Reunião Administrativa / Deliberação de Sprint (Padrão A4 SP-Águas).

## 📂 12. Estrutura de Diretórios, Variáveis de Ambiente (`.env`), Portas e Operação DRP

### 12.1 Árvore de Arquivos do Projeto

```
C:\Cockpit_GTI\
├── main.py                              # Servidor Backend Principal (Flask :5000 / APIs / RAG / Auth)
├── docker-compose.yml                   # Orquestração Docker (MariaDB :3306, GLPI :8088, OP :8090, New API :3001)
├── .env                                 # Variáveis de Ambiente e Segredos (Não versionado no Git)
├── frontend\
│   ├── painel.html                      # Aplicação Single-Page Mestre (4 Visões, Login RBAC, Gavetas e Modais)
│   ├── estilo_spaguas.css               # Design System Glassmorphism Dual-Theme (Dark & Light)
│   └── tema.js                          # Controlador de Transição de Tema e Persistência
├── backend\
│   ├── auth_rbac.py                     # Autenticação de Usuários, Hash Bcrypt e Escopo por Diretoria
│   ├── ai_pipeline_newapi.py            # Orquestrador IA 1 (RAG) -> IA 2 (Task Log JSON) -> IA 3 (Microsserviços)
│   ├── rag_engine.py                    # Motor RAG Híbrido (SQL MariaDB + Embeddings nomic-embed-text)
│   ├── connectors_manager.py            # Gerenciador dos 11 Conectores Internos/Externos e Cron Jobs
│   └── sei_pdf_parser_v71.py            # Extrator e Higienizador Idempotente (UPSERT) de PDFs do SEI
├── data\
│   ├── dados_processos_sei.json         # Fallback SSOT Local (197 processos reais higienizados)
│   ├── config_conectores_ia_rag.json    # Persistência espelhada dos parâmetros editados no Frontend
│   └── base_regimental_rag\             # Deliberação nº 21/2026, PCA 2027, Lei 14.133 e Súmula 269 TCU
└── README.md                            # Documentação Oficial de Arquitetura, Engenharia e Operação

```

### 12.2 Modelo do Arquivo de Configuração `.env`

```
# --- SERVIDOR DE APLICAÇÃO & SEGURANÇA RBAC ---
COCKPIT_HOST=0.0.0.0
COCKPIT_PORT=5000
COCKPIT_SECRET_KEY=spaguas-sagti-v11-jwt-secret-key-2026
COCKPIT_DEFAULT_THEME=dark

# --- BANCO DE DADOS OFICIAL (MARIADB 10.11 SSOT) ---
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=glpidb
DB_USER=root
DB_PASSWORD=spaguas_root_pwd
DB_ENABLE_JSON_FALLBACK=true

# --- GATEWAY MULTI-IA (NEW API :3001 & OLLAMA LOCAL :11434) ---
NEWAPI_BASE_URL=http://127.0.0.1:3001/v1
OLLAMA_BASE_URL=http://127.0.0.1:11434
IA1_PRINCIPAL_MODEL=gemini-2.5-pro
IA1_FALLBACK_MODEL=mistral-nemo:12b
IA2_ORCHESTRATOR_MODEL=deepseek-r1:14b
IA3_MICROSERVICES_MODEL=qwen2.5-coder:14b
RAG_EMBEDDING_MODEL=nomic-embed-text
RAG_TOP_K=8
RAG_SIMILARITY_THRESHOLD=0.72

# --- CONECTORES INTERNOS (OPENPROJECT & GLPI) ---
OPENPROJECT_API_URL=http://127.0.0.1:8090/api/v3
OPENPROJECT_WRITE_SCOPE_LOCK=spaguas-sa-gti
GLPI_API_URL=http://127.0.0.1:8088/apirest.php
GLPI_READ_ONLY_MODE=true

```

### 12.3 Mapa de Portas de Rede e Acesso Remoto Seguro (Tailscale)

| Porta | Serviço / Componente | Protocolo | Escopo de Exposição | 
| ----- | ----- | ----- | ----- | 
| **`:5000`** | **Cockpit GTI (Aplicação Principal Flask)** | HTTP/REST | LAN (`10.20.40.63`) + VPN Tailscale (`100.88.193.101`) | 
| **`:3306`** | **MariaDB 10.11 (`glpidb` SSOT)** | TCP/MySQL | Localhost (`127.0.0.1`) e Containers Docker | 
| **`:3001`** | **New API (Gateway Unificado das 3 IAs)** | HTTP/OpenAI | Localhost + Administração via Eixo 4 | 
| **`:11434`** | **Ollama Server (`C:\AgentesIA`)** | HTTP/REST | Localhost + Consumido pela New API (`:3001`) | 
| **`:8088`** | **GLPI 10 (ITSM & CMDB)** | HTTP/REST | Localhost / Produção (`atendimento.spaguas.sp.gov.br`) | 
| **`:8090`** | **OpenProject 14 (PMIS & Kanban)** | HTTP/REST | Localhost / Produção (`projetos.spaguas.sp.gov.br`) | 

### 12.4 Procedimento de Backup e Recuperação de Desastres (DRP / Ponto de Restauração)

```
# 1. Gerar Snapshot Físico + Dump SQL Completo antes de qualquer manutenção
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
mysqldump -u root -p glpidb > "C:\Cockpit_GTI\data\dump_glpidb_$stamp.sql"
Compress-Archive -Path "C:\Cockpit_GTI\*" -DestinationPath "C:\Cockpit_GTI_Snapshot_v11_$stamp.zip" -Force

# 2. Versionar no Git e sincronizar com o repositório oficial
git add -A
git commit -m "Snapshot Oficial Homologado v11.0 ($stamp)"
git tag -f "v11.0-homologado"
git push origin main --tags

```

**Superintendência de Tecnologia da Informação (SA-GTI) • Agência de Águas do Estado de São Paulo (SP-Águas)**

*Concepção, Arquitetura e Gestão do Projeto: Luiz Antonio Seixeiro*