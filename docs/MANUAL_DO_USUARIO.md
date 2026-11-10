# 📘 Manual do Usuário — Cockpit Executivo & Operacional SA-GTI

**Plataforma de Governança Digital, Gestão de Processos SEI e Rituais Ágeis**  
**Autarquia:** Agência de Águas do Estado de São Paulo (SP-Águas)  
**Unidade:** Superintendência de Administração — Gerência de Tecnologia da Informação (SA-GTI)  
**Versão:** 11.0 Oficial  

---

## 1. Acesso e Controle de Acesso por Perfil (RBAC)

O Cockpit GTI implementa autenticação institucional e controle de acesso baseado em papéis (RBAC). No canto inferior da barra lateral, cada colaborador visualiza seu nome, avatar e um **Seletor Dinâmico de Perfis**.

### Perfis do Sistema:
1. 👑 **Super-Admin (Luiz / GTI):** Acesso irrestrito a todos os módulos, configurações de conectores, parametrização de aging e motores de IA.
2. 👔 **Gestor de TIC (SA-GTI):** Visão completa de portfólio, aprovação de minutas, acompanhamento de contratos e rituais ágeis.
3. 💻 **Analista de TIC (DIF/DGD):** Gestão de processos sob custódia nominal na Mesa de Trabalho, elaboração de artefatos (DFD, TR, ETP) e resolução de chamados.
4. 🏛️ **Demandante (Bacias / Diretorias):** Modo somente leitura voltado para acompanhamento de demandas, status de processos e consulta ao acervo.

---

## 2. Módulo Cockpit (Gestão à Vista 360°)

O Cockpit consolida a visão estratégica e os indicadores de governança da SA-GTI em tempo real:

* **Acervo SEI:** Monitoramento de 179 processos divididos em 4 faixas de criticidade:
  - 🔴 **Farol 1 — Intervenção Imediata:** Processos com pendências críticas ou prazos legais expirados.
  - 🟠 **Farol 2 — Saneamento Prioritário:** Processos que requerem instrução técnica urgente.
  - 🟡 **Farol 3 — Monitoramento Ativo:** Processos em tramitação regular sob acompanhamento.
  - 🟢 **Farol 4 — Fluxo Normal:** Processos dentro dos prazos regulamentares.
* **Aging Líquido & Regra dos Poréns:** O sistema calcula automaticamente o tempo de tramitação, expurgando suspensões externas (manifestações de terceiros, diligências de órgãos de controle e prazos recursais).
* **Portfólio OpenProject:** Rastreamento dos 500 pacotes de trabalho e 29 projetos oficiais com filtros por gerência, tipo e status.
* **Atendimento GLPI 10:** Monitoramento de chamados de suporte e painel do parque de hardware/software (CMDB).
* **Auditoria TCE-SP & Súmula 269:** Acompanhamento de conformidade normativa, contratos de TIC e aceites técnicos.

---

## 3. Módulo Mesa de Trabalho & Ações Rápidas de Governança

Área dedicada à rotina operacional dos analistas e gestores:

* **Custódia Nominal:** Filtro automático que isola apenas os processos sob responsabilidade direta do usuário logado.
* **Ações Rápidas de Governança Digital:**
  - 📄 **Elaborar DFD:** Geração de Documento de Formalização de Demanda em conformidade com o PCA e PDTIC.
  - 📋 **Elaborar TR:** Estruturação de Termo de Referência com catálogo UST/PF, níveis de serviço (SLA) e tabela IMR.
  - 📊 **Elaborar ETP:** Elaboração de Estudo Técnico Preliminar e viabilidade de TCO para 36 meses.
* **Alertas de SLA e Watchlist:** Fixação de processos críticos para monitoramento prioritário com alertas visuais.

---

## 4. Módulo War Room (Daily Scrum de 15 Minutos)

Ambiente estruturado para a condução do ritual diário de alinhamento ágil da SA-GTI:

* **Cronômetro Timebox:** Contador regressivo de 15 minutos com alertas sonoros e visuais.
* **Pauta Dinâmica da Daily:** Importação direta de processos do SEI, pacotes do OpenProject ou chamados do GLPI para debate.
* **Mural de Post-its & Avisos:** Registro de Impedimentos (*Poréns*), Lembretes, Decisões e Ações.
* **Geração de Ata em PDF A4:** Emissão automatizada da Ata de Daily Scrum diagramada no padrão oficial da SP-Águas com 1 clique.

---

## 5. Módulo Central de Configurações (Eixo 4)

Ambiente administrativo estruturado em 7 sub-painéis:

1. 👥 **Gestão de Usuários & Perfis:** Cadastro, edição e ativação de colaboradores e credenciais.
2. 🛡️ **Perfis de Acesso & RBAC:** Matriz granular de permissões por módulo e perfil.
3. ⚖️ **Parâmetros de Gestão & Sprints:** Configuração de ciclos de sprint, timeboxes e limites de WIP.
4. 🔌 **Conectores & Varredura:** Monitoramento de 11 motores (SEI, OpenProject, GLPI, DOE-SP, PNCP, etc.).
5. 🤖 **Pool das 3 IAs & Agentes:** Configuração de endpoints, modelos e testes de latência da IA 1 (Qwen 2.5 Coder) e IA 2 (Llama 3.2).
6. 💾 **Backup & Restauração:** Política de cópias de segurança (Regra 3-2-1-1-0) e histórico de snapshots DRP.
7. 📖 **Documentação Oficial:** Central integrada de consulta técnica, manual operacional e link para o GitHub.
