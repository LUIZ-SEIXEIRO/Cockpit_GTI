
## Relatório de Auditoria Funcional das Abas do Cockpit SP-Aguas (SA-GTI)

**Data da Auditoria:** 26 de Outubro de 2023
**Auditor:** Arquiteto/Tech Lead SA-GTI
**Objetivo:** Avaliar a situação funcional atual de cada uma das 15 abas do `frontend/painel.html` em termos de origem de dados, renderização e interatividade, identificando pontos de atenção para a integração com as APIs REST.

---

### Tabela Resumo Executivo

| Aba | Título da Aba | Origem dos Dados (Status Atual Inferido) | Status Operacional (Inferido) | Ações de Correção Recomendadas (Prioridade Alta) |
| :-- | :---------------------------------- | :--------------------------------------- | :-------------------------- | :----------------------------------------------- |
| 01  | Central de Dashboards 360°          | Mock Inline / `window.DASH_DATA`         | 🟡 Funcional com Dados Mockados | Integração com APIs de métricas diversas.        |
| 02  | Portfólio OpenProject               | `window.OP_PACOTES_OFICIAIS` (Estático)  | 🟡 Funcional com Dados Mockados | Integração com `/api/v1/openproject/pacotes`. |
| 03  | SA-GTI Tracks & Projetos            | Mock Inline / `window.TRACKS_DATA`       | 🟡 Funcional com Dados Mockados | Integração com API de projetos internos.         |
| 04  | PDTIC 2027-2030, 5 Eixos e KPIs     | Mock Inline / `window.PDTIC_KPIs`        | 🟡 Funcional com Dados Mockados | Integração com API de gestão de metas.          |
| 05  | Gestão GLPI 10 & Helpdesk ITSM      | `window.CHAMADOS_ITSM_SUPORTE` (Estático) | 🟡 Funcional com Dados Mockados | Integração com `/api/v1/glpi/chamados`.         |
| 06  | Visão Estratégica & Faróis          | Mock Inline / `window.FAROIS_DATA`       | 🟡 Funcional com Dados Mockados | Integração com API de visão estratégica.         |
| 07  | Mesa de Trabalho Operacional        | `window.PROCESSOS` (Estático/Mock)       | 🟡 Funcional com Dados Mockados | Integração com `/api/v1/sei/processos`.         |
| 08  | Gestão Ágil & Sprint Planning       | Mock Inline / `window.KANBAN_DATA`       | 🟡 Funcional com Dados Mockados | Integração com API de gestão ágil (OpenProject/Jira). |
| 09  | War Room: Daily Scrum & Gestão Pauta| Mock Inline / `window.PAUTA_DATA`        | 🟡 Funcional com Dados Mockados | Integração com API de pauta de reunião.          |
| 10  | Acervo Probatório SEI               | `window.PROCESSOS` (Estático/Mock)       | 🟡 Funcional com Dados Mockados | Integração com `/api/v1/sei/processos`.         |
| 11  | Processos Fixados                   | `window.PROCESSOS` (Subset/Mock)         | 🟡 Funcional com Dados Mockados | Integração com `/api/v1/sei/fixados`.           |
| 12  | Auditoria TCE-SP & IMR              | Mock Inline / `window.AUDITORIA_DATA`    | 🟡 Funcional com Dados Mockados | Integração com `/api/v1/auditoria/tce-tcu`.     |
| 13  | Chat IA & RACI                      | `window.chamarNewApiClosedWorld` (Mock/Placeholder) | 🔴 Requer Correção / Atenção | Implementar `POST /api/v1/ia/processar`.        |
| 14  | Cadernos Temáticos, Regimento & Modelos | Static HTML / LocalStorage | 🟢 100% Funcional (Estático) | N/A (Se conteúdo é estático, não requer API)     |
| 15  | Central de Configurações            | LocalStorage / Forms HTML                | 🟢 100% Funcional (Estático) | N/A (Ações locais ou POST diretos, se aplicável) |

