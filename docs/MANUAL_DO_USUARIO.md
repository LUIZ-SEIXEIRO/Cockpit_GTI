# 📘 Manual do Usuário (Operacional, Tático & Executivo) — Cockpit GTI 360°

**Plataforma Integrada de Governança Digital, Acervo Processual SEI!, Portfólio OpenProject, Sustentação ITSM GLPI & Orquestração Multi-IA**  
**Autarquia:** Agência de Águas do Estado de São Paulo (**SP-Águas**)  
**Unidade Gestora:** Superintendência de Administração — Gerência de Tecnologia da Informação (**SA-GTI**)  
**Divisões Integradas:** Divisão de Infraestrutura (**DIF**) & Divisão de Governança Digital e Sistemas (**DGD**)  
**Repositório Oficial:** [github.com/LUIZ-SEIXEIRO/Cockpit_GTI](https://github.com/LUIZ-SEIXEIRO/Cockpit_GTI)  
**Versão da Plataforma:** 11.0 Oficial (Stack Docker Unificada)

---

## 📑 Sumário Navegável

1. [Introdução Institucional e Propósito da Plataforma](#1-introdução-institucional-e-propósito-da-plataforma)
2. [Arquitetura Visual de Navegação (Os 4 Eixos Mestres)](#2-arquitetura-visual-de-navegação-os-4-eixos-mestres)
3. [Controle de Acesso Baseado em Papéis (RBAC) e Sessão do Usuário](#3-controle-de-acesso-baseado-em-papéis-rbac-e-sessão-do-usuário)
4. [EIXO 1 — Módulo Cockpit (Gestão à Vista 360°)](#4-eixo-1--módulo-cockpit-gestão-à-vista-360)
   - [4.1. Sub-aba 1.1: 📂 Acervo SEI (360°) e suas 6 Visões Analíticas](#41-sub-aba-11--acervo-sei-360-e-suas-6-visões-analíticas)
   - [4.2. Sub-aba 1.2: 🏗️ Portfólio OpenProject (500 Pacotes) e seus 5 Recortes](#42-sub-aba-12-️-portfólio-openproject-500-pacotes-e-seus-5-recortes)
   - [4.3. Sub-aba 1.3: 🎫 Atendimento GLPI 10 (ITSM & CMDB) e suas 3 Sub-abas](#43-sub-aba-13--atendimento-glpi-10-itsm--cmdb-e-suas-3-sub-abas)
   - [4.4. Sub-aba 1.4: ⚖️ Auditoria TCE-SP & Súmula 269 TCU](#44-sub-aba-14-️-auditoria-tce-sp--súmula-269-tcu)
5. [EIXO 2 — Módulo Mesa de Trabalho (Cockpit Operacional, SEI & IA)](#5-eixo-2--módulo-mesa-de-trabalho-cockpit-operacional-sei--ia)
   - [5.1. Sub-aba 2.1: 🖥️ Mesa de Trabalho (Custódia) e seus 4 Filtros Rápidos](#51-sub-aba-21-️-mesa-de-trabalho-custódia-e-seus-4-filtros-rápidos)
   - [5.2. Sub-aba 2.2: 📂 Acervo SEI (Consulta Multicritério dos 179 Processos)](#52-sub-aba-22--acervo-sei-consulta-multicritério-dos-179-processos)
   - [5.3. Sub-aba 2.3: 🤖 Assistente IA (Copiloto 360° & Escrita Controlada)](#53-sub-aba-23--assistente-ia-copiloto-360--escrita-controlada)
   - [5.4. Sub-aba 2.4: 📚 Cadernos & Toolkits (29 Documentos Homologados)](#54-sub-aba-24--cadernos--toolkits-29-documentos-homologados)
   - [5.5. Sub-aba 2.5: 📊 Matrizes RACI (Governança de Responsabilidades)](#55-sub-aba-25--matrizes-raci-governança-de-responsabilidades)
   - [5.6. Sub-aba 2.6: 📑 Relatórios Daily & Sprints (Acervo de Rituais)](#56-sub-aba-26--relatórios-daily--sprints-acervo-de-rituais)
   - [5.7. Sub-aba 2.7: 🗂️ Drive Contexto IA (Base RAG em PDF)](#57-sub-aba-27-️-drive-contexto-ia-base-rag-em-pdf)
6. [EIXO 3 — Módulo War Room & Rituais Ágeis](#6-eixo-3--módulo-war-room--rituais-ágeis)
   - [6.1. Sub-aba 3.1: 👥 War Room: Daily & Rituais (Timebox 15m)](#61-sub-aba-31--war-room-daily--rituais-timebox-15m)
   - [6.2. Sub-aba 3.2: 🏃 Gestão Ágil & Sprints (Quadro Kanban Interativo)](#62-sub-aba-32--gestão-ágil--sprints-quadro-kanban-interativo)
7. [EIXO 4 — Módulo Configurações & Governança Técnica](#7-eixo-4--módulo-configurações--governança-técnica)
   - [7.1. Sub-aba 4.1: 👥 Gestão de Usuários & Perfis](#71-sub-aba-41--gestão-de-usuários--perfis)
   - [7.2. Sub-aba 4.2: 🛡️ Perfis de Acesso & RBAC](#72-sub-aba-42-️-perfis-de-acesso--rbac)
   - [7.3. Sub-aba 4.3: ⚖️ Parâmetros de Gestão, Aging & Sprints](#73-sub-aba-43-️-parâmetros-de-gestão-aging--sprints)
   - [7.4. Sub-aba 4.4: 🔌 Conectores & Varredura Sistêmica (11 Motores)](#74-sub-aba-44--conectores--varredura-sistêmica-11-motores)
   - [7.5. Sub-aba 4.5: 🤖 Pool Multi-IA & Agentes Especializados](#75-sub-aba-45--pool-multi-ia--agentes-especializados)
   - [7.6. Sub-aba 4.6: 💾 Backup, Resiliência & DRP (Regra 3-2-1-1-0)](#76-sub-aba-46--backup-resiliência--drp-regra-3-2-1-1-0)
   - [7.7. Sub-aba 4.7: 📖 Documentação Oficial Integrada](#77-sub-aba-47--documentação-oficial-integrada)
8. [Roteiros Práticos do Dia a Dia (Passo a Passo)](#8-roteiros-práticos-do-dia-a-dia-passo-a-passo)
9. [Glossário de Termos Técnicos e Administrativos da SP-Águas](#9-glossário-de-termos-técnicos-e-administrativos-da-sp-águas)

---

## 1. Introdução Institucional e Propósito da Plataforma

O **Cockpit GTI 360°** é a plataforma unificada de comando, controle operacional, instrução processual e inteligência artificial desenvolvida para a **Gerência de Tecnologia da Informação (SA-GTI)** da **Agência de Águas do Estado de São Paulo (SP-Águas)**.

Antes do Cockpit GTI, a operação e a tomada de decisão da equipe técnica e gerencial dependiam da consulta fragmentada a múltiplos sistemas isolados:
* **SEI! (Sistema Eletrônico de Informações):** para tramitação de processos administrativos e contratações públicas;
* **OpenProject:** para acompanhamento de cronogramas, pacotes de trabalho (*Work Packages*) e iniciativas do PDTIC;
* **GLPI 10:** para triagem de chamados de suporte técnico (Helpdesk) e inventário do parque tecnológico (CMDB);
* **Planilhas e Documentos Dispersos:** para controle de prazos contratuais, Instrumentos de Medição de Resultados (IMR) e atas de reunião.

### Objetivos Estratégicos do Cockpit GTI:
1. **Unificação em Tela Única (Single Pane of Glass):** Concentrar os 179 processos administrativos da SA-GTI, os 500 pacotes de trabalho do OpenProject e a fila de chamados e ativos do GLPI 10 em uma interface rápida, responsiva e sem recarregamento de página (*Single-Page Application*).
2. **Justiça na Apuração de Prazos (Aging Líquido vs. Regra dos "Poréns"):** Separar de forma transparente o tempo em que o processo está sob responsabilidade técnica da SA-GTI (*Custódia Interna*) do tempo em que aguarda manifestações externas (*Suspensões / Poréns*, como pareceres da Consultoria Jurídica, cotações de fornecedores ou deliberações superiores).
3. **Aceleração da Instrução Licitatória com Inteligência Artificial Local:** Prover um **Pool Multi-IA 100% local** (via *Ollama* e *New API*) capaz de redigir minutas de **DFD**, **ETP**, **TR**, **Pareceres Técnicos** e **Dossiês de Governança** em estrita conformidade com a **Lei Federal nº 14.133/2021** e a **Súmula 269 do TCU**, garantindo soberania de dados e conformidade com a **LGPD** (nenhum dado sensível da autarquia é enviado para nuvens externas sem controle).
4. **Rastreabilidade e Rituais Ágeis Auditáveis:** Transformar reuniões diárias (*Daily Scrum* de 15 minutos) e ciclos de *Sprints* em registros formais, com geração automática de Atas Administrativas em PDF A4 e sincronização controlada de pareceres diretamente nos cartões do OpenProject.

---

## 2. Arquitetura Visual de Navegação (Os 4 Eixos Mestres)

Para proporcionar máxima clareza visual e evitar poluição de tela, a navegação do Cockpit GTI foi projetada em **dois níveis hierárquicos**:

1. **Menu Lateral Esquerdo (Sidebar Ultralimpa):** Contém os **4 Eixos Mestres** da plataforma. Pode ser recolhido ou expandido clicando no botão `◀` no topo esquerdo.
2. **Barra Superior de Sub-Abas Contextual:** Ao selecionar um dos 4 Eixos na barra lateral, o topo da tela exibe automaticamente as sub-abas pertencentes àquele eixo, com contadores dinâmicos (*badges*).

| Eixo Mestre (Menu Lateral) | Público-Alvo Principal | Sub-Abas Superiores Disponíveis | Objetivo Central do Eixo |
| :--- | :--- | :--- | :--- |
| **1. 📺 Cockpit** | Diretoria, Gerência SA-GTI, Chefes de Divisão (DIF/DGD) e Órgãos de Controle | • `📂 Acervo SEI (360°)`<br>• `🏗️ Portfólio OpenProject (500)`<br>• `🎫 Atendimento GLPI 10 (15)`<br>• `⚖️ Auditoria TCE-SP & Súmula 269` | Monitoramento executivo em tempo real, indicadores estratégicos, faróis de risco, portfólio de projetos e conformidade legal. |
| **2. 💼 Mesa de Trabalho** | Gestores, Analistas de TIC e Equipe Técnica / Administrativa | • `🖥️ Mesa de Trabalho (Custódia)`<br>• `📂 Acervo SEI (179)`<br>• `🤖 Assistente IA (4 Cam)`<br>• `📚 Cadernos & Toolkits (29)`<br>• `📊 Matrizes RACI (3)`<br>• `📑 Relatórios Daily & Sprints (5)`<br>• `🗂️ Drive Contexto IA (3 PDFs)` | Execução diária das demandas atribuídas ao servidor, consulta avançada de processos, geração de minutas com IA e consulta a modelos normativos. |
| **3. 🤝 War Room** | Scrum Master, Product Owner, Gestores e Toda a Equipe SA-GTI | • `👥 War Room: Daily & Rituais (15m)`<br>• `🏃 Gestão Ágil & Sprints (Kanban)` | Condução de reuniões diárias cronometradas, deliberação de impedimentos, emissão de atas em PDF e movimentação de cartões na Sprint. |
| **4. ⚙️ Configurações** | Super-Admin e Administradores da Plataforma | • `👥 Usuários` • `🛡️ RBAC`<br>• `⚖️ Parâmetros` • `🔌 Conectores`<br>• `🤖 Pool de IAs` • `💾 Backup DRP`<br>• `📖 Documentação` | Parametrização técnica do sistema, calibração dos agentes de IA, gestão de permissões, monitoramento de motores e cópias de segurança. |

---

## 3. Controle de Acesso Baseado em Papéis (RBAC) e Sessão do Usuário

No rodapé do menu lateral esquerdo encontra-se o **Painel de Sessão do Usuário**, que exibe as iniciais do servidor logado, seu nome completo, o botão de encerramento de sessão (`🚪 Logout`) e o **Seletor Dinâmico de Perfil Ativo**.

### Os 4 Perfis Institucionais de Acesso:

| Perfil | Ícone | Escopo de Visibilidade e Permissões | Quem Utiliza |
| :--- | :---: | :--- | :--- |
| **Super-Admin** | 👑 | Acesso total e irrestrito aos 4 Eixos, edição de parâmetros de aging, configuração de chaves e modelos do Pool Multi-IA, execução de varreduras, exclusão de registros e homologação no OpenProject. | Gestor de Governança / Administrador Geral da SA-GTI (Luiz Seixeiro). |
| **Gestor** | 👔 | Acesso completo aos painéis executivos (Eixo 1), Mesa de Trabalho (Eixo 2) e War Room (Eixo 3). Pode aprovar minutas, conduzir rituais ágeis, editar matrizes RACI e visualizar configurações. | Gerente da SA-GTI e Chefes de Divisão (DIF e DGD). |
| **Analista** | 💻 | Foco operacional nos processos sob sua custódia, uso completo do Assistente de IA para redação de DFD/ETP/TR, consulta aos Cadernos Técnicos e participação na Daily/Kanban. Oculta abas estritamente administrativas. | Analistas de TIC, Engenheiros de Dados, Especialistas de Infraestrutura e Fiscais Técnicos. |
| **Demandante** | 🏛️ | Visão simplificada e consultiva (*Read-Only*). Permite acompanhar o andamento dos processos e projetos demandados pela sua respectiva Diretoria ou Bacia Hidrográfica sem risco de alteração acidental. | Diretorias Finalísticas da SP-Águas e Diretorias de Bacias Hidrográficas. |

> **💡 Dica Prática (Comutação Instantânea de Perfil):** Se você possui perfil `👑 Super-Admin`, pode clicar a qualquer momento sobre o seletor no canto inferior esquerdo e alternar para `👔 Gestor`, `💻 Analista` ou `🏛️ Demandante` para validar exatamente como cada grupo enxerga a plataforma.

---

## 4. EIXO 1 — Módulo Cockpit (Gestão à Vista 360°)

Ao clicar em **📺 Cockpit** no menu lateral, a plataforma apresenta o panorama executivo da SA-GTI. Este eixo é composto por **4 Sub-Abas Superiores**, detalhadas a seguir.

---

### 4.1. Sub-aba 1.1: 📂 Acervo SEI (360°) e suas 6 Visões Analíticas

Esta é a tela inicial padrão do Cockpit GTI. Ela consolida os **179 processos administrativos monitorados** da SA-GTI e oferece uma barra de pílulas (*Segmented Pills*) que permite alternar entre **6 modos de visualização**:

#### A) 🌐 Visão Consolidada 360° (179 Processos)
* **Objetivo:** Apresentar a fotografia executiva global do acervo da SA-GTI.
* **Scorecards Superiores (5 Indicadores de Farol):**
  1. **🌐 Acervo Total de Processos (179):** 100% dos processos mapeados no banco de dados.
  2. **🔴 1 - Intervenção Imediata:** Processos com prazos críticos vencidos ou risco iminente de descontinuidade contratual.
  3. **🟠 2 - Saneamento Prioritário:** Processos que exigem instrução técnica ou resposta urgente da equipe no curto prazo.
  4. **🟡 3 - Monitoramento Ativo:** Processos em tramitação regular que requerem acompanhamento periódico.
  5. **🟢 4 - Fluxo Normal:** Processos dentro do prazo regulamentar ou já saneados.
* **Gráficos e Tabelas Executivas:** Exibe a distribuição volumétrica por Bucket Temático (A-001 a A-018), a proporção entre Custódia Interna e Suspensões Externas ("Poréns") e o ranking de carga de trabalho por responsável técnico.

#### B) 📑 Esteira de Contratação (55 Processos)
* **Objetivo:** Isolar exclusivamente os processos de aquisições, licitações, renovações contratuais, termos aditivos e atas de registro de preços regidos pela **Lei Federal nº 14.133/2021**.
* **Funcionalidades:** Agrupa os processos pelas fases da contratação pública (Planejamento/DFD, Elaboração de ETP/TR, Pesquisa de Preços, Análise Jurídica CJ, Pregão/Contratação e Execução/Fiscalização), permitindo identificar gargalos na esteira de compras de TIC.

#### C) ⚙️ Rotina Operacional (93 Processos)
* **Objetivo:** Monitorar processos de natureza contínua e administrativa (atestes mensais de faturas de links/telefonia, conciliação SIAFEM com a DMO, solicitações de acesso, sindicâncias, ofícios e demandas correntes).
* **Funcionalidades:** Foca no giro rápido de processos (*throughput*), destacando demandas de baixa complexidade que não podem acumular *aging* na fila.

#### D) 🚀 Portfólio Estratégico (31 Processos)
* **Objetivo:** Acompanhar os processos estruturantes vinculados às metas estratégicas da autarquia e ao **PDTIC 2027–2030** (como Modernização de Data Center e Nuvem, Fábrica de Software, Interoperabilidade com ANA/SIGRH e Governança de Dados/LGPD).
* **Funcionalidades:** Cruza o número do processo SEI diretamente com os códigos de iniciativa do PDTIC e seus respectivos pacotes de trabalho no OpenProject.

#### E) 🎯 Faróis & Gargalos (87 Processos em Atenção)
* **Objetivo:** Servir como painel de controle de riscos e desobstrução de gargalos para o gestor.
* **Filtros Interativos de Farol:** Permite clicar diretamente nos botões `Todos`, `🔴 Vermelho`, `🟠 Laranja`, `🟡 Amarelo` ou `🟢 Verde` para filtrar a grade de processos.
* **Análise de Custódia vs. Poréns:** Exibe gráficos comparativos mostrando quantos dias cada processo passou parado internamente vs. aguardando órgãos externos, protegendo a equipe técnica de cobranças indevidas por atrasos alheios à SA-GTI.

#### F) 📄 Relatório Executivo do Dashboard
* **Objetivo:** Gerar uma visualização consolidada, formatada para impressão em **PDF A4** ou apresentação em reuniões de Diretoria, sintetizando os números dos 4 faróis, distribuição por área e processos críticos da semana.

---

### 4.2. Sub-aba 1.2: 🏗️ Portfólio OpenProject (500 Pacotes) e seus 5 Recortes

Esta sub-aba integra o Cockpit GTI ao servidor **OpenProject da SP-Águas** (`projetos.spaguas.sp.gov.br`), permitindo auditar e gerenciar os **500 Pacotes de Trabalho (Work Packages)** distribuídos em **29 Projetos Oficiais**.

Na barra superior interna do módulo, o usuário conta com **5 modos e filtros rápidos**:

1. **🌐 Todos os Projetos (500 WPs):**
   * Lista completa e paginada de todos os pacotes de trabalho da autarquia, com filtros combinados por **Projeto**, **Tipo de Pacote** (Fase, Marco, Tarefa, Risco, Entrega), **Status** (Novo, Em andamento, Em espera, Fechado), **Responsável** e busca textual por ID ou assunto.
2. **🏛️ Recorte SA-GTI: Tracks & Projetos (97 WPs):**
   * Filtra instantaneamente os pacotes sob responsabilidade direta da Gerência de Tecnologia da Informação, divididos em:
     * **Track 1 (Operação e Sustentação):** Contratos críticos em andamento (links de comunicação, telefonia, parque de impressão, suporte).
     * **Track 2 (Transformação Digital e Contratações):** Novos projetos estruturantes modelados em UST/Pontos de Função.
3. **📈 Recorte PDTIC 2027–2030 & KPIs:**
   * Apresenta o alinhamento dos projetos com os **5 Eixos Estratégicos do PDTIC (E1 a E5)**, cobrindo as **35 Iniciativas Oficiais** e os **8 Indicadores Estratégicos (KPI-001 a KPI-008)**.
4. **📄 Relatório Executivo OpenProject:**
   * Gera um dossiê analítico do portfólio de projetos com gráficos de progresso físico, distribuição por status e listagem de marcos (*milestones*) críticos, pronto para exportação/impressão em PDF.
5. **⚡ Botões de Sincronização e Auditoria de Logs:**
   * **`🔄 Sincronizar OpenProject`:** Dispara a atualização imediata com a API v3 do OpenProject.
   * **`📋 Histórico de Sincronização Automática`:** Abre o modal de auditoria (`registro_execucao_agendada.json`) exibindo todas as sincronizações horárias realizadas pelo agendador de backend, incluindo data/hora, cards atualizados e status HTTP.

---

### 4.3. Sub-aba 1.3: 🎫 Atendimento GLPI 10 (ITSM & CMDB) e suas 3 Sub-abas

Conecta a plataforma à central de serviços **GLPI 10 da SP-Águas**, unificando a gestão de suporte ao usuário (Helpdesk/Service Desk) e o inventário físico/lógico de equipamentos de TIC. Possui **3 sub-abas internas**:

#### 1. 🎫 Fila Operacional de Chamados (ITSM)
* **Objetivo:** Monitorar em tempo real os chamados técnicos abertos e pendentes de solução na SA-GTI.
* **Indicadores de SLA:** Apresenta cartões com o total de chamados ativos, incidentes vs. requisições, chamados atribuídos e alertas de vencimento de SLA.
* **Filtros Rápidos por Status:** Botões para isolar chamados `Novos`, `Em Atendimento (Atribuídos)`, `Planejados`, `Pendentes` ou `Solucionados`.
* **Acesso Direto:** Cada linha da tabela traz o ID do ticket, título, requerente, localização/bacia, técnico responsável, data de abertura e link direto para abertura do ticket no GLPI oficial.

#### 2. 💻 Parque de Ativos & CMDB (Inventário de Hardware e Software)
* **Objetivo:** Espelhar com fidelidade o painel oficial de inventário (`dashboard_assets.php`) do GLPI 10 da SP-Águas.
* **Quantitativos Monitorados do Parque:**
  * **🖥️ 443 Computadores** (Estações de trabalho e notebooks distribuídos entre Sede e Bacias);
  * **🖵 436 Monitores**;
  * **🖨️ 30 Impressoras / Multifuncionais**;
  * **🌐 Equipamentos de Rede, Dispositivos e Periféricos**;
  * **📦 ~8.900 Instalações de Software catalogadas**.
* **Funcionalidades:** Permite pesquisar ativos por patrimônio, número de série, modelo, fabricante ou unidade de localização, apoiando o planejamento de renovação tecnológica (*refresh* de parque) e dimensionamento de licenças.

#### 3. 📊 Relatório Gerencial GLPI
* **Objetivo:** Emitir o boletim gerencial de sustentação e atendimento de suporte técnico, consolidando indicadores de tempo médio de atendimento (TMA), taxa de resolução e distribuição de demandas por diretoria, pronto para impressão ou anexação em processos de fiscalização contratual.

---

### 4.4. Sub-aba 1.4: ⚖️ Auditoria TCE-SP & Súmula 269 TCU

Painel especializado em **Governança, Riscos e Conformidade (GRC)** voltado à prevenção de apontamentos do **Tribunal de Contas do Estado de São Paulo (TCE-SP)** e ao cumprimento da jurisprudência do **TCU**.

* **Índice Geral de Conformidade Normativa (88.5% / Meta > 95%):** Mede o grau de aderência dos contratos e processos da SA-GTI às exigências legais.
* **Controle Estrito da Súmula 269 do TCU:**
  * Audita os contratos de serviços de TIC para assegurar que todas as ordens de serviço sejam mensuradas por **resultados objetivos e entregáveis aferíveis** (Pontos de Função, UST catalogada com pesos fixos ou níveis de serviço com IMR), vedando pagamentos por mera disponibilidade de mão de obra ou hora trabalhada sem artefato vinculado.
* **Matriz de Riscos Corporativos de TIC (R01 a R12):**
  * Monitora os 12 riscos críticos do PDTIC (como risco de indisponibilidade de links nas bacias, falha de backup/ransomware, evasão de conhecimento técnico, defasagem contratual e glosas por descumprimento de SLA), detalhando probabilidade, impacto, plano de mitigação e responsável.
* **Monitoramento de Contratos Críticos e Pagamentos Indenizatórios:**
  * Rastreia a vigência dos contratos vigentes para evitar lacunas contratuais e eliminar qualquer ocorrência de despesa sem cobertura contratual.

---

## 5. EIXO 2 — Módulo Mesa de Trabalho (Cockpit Operacional, SEI & IA)

Ao selecionar **💼 Mesa de Trabalho** no menu lateral esquerdo, o usuário ingressa no ambiente de produção diária da SA-GTI. Este eixo reúne **7 Sub-Abas Superiores** que cobrem todo o ciclo de vida de instrução de um processo ou projeto.

---

### 5.1. Sub-aba 2.1: 🖥️ Mesa de Trabalho (Custódia) e seus 4 Filtros Rápidos

Projetada para responder imediatamente à pergunta: *"O que está sob minha responsabilidade hoje e qual é a minha prioridade?"*

#### Scorecards Individuais no Topo (4 Indicadores):
1. **📌 Processos sob Minha Custódia:** Total de processos atribuídos nominalmente ao usuário logado.
2. **🚨 Prazos Críticos na Semana:** Processos com *aging* elevado (> 90 dias) ou prazo fatal próximo que exigem despacho imediato.
3. **⏸️ Aguardando Retorno ("Poréns"):** Processos do usuário que estão com contagem de prazo interno suspensa aguardando manifestação externa (ex: CJ ou Fornecedor).
4. **🛡️ Eficiência Líquida Individual (%):** Percentual de demandas conduzidas dentro do SLA regulamentar da SA-GTI.

#### As 4 Pílulas de Filtro da Grade Operacional Unificada:
Na barra da tabela principal, o usuário pode comutar entre **4 filas de trabalho**:
1. **`📌 Minha Custódia`:** Exibe apenas os processos SEI atribuídos ao usuário logado.
2. **`⭐ Fixados / Acompanhamento`:** Exibe a *Watchlist* pessoal do usuário — processos que ele marcou com estrela (`⭐`) para acompanhar de perto, mesmo que estejam tramitando em outra área.
3. **`📦 Pacotes OpenProject`:** Lista os pacotes de trabalho do OpenProject sob responsabilidade ou acompanhamento do usuário, sem precisar sair da Mesa de Trabalho.
4. **`🎫 Chamados GLPI`:** Lista os tickets de suporte técnico vinculados à sua área de atuação.

#### Botões de Ação por Linha na Tabela:
Em cada processo listado na grade, os botões da coluna **Ações** permitem:
* **🔍 Ver Dossiê Completo:** Abre a ficha analítica detalhada do processo (histórico, resumo executivo, linha do tempo, bucket, status no OpenProject e pareceres anteriores).
* **🤖 Despachar com IA:** Abre o Assistente de IA já pré-carregado com todos os dados daquele processo SEI para redigir um despacho, parecer ou minuta em segundos.
* **⭐ Fixar / Desafixar:** Adiciona ou remove o processo da sua lista de acompanhamento prioritário.

#### Mural Lateral da Coordenação SA-GTI & Alertas IA:
No lado direito da Mesa de Trabalho, o mural exibe comunicados oficiais da gerência (ex: horários de *Sprint Planning*, avisos de fechamento de atestes PRODESP, novos decretos estaduais indexados pela IA e status do pipeline de agentes).

---

### 5.2. Sub-aba 2.2: 📂 Acervo SEI (Consulta Multicritério dos 179 Processos)

É o motor de busca e auditoria completa de todo o acervo processual da SA-GTI.

* **9 Filtros Multicritério Combináveis:**
  1. **Busca Textual Global:** Pesquisa simultânea por número do processo SEI (`000.00000000/202X-XX`), palavra-chave do objeto, nome do fornecedor ou nota técnica.
  2. **Filtro por Diretoria / Bacia Hidrográfica:** Isola demandas da Sede ou de bacias específicas (AT, BS, BPG, BP, BSM, BT, BTB, etc.).
  3. **Filtro por Responsável Técnico:** Filtra processos atribuídos a cada membro da equipe (ex: Luiz Seixeiro, Marcos, Diego, Rafael, etc.).
  4. **Filtro por Bucket Canônico (A-001 a A-018):** Filtra pelas 18 categorias temáticas da SA-GTI (ex: Contratação de Software, Infraestrutura de Rede, Telefonia, Governança, Segurança da Informação, etc.).
  5. **Filtro por Faixa de Criticidade (Farol 1 a 4):** Isola processos críticos, em saneamento, em monitoramento ou normais.
  6. **Filtro por Condição de "Porém" (Suspensão Externa):** Permite ver apenas processos travados externamente ou apenas processos sob custódia interna ativa.
  7. **Filtro por Vínculo com OpenProject:** Identifica quais processos já possuem card sincronizado no OpenProject.
  8. **Ordenação Dinâmica:** Por maior *aging* bruto, maior *aging* líquido, data de última movimentação ou criticidade.
  9. **Paginação Configurável:** Exibição de 10, 25, 50 ou todos os registros por página.
* **Exportação Oficial (`📄 Exportar CSV`):** Gera instantaneamente uma planilha estruturada (compatível com Excel e Google Sheets) contendo todos os registros filtrados em tela para relatórios de auditoria.

---

### 5.3. Sub-aba 2.3: 🤖 Assistente IA (Copiloto 360° & Escrita Controlada)

Central interativa de diálogo com o **Pool Multi-IA da SA-GTI**, conectada ao Gateway **New API (`:3001`)** e ao **Ollama (`:11434`)**.

#### Funcionalidades Principais do Assistente IA:
1. **Seletor de Agente Especializado:**
   * **Slot #1 — IA 1 Principal (`qwen2.5:14b` / `qwen2.5:7b`):** Especialista em diálogo executivo, consulta ao acervo SEI, elaboração de despachos, e-mails institucionais e redação de artefatos licitatórios.
   * **Slot #2 — IA 2 Orquestração (`qwen2.5-coder:7b`):** Especialista em governança técnica, conformidade com a Lei 14.133/2021 e Súmula 269 TCU, análise de pacotes de trabalho e gravação de dossiês no OpenProject.
   * **Slot #3 — IA 3 Microsserviços (`qwen2.5-coder:1.5b` / `llama3.2:1b`):** Respostas ultrarrápidas para triagem de tickets GLPI, resumos de pauta de Daily e checagens operacionais.
2. **Atalhos Rápidos de Governança Licitatória (1 Clique):**
   * **`📄 Elaborar DFD`:** Gera minuta completa de Documento de Formalização de Demanda alinhada ao PCA e ao PDTIC 2027–2030.
   * **`📊 Elaborar ETP`:** Estrutura o Estudo Técnico Preliminar com análise de cenários, viabilidade técnica e cálculo de TCO (Custo Total de Propriedade para 36 meses).
   * **`📋 Elaborar TR`:** Constrói a estrutura do Termo de Referência com catálogo de serviços em UST/PF, níveis mínimos de serviço (SLA), tabela de Instrumento de Medição de Resultados (IMR) e regime de glosas.
3. **Vínculo de Contexto em Tempo Real:**
   * Permite selecionar um **Processo SEI específico**, um **Card do OpenProject** ou documentos do **Drive Contexto IA** para que a resposta do agente seja 100% fundamentada nos dados reais do processo (zero respostas genéricas ou evasivas).
4. **Canal de Escrita Controlada no OpenProject (Dupla Confirmação):**
   * Quando o usuário pede no chat: *"Escreva no card #1498 o parecer técnico deste processo"* ou *"Altere o status do card #1497 para Em andamento"*, a IA **não altera o banco às cegas**. Ela gera a prévia completa do texto e exibe um cartão de confirmação com o botão **`[✅ Confirmar e Gravar no OpenProject]`**. Somente após o clique humano o backend envia a requisição autenticada via API v3.

---

### 5.4. Sub-aba 2.4: 📚 Cadernos & Toolkits (29 Documentos Homologados)

Biblioteca normativa e repositório oficial de modelos padronizados da SA-GTI.

* **O que contém:** 29 artefatos e regulamentos técnicos homologados, organizados por categoria:
  * **Artefatos da Lei Federal nº 14.133/2021:** Modelos canônicos de DFD, ETP, Mapa Comparativo de Preços, Matriz de Alocação de Riscos, Termo de Referência (Software, Nuvem, Infraestrutura e Links) e Pareceres de Aceite (TRP e TRD).
  * **Catálogos e Métricas (Súmula 269 TCU):** Catálogo de Unidades de Serviço Técnico (UST), Guia de Contagem de Pontos de Função (IFPUG) e Tabelas de IMR e Glosas.
  * **Normativos Internos e Estaduais:** Regimento Interno da SP-Águas, Deliberações do Comitê de Governança Digital, Política de Segurança da Informação (POSI), Diretrizes de Backup 3-2-1-1-0 e Plano Diretor de TIC (PDTIC 2027–2030).
* **Funcionalidades:**
  * Visualização integral do conteúdo formatado dentro da própria tela;
  * Busca rápida por título, tag ou base legal;
  * Botão **`📄 Gerar / Exportar PDF A4`** com cabeçalho institucional da SP-Águas;
  * Botão **`➕ Novo Caderno`** para cadastrar novas minutas ou normativos na biblioteca.

---

### 5.5. Sub-aba 2.5: 📊 Matrizes RACI (Governança de Responsabilidades)

Ferramenta dedicada ao mapeamento claro de papéis em cada macroprocesso e projeto crítico da SA-GTI, eliminando ambiguidades operacionais:

* **Metodologia RACI:**
  * **R (*Responsible* / Responsável pela Execução):** Quem executa diretamente a tarefa técnica ou instrução processual;
  * **A (*Accountable* / Aprovador / Dono):** Autoridade única que responde pela homologação e aceite final da entrega;
  * **C (*Consulted* / Consultado):** Especialistas ou áreas (ex: DMO, CJ, Segurança) consultadas antes da decisão;
  * **I (*Informed* / Informado):** Partes mantidas atualizadas sobre o avanço ou conclusão da entrega.
* **Funcionalidades:** Permite visualizar as matrizes existentes (Contratações de TIC, Sustentação de Infraestrutura/NOC, Desenvolvimento e Fábrica de Software), filtrar por servidor ou divisão, criar novas linhas de responsabilidade e exportar a matriz para documentação de projetos.

---

### 5.6. Sub-aba 2.6: 📑 Relatórios Daily & Sprints (Acervo de Rituais)

Repositório histórico e auditável de todas as reuniões ágeis realizadas pela equipe da SA-GTI:

* **Tipos de Registros Armazenados:**
  * Atas de **Daily Scrum** (reuniões diárias de 15 minutos);
  * Relatórios de **Sprint Planning** (planejamento de metas da semana/quinzena);
  * Relatórios de **Sprint Review & Retrospective** (balanço de entregas concluídas e lições aprendidas).
* **Ações Disponíveis em Cada Relatório:**
  * **👁️ Visualizar / Imprimir PDF:** Abre a ata diagramada no padrão oficial da SP-Águas pronta para impressão ou salvamento em PDF;
  * **✏️ Editar Registro:** Permite complementar deliberações, corrigir participantes ou atualizar o status de ações pendentes;
  * **⭐ Fixar no Topo:** Mantém atas prioritárias destacadas no início da lista;
  * **🗑️ Excluir:** Remove registros de teste (restrito a perfis autorizados).

---

### 5.7. Sub-aba 2.7: 🗂️ Drive Contexto IA (Base RAG em PDF)

Repositório de arquivos **PDF de referência técnica e documental** que alimentam a memória contextual (*Retrieval-Augmented Generation — RAG*) dos agentes de IA (Slot #1 e Slot #2).

* **Objetivo:** Permitir que o usuário anexe editais, contratos assinados, termos de referência antigos, acórdãos do TCE-SP/TCU ou manuais técnicos em PDF para que as IAs consultem o texto exato desses documentos durante a geração de pareceres.
* **Funcionalidades:**
  * Listagem dos PDFs indexados com tamanho, data de inclusão, categoria e status de vetorização/leitura;
  * Seleção de quais documentos devem permanecer ativos no contexto global do chat;
  * Filtro por tipo documental e visualização rápida dos metadados extraídos.

---

## 6. EIXO 3 — Módulo War Room & Rituais Ágeis

Ao clicar em **🤝 War Room** no menu lateral esquerdo, a equipe acessa o ambiente colaborativo desenhado para reuniões de alinhamento, tomada de decisão rápida e gestão visual de entregas. Possui **2 Sub-Abas Superiores**.

---

### 6.1. Sub-aba 3.1: 👥 War Room: Daily & Rituais (Timebox 15m)

Ambiente interativo projetado para projetar na tela da sala de reuniões (ou compartilhar em videoconferência) durante o ritual diário da equipe SA-GTI.

#### Componentes da Sala de Guerra (War Room):
1. **⏱️ Cronômetro Regressivo de 15 Minutos (Timebox Oficial):**
   * Possui botões **`▶️ Iniciar`**, **`⏸️ Pausar`** e **`🔄 Reiniciar (15:00)`**.
   * Muda automaticamente de cor conforme o tempo avança (Verde ➔ Amarelo nos últimos 5 minutos ➔ Vermelho piscante no último minuto), mantendo a reunião focada e objetiva.
2. **📋 Seletor de Pauta Multissistêmica (3 Fontes Integradas):**
   * Permite puxar itens reais para a pauta do dia a partir de **3 abas de origem**:
     * **`📂 Processos SEI`:** Seleciona processos críticos ou com *aging* elevado para cobrar posicionamento na reunião;
     * **`🏗️ Pacotes OpenProject`:** Seleciona tarefas e marcos da Sprint ativa;
     * **`🎫 Chamados GLPI`:** Seleciona tickets urgentes de suporte ou infraestrutura que exigem ação coordenada.
3. **📌 Mural Colaborativo de Post-its (4 Categorias):**
   * Permite criar cartões rápidos durante a fala dos participantes, classificados por cor e tipo:
     * 🟥 **Impedimento / "Porém" Crítico** (bloqueios técnicos ou administrativos);
     * 🟨 **Lembrete / Atenção** (prazos de faturas, janelas de manutenção);
     * 🟦 **Decisão de Governança** (deliberações tomadas pela gerência na reunião);
     * 🟩 **Plano de Ação / Próximo Passo** (tarefa atribuída com responsável e prazo).
4. **📄 Fechamento do Ritual e Geração de Ata:**
   * Ao final dos 15 minutos, o botão **`📄 Gerar Ata Oficial da Daily (PDF)`** compila automaticamente a data, horário, participantes presentes, itens debatidos na pauta, post-its de impedimentos e plano de ação em um documento formal, salvando-o também na sub-aba *Relatórios Daily & Sprints*.

---

### 6.2. Sub-aba 3.2: 🏃 Gestão Ágil & Sprints (Quadro Kanban Interativo)

Quadro **Kanban** visual e interativo para gestão do fluxo de trabalho semanal/quinzenal da SA-GTI, integrado aos pacotes do OpenProject e aos processos do SEI.

* **Colunas do Quadro Kanban:**
  * **📥 Backlog / A Fazer:** Demandas priorizadas para a Sprint atual aguardando início de execução;
  * **⚡ Em Andamento (WIP):** Itens em execução ativa pela equipe técnica (com controle visual de limite de *Work In Progress*);
  * **⏸️ Em Espera / Revisão / "Poréns":** Demandas aguardando validação da gerência, homologação de área demandante ou retorno externo;
  * **✅ Concluído (Done):** Entregas finalizadas e homologadas dentro do ciclo da Sprint.
* **Recursos Operacionais do Kanban:**
  * **Arrastar e Soltar (*Drag-and-Drop*):** Mova cartões entre colunas com atualização imediata de status;
  * **Filtro por Responsável e por Sprint:** Selecione um analista específico ou comute entre Sprints para focar apenas nas entregas daquela pessoa ou semana;
  * **Sincronização com OpenProject:** Botão para refletir o status e os comentários dos cartões diretamente nos *Work Packages* correspondentes no servidor OpenProject.

---

## 7. EIXO 4 — Módulo Configurações & Governança Técnica

Ao clicar em **⚙️ Configurações** no menu lateral esquerdo, os administradores acessam o centro de controle técnico da plataforma, organizado em **7 Sub-Abas Internas** (pílulas superiores).

---

### 7.1. Sub-aba 4.1: 👥 Gestão de Usuários & Perfis

* **Objetivo:** Cadastrar e administrar as contas dos servidores e colaboradores que acessam o Cockpit GTI.
* **Funcionalidades:**
  * Tabela completa com Nome, E-mail Institucional (`@spaguas.sp.gov.br`), Cargo/Unidade (SA-GTI, DIF, DGD, Bacias), Perfil Primário, Perfis Secundários Habilitados e Status (`Ativo` / `Inativo`);
  * Botão **`➕ Novo Usuário`** e modal de edição para atribuir múltiplos perfis (permitindo que gestores alternem entre visões na barra lateral).

---

### 7.2. Sub-aba 4.2: 🛡️ Perfis de Acesso & RBAC

* **Objetivo:** Auditar e parametrizar a matriz de controle de acesso baseado em papéis (*Role-Based Access Control*).
* **Funcionalidades:** Exibe a tabela comparativa de permissões entre **Super-Admin**, **Gestor**, **Analista** e **Demandante**, demonstrando visualmente quais módulos, botões de escrita, exportações e configurações estão liberados ou bloqueados para cada perfil.

---

### 7.3. Sub-aba 4.3: ⚖️ Parâmetros de Gestão, Aging & Sprints

* **Objetivo:** Calibrar as regras de negócio que governam os cálculos automáticos do Cockpit GTI.
* **Parâmetros Configuráveis:**
  * **Limiares de Faixas de Aging (Faróis SEI):** Definição da quantidade de dias para mudança automática de cor (ex: Verde até 30 dias, Amarelo de 31 a 60 dias, Laranja de 61 a 90 dias, Vermelho acima de 90 dias);
  * **Regras de Expurgo de "Poréns":** Ativação/desativação do desconto automático de dias em suspensões externas;
  * **Cadência de Rituais Ágeis:** Duração padrão da Sprint (1 ou 2 semanas), tempo do cronômetro da Daily (15 minutos) e limite máximo de tarefas simultâneas (*WIP Limit*) por analista.

---

### 7.4. Sub-aba 4.4: 🔌 Conectores & Varredura Sistêmica (11 Motores)

Central de monitoramento de integrações e robôs de coleta de dados da plataforma, dividida em **2 sub-visões**:

1. **📡 Matriz de Conectores e Status dos Motores:**
   * Monitora o estado operacional, protocolo, porta, frequência de sincronização e latência dos motores integrados:
     1. **Motor #1 — SEI-SP / DOE-SP:** Ingestão de processos e publicações no Diário Oficial do Estado;
     2. **Motor #2 — Gateway New API (`:3001`) / Ollama (`:11434`):** Orquestrador de modelos locais de IA;
     3. **Motor #3 — OpenProject API v3 (`:443` / `:8090`):** Sincronização de projetos e pacotes de trabalho;
     4. **Motor #4 — GLPI 10 REST API (`:443` / `:8088`):** Coleta de chamados ITSM e inventário CMDB;
     5. **Motor #5 — MariaDB Local (`:3306`):** Persistência relacional e cache estruturado;
     6. **Motores #6 a #11 — Fontes Regulatórias Externas:** PNCP (Portal Nacional de Contratações Públicas), TCE-SP, SIGRH, Portal SP-Águas e Zabbix/Telemetria.
   * **Botões de Ação:** Permite executar **`⚡ Ciclo de Varredura Multissistêmica`**, testar conectividade individual, pausar/ativar um motor ou editar seu endpoint (`⚙️ Editar Motor`).
2. **🔧 Configurações Avançadas de Endpoints e Tokens:**
   * Painel para informar/atualizar o Token de API do OpenProject, URL base do GLPI, credenciais de leitura e ativação/pausa do agendador automático horário.

---

### 7.5. Sub-aba 4.5: 🤖 Pool Multi-IA & Agentes Especializados

Painel de engenharia e calibração em tempo real dos **Agentes de Inteligência Artificial** do Cockpit GTI.

#### Estrutura de Cada Cartão de Agente (Slot #1, Slot #2 e Slot #3):
Para cada agente do pool, o administrador pode configurar de forma independente:
* **Nome do Agente:** Identificação funcional do slot;
* **Modelo da IA (`model`):** Nome exato do modelo carregado no Ollama/New API (ex: `qwen2.5:14b`, `qwen2.5-coder:7b`, `qwen2.5-coder:1.5b`, `llama3.2:1b`, `deepseek-r1:14b`);
* **Endpoint Base:** Endereço do gateway OpenAI-compatível (padrão oficial na rede/container: `http://100.103.100.98:3001/v1`);
* **API Key Individual (`sk-...`):** Chave de autenticação gerada no New API (com botão `👁️` para exibir/ocultar);
* **Prompt do Agente / Instruções Especializadas (*System Prompt*):** Diretrizes comportamentais e normativas injetadas em todas as respostas daquele agente;
* **Hiperparâmetros Técnicos:**
  * `TEMP` (Temperatura: `0.0` para máxima precisão determinística e zero alucinação em textos jurídicos/técnicos);
  * `MAX TOK` (Limite de tokens gerados por resposta, ex: `1024` ou `2048`);
  * `TIMEOUT (S)` (Tempo limite de espera da requisição, ex: `15s`).

#### Botões de Diagnóstico e Persistência:
* **`⚡ Testar este Agente`:** Dispara um *ping* real via backend (`/api/v1/ia/testar_slot`) até o modelo configurado no New API/Ollama, medindo o tempo de resposta em milissegundos e exibindo o selo **`🟢 OK (modelo • XXms)`** ou o código HTTP exato em caso de falha.
* **`💾 Salvar Configuração do Pool`:** Grava todos os parâmetros no navegador (`localStorage`) e no arquivo `config_pool_ias.json` do servidor backend (`POST /api/v1/ia/pool`).

---

### 7.6. Sub-aba 4.6: 💾 Backup, Resiliência & DRP (Regra 3-2-1-1-0)

Painel de governança de continuidade de negócios e proteção dos dados da plataforma:

* **Conformidade com a Regra Canônica 3-2-1-1-0:**
  * **3** cópias dos dados críticos (`processos.json`, `config_pool_ias.json`, atas, matrizes RACI e banco do New API);
  * **2** mídias/camadas distintas (volumes Docker e diretório físico persistente em disco);
  * **1** cópia fora do ambiente de execução (repositório remoto versionado e snapshots exportáveis);
  * **1** cópia imutável / *offline* de segurança;
  * **0** erros nos testes de verificação de integridade e restauração (*Restore*).
* **Funcionalidades:** Permite gerar e baixar um **Snapshot Completo do Estado do Cockpit (JSON/ZIP)** com 1 clique e restaurar configurações anteriores em caso de migração de máquina.

---

### 7.7. Sub-aba 4.7: 📖 Documentação Oficial Integrada

Central de conhecimento embutida na própria plataforma para consulta imediata sem precisar sair do Cockpit:
* **Sub-aba 1 — 📘 Manual do Usuário:** Guia operacional e executivo completo;
* **Sub-aba 2 — ⚙️ Documentação Técnica & Arquitetura:** Especificações de engenharia, APIs, Docker e integrações;
* **Sub-aba 3 — 🐙 Repositório GitHub & Estrutura do Projeto:** Árvore de arquivos, comandos Git/Docker e atalho direto para o repositório oficial no GitHub.

---

## 8. Roteiros Práticos do Dia a Dia (Passo a Passo)

### Roteiro 1: Como auditar seus processos urgentes e gerar uma minuta de TR/ETP com IA
1. No menu lateral esquerdo, clique em **💼 Mesa de Trabalho**.
2. Na grade principal, mantenha selecionada a pílula **`📌 Minha Custódia`** (ou clique em **`📂 Acervo SEI`** na barra superior para pesquisar qualquer processo da gerência).
3. Localize o processo desejado e clique no botão **`🤖 Despachar com IA`** na coluna *Ações* (ou acesse a sub-aba **`🤖 Assistente IA`**).
4. Com o processo vinculado, clique em um dos botões de ação rápida no topo do chat: **`📄 Elaborar DFD`**, **`📊 Elaborar ETP`** ou **`📋 Elaborar TR`**.
5. A **IA 1 (`qwen2.5:14b`)** redigirá a minuta completa estruturada segundo a Lei 14.133/2021 e os dados reais do processo. Copie o texto com 1 clique para colar diretamente no SEI!.

### Roteiro 2: Como conduzir a Daily Scrum de 15 minutos e emitir a Ata em PDF
1. No menu lateral esquerdo, clique em **🤝 War Room**.
2. Na sub-aba **`👥 War Room: Daily & Rituais`**, clique em **`▶️ Iniciar`** no cronômetro regressivo de 15 minutos.
3. No painel de pauta, alterne entre as abas **`📂 SEI`**, **`🏗️ OpenProject`** e **`🎫 GLPI`** para selecionar os itens que serão discutidos pela equipe.
4. Durante a reunião, registre impedimentos ou decisões no **Mural de Post-its**.
5. Ao encerrar, clique em **`📄 Gerar Ata Oficial da Daily (PDF)`** para emitir o documento formatado no padrão da SP-Águas.

### Roteiro 3: Como homologar um Dossiê Técnico e gravá-lo em um Card do OpenProject
1. Acesse **💼 Mesa de Trabalho** ➔ sub-aba **`🤖 Assistente IA`**.
2. Selecione o **Slot #2 (IA 2 — Orquestração `qwen2.5-coder:7b`)** e peça: *"Elabore e grave o dossiê de governança atualizado no card #1498 do OpenProject"*.
3. A IA exibirá a minuta do dossiê em tela e apresentará o botão verde **`[✅ Confirmar e Gravar]`**.
4. Revise o texto e clique no botão de confirmação para que o backend atualize a descrição e registre o comentário na *timeline* do pacote no OpenProject.

### Roteiro 4: Como trocar ou testar os modelos de IA no Notebook (Docker Desktop)
1. Certifique-se de que a stack unificada `cockpit-gti` está rodando no Docker Desktop (`cockpit-gti-backend`, `cockpit-gti-newapi` e `cockpit-gti-ollama`).
2. Caso tenha baixado um novo modelo no Ollama (ex: `ollama pull qwen2.5:14b`), acesse o **New API** em `http://localhost:3001/`, adicione a etiqueta do modelo no Canal do grupo **SP - ÁGUAS** e garanta que o seu Token tenha permissão para todos os modelos.
3. No Cockpit GTI (`http://localhost:5000/`), vá em **⚙️ Configurações** ➔ **`🤖 Pool de IAs`**.
4. Informe o nome do modelo no Slot desejado, mantenha o endpoint em `http://100.103.100.98:3001/v1` e clique em **`⚡ Testar este Agente`**.
5. Confirmado o retorno **`🟢 OK`**, clique em **`💾 Salvar Configuração do Pool`**.

---

## 9. Glossário de Termos Técnicos e Administrativos da SP-Águas

* **Aging Bruto:** Tempo total corrido (em dias) desde a abertura ou chegada do processo administrativo na unidade.
* **Aging Líquido:** Tempo efetivo sob responsabilidade interna da SA-GTI, descontados os períodos de suspensão externa (*Poréns*).
* **CMDB (*Configuration Management Database*):** Base de dados de gerenciamento de configuração no GLPI 10 que inventaria todos os ativos de hardware e software da autarquia.
* **DFD (Documento de Formalização de Demanda):** Artefato inaugural da contratação pública (Lei 14.133/2021) que justifica a necessidade da área requisitante e vincula a demanda ao PCA.
* **ETP (Estudo Técnico Preliminar):** Documento que demonstra a viabilidade técnica e econômica da contratação, comparando soluções de mercado e apurando o TCO.
* **IMR (Instrumento de Medição de Resultados):** Mecanismo contratual de aferição de qualidade e disponibilidade (SLAs) que vincula o pagamento da contratada ao atingimento de metas objetivas, aplicando glosas em caso de descumprimento.
* **New API (`:3001`):** Gateway centralizador que gerencia chaves de acesso (`sk-...`), canais, cotas e roteamento para múltiplos modelos de Inteligência Artificial utilizando o padrão de API da OpenAI.
* **Ollama (`:11434`):** Motor de execução local de Grandes Modelos de Linguagem (LLMs) como *Qwen 2.5*, *Llama 3.2* e *DeepSeek R1*, rodando diretamente no hardware do servidor/notebook.
* **PDTIC (Plano Diretor de Tecnologia da Informação e Comunicação):** Instrumento de planejamento estratégico plurianual (2027–2030) que alinha as iniciativas e investimentos de TIC aos objetivos institucionais da SP-Águas.
* **Regra Jurídica dos "Poréns":** Critério de governança processual da SA-GTI que identifica e isola processos cujo andamento depende de ato externo à gerência (ex: parecer da Consultoria Jurídica, resposta de fornecedor, homologação de diretoria ou análise de órgão de controle).
* **Súmula 269 do TCU:** Jurisprudência do Tribunal de Contas da União que determina que as contratações de serviços de TI devem ser vinculadas a resultados e métricas objetivas (como Pontos de Função ou UST), vedando a remuneração por mera alocação de horas/postos sem medição de entregas.
* **TR (Termo de Referência):** Documento técnico vinculante do edital que especifica o objeto, requisitos técnicos, modelo de execução, gestão do contrato, critérios de medição/pagamento e sanções.
* **Work Package (Pacote de Trabalho):** Unidade rastreável de entrega, tarefa, fase ou marco dentro de um projeto no sistema OpenProject.
