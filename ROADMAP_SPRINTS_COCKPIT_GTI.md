# 🧭 SP Águas - Cockpit de Gestão Centralizada e Automatizada
## Roadmap de Engenharia de Software e Backlog Priorizado (6 Sprints)

### 🏗️ Visão Geral da Arquitetura
- **Infraestrutura:** Docker Desktop no disco H: (\Cockpit-GTI\) orquestrando FastAPI (:8000), GLPI (:8088), OpenProject (:8090), New API (:3001) e MariaDB (:3306).
- **Backend:** Servidor central em Python FastAPI com conectores de Sistemas Internos (Grupo A) e Busca Ativa Externa (Grupo B - Zero CORS).
- **IA Gateway (New API :3001):** Orquestrador de failover em 3 níveis (IA 01 - Alto Desempenho, IA 02 - RAG/Orquestração, IA 03 - Micro-tarefas).
- **Frontend SPA:** Single Page Application (painel.html, estilo_spaguas.css, 00_roteador_abas.js) integrando 14 abas modulares de gestão e auditoria.

---

## 📅 Divisão em Sprints Incrementais

### 🚀 Sprint 1: Fundação de Infraestrutura e Backend Central
- **Meta da Sprint:** Estabelecer a conectividade do FastAPI com o MariaDB, criar o healthcheck de serviços e garantir que a casca do painel.html seja servida na porta :8000.
- **Backlog Priorizado:**
  - [ ] **US-1.1:** Criar modulo 'database_mariadb.py' com pool de conexões assíncronas e leitura de variáveis do .env.
  - [ ] **US-1.2:** Implementar rota 'GET /api/v1/healthcheck' validando o status do MariaDB, New API e Docker.
  - [ ] **US-1.3:** Configurar o FastAPI ('main.py') para servir os arquivos estáticos do frontend (painel.html, estilo_spaguas.css).
- **Critério de Aceite:** Acessar 'http://localhost:8000/' e visualizar o painel.html com o healthcheck respondendo '200 OK'.

### 🤖 Sprint 2: Hub de Inteligência Artificial e Failover Multi-Agente
- **Meta da Sprint:** Estruturar a esteira de IA com New API (:3001) e os 3 agentes especializados.
- **Backlog Priorizado:**
  - [ ] **US-2.1:** Implementar orquestrador 'ia_01_principal_processamento.py' para análise de ETP, TR e minutas.
  - [ ] **US-2.2:** Implementar 'ia_02_orquestracao_intermediario.py' para RAG e organização de tarefas.
  - [ ] **US-2.3:** Implementar 'ia_03_micro_tarefas_log.py' (~0.4 GB RAM) para classificação rápida de chamados.
  - [ ] **US-2.4:** Criar rota 'POST /api/v1/ia/processar' com lógica de failover (Nível 1 -> Nível 2 -> Nível 3).
- **Critério de Aceite:** Disparo de prompt pelo backend retornando resposta estruturada com log de latência e consumo de tokens.

### 🏢 Sprint 3: Conectores dos Sistemas Internos de Produção (Grupo A)
- **Meta da Sprint:** Integrar as APIs oficiais de GLPI (ITSM) e OpenProject (Portfólio de Projetos).
- **Backlog Priorizado:**
  - [ ] **US-3.1:** Implementar 'sis_01_glpi_8088_prod.py' com autenticação por App-Token e User-Token para puxar chamados abertos.
  - [ ] **US-3.2:** Implementar 'sis_02_openproject_8090_prod.py' para sincronização de Work Packages e cronogramas de Gantt.
  - [ ] **US-3.3:** Criar rotas no FastAPI para cache das respostas em tabelas locais no MariaDB.
- **Critério de Aceite:** Chamados do GLPI e Pacotes do OpenProject consultados via backend sem expor credenciais no frontend.

### 🌐 Sprint 4: Robôs de Busca Ativa Externa (Grupo B - Zero CORS)
- **Meta da Sprint:** Coletar dados de Diário Oficial, PNCP, SIGRH/SOI e Zabbix sem bloqueios de CORS no navegador.
- **Backlog Priorizado:**
  - [ ] **US-4.1:** Implementar 'ext_01_doesp_gov_br.py' para monitoramento de termos da SP-Águas no DOE-SP.
  - [ ] **US-4.2:** Implementar 'ext_02_pncp_gov_br.py' com filtro de UASG e CNPJ para editais e PCA 2027.
  - [ ] **US-4.3:** Implementar 'ext_03_sigrh_soi_gov_br.py' para telemetria de bacias e outorgas.
  - [ ] **US-4.4:** Implementar 'ext_04_zabbix_noc_bacias.py' para alertas de infraestrutura de rede.
- **Critério de Aceite:** Endpoint 'GET /api/v1/busca-externa/status' retornando os feeds externos em JSON unificado.

### 📊 Sprint 5: Frontend SPA Modular e Dashboards Táticos (Abas 01 a 08)
- **Meta da Sprint:** Integrar as abas de operação, portfólio e rituais ágeis na interface única.
- **Backlog Priorizado:**
  - [ ] **US-5.1:** Refatorar '00_roteador_abas.js' com histórico de navegação, breadcrumbs e preservação de estado no F5.
  - [ ] **US-5.2:** Conectar 'aba_01_dashboards.js' e 'aba_02_portfolio_openproject.js' aos endpoints do backend.
  - [ ] **US-5.3:** Ativar 'aba_04_gestao_glpi.js', 'aba_07_gestao_agil.js' e 'aba_08_daily_warroom.js'.
- **Critério de Aceite:** Troca instantânea entre as 8 primeiras abas sem recarregar a página e exibindo dados reais do MariaDB.

### 🛡️ Sprint 6: Governança, Auditoria Contínua e Homologação Fim a Fim (Abas 09 a 15)
- **Meta da Sprint:** Conectar os módulos de conformidade (TCE/TCU), acervo SEI, chat com IA e entrega final.
- **Backlog Priorizado:**
  - [ ] **US-6.1:** Conectar 'aba_09_consulta_sei.js' e 'aba_10_fixados.js' à base local de processos.
  - [ ] **US-6.2:** Ativar 'aba_11_auditoria_tce.js' com a matriz de riscos e conformidade da Súmula 269 TCU.
  - [ ] **US-6.3:** Conectar 'aba_13_esteira_ia.js' ao gateway de IA para chat contextualizado com o repositório.
  - [ ] **US-6.4:** Bateria de testes de carga, auditoria de segurança (CORS/Headers) e geração do pacote de entrega.
- **Critério de Aceite:** Sistema completo operando localmente no disco H:, com as 14 abas ativas, logs centralizados e documentação final aprovada.