---

### Detalhes da Auditoria por Aba

#### Aba 01 (view-dashboards): Central de Dashboards 360° e gráficos ApexCharts
*   **Origem dos Dados:** Provavelmente dados mockados diretamente no HTML ou em uma variável `window.DASH_DATA` preenchida estaticamente. Os gráficos ApexCharts seriam inicializados com esses dados.
*   **Funções de Renderização:** Espera-se uma função como `renderDashboardAba01()` que inicializa e atualiza os gráficos ApexCharts com os dados disponíveis.
*   **Interatividade (Filtros, Modais e Botões):** Pode haver seletores de período, filtros por métrica. É provável que os handlers existam, mas operem sobre os dados mockados, sem uma nova chamada API.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Mapear quais gráficos/dashboards requerem dados dinâmicos.
    *   Criar endpoints REST para cada tipo de dado (ex: `/api/v1/dashboards/metricas_diarias`).
    *   Modificar `renderDashboardAba01()` para fazer `fetch()` assíncrono e atualizar os gráficos.
    *   Implementar indicadores de carregamento durante a busca de dados.

#### Aba 02 (view-portfolio_openproject): Portfólio OpenProject (500 pacotes / 29 projetos)
*   **Origem dos Dados:** `window.OP_PACOTES_OFICIAIS` (500 pacotes estáticos) conforme mencionado.
*   **Funções de Renderização:** Espera-se `renderPortfolioOpenProject()` ou similar, que itera sobre `window.OP_PACOTES_OFICIAIS` para construir a tabela ou cards. `window.filtrarPortfolioOpenProject()` para aplicar filtros.
*   **Interatividade (Filtros, Modais e Botões):** Filtros por status, gerente, prazo. Os handlers para estes filtros devem existir, mas apenas filtram os dados estáticos em memória.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Integrar com `GET /api/v1/openproject/pacotes` para atualizar `window.OP_PACOTES_OFICIAIS`.
    *   Manter a lógica de fallback para os 500 pacotes estáticos em caso de falha da API.
    *   Garantir que `window.filtrarPortfolioOpenProject()` seja chamada após a hidratação.

#### Aba 03 (view-tracks_sagti): SA-GTI Tracks & Projetos (Track 1 Operação e Track 2 Renegociação)
*   **Origem dos Dados:** Provavelmente dados mockados ou estáticos em uma variável `window.TRACKS_DATA`.
*   **Funções de Renderização:** Função como `renderTracksSA_GTI()` que exibe o progresso ou detalhes dos projetos.
*   **Interatividade (Filtros, Modais e Botões):** Pode haver botões para expandir detalhes ou filtros básicos.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Definir endpoint REST para dados de Tracks (ex: `/api/v1/sagti/tracks`).
    *   Integrar e atualizar a interface dinamicamente.

#### Aba 04 (view-pdtic_eixos): PDTIC 2027-2030, 5 Eixos e KPIs (KPI-001 a KPI-008)
*   **Origem dos Dados:** Mock inline ou variável `window.PDTIC_KPIs`.
*   **Funções de Renderização:** `renderPDTIC_KPIs()` ou similar para exibir as tabelas de KPIs e seus status.
*   **Interatividade (Filtros, Modais e Botões):** Navegação entre eixos, talvez filtros de período para KPIs.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Definir endpoint REST para dados de KPIs do PDTIC (ex: `/api/v1/pdtic/kpis`).
    *   Integrar e atualizar a interface.

