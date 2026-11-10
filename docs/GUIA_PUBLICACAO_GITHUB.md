# 🐙 Guia Oficial de Publicação e Manutenção no GitHub

**Repositório Oficial:** [https://github.com/luizseixeiro/cockpit-gti-spaguas](https://github.com/luizseixeiro/cockpit-gti-spaguas)  
**Organização:** SP-Águas — SA-GTI (Superintendência de Administração / Gerência de TI)  
**Responsável:** Luiz Antonio Seixeiro  

---

## 1. Passo a Passo para Primeiro Envio (Git Push Inicial)

Se você estiver inicializando o repositório a partir desta pasta limpa:

```bash
# 1. Acesse o diretório do projeto
cd C:\Cockpit_GTI

# 2. Inicialize o repositório Git local (caso ainda não inicializado)
git init

# 3. Adicione o repositório remoto do GitHub
git remote add origin https://github.com/luizseixeiro/cockpit-gti-spaguas.git

# 4. Verifique o status dos arquivos (arquivos temporários e zips já são ignorados pelo .gitignore)
git status

# 5. Adicione todos os arquivos higienizados da release
git add .

# 6. Registre o commit canônico de release
git commit -m "feat: release oficial v11.0.0 - Cockpit GTI SP-Águas (Governança, OpenProject, GLPI & Multi-IA)"

# 7. Renomeie o branch principal para main e envie para o GitHub
git branch -M main
git push -u origin main --force
```

---

## 2. Padrão de Commits Semânticos Recomendado

Para manter o histórico do repositório profissional e alinhado aos padrões de auditoria do TCE-SP:

* `feat:` Adição de nova funcionalidade ou módulo (ex: `feat: conector openproject api v3`).
* `fix:` Correção de bug ou ajuste de layout (ex: `fix: sub-aba documentacao em configuracoes`).
* `docs:` Atualização de documentações, manuais ou README (ex: `docs: inclusao manual do usuario v11`).
* `perf:` Melhoria de desempenho ou otimização de consultas MariaDB/LLM.
* `refactor:` Refatoração de código sem alteração funcional de regras de negócio.

---

## 3. Estrutura Canônica de Diretórios do Repositório

```
cockpit-gti-spaguas/
├── .gitignore                      # Regras estritas de expurgo de temporários e backups
├── README.md                       # Documento executivo principal para o GitHub
├── requirements.txt                # Dependências Python mínimas (Flask, requests, PyMySQL)
├── painel.html                     # Aplicação Web SPA Oficial (Dark/Light Glassmorphism)
├── backend/
│   ├── main.py                     # Servidor Flask (:5000) e API REST de integração
│   ├── config_pool_ias.json        # Parametrização oficial do Pool de IAs
│   ├── sincronizar_openproject_backend.py # Agendador e sincronizador OpenProject
│   └── atualizar_e_reiniciar_cockpit.py   # Utilitário de orquestração do backend
├── frontend/
│   ├── painel.html                 # Cópia sincronizada para serving local
│   ├── conector_api.js             # Script de telemetria dos 5 pilares de infra
│   └── estilo_spaguas.css          # Estilo visual institucional complementar
├── data/
│   ├── processos.json              # Base canônica de 179 processos SEI da SA-GTI
│   ├── glpi_producao_cache.json    # Snapshot de tickets e inventário CMDB GLPI 10
│   ├── registro_execucao_agendada.json # Histórico de sincronizações agendadas
│   └── mapa_sei_op_manual.json     # Vínculos manuais de cards SEI <-> OpenProject
├── docs/
│   ├── MANUAL_DO_USUARIO.md        # Manual detalhado para analistas e gestores
│   ├── DOCUMENTACAO_TECNICA.md     # Especificações de arquitetura, conectores e SQL
│   └── GUIA_PUBLICACAO_GITHUB.md   # Este guia de governança e publicação
└── scripts/
    ├── iniciar_cockpit.bat         # Launcher rápido para Windows (Batch)
    ├── iniciar_cockpit.ps1         # Launcher corporativo para Windows (PowerShell)
    ├── iniciar_cockpit.sh          # Launcher para ambientes Linux / macOS
    └── atualizar_painel_windows.ps1 # Atualizador automatizado de arquivos locais
```
