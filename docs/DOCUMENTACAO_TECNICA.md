# ⚙️ Documentação Técnica & Arquitetura — Cockpit GTI v11.0

**Especificações de Engenharia de Software, Conectores, Banco de Dados & Inteligência Artificial**  
**Autarquia:** SP-Águas (SA-GTI)  
**Repositório Oficial:** [github.com/luizseixeiro/cockpit-gti-spaguas](https://github.com/luizseixeiro/cockpit-gti-spaguas)  

---

## 1. Arquitetura Geral da Solução

O Cockpit GTI adota arquitetura híbrida focada em resiliência, baixa latência e operação autônoma sem dependências de nuvem pública externa:

```
[ Navegador Web / PWA ] (painel.html)
        │
        ├── Vanilla JavaScript ES6+ (Sem frameworks pesados)
        ├── CSS3 Glassmorphism SaaS Dual-Theme (Dark & Light)
        └── Telemetria em Tempo Real (:5000 / conector_api.js)
        │
        ▼
[ Backend Flask Python :5000 ] (backend/main.py)
        ├── Proxy REST & Endpoints de Integração
        ├── Agendador Horário OpenProject (sincronizar_openproject_backend.py)
        └── Gerenciador do Pool de IAs (config_pool_ias.json)
        │
        ├── [ MariaDB :3306 ] (Tabelas processos_sei, snapshots_drp, feeds)
        ├── [ OpenProject API v3 :8090 ] (500 WPs, 29 Projetos)
        ├── [ GLPI 10 REST API :8088 ] (Tickets ITSM, CMDB Ativos)
        └── [ New API :3001 ] (Orquestrador de LLMs Locais)
                 ├── IA 1: Qwen 2.5 Coder 7B (Copiloto, Análise e DFD/TR/ETP)
                 └── IA 2: Llama 3.2 1B (Classificação Rápida e Resumos)
```

---

## 2. Hub de Conectores & Protocolos

| Conector | Protocolo / Porta | Dados Integrados | Modo de Acesso |
| :--- | :--- | :--- | :--- |
| **SEI-SP** | Ingestão PDF / MariaDB `:3306` | 179 Processos administrativos, aging líquido, histórico de despachos | Leitura e Ingestão Local |
| **OpenProject** | REST API v3 / `:443` ou `:8090` | 500 Pacotes de Trabalho, 29 Projetos, status Kanban, estimativas | Bidirecional (Leitura & Escrita de Cards) |
| **GLPI 10** | REST API / `:8088` | Chamados ITSM, SLA de atendimento, 443 PCs, 436 Monitores | Read-Only (Auditoria e CMDB) |
| **DOE-SP** | HTTP GET / Web Scraping | Publicações no Diário Oficial do Estado de São Paulo | Extração Automatizada |
| **New API** | OpenAI-Compatible / `:3001` | LLMs locais aceleradas por hardware local | Inferência de IA Privada |

---

## 3. Endpoints da API REST (:5000)

* `GET /api/v1/telemetria`: Retorna o status de saúde dos 5 serviços essenciais.
* `GET /api/v1/ia/pool`: Obtém a configuração atual dos slots de IA.
* `POST /api/v1/ia/pool`: Salva a parametrização de endpoints e chaves no disco.
* `POST /api/v1/ia/testar_slot`: Executa teste de conectividade e apuração de latência (ms) de um slot.
* `POST /api/v1/ia/chat`: Roteia prompt contextualizado para a IA selecionada (Principal ou Auxiliar).
* `POST /api/v1/openproject/sync_card`: Envia atualização ou comentário estruturado de processo SEI para o card correspondente no OpenProject via API v3.
* `GET /api/v1/openproject/historico_agendado_v2`: Histórico das execuções periódicas do agendador.
* `GET /api/v1/glpi/tickets`: Espelho dos chamados de suporte técnico em tempo real.

---

## 4. Conformidade Normativa & Governança

* **Lei Federal nº 14.133/2021:** Toda a esteira de contratações respeita as fases preparatórias e os artefatos vinculantes (DFD, ETP, Matriz de Riscos, TR).
* **Súmula 269 do TCU:** Monitoramento estrito de entregas da fábrica de software com base em resultados mensuráveis (UST/PF) e proibição de pagamento por mera disponibilização de pessoal.
* **PDTIC 2027-2030 SP-Águas:** Mapeamento direto de 35 iniciativas e 8 indicadores estratégicos (KPIs).
* **Política de Resiliência 3-2-1-1-0:** Retenção de cópias locais, em disco externo imutável e testes rotineiros de restore.