#### Aba 05 (view-gestao_glpi): Gestão GLPI 10 & Helpdesk ITSM
*   **Origem dos Dados:** `window.CHAMADOS_ITSM_SUPORTE` (provavelmente estático ou mockado inicialmente).
*   **Funções de Renderização:** `renderTabelaGlpiChamados()` ou similar. `window.filtrarTabelaGlpi()` para filtros.
*   **Interatividade (Filtros, Modais e Botões):** Filtros por status, categoria, responsável, prioridade. Botões para abrir detalhes do chamado (modais).
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Integrar com `GET /api/v1/glpi/chamados` para atualizar `window.CHAMADOS_ITSM_SUPORTE`.
    *   Garantir que `window.filtrarTabelaGlpi()` seja chamada após a hidratação.
    *   Considerar a implementação de modais para detalhes de chamados.

#### Aba 06 (view-visao_estrategica): Visão Estratégica & Faróis (Custódia vs. Poréns)
*   **Origem dos Dados:** Mock inline ou variável `window.FAROIS_DATA`.
*   **Funções de Renderização:** `renderVisaoEstrategica()` que exibe um painel de faróis com indicadores.
*   **Interatividade (Filtros, Modais e Botões):** Interatividade para drill-down em faróis específicos.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Definir endpoint REST para dados da Visão Estratégica (ex: `/api/v1/estrategia/farois`).
    *   Integrar e atualizar a interface dinamicamente.

#### Aba 07 (view-mesa_trabalho): Mesa de Trabalho Operacional — Luiz Seixeiro
*   **Origem dos Dados:** `window.PROCESSOS` (compartilhado com SEI, provavelmente estático/mockado).
*   **Funções de Renderização:** Uma função dedicada a renderizar os itens da mesa de trabalho, que pode ser um subconjunto ou uma visão diferente de `window.PROCESSOS`. Ex: `renderMesaTrabalho()`.
*   **Interatividade (Filtros, Modais e Botões):** Botões de ação rápida (ex: "Visualizar SEI", "Arquivar"), filtros de prioridade.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Integrar com `GET /api/v1/sei/processos` e `GET /api/v1/sei/fixados`.
    *   Garantir que a renderização da mesa de trabalho seja atualizada após a hidratação de `window.PROCESSOS`.

#### Aba 08 (view-gestao_agil): Gestão Ágil & Sprint Planning (Kanban)
*   **Origem dos Dados:** Mock inline ou variável `window.KANBAN_DATA`.
*   **Funções de Renderização:** `renderKanbanBoard()` que constrói o quadro Kanban.
*   **Interatividade (Filtros, Modais e Botões):** Drag-and-drop de cards, filtros por membro da equipe, status da sprint, etc. Muitos handlers provavelmente presentes, mas operam localmente.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Definir endpoint REST para dados de gestão ágil (ex: `/api/v1/agil/kanban`).
    *   Implementar APIs para atualização de estado (POST/PUT para mover cards).
    *   Integrar com sistema externo (OpenProject, se for o caso).

#### Aba 09 (view-daily_warroom): War Room: Daily Scrum & Gestão de Pauta (15 min)
*   **Origem dos Dados:** Mock inline ou variável `window.PAUTA_DATA`.
*   **Funções de Renderização:** `renderDailyScrum()` que apresenta itens de pauta, participantes, tempos.
*   **Interatividade (Filtros, Modais e Botões):** Botões para avançar na pauta, marcar itens como concluídos.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Definir endpoint REST para dados de Daily Scrum (ex: `/api/v1/warroom/daily`).
    *   Implementar APIs para gestão da pauta (POST/PUT).

#### Aba 10 (view-consulta): Acervo Probatório SEI (179 processos)
*   **Origem dos Dados:** `window.PROCESSOS` (estático/mockado).
*   **Funções de Renderização:** `renderTabelaSeiProcessos()` que preenche a tabela de processos.
*   **Interatividade (Filtros, Modais e Botões):** Filtros por número, assunto, interessado. Botão para visualização detalhada do processo (link externo ou modal).
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Integrar com `GET /api/v1/sei/processos` para atualizar `window.PROCESSOS`.
    *   Garantir a atualização da renderização após a hidratação.

#### Aba 11 (view-fixados): Processos Fixados (Watchlist Prioritária)
*   **Origem dos Dados:** Um subconjunto de `window.PROCESSOS` ou uma variável separada `window.PROCESSOS_FIXADOS` (estático/mockado).
*   **Funções de Renderização:** `renderProcessosFixados()` que exibe a watchlist prioritária.
*   **Interatividade (Filtros, Modais e Botões):** Botões para remover da watchlist, adicionar notas.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Integrar com `GET /api/v1/sei/fixados` para atualizar `window.PROCESSOS_FIXADOS`.
    *   Implementar lógica para "fixar" e "desafixar" processos via API (POST/DELETE `/api/v1/sei/fixados`).

#### Aba 12 (view-auditoria): Auditoria TCE-SP & IMR (Súmula 269 TCU)
*   **Origem dos Dados:** Mock inline ou variável `window.AUDITORIA_DATA`.
*   **Funções de Renderização:** `renderPainelAuditoria()` que exibe o painel de conformidade e a tabela de pontos de controle.
*   **Interatividade (Filtros, Modais e Botões):** Filtros por tipo de auditoria, período, status de conformidade.
*   **Status Operacional:** 🟡 Funcional com Dados Mockados
*   **Ações de Correção Recomendadas:**
    *   Integrar com `GET /api/v1/auditoria/tce-tcu` para popular os dados.
    *   Garantir que a renderização de painel e tabela seja atualizada.

#### Aba 13 (view-esteira_ia): Chat IA & RACI (Motor 4 Camadas / New API :3001)
*   **Origem dos Dados:** Interação via `window.chamarNewApiClosedWorld` (atual placeholder ou função mockada). A UI provavelmente já existe para exibir histórico de chat.
*   **Funções de Renderização:** Funções para adicionar mensagens do usuário e respostas da IA ao histórico do chat.
*   **Interatividade (Filtros, Modais e Botões):** Campo de entrada de texto, botão de envio, histórico de mensagens.
*   **Status Operacional:** 🔴 Requer Correção / Atenção
*   **Ações de Correção Recomendadas:**
    *   Interceptar `window.chamarNewApiClosedWorld` no `conector_api.js` para chamar `POST /api/v1/ia/processar`.
    *   Implementar exibição do tempo de inferência e motor utilizado na UI do chat.
    *   Tratamento de erros robusto para falhas na API de IA.

#### Aba 14 (view-cadernos): Cadernos Temáticos, Regimento & Modelos A4
*   **Origem dos Dados:** Provavelmente links estáticos, iframes para PDFs ou conteúdo HTML predefinido. Pode usar `localStorage` para últimas visualizações.
*   **Funções de Renderização:** `renderCadernos()` que lista os cadernos ou carrega o conteúdo.
*   **Interatividade (Filtros, Modais e Botões):** Botões para abrir documentos, filtros por categoria.
*   **Status Operacional:** 🟢 100% Funcional (Estático)
*   **Ações de Correção Recomendadas:**
    *   N/A para integração com API neste momento, a menos que haja um repositório de documentos dinâmico a ser integrado futuramente.

#### Aba 15 (view-configuracoes): Central de Configurações, 5 Sub-abas (RBAC, Aging, Conectores, IAs, Backup)
*   **Origem dos Dados:** Provavelmente formulários HTML com valores padrão ou preenchidos de `localStorage`.
*   **Funções de Renderização:** `renderConfiguracoes()` e funções específicas para cada sub-aba.
*   **Interatividade (Filtros, Modais e Botões):** Campos de entrada, botões "Salvar", "Testar Conexão", "Executar Backup". Ações de salvar provavelmente usam `localStorage` ou enviam formulários POST diretos.
*   **Status Operacional:** 🟢 100% Funcional (Estático)
*   **Ações de Correção Recomendadas:**
    *   Para configurações que interagem com o backend (conectores, IAs), implementar `GET`/`POST`/`PUT` para `/api/v1/configuracoes/...` endpoints.
