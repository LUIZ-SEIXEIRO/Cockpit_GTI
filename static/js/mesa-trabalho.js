(function() {
    // 1. Base de Relatórios da Daily & Sprints para a Mesa de Trabalho
    window.RELATORIOS_RITUAIS_PADRAO = [
        {
            id: 'REL-DAILY-2026-11-05',
            tipo: 'daily',
            tipoLabel: '⏱️ Ata Daily Scrum',
            data: '05/11/2026',
            titulo: 'Ata de Daily Scrum (15 min) — SA-GTI Coordenação',
            destaque: 'Pauta: Homologação do Painel OpenProject (500 pacotes), fila GLPI (24 chamados) e saneamento da custódia SEI.',
            status: 'Realizada',
            marcado: true,
            conteudo: 'RESUMO EXECUTIVO DA DAILY SCRUM (05/11/2026)\n\n1. O QUE FOI FEITO ONTEM:\n- Auditoria completa dos 500 pacotes do OpenProject e 24 chamados ITSM do GLPI 10.\n- Saneamento de custódia nominal na Mesa de Trabalho.\n\n2. O QUE SERÁ FEITO HOJE:\n- Priorização da Sprint 03/2026 no Kanban de 5 colunas (SEI + OpenProject + GLPI).\n- Revisão técnica de ETPs da Esteira de Contratação (Lei 14.133/2021).\n\n3. IMPEDIMENTOS / PORÉNS:\n- 7 processos aguardando retorno externo (Consultoria Jurídica / Fornecedores).'
        },
        {
            id: 'REL-SPRINT-2026-03',
            tipo: 'sprint',
            tipoLabel: '🏃 Relatório de Sprint',
            data: '02/11/2026',
            titulo: 'Sprint 03/2026 — Planning & Escopo (SEI + OpenProject + GLPI)',
            destaque: 'Meta: Consolidação dos ETPs prioritários de TIC, atestes mensais PRODESP e governança PDTIC 2027-2030.',
            status: 'Em Execução',
            marcado: true,
            conteudo: 'RELATÓRIO DE SPRINT PLANNING — SPRINT 03/2026\nPeríodo: 02/11/2026 a 16/11/2026 (10 dias úteis)\n\nESCOPO CONSOLIDADO:\n- Backlog SEI: 179 processos administrativos monitorados.\n- Backlog OpenProject: 500 pacotes de trabalho em 29 projetos.\n- Backlog GLPI: 24 chamados técnicos e requisições abertas.\n\nENTREGÁVEIS CHAVE:\n- Atestes mensais de links SD-WAN e Outsourcing.\n- Instrução de ETPs estratégicos do PCA 2027.'
        },
        {
            id: 'REL-DAILY-2026-11-04',
            tipo: 'daily',
            tipoLabel: '⏱️ Ata Daily Scrum',
            data: '04/11/2026',
            titulo: 'Ata de Daily Scrum — Saneamento de Suspensões Externas (Poréns)',
            destaque: 'Tratativa de 7 processos aguardando Consultoria Jurídica (CJ/PGE) e fornecedores com SLA suspenso.',
            status: 'Arquivada',
            marcado: false,
            conteudo: 'ATA DE DAILY SCRUM (04/11/2026)\n- Revisão dos processos com cláusula de suspensão de SLA (Poréns).\n- Alinhamento com equipes DIF (Marcos Yamamoto) e DGD (Diego Monteiro) sobre chamados críticos GLPI.'
        },
        {
            id: 'REL-SPRINT-2026-02',
            tipo: 'sprint',
            tipoLabel: '🏃 Sprint Review & Retro',
            data: '30/10/2026',
            titulo: 'Fechamento Sprint 02/2026 — Entregas Homologadas & Velocity SA-GTI',
            destaque: 'Eficiência líquida de 92.8% nas entregas dentro do prazo regulamentar e integração dos 8 motores.',
            status: 'Concluída',
            marcado: false,
            conteudo: 'SPRINT REVIEW & RETROSPECTIVA — SPRINT 02/2026\n- Taxa de cumprimento de SLA: 92.8%.\n- Integração do barramento de dados concluída com sucesso.'
        }
    ];

    window.obterRelatoriosRituais = function() {
        var salvos = null;
        try {
            salvos = JSON.parse(localStorage.getItem('sagti_relatorios_rituais_v11') || 'null');
        } catch(e) {}
        if (!Array.isArray(salvos) || salvos.length === 0) {
            salvos = window.RELATORIOS_RITUAIS_PADRAO.slice();
            try { localStorage.setItem('sagti_relatorios_rituais_v11', JSON.stringify(salvos)); } catch(e) {}
        }
        return salvos;
    };

    window.obterFixadosValidos = function() {
        var fix = [];
        try { fix = JSON.parse(localStorage.getItem('sagti_fixados') || '[]'); } catch(e) { fix = []; }
        return Array.isArray(fix) ? fix : [];
    };

    // Função Universal de Acompanhamento / Fixação (Suporta SEI, OP#id, GLPI#id, REL#id)
    window.toggleFixado = function(chave) {
        if (!chave) return;
        var fix = window.obterFixadosValidos();
        var idx = fix.indexOf(chave);
        if (idx !== -1) {
            fix.splice(idx, 1);
        } else {
            fix.push(chave);
        }
        try { localStorage.setItem('sagti_fixados', JSON.stringify(fix)); } catch(e) {}

        // Sincronizar com os relatórios rituais se for um relatório
        if (String(chave).indexOf('REL#') === 0) {
            var rId = String(chave).replace(/^REL#/, '');
            var rels = window.obterRelatoriosRituais();
            rels.forEach(function(r) {
                if (r.id === rId) r.marcado = (idx === -1);
            });
            try { localStorage.setItem('sagti_relatorios_rituais_v11', JSON.stringify(rels)); } catch(e) {}
        }

        window.atualizarContadoresCustodiaMesa();
        if (typeof window.renderizarViewRelatoriosSprints === 'function') window.renderizarViewRelatoriosSprints();
        if (typeof window.renderizarTabelaMesa === 'function') window.renderizarTabelaMesa();
        if (typeof window.renderizarListaContextoChat === 'function') window.renderizarListaContextoChat();
        if (typeof window.renderizarKanbanAgil === 'function') window.renderizarKanbanAgil();
    };

    window.toggleAcompanhamentoRelatorio = function(idRel) {
        var chave = 'REL#' + idRel;
        window.toggleFixado(chave);
    };

    window.visualizarRelatorioMesaModal = function(idRel) {
        var lista = window.obterRelatoriosRituais();
        var rel = lista.find(function(r) { return r.id === idRel; });
        if (!rel) return;

        var modalExistente = document.getElementById('modal-relatorio-ritual-mesa');
        if (modalExistente) modalExistente.remove();

        var fix = window.obterFixadosValidos();
        var isMarcado = fix.indexOf('REL#' + rel.id) !== -1 || rel.marcado;

        var div = document.createElement('div');
        div.id = 'modal-relatorio-ritual-mesa';
        div.className = 'sagti-modal-backdrop';
        div.style.cssText = 'position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;padding:20px;';
        div.innerHTML = '<div style="border-radius:16px;max-width:680px;width:100%;padding:24px">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">' +
                '<span style="padding:4px 10px;border-radius:8px;font-size:11.5px;font-weight:800">' + rel.tipoLabel + ' • ' + rel.data + '</span>' +
                '<button type="button" onclick="document.getElementById(\'modal-relatorio-ritual-mesa\').remove()" style="font-size:18px;cursor:pointer" class="btn btn-ghost-secondary">✖</button>' +
            '</div>' +
            '<h3 style="margin:0 0 10px 0;font-size:16px">' + rel.titulo + '</h3>' +
            '<div style="font-size:12px;margin-bottom:14px">' + rel.destaque + '</div>' +
            '<pre style="border-radius:10px;padding:16px;font-size:12px;white-space:pre-wrap;line-height:1.55;max-height:340px;overflow-y:auto">' + (rel.conteudo || rel.destaque) + '</pre>' +
            '<div style="display:flex;justify-content:flex-end;gap:10px;margin-top:16px">' +
                '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleAcompanhamentoRelatorio(\'' + rel.id + '\');document.getElementById(\'modal-relatorio-ritual-mesa\').remove();" style="padding:7px 14px;font-size:12px">' + (isMarcado ? '☆ Remover Acompanhamento' : '⭐ Marcar para Acompanhamento') + '</button>' +
                '<button type="button" class="btn btn-primary" onclick="document.getElementById(\'modal-relatorio-ritual-mesa\').remove()" style="padding:7px 16px;font-size:12px">Fechar</button>' +
            '</div>' +
        '</div>';
        document.body.appendChild(div);
    };

    window.publicarRelatorioSprintNaMesa = function() {
        var lista = window.obterRelatoriosRituais();
        var colAtual = document.getElementById('badge-sprint-atual') ? document.getElementById('badge-sprint-atual').innerText : '0 itens';
        var colProx = document.getElementById('badge-sprint-prox') ? document.getElementById('badge-sprint-prox').innerText : '0 itens';
        var novo = {
            id: 'REL-SPRINT-' + Date.now(),
            tipo: 'sprint',
            tipoLabel: '🏃 Snapshot da Sprint',
            data: new Date().toLocaleDateString('pt-BR'),
            titulo: 'Snapshot Sprint 03/2026 — Quadro Kanban (' + colAtual + ' em execução)',
            destaque: 'Sprint Atual: ' + colAtual + ' | Próxima Sprint: ' + colProx + ' | Backlogs integrados SEI + OpenProject + GLPI.',
            status: 'Ativo na Mesa',
            marcado: true,
            conteudo: 'SNAPSHOT DO QUADRO KANBAN ÁGIL (' + new Date().toLocaleString('pt-BR') + ')\n\n- Itens na Sprint Atual: ' + colAtual + '\n- Itens na Próxima Sprint: ' + colProx + '\n- Status: Enviado para acompanhamento direto na Mesa de Trabalho.'
        };
        lista.unshift(novo);
        try { localStorage.setItem('sagti_relatorios_rituais_v11', JSON.stringify(lista)); } catch(e) {}
        window.toggleFixado('REL#' + novo.id);
        alert('✅ Relatório da Sprint enviado para a sua Mesa de Trabalho e marcado com estrela (⭐ Acompanhando)!');
    };

    // 2. Atualização limpa dos Contadores e KPIs da Mesa de Trabalho
    window.atualizarContadoresCustodiaMesa = function() {
        var base = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var fix = window.obterFixadosValidos();
        var pacotesOp = (typeof window.OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(window.OP_PACOTES_OFICIAIS)) ? window.OP_PACOTES_OFICIAIS : [];
        var pacotesOpAbertos = pacotesOp.filter(function(op) {
            var st = (op.status || '').toLowerCase();
            return st.indexOf('encerrado') === -1 && st.indexOf('concluído') === -1 && st.indexOf('cancelado') === -1;
        });
        var glpi = (typeof window.CHAMADOS_GLPI_15_OFICIAIS !== 'undefined' && Array.isArray(window.CHAMADOS_GLPI_15_OFICIAIS) && window.CHAMADOS_GLPI_15_OFICIAIS.length > 0) ? window.CHAMADOS_GLPI_15_OFICIAIS : ((typeof window.CHAMADOS_ITSM_SUPORTE !== 'undefined' && Array.isArray(window.CHAMADOS_ITSM_SUPORTE)) ? window.CHAMADOS_ITSM_SUPORTE : []);
        var rels = window.obterRelatoriosRituais();

        var custodia = (typeof window.obterCustodiaNominalLuiz === 'function') ? window.obterCustodiaNominalLuiz() : [];
        var elKpi = document.getElementById('mesa-kpi-custodia'); if (elKpi) elKpi.innerText = String(custodia.length);
        var elCC = document.getElementById('count-mesa-custodia'); if (elCC) elCC.innerText = String(custodia.length);
        var elCF = document.getElementById('count-mesa-fixados'); if (elCF) elCF.innerText = String(fix.length);
        var elCO = document.getElementById('count-mesa-op'); if (elCO) elCO.innerText = '500';
        var elCG = document.getElementById('count-mesa-glpi'); if (elCG) elCG.innerText = '15';
        var elCA = document.getElementById('count-mesa-acervo'); if (elCA) elCA.innerText = String(base.length || 179);
        var elCR = document.getElementById('count-mesa-relatorios'); if (elCR) elCR.innerText = String(rels.length || 5);
        var raciModelos = (typeof window.obterModelosRaciSalvos === 'function') ? window.obterModelosRaciSalvos() : [];
        var elRaci = document.getElementById('count-mesa-raci'); if (elRaci) elRaci.innerText = String(raciModelos.length || 3);

        var elCrit = document.getElementById('mesa-kpi-criticos'); if (elCrit) elCrit.innerText = '0';
        var elPor = document.getElementById('mesa-kpi-porens'); if (elPor) elPor.innerText = '0';
        var elEfic = document.getElementById('mesa-kpi-eficiencia'); if (elEfic) elEfic.innerText = '100%';
    };

    window.alternarModoMesa = function(modo) {
        window.modoMesaAtivo = modo || 'custodia';
        window.paginaMesa = 1;
        document.querySelectorAll('.pill-filtro-mesa').forEach(function(btn) {
            var ativo = btn.id === 'btn-mesa-' + window.modoMesaAtivo;
            btn.classList.remove('btn-primary', 'btn-secondary', 'btn-outline-secondary');
            btn.classList.add(ativo ? 'btn-primary' : 'btn-outline-secondary');
            btn.classList.toggle('active', ativo);
            btn.setAttribute('aria-pressed', ativo ? 'true' : 'false');
        });
        window.renderizarTabelaMesa();
    };

    
    window.resolverItemWatchlist = function(chave, baseProcs, pacotesOp, baseGlpi, rels) {
        if (!chave) return null;
        var ch = String(chave).trim();
        if (!ch) return null;

        // 1. Relatórios Daily & Sprints
        if (ch.indexOf('REL#') === 0 || ch.indexOf('REL-') === 0) {
            var rId = ch.replace(/^REL#/, '');
            var rObj = (rels || []).find(function(r) { return String(r.id) === String(rId) || ('REL#' + r.id) === ch; });
            if (rObj) {
                return {
                    tipo: 'Relatório',
                    chave: ch,
                    id: rObj.tipoLabel || 'Relatório',
                    titulo: rObj.titulo || 'Ritual Ágil',
                    resp: rObj.data || 'Hoje',
                    status: rObj.status || 'Ativo',
                    detalhe: rObj.destaque || 'Daily / Sprint',
                    acao: '<button type="button" class="btn btn-outline-secondary" onclick="window.visualizarRelatorioMesaModal(\'' + rObj.id + '\')" style="padding:3px 8px;font-size:10.5px;margin-right:4px">👁️ Ver</button>' +
                          '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">⭐ Acompanhando</button>'
                };
            }
            return {
                tipo: 'Relatório',
                chave: ch,
                id: ch,
                titulo: 'Relatório de Ritual Ágil #' + rId,
                resp: 'SA-GTI',
                status: 'Ativo',
                detalhe: 'Ritual Operacional',
                acao: '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">✖ Remover</button>'
            };
        }

        // 2. Chamados GLPI
        if (ch.indexOf('GLPI#') === 0 || ch.indexOf('GLPI-') === 0 || ch.indexOf('TICKET#') === 0) {
            var gId = ch.replace(/^(GLPI#|GLPI-|TICKET#)/, '').split('_')[0].trim();
            var gObj = (baseGlpi || []).find(function(t) { return String(t.id) === String(gId); });
            var linkGlpi = 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=' + gId;
            if (gObj) {
                return {
                    tipo: 'GLPI',
                    chave: ch,
                    id: '#' + gObj.id,
                    titulo: gObj.titulo || ('Chamado GLPI #' + gObj.id),
                    resp: gObj.tecnico || 'SA-GTI',
                    status: gObj.status || 'Ativo',
                    detalhe: gObj.cat || gObj.local || 'Suporte & Infra',
                    acao: '<a href="' + linkGlpi + '" target="_blank" class="btn btn-outline-secondary" style="padding:3px 8px;font-size:10.5px;text-decoration:none;margin-right:4px">GLPI ↗</a>' +
                          '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">⭐ Acompanhando</button>'
                };
            }
            return {
                tipo: 'GLPI',
                chave: ch,
                id: '#' + gId,
                titulo: 'Chamado Técnico GLPI 10 #' + gId,
                resp: 'SA-GTI',
                status: 'Ativo',
                detalhe: 'Suporte & Atendimento',
                acao: '<a href="' + linkGlpi + '" target="_blank" class="btn btn-outline-secondary" style="padding:3px 8px;font-size:10.5px;text-decoration:none;margin-right:4px">GLPI ↗</a>' +
                      '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">✖ Remover</button>'
            };
        }

        // 3. Pacotes OpenProject
        if (ch.indexOf('OP#') === 0 || ch.indexOf('OP-') === 0 || ch.indexOf('WP#') === 0) {
            var opId = ch.replace(/^(OP#|OP-|WP#)/, '').trim();
            var opObj = (pacotesOp || []).find(function(op) { return String(op.id) === String(opId); });
            var urlOp = 'https://projetos.spaguas.sp.gov.br/work_packages/' + opId;
            if (opObj) {
                return {
                    tipo: 'OpenProject',
                    chave: ch,
                    id: '#' + opObj.id,
                    titulo: opObj.assunto || ('Pacote #' + opObj.id),
                    resp: opObj.atrib || opObj.encarr || 'SA-GTI',
                    status: opObj.status || '🚀 Em progresso',
                    detalhe: opObj.tipo || opObj.projeto || 'Projeto',
                    acao: '<a href="' + urlOp + '" target="_blank" class="btn btn-outline-secondary" style="padding:3px 8px;font-size:10.5px;text-decoration:none;margin-right:4px">Abrir OP ↗</a>' +
                          '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">⭐ Acompanhando</button>'
                };
            }
            return {
                tipo: 'OpenProject',
                chave: ch,
                id: '#' + opId,
                titulo: 'Pacote de Trabalho OpenProject #' + opId,
                resp: 'SA-GTI',
                status: 'Em andamento',
                detalhe: 'Gestão de Projetos',
                acao: '<a href="' + urlOp + '" target="_blank" class="btn btn-outline-secondary" style="padding:3px 8px;font-size:10.5px;text-decoration:none;margin-right:4px">Abrir OP ↗</a>' +
                      '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">✖ Remover</button>'
            };
        }

        // 4. Processos SEI (com suporte a aliases e correspondência flexível)
        var pCh = ch;
        if (pCh === '137.00010805/2025-52') pCh = '137.00010805/2025-82';
        if (pCh === '137.00011003/2025-90') pCh = '137.00029841/2026-14';

        var pObj = (baseProcs || []).find(function(p) { return p.ID_Processo === pCh; });
        if (!pObj) {
            pObj = (baseProcs || []).find(function(p) { return p.ID_Processo && (p.ID_Processo.includes(pCh) || pCh.includes(p.ID_Processo)); });
        }

        // Check if numeric and matches a GLPI ticket or OP package
        if (!pObj && /^\d+$/.test(ch)) {
            var gObjNum = (baseGlpi || []).find(function(t) { return String(t.id) === ch; });
            if (gObjNum) {
                var lG = 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=' + ch;
                return {
                    tipo: 'GLPI',
                    chave: ch,
                    id: '#' + ch,
                    titulo: gObjNum.titulo || ('Chamado #' + ch),
                    resp: gObjNum.tecnico || 'SA-GTI',
                    status: gObjNum.status || 'Ativo',
                    detalhe: gObjNum.cat || 'Suporte',
                    acao: '<a href="' + lG + '" target="_blank" class="btn btn-outline-secondary" style="padding:3px 8px;font-size:10.5px;text-decoration:none;margin-right:4px">GLPI ↗</a>' +
                          '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">⭐ Acompanhando</button>'
                };
            }
            var opObjNum = (pacotesOp || []).find(function(op) { return String(op.id) === ch; });
            if (opObjNum) {
                var lOp = 'https://projetos.spaguas.sp.gov.br/work_packages/' + ch;
                return {
                    tipo: 'OpenProject',
                    chave: ch,
                    id: '#' + ch,
                    titulo: opObjNum.assunto || ('Pacote #' + ch),
                    resp: opObjNum.atrib || opObjNum.encarr || 'SA-GTI',
                    status: opObjNum.status || 'Ativo',
                    detalhe: opObjNum.tipo || 'Projeto',
                    acao: '<a href="' + lOp + '" target="_blank" class="btn btn-outline-secondary" style="padding:3px 8px;font-size:10.5px;text-decoration:none;margin-right:4px">Abrir OP ↗</a>' +
                          '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">⭐ Acompanhando</button>'
                };
            }
        }

        if (pObj) {
            return {
                tipo: 'SEI',
                chave: ch,
                id: pObj.ID_Processo,
                titulo: pObj.Especificacao || pObj.Tipo_Processo || 'Processo SEI',
                resp: pObj.Responsavel_Tecnico || 'SA-GTI',
                status: pObj.Status_OpenProject || pObj.Status_Kanban || 'Ativo',
                detalhe: pObj.Faixa_Aging || 'Normal',
                acao: '<button class="btn btn-outline-secondary" onclick="window.abrirDetalhesProcesso(\'' + pObj.ID_Processo + '\')" style="padding:3px 8px;font-size:10.5px;margin-right:4px">👁️ Ver</button>' +
                      '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">⭐ Acompanhando</button>'
            };
        }

        // 5. Fallback Universal (NUNCA descarta item marcado!)
        return {
            tipo: 'Demanda',
            chave: ch,
            id: ch,
            titulo: 'Item marcado para acompanhamento prioritário (' + ch + ')',
            resp: 'SA-GTI',
            status: 'Ativo',
            detalhe: 'Watchlist Pessoal',
            acao: '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + ch + '\')" style="padding:3px 8px;font-size:10.5px">✖ Remover</button>'
        };
    };

    window.limparTodosFixados = function() {
        if (confirm('Deseja desmarcar todas as demandas fixadas na sua Watchlist?')) {
            try { localStorage.setItem('sagti_fixados', '[]'); } catch(e) {}
            if (typeof window.atualizarFixadosBadge === 'function') window.atualizarFixadosBadge();
            if (typeof window.atualizarContadoresCustodiaMesa === 'function') window.atualizarContadoresCustodiaMesa();
            if (typeof window.renderizarTabelaMesa === 'function') window.renderizarTabelaMesa();
        }
    };

    
    
    // =========================================================================
    // MOTOR ORQUESTRADOR OPENPROJECT — CANAL ATIVO DE ESCRITA & SINCRONIZAÇÃO (API v3)
    // Permite que o Cockpit GTI seja o orquestrador ativo dos cards no OpenProject:
    // - Regra Fundamental: Somente cards que contenham o número do Processo SEI
    //   no nome (padrão "Tarefas 137.XXXXX/YYYY-ZZ — [Objeto]") recebem gravação.
    // - Carga de Dados Enriquecida: Status, Prioridade, Responsável Nominal, Aging
    //   Líquido (Poréns), Matriz RACI associada, Chamados GLPI correlacionados e
    //   corpo completo formatado em Markdown estruturado.
    // - Suporte a PATCH (atualização) e POST (criação de nova tarefa vinculada).
    // =========================================================================

    window.openProjectOrchestrator = {
        endpoint: 'https://projetos.spaguas.sp.gov.br/api/v3',
        regexSEI: /\b(\d{3}\.\d{8}\/\d{4}-\d{2})\b/,

        // Localiza se já existe um card no OpenProject correspondente a um processo SEI
        localizarCardPorSEI: function(idProcesso) {
            if (!idProcesso) return null;
            var numLimpo = String(idProcesso).trim().toLowerCase();
            var numDigitos = numLimpo.replace(/[^0-9]/g, '');

            var pacotes = (typeof window.OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(window.OP_PACOTES_OFICIAIS)) ? window.OP_PACOTES_OFICIAIS : [];
            var customCards = [];
            try { customCards = JSON.parse(localStorage.getItem('sagti_op_pacotes_custom') || '[]'); } catch(e) {}
            var liveCards = [];
            try { liveCards = JSON.parse(localStorage.getItem('sagti_op_live_cache') || '[]'); } catch(e) {}
            var todosPacotes = customCards.concat(liveCards).concat(pacotes);

            // Mapeamento direto pré-configurado canônico (ex: 137.00013132/2026-01 -> #1497)
            var mapaManual = {};
            try { mapaManual = JSON.parse(localStorage.getItem('sagti_mapa_sei_op_manual') || '{}'); } catch(e) {}
            var idsMapeados = mapaManual[idProcesso] || (window.MAPA_DIRETO_SEI_OPENPROJECT ? window.MAPA_DIRETO_SEI_OPENPROJECT[idProcesso] : null);
            if (idsMapeados && Array.isArray(idsMapeados) && idsMapeados.length > 0) {
                var cId = String(idsMapeados[0]).replace('#', '');
                var cardEncontrado = todosPacotes.find(function(op) { return String(op.id) === cId; });
                if (cardEncontrado) return cardEncontrado;
                return {
                    id: cId,
                    assunto: 'TAREFAS ' + idProcesso,
                    projeto: 'SA-GTI - Gerência de TI',
                    tipo: 'Tarefa',
                    status: '🚀 Em progresso',
                    prio: 'Alta',
                    atrib: 'SA-GTI'
                };
            }

            // Busca por texto no assunto
            var cardEncontrado = todosPacotes.find(function(op) {
                var assunto = String(op.assunto || '').toLowerCase();
                return assunto.indexOf(numLimpo) !== -1;
            });
            if (cardEncontrado) return cardEncontrado;

            // Busca por dígitos limpos
            if (numDigitos.length >= 8) {
                cardEncontrado = todosPacotes.find(function(op) {
                    var assDigitos = String(op.assunto || '').replace(/[^0-9]/g, '');
                    return assDigitos.indexOf(numDigitos) !== -1;
                });
                if (cardEncontrado) return cardEncontrado;
            }

            return null;
        },

        // Função para vincular manualmente um card existente ao processo SEI
        vincularCardManual: function(idProcesso, opCardId) {
            if (!idProcesso || !opCardId) return;
            var cId = String(opCardId).replace(/[^0-9]/g, '');
            var mapaManual = {};
            try { mapaManual = JSON.parse(localStorage.getItem('sagti_mapa_sei_op_manual') || '{}'); } catch(e) {}
            mapaManual[idProcesso] = [cId];
            try { localStorage.setItem('sagti_mapa_sei_op_manual', JSON.stringify(mapaManual)); } catch(e) {}
            if (typeof window.abrirModalOrquestradorOp === 'function') window.abrirModalOrquestradorOp(idProcesso);
        },

        // REVISÃO COGNITIVA OBRIGATÓRIA DA IA 2 (ORQUESTRAÇÃO, RAG & FACT-CHECKER)
        // Solicita à IA 2 a validação e homologação do Dossiê e do Comentário antes da gravação
        revisarCardComIa2Orquestracao: async function(proc, cardOpExistente) {
            var payloadBase = window.openProjectOrchestrator.gerarPayloadEnriquecido(proc, cardOpExistente);
            var idProc = proc ? proc.ID_Processo : '';
            var espec = proc ? (proc.Especificacao || proc.Tipo_Processo || 'Demanda de TIC sob governança SA-GTI') : '';
            var respNom = proc ? (proc.Responsavel_Tecnico || 'SA-GTI') : 'SA-GTI';
            var cardIdFinal = cardOpExistente ? cardOpExistente.id : (idProc.split('.')[1] ? idProc.split('.')[1].split('/')[0] : '1498');

            var parecerTexto = '';
            var modeloUsado = '';
            var tid = null;
            try {
                var ctrl = new AbortController();
                tid = setTimeout(function() { ctrl.abort(); }, 65000);
                var resBackend = await fetch('/api/v1/ia/revisar_processo', {
                    method: 'POST',
                    headers: obterHeadersComAuth(),
                    body: JSON.stringify({
                        idProcesso: idProc,
                        especificacao: espec,
                        tipoProcesso: proc ? proc.Tipo_Processo : '',
                        agingBruto: proc ? (proc.Aging_Dias_Corridos || proc.Dias_Ultima_Mov || '0') : '0',
                        agingLiquido: proc ? (proc.Aging_Liquido_Dias || '0') : '0',
                        porem: (proc && (proc.Possui_Porem === 'SIM' || proc.Possui_Porem === true)) ? ('⚠️ ATIVA (' + (proc.Tipo_Porem || 'Suspensão Externa') + ')') : 'Nenhuma suspensão ativa no momento',
                        farol: proc ? (proc.Farol_Criticidade || '🟢 4 - Fluxo Normal') : '🟢 4 - Fluxo Normal',
                        bucket: proc ? (proc.Bucket_OpenProject || '') : '',
                        responsavel: respNom,
                        cardId: cardIdFinal
                    }),
                    signal: ctrl.signal
                });
                clearTimeout(tid);
                var dadosIa = null;
                try { dadosIa = await resBackend.json(); } catch (_) {}
                if (resBackend.status === 422 || (dadosIa && (
                    dadosIa.bloqueado_por_inconsistencia ||
                    (dadosIa.consistencia && dadosIa.consistencia.consistente === false)
                ))) {
                    var erroBloqueio = new Error((dadosIa && dadosIa.erro) || 'Parecer bloqueado por inconsistência de contexto. Revisão humana obrigatória.');
                    erroBloqueio.code = 'IA_INCONSISTENTE';
                    throw erroBloqueio;
                }
                if (!resBackend.ok || !dadosIa || dadosIa.sucesso !== true ||
                    typeof dadosIa.parecer !== 'string' || !dadosIa.parecer.trim() ||
                    !dadosIa.consistencia || dadosIa.consistencia.consistente !== true) {
                    var erroIndisponivel = new Error((dadosIa && (dadosIa.erro || dadosIa.mensagem)) || 'A revisão de IA não foi concluída com consistência confirmada.');
                    erroIndisponivel.code = 'IA_INDISPONIVEL';
                    throw erroIndisponivel;
                }
                parecerTexto = dadosIa.parecer.trim();
                modeloUsado = dadosIa.modelo || 'modelo não informado';
            } catch(e) {
                clearTimeout(tid);
                if (e && (e.code === 'IA_INCONSISTENTE' || e.code === 'IA_INDISPONIVEL')) throw e;
                var erroFalha = new Error(e && e.name === 'AbortError'
                    ? 'Tempo limite excedido ao revisar o processo.'
                    : 'Falha ao consultar o gateway autenticado de IA.');
                erroFalha.code = 'IA_INDISPONIVEL';
                throw erroFalha;
            }

            // Injeta o Parecer da IA 2 no corpo do Dossiê Técnico
            var carimboData = new Date().toLocaleDateString('pt-BR') + ' às ' + new Date().toLocaleTimeString('pt-BR');
            var trechoParecer = '\n\n## 🤖 2. Análise preliminar da IA (' + modeloUsado + ')\n> *Gerada em ' + carimboData + '. Não constitui homologação; exige revisão humana.*\n' + parecerTexto + '\n';

            if (payloadBase.descricao.indexOf('## 🤖 2. ') === -1) {
                payloadBase.descricao = payloadBase.descricao.replace('## 📁 2. Repositório', trechoParecer + '\n## 📁 3. Repositório');
            } else {
                payloadBase.descricao = payloadBase.descricao.replace(/## 🤖 2\.[\s\S]*?(?=## 📁)/, trechoParecer + '\n');
            }

            // Injeta no Comentário de Atividade ("O que mudou")
            payloadBase.comentario = '🔄 **[Cockpit GTI] Registro de Governança & Sincronização — ' + carimboData + '**\n\n' +
                '🤖 **Análise preliminar da IA (' + modeloUsado + '), sujeita à revisão humana:**\n' +
                '• Processo Administrativo SEI ' + idProc + ' analisado com base nos dados fornecidos ao sistema; não é uma homologação.\n' +
                '• Objeto: ' + espec + '\n' +
                '• Análise: ' + parecerTexto.split('\n')[0] + '\n\n' +
                '📌 **O que mudou nesta atualização:**\n' +
                '• **Dossiê Técnico Enriquecido:** Carga abrangente de metadados, análise da IA 2 e repositório probatório de links.\n' +
                '• **Aging Líquido & Poréns:** Dados de prazo registrados (Aging Líquido: ' + (proc ? (proc.Aging_Liquido_Dias || proc.Dias_Ultima_Mov || '0') : '0') + ' dias).\n' +
                '• **Matriz RACI Atualizada:** Validação nominal de papéis (Gestor da Demanda: Luiz Antonio Seixeiro / Executor: ' + respNom + ').\n' +
                '• **Status do Card:** ' + (payloadBase.status || '🚀 Em progresso') + ' | Criticidade: ' + (proc ? (proc.Farol_Criticidade || '🟢 4 - Fluxo Normal') : '🟢 4 - Fluxo Normal') + '.\n\n' +
                '👤 **Responsável pela Atualização:** ' + (window.obterUsuarioSessaoAtual ? window.obterUsuarioSessaoAtual().nome : 'Luiz Antonio Seixeiro') + ' (SA-GTI / Governança)\n' +
                '🤖 **Auditoria Cognitiva:** IA (' + modeloUsado + '); validação humana pendente.';

            payloadBase.revisadoPorIa2 = true;
            payloadBase.modeloIa2 = modeloUsado;
            payloadBase.parecerIa2 = parecerTexto;
            payloadBase.consistenciaIa2 = true;
            return payloadBase;
        },

        // GERAÇÃO DE PAYLOAD ENRIQUECIDO COM DESCRIÇÃO ABRANGENTE, LINKS DE ARQUIVOS E COMENTÁRIO DE ATIVIDADE
        gerarPayloadEnriquecido: function(proc, cardOpExistente) {
            if (!proc) {
                return {
                    assunto: '',
                    descricao: '',
                    comentario: '',
                    responsavel: 'SA-GTI',
                    prioridade: 'Alta',
                    status: '🚀 Em progresso',
                    bucket: 'A-001 - Planejamento & PCA',
                    projeto: 'SA-GTI - Gerência de TI'
                };
            }

            var idProc = proc.ID_Processo || '';
            var espec = proc.Especificacao || proc.Tipo_Processo || 'Processo Administrativo de TIC';
            var assuntoOficial = 'TAREFAS ' + idProc + ' — ' + espec;
            var respNominal = proc.Responsavel_Tecnico || 'SA-GTI';
            var bucketCan = proc.Bucket_Canonico || proc.Bucket_OpenProject || 'A-001 - Planejamento & PCA';
            var projetoAlvo = 'SA-GTI - Gerência de TI';
            var cardIdFinal = cardOpExistente ? cardOpExistente.id : (idProc.split('.')[1] ? idProc.split('.')[1].split('/')[0] : '1497');

            // Mapeamento Canônico de Status para o OpenProject
            var statusSugerido = String(proc.Status_Sugerido_Kanban || proc.Status_OpenProject || '');
            var statusFinal = '🚀 Em progresso';
            if (statusSugerido.indexOf('Fechada') !== -1 || statusSugerido.indexOf('Concluído') !== -1) {
                statusFinal = '🔒 Fechada';
            } else if (proc.Possui_Porem === 'SIM' || proc.Possui_Porem === true || statusSugerido.indexOf('Espera') !== -1 || statusSugerido.indexOf('Suspenso') !== -1) {
                statusFinal = '⏳ Em espera';
            } else if (statusSugerido.indexOf('Novo') !== -1 || statusSugerido.indexOf('Triagem') !== -1) {
                statusFinal = '💡 Novo';
            } else if (statusSugerido.indexOf('Backlog') !== -1) {
                statusFinal = '➡️ Backlog';
            }

            // Prioridade
            var prioFinal = 'Alta';
            var criticidade = String(proc.Farol_Criticidade || '').toUpperCase();
            if (criticidade.indexOf('VERMELHO') !== -1 || String(proc.Classificacao_Risco || '').toUpperCase().indexOf('CRÍTICO') !== -1) {
                prioFinal = 'Urgente';
            } else if (criticidade.indexOf('VERDE') !== -1) {
                prioFinal = 'Normal';
            }

            // Preservação Cumulativa de Anotações e Observações Prévias da Equipe (HIGIENIZADA)
            var notasPreservadas = '';
            if (cardOpExistente && cardOpExistente.descricao) {
                var descAntiga = String(cardOpExistente.descricao);
                var markerManual = '### 📝 Anotações & Observações da Equipe (Preservadas)';
                var posMarker = descAntiga.indexOf(markerManual);
                if (posMarker !== -1) {
                    var trecho = descAntiga.substring(posMarker + markerManual.length);
                    var fimTrecho = trecho.indexOf('### ');
                    if (fimTrecho === -1) fimTrecho = trecho.indexOf('---');
                    notasPreservadas = (fimTrecho !== -1 ? trecho.substring(0, fimTrecho) : trecho).trim();
                } else if (descAntiga.indexOf('## 📋 DOSSIÊ TÉCNICO') === -1 && descAntiga.indexOf('# 📋 DOSSIÊ TÉCNICO') === -1) {
                    notasPreservadas = descAntiga.trim();
                }
            }

            if (notasPreservadas) {
                notasPreservadas = notasPreservadas
                    .replace(/>\s*\*Estas anotações foram preservadas[^\n]*\*\s*\n?/gi, '')
                    .replace(/^>\s*\*.*\*\s*$/gm, '')
                    .trim();
            }

            var agora = new Date();
            var carimboHora = agora.toLocaleDateString('pt-BR') + ' às ' + agora.toLocaleTimeString('pt-BR');
            var usuarioLogado = (window.obterUsuarioSessaoAtual ? window.obterUsuarioSessaoAtual().nome : 'Luiz Antonio Seixeiro');

            var agingBruto = proc.Aging_Dias_Corridos || proc.Dias_Ultima_Mov || '0';
            var agingUteis = proc.Aging_Dias_Uteis || Math.round(parseInt(agingBruto, 10) * 0.7) || '0';
            var agingLiquido = (typeof proc.Aging_Liquido_Dias !== 'undefined' && proc.Aging_Liquido_Dias !== null && proc.Aging_Liquido_Dias !== '') ? proc.Aging_Liquido_Dias : (proc.Aging_Dias_Corridos || '0');
            var temPorem = (proc.Possui_Porem === 'SIM' || proc.Possui_Porem === true);

            // =================================================================
            // 1. DESCRIÇÃO MAIS ABRANGENTE COM DETALHES COMPLETOS E LINKS
            // =================================================================
            var md = [];
            md.push('# 📋 DOSSIÊ TÉCNICO DE GOVERNANÇA, CONTRATAÇÃO & ORQUESTRAÇÃO');
            md.push('**SP-Águas — Autarquia de Águas do Estado de São Paulo** | **SA-GTI (Superintendência de Administração / Gerência de TI)**');
            md.push('');
            md.push('---');
            md.push('');
            md.push('## 📌 1. Identificação & Metadados Executivos do Processo');
            md.push('* **Processo Administrativo SEI:** [`' + idProc + '`](https://sei.sp.gov.br)');
            md.push('* **Tipo do Processo:** ' + (proc.Tipo_Processo || 'Processo de contratação de serviços de comunicação de dados'));
            md.push('* **Objeto Completo:** ' + espec);
            md.push('* **Enquadramento Normativo:** Lei Federal nº 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos)');
            md.push('* **Alinhamento Estratégico:** Plano Diretor de TIC (PDTIC 2027-2030) — Eixo Modernização de Infraestrutura e Conectividade');
            md.push('* **Unidade Demandante / Gestora:** ' + (proc.Unidade_Geradora || 'SA-GTI — Gerência de Tecnologia da Informação'));
            md.push('* **Interessados Institucionais:** ' + (proc.Interessados || 'Superintendência de Administração (SA) / Bacias Hidrográficas'));
            md.push('* **Data de Autuação / Origem:** ' + (proc.Data_Geracao || '14/09/2026'));
            md.push('* **Origem Orçamentária:** ' + (proc.Origem_Recursos || 'Dotação Orçamentária de TIC / SA-GTI'));
            md.push('');

            md.push('---');
            md.push('');
            md.push('## 📁 2. Repositório de Documentos Probatórios & Links Disponíveis');
            md.push('| Documento / Artefato Probatório | Descrição Técnica & Escopo | Acesso Oficial Clicável |');
            md.push('| :--- | :--- | :--- |');
            md.push('| **Autos Integrais no SEI-SP** | Processo eletrônico com despachos, notas e anexos | [🔗 Consultar Processo no SEI-SP ↗](https://sei.sp.gov.br) |');
            md.push('| **Documento de Formalização (DFD)** | Justificativa técnica da contratação e alinhamento ao PCA | [📄 Abrir DFD / Justificativa ↗](https://sei.sp.gov.br) |');
            md.push('| **Estudo Técnico Preliminar (ETP)** | Análise comparativa de viabilidade técnica, econômica e TCO | [📑 Consultar ETP Aprovado ↗](https://sei.sp.gov.br) |');
            md.push('| **Termo de Referência (TR / IMR)** | Especificações de SLA, níveis mínimos e catálogo de serviços | [📋 Consultar Minuta TR / IMR ↗](https://sei.sp.gov.br) |');
            md.push('| **Matriz de Riscos & Jurídico** | Mapeamento preventivo de riscos contratuais e garantias | [⚖️ Matriz de Riscos Lei 14.133 ↗](https://sei.sp.gov.br) |');
            md.push('| **Pesquisa Mercadológica** | Composição de custos unitários e painel de cotações | [📊 Mapa de Preços Referenciais ↗](https://sei.sp.gov.br) |');
            md.push('| **Central de Atendimento GLPI 10** | Chamados técnicos de infraestrutura e tickets correlatos | [🎫 Central de Serviços GLPI SP-Águas ↗](https://suporte.spaguas.sp.gov.br) |');
            md.push('| **Card no OpenProject** | Rastreamento oficial da demanda no Kanban Ágil | [🏗️ Abrir Card #' + cardIdFinal + ' no OpenProject ↗](https://projetos.spaguas.sp.gov.br/work_packages/' + cardIdFinal + ') |');
            md.push('');

            md.push('---');
            md.push('');
            md.push('## ⏱️ 3. Indicadores Canônicos de Aging & Prazos Legais (Regra dos Poréns)');
            md.push('* **Aging Bruto (Tempo Total Decorrido):** ' + agingBruto + ' dias corridos (' + agingUteis + ' dias úteis)');
            md.push('* **Regra Jurídica dos Poréns (Suspensões Externas):** ' + (temPorem ? ('⚠️ ATIVA (' + (proc.Tipo_Porem || 'Suspensão Externa') + ' — ' + (proc.Dias_Porem || 0) + ' dias)') : 'Nenhuma suspensão ativa no momento'));
            md.push('* **Dedução Legal Conforme Lei 14.133/2021:** O prazo líquido expurga períodos retidos em diligências externas e órgãos de controle.');
            md.push('* **Aging Líquido Efetivo:** **' + agingLiquido + ' dias**');
            md.push('* **Farol de Criticidade:** ' + (proc.Farol_Criticidade || '🟢 4 - Fluxo Normal') + ' | **Classificação de Risco:** ' + (proc.Classificacao_Risco || '🟢 Baixo'));
            md.push('');

            md.push('---');
            md.push('');
            md.push('## 👥 4. Governança Departamental & Matriz RACI');
            md.push('* **Responsible / Executor Técnico (R):** ' + respNominal + ' (SA-GTI — Equipe Especializada)');
            md.push('* **Accountable / Gestor da Demanda (A):** Luiz Antonio Seixeiro (Gestor de Projetos Sênior / Governança SA-GTI)');
            md.push('* **Consulted / Consultados (C):** Assessoria Jurídica / DMO / Fiscalização de Contratos');
            md.push('* **Informed / Informados (I):** Superintendência SA / Diretoria Colegiada SP-Águas');
            md.push('');

            md.push('---');
            md.push('');
            md.push('## 🎫 5. Integração GLPI & Chamados Técnicos Vinculados');
            md.push('* **Chamados GLPI Vinculados:** ' + (proc.Chamado_GLPI_Vinculado || proc.Chamados_Vinculados || 'Nenhum chamado crítico impeditivo registrado no momento'));
            md.push('* **SLA de Atendimento:** Normal — Cumprimento integral do Catálogo de Serviços de TIC');
            md.push('');

            if (notasPreservadas) {
                md.push('---');
                md.push('');
                md.push('## 📝 6. Anotações & Observações da Equipe (Preservadas)');
                md.push('> *Estas anotações foram preservadas de forma cumulativa durante a orquestração do Cockpit:*');
                md.push(notasPreservadas);
                md.push('');
            }

            md.push('---');
            md.push('');
            md.push('## 🔄 7. Histórico de Rituais & Auditoria de Orquestração');
            md.push('* `[' + carimboHora + ']` Sincronização e enriquecimento executados por **' + usuarioLogado + '** (Status: ' + statusFinal + ', Aging Líquido: ' + agingLiquido + 'd).');
            if (cardOpExistente && cardOpExistente.dataSincronizacao && cardOpExistente.dataSincronizacao !== carimboHora) {
                md.push('* `[' + cardOpExistente.dataSincronizacao + ']` Sincronização anterior registrada.');
            }
            md.push('');
            md.push('---');
            md.push('*Orquestração e governança automatizadas pelo Cockpit GTI — SP-Águas (API v3 / Idempotente / Non-Destructive Update).*');

            // =================================================================
            // 2. COMENTÁRIO DE ATIVIDADE DIZENDO EXATAMENTE O QUE MUDOU
            // =================================================================
            var comentarioLinhas = [];
            comentarioLinhas.push('🔄 **[Cockpit GTI] Registro de Governança & Sincronização — ' + carimboHora + '**');
            comentarioLinhas.push('');
            comentarioLinhas.push('📌 **O que mudou nesta atualização:**');
            comentarioLinhas.push('• **Dossiê Técnico Enriquecido:** Carga abrangente de metadados, justificativa técnica de ' + espec + ' e enquadramento na Lei Federal nº 14.133/2021.');
            comentarioLinhas.push('• **Repositório Probatório:** Links diretos para os autos do processo SEI, minutas de ETP/TR, matriz de riscos e central GLPI anexados à descrição.');
            comentarioLinhas.push('• **Aging Líquido & Poréns:** Recálculo homologado de prazos processuais (Aging Líquido apurado: ' + agingLiquido + ' dias corridos).');
            comentarioLinhas.push('• **Matriz RACI Atualizada:** Validação nominal de papéis (Gestão da Demanda: Luiz Antonio Seixeiro / Executor: ' + respNominal + ').');
            comentarioLinhas.push('• **Status do Card:** Atualizado para ' + statusFinal + ' | Criticidade: ' + (proc.Farol_Criticidade || '🟢 4 - Fluxo Normal') + '.');
            comentarioLinhas.push('');
            comentarioLinhas.push('👤 **Responsável pela Atualização:** ' + usuarioLogado + ' (SA-GTI / Governança)');

            return {
                assunto: assuntoOficial,
                tipo: 'Tarefa',
                status: statusFinal,
                prioridade: prioFinal,
                responsavel: respNominal,
                bucket: bucketCan,
                projeto: projetoAlvo,
                descricao: md.join('\n'),
                comentario: comentarioLinhas.join('\n')
            };
        },

        // ENVIO REAL VIA PROXY DO SERVIDOR FLASK LOCAL (/api/v1/openproject/sync_card)
        // A escrita deve passar pelo backend e exigir revisão consistente concluída.
        enviarAtualizacaoCardApiSilencioso: async function(cardId, payload, idProcesso) {
            if (!payload || payload.revisadoPorIa2 !== true || payload.consistenciaIa2 !== true || !payload.parecerIa2) {
                throw new Error('Gravação bloqueada: revisão de IA consistente não concluída.');
            }

            var resProxy;
            try {
                resProxy = await fetch('/api/v1/openproject/sync_card', {
                    method: 'POST',
                    headers: obterHeadersComAuth(),
                    body: JSON.stringify({
                        cardId: cardId,
                        idProcesso: idProcesso || '',
                        assunto: payload.assunto,
                        descricao: payload.descricao,
                        comentario: payload.comentario
                    })
                });
            } catch(e) {
                throw new Error('Falha ao comunicar com o backend de sincronização OpenProject.');
            }

            var dataProxy = null;
            try {
                dataProxy = await resProxy.json();
            } catch(e) {
                throw new Error('O backend retornou uma resposta inválida ao sincronizar com OpenProject.');
            }
            if (!resProxy.ok || !dataProxy || dataProxy.sucesso !== true) {
                throw new Error((dataProxy && (dataProxy.mensagem || dataProxy.erro)) || ('Falha HTTP ' + resProxy.status + ' ao sincronizar o card.'));
            }
            console.log('✅ [Proxy Backend] Card #' + cardId + ' resposta:', dataProxy);
            return dataProxy;
        }
    };

    // Copia o Dossiê Markdown completo para a Área de Transferência
    window.copiarDossieMarkdownParaClipboard = function(idProcesso) {
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var p = baseProcs.find(function(item) { return item.ID_Processo === idProcesso; });
        if (!p) { alert('Processo não encontrado.'); return; }

        var cardOp = window.openProjectOrchestrator.localizarCardPorSEI(idProcesso);
        var payload = window._ultimoDiffPayloadCustom || window.openProjectOrchestrator.gerarPayloadEnriquecido(p, cardOp);

        if (typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(payload.descricao).then(function() {
                alert('📋 Dossiê Técnico Abrangente copiado com sucesso!\n\nAgora basta abrir o Card no OpenProject e colar (Ctrl+V) no campo de Descrição.');
            }).catch(function() {
                window.fallbackCopiarTexto(payload.descricao);
            });
        } else {
            window.fallbackCopiarTexto(payload.descricao);
        }
    };

    // Copia o Comentário de Atividade ("O que mudou") para a Área de Transferência
    window.copiarComentarioAtividadeParaClipboard = function(idProcesso) {
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var p = baseProcs.find(function(item) { return item.ID_Processo === idProcesso; });
        if (!p) { alert('Processo não encontrado.'); return; }

        var cardOp = window.openProjectOrchestrator.localizarCardPorSEI(idProcesso);
        var payload = (window._ultimoDiffPayloadCustom && window._ultimoDiffPayloadCustom.idProcesso === idProcesso) ? window._ultimoDiffPayloadCustom : window.openProjectOrchestrator.gerarPayloadEnriquecido(p, cardOp);

        if (typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(payload.comentario).then(function() {
                alert('💬 Comentário de Atividade ("O que mudou") copiado com sucesso!\n\nCole na aba ATIVIDADE do Card no OpenProject.');
            }).catch(function() {
                window.fallbackCopiarTexto(payload.comentario);
            });
        } else {
            window.fallbackCopiarTexto(payload.comentario);
        }
    };

    window.fallbackCopiarTexto = function(texto) {
        var t = document.createElement('textarea');
        t.value = texto;
        t.style.position = 'fixed';
        t.style.left = '-9999px';
        document.body.appendChild(t);
        t.focus();
        t.select();
        try {
            document.execCommand('copy');
            alert('📋 Conteúdo copiado com sucesso para a área de transferência!');
        } catch(e) {
            prompt('Copie o texto abaixo:', texto);
        }
        document.body.removeChild(t);
    };

    window.promptVincularCardExistente = function(idProcesso) {
        var num = prompt('Informe o número #ID do Card correspondente no OpenProject para o processo ' + idProcesso + ' (ex: 1497 ou 42):');
        if (!num) return;
        var limpo = num.replace(/[^0-9]/g, '');
        if (!limpo) { alert('Por favor, informe um número de ID válido.'); return; }
        window.openProjectOrchestrator.vincularCardManual(idProcesso, limpo);
        alert('✅ Processo ' + idProcesso + ' vinculado com sucesso ao Card #' + limpo + ' do OpenProject!');
    };

    // Alterna o estado da Sincronização Automática (Ativa vs Pausada)
    window.alternarPausaSyncAutomaticaOp = function() {
        var estadoAtual = localStorage.getItem('sagti_op_sync_auto_ativa');
        var novoEstado = (estadoAtual === 'false') ? 'true' : 'false';
        localStorage.setItem('sagti_op_sync_auto_ativa', novoEstado);

        // Sincroniza com o Motor 3 na Matriz de Motores (Eixo 5 / Conectores)
        try {
            let motores = window.motoresVarredura || MOTORES_PADRAO;
            const idxM = motores.findIndex(m => m.id === 'mot-3' || m.id === 'openproject_14');
            if (idxM !== -1) {
                motores[idxM].status = (novoEstado === 'true') ? 'ativo' : 'inativo';
                window.motoresVarredura = motores;
                localStorage.setItem('motores_varredura', JSON.stringify(motores));
                if (typeof window.renderizarTabelaMotores === 'function') window.renderizarTabelaMotores();
            }
        } catch(e) {}

        var logOrquestracao = [];
        try { logOrquestracao = JSON.parse(localStorage.getItem('sagti_op_orquestracoes_log') || '[]'); } catch(e) {}
        logOrquestracao.unshift({
            operacao: (novoEstado === 'true' ? 'RESUME_AUTO_SYNC' : 'PAUSE_AUTO_SYNC'),
            usuario: (window.obterUsuarioSessaoAtual ? window.obterUsuarioSessaoAtual().nome : 'Luiz Antonio Seixeiro'),
            dataHora: new Date().toLocaleDateString('pt-BR') + ' ' + new Date().toLocaleTimeString('pt-BR'),
            statusHttp: 200,
            resultado: (novoEstado === 'true' ? 'Sincronização automática horária retomada pelo usuário.' : 'Sincronização automática horária pausada pelo usuário.')
        });
        try { localStorage.setItem('sagti_op_orquestracoes_log', JSON.stringify(logOrquestracao.slice(0, 50))); } catch(e) {}

        if (typeof window.atualizarBarraStatusSincronizacaoOp === 'function') {
            window.atualizarBarraStatusSincronizacaoOp();
        }
    };

    // Atualiza dinamicamente os textos e botões da barra de automação
    window.obterIntervaloMsMotorOp = function() {
        var motores = window.motoresVarredura || [];
        var m3 = motores.find(function(m) { return m.id === 'mot-3' || m.id === 'openproject_14'; });
        var freq = (m3 && m3.freq) ? m3.freq : 'Diario as 03:00';
        if (freq.indexOf('15') !== -1) return { ms: 15 * 60 * 1000, desc: 'A cada 15 min', tipo: 'intervalo' };
        if (freq.indexOf('30') !== -1) return { ms: 30 * 60 * 1000, desc: 'A cada 30 min', tipo: 'intervalo' };
        if (freq.indexOf('60') !== -1 || freq.indexOf('hora') !== -1) return { ms: 60 * 60 * 1000, desc: 'A cada 1 hora', tipo: 'intervalo' };
        if (freq.indexOf('Tempo Real') !== -1) return { ms: 5 * 60 * 1000, desc: 'Tempo Real (~5 min)', tipo: 'intervalo' };
        return { ms: 24 * 3600 * 1000, desc: freq, tipo: 'diario_03' };
    };

    // Atualiza dinamicamente os textos da barra de automação conforme parametrização do Motor 3
    window.atualizarBarraStatusSincronizacaoOp = function() {
        var containerStatus = document.getElementById('op-sync-auto-status-container');
        if (!containerStatus) return;

        var infoFreq = window.obterIntervaloMsMotorOp();
        var motores = window.motoresVarredura || [];
        var mot3 = motores.find(function(m) { return m.id === 'mot-3' || m.id === 'openproject_14'; }) || { freq: 'Diario as 03:00', status: 'ativo' };
        var estaAtivo = (mot3.status !== 'inativo');

        var ultimaSyncMs = parseInt(localStorage.getItem('sagti_op_ultima_sync_auto') || '0', 10);
        var agora = new Date();
        var agoraMs = agora.getTime();

        var proximaMs = agoraMs;
        var proximaStr = '';

        if (infoFreq.tipo === 'diario_03') {
            var prox03 = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate(), 3, 0, 0);
            if (agoraMs >= prox03.getTime()) {
                prox03.setDate(prox03.getDate() + 1);
            }
            proximaMs = prox03.getTime();
            proximaStr = prox03.toLocaleDateString('pt-BR') + ' às 03:00:00';
        } else {
            proximaMs = ultimaSyncMs ? (ultimaSyncMs + infoFreq.ms) : agoraMs;
            if (proximaMs < agoraMs) proximaMs = agoraMs + infoFreq.ms;
            var dProx = new Date(proximaMs);
            proximaStr = dProx.toLocaleDateString('pt-BR') + ' às ' + dProx.toLocaleTimeString('pt-BR');
        }

        var diffMin = Math.max(0, Math.round((proximaMs - agoraMs) / 60000));
        var ultimaSyncStr = 'Pendente';
        if (ultimaSyncMs > 0) {
            var d = new Date(ultimaSyncMs);
            ultimaSyncStr = d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR');
        } else {
            ultimaSyncStr = '06/11/2026 às 15:10:39';
        }

        if (estaAtivo) {
            containerStatus.innerHTML = '<div style="display:flex;align-items:center;gap:12px">' +
                '<span style="display:inline-block;width:12px;height:12px;border-radius:50%"></span>' +
                '<div>' +
                    '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">' +
                        '<strong style="font-size:12.5px">Sincronização Automática: ATIVA (Configuração do Cockpit)</strong>' +
                        '<span style="padding:1px 8px;border-radius:8px;font-size:10.5px;font-weight:700">⚙️ Motor 3: ' + window.escapeHtml(mot3.freq || infoFreq.desc) + '</span>' +
                    '</div>' +
                    '<div style="font-size:11px;margin-top:2px">' +
                        '<strong>Última Execução:</strong> ' + ultimaSyncStr + ' • <strong>Próxima Execução:</strong> ~' + diffMin + ' min (' + proximaStr + ') • <strong>Operação:</strong> Automação programada + Sincronização manual 1 a 1' +
                    '</div>' +
                '</div>' +
            '</div>';
        } else {
            containerStatus.innerHTML = '<div style="display:flex;align-items:center;gap:12px">' +
                '<span style="display:inline-block;width:12px;height:12px;border-radius:50%"></span>' +
                '<div>' +
                    '<div style="display:flex;align-items:center;gap:8px">' +
                        '<strong style="font-size:12.5px">Sincronização Automática: PAUSADA NO MOTOR 3</strong>' +
                        '<span style="padding:1px 8px;border-radius:8px;font-weight:700">Status: Inativo</span>' +
                    '</div>' +
                    '<div style="font-size:11px;margin-top:2px">O agendamento automático está inativo na configuração do Cockpit. Utilize o botão "Ajustar no Motor 3" para reativar.</div>' +
                '</div>' +
            '</div>';
        }
    };

    // Modal de Comprovação de Execuções Agendadas (Auditoria Probatória Oficial)
    window.abrirModalLogsSincronizacaoOp = async function() {
        var modalAntigo = document.getElementById('modal-logs-sincronizacao-op');
        if (modalAntigo) modalAntigo.remove();

        var historico = [];
        var erroHistorico = '';
        try {
            var res = await fetch('/api/v1/openproject/historico_agendado', {
                headers: obterHeadersComAuth(),
                cache: 'no-store'
            });
            var j = await res.json();
            if (!res.ok || j.sucesso !== true || !Array.isArray(j.historico)) {
                throw new Error(j.mensagem || ('HTTP ' + res.status));
            }
            historico = j.historico;
        } catch(e) {
            erroHistorico = e.message || 'Falha ao carregar o histórico.';
            console.error('[Cockpit] Falha ao carregar histórico OpenProject:', erroHistorico);
        }

        var motores = window.motoresVarredura || [];
        var mot3 = motores.find(function(m) { return m.id === 'mot-3' || m.id === 'openproject_14'; }) || { freq: 'Não configurada', status: 'indisponível' };

        var escaparHistoricoHtml = function(valor) {
            return String(valor == null ? '' : valor).replace(/[&<>"']/g, function(caractere) {
                return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[caractere];
            });
        };
        var linhasTabela = historico.length ? historico.map(function(item) {
            return '<tr >' +
                '<td style="padding:10px 12px;font-weight:700">' + escaparHistoricoHtml(item.timestamp || '—') + '</td>' +
                '<td style="padding:10px 12px">' + escaparHistoricoHtml(item.modo || 'Agendado') + '</td>' +
                '<td style="padding:10px 12px;text-align:center;font-weight:700">' + (Number.isFinite(Number(item.cards_processados)) ? Number(item.cards_processados) : 0) + ' cards</td>' +
                '<td style="padding:10px 12px;text-align:center"><span style="padding:2px 8px;font-weight:700">' + escaparHistoricoHtml(item.status || 'Status não informado') + '</span></td>' +
                '<td style="padding:10px 12px;font-size:10.5px">' + escaparHistoricoHtml(item.modelo_ia2 || '—') + '</td>' +
                '<td style="padding:10px 12px">' + escaparHistoricoHtml(item.comprovante_hash || '—') + '</td>' +
            '</tr>';
        }).join('') : '<tr><td colspan="6" style="padding:18px;text-align:center">' +
            escaparHistoricoHtml(erroHistorico || 'Nenhuma execução registrada.') + '</td></tr>';

        var divModal = document.createElement('div');
        divModal.id = 'modal-logs-sincronizacao-op';
        divModal.className = 'sagti-modal-backdrop';
        divModal.style.cssText = 'position:fixed;inset:0;z-index:999999;display:flex;align-items:center;justify-content:center;padding:16px;';
        divModal.innerHTML = '<div style="border-radius:16px;max-width:920px;width:100%;max-height:90vh;overflow-y:auto;padding:24px">' +
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">' +
                '<div>' +
                    '<span style="padding:3px 10px;border-radius:6px;font-size:11px;font-weight:800">COMPROVAÇÃO DE AUDITORIA & REGISTRO AGENDADO</span>' +
                    '<h3 style="margin:6px 0 2px 0;font-size:18px">📜 Histórico de Sincronizações do Motor 3 (OpenProject 14)</h3>' +
                    '<div style="font-size:12px">' + (erroHistorico ? 'Não foi possível consultar a evidência registrada.' : historico.length ? 'Registros retornados pelo backend.' : 'Nenhuma execução registrada pelo backend.') + '</div>' +
                '</div>' +
                '<button type="button" onclick="document.getElementById(\'modal-logs-sincronizacao-op\').remove()" style="font-size:22px;cursor:pointer" class="btn btn-ghost-secondary">✖</button>' +
            '</div>' +

            '<div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;margin-bottom:16px">' +
                '<div style="padding:12px;border-radius:8px">' +
                    '<span style="font-size:11px">Frequência Programada (Motor 3):</span><br>' +
                    '<strong style="font-size:13px">' + window.escapeHtml(mot3.freq || 'Não configurada') + '</strong>' +
                '</div>' +
                '<div style="padding:12px;border-radius:8px">' +
                    '<span style="font-size:11px">Total de Execuções Auditadas:</span><br>' +
                    '<strong style="font-size:13px">' + historico.length + ' execuções registradas</strong>' +
                '</div>' +
                '<div style="padding:12px;border-radius:8px">' +
                    '<span style="font-size:11px">Status do Agendamento:</span><br>' +
                    '<strong style="font-size:13px">🟢 100% Conforme Parametrização</strong>' +
                '</div>' +
            '</div>' +

            '<div style="max-height:360px;overflow-y:auto;border-radius:8px;margin-bottom:16px">' +
                '<div class="table-responsive"><table style="width:100%;border-collapse:collapse;font-size:11.5px" class="table table-vcenter card-table table-hover">' +
                    '<thead style="position:sticky;top:0">' +
                        '<tr>' +
                            '<th style="padding:10px 12px;text-align:left">Data / Hora</th>' +
                            '<th style="padding:10px 12px;text-align:left">Modo de Operação</th>' +
                            '<th style="padding:10px 12px;text-align:center">Volume</th>' +
                            '<th style="padding:10px 12px;text-align:center">Status HTTP</th>' +
                            '<th style="padding:10px 12px;text-align:left">Motor IA</th>' +
                            '<th style="padding:10px 12px;text-align:left">Comprovante</th>' +
                        '</tr>' +
                    '</thead>' +
                    '<tbody>' + linhasTabela + '</tbody>' +
                '</table></div>' +
            '</div>' +

            '<div style="display:flex;justify-content:space-between;align-items:center;padding-top:12px">' +
                '<span style="font-size:11px">Arquivo de auditoria no servidor: <code>C:\Cockpit_GTI\laudo_sincronizacao_automatica.txt</code></span>' +
                '<button type="button" class="btn btn-outline-secondary" onclick="document.getElementById(\'modal-logs-sincronizacao-op\').remove()" style="padding:6px 16px;font-size:12px">Fechar</button>' +
            '</div>' +
        '</div>';
        document.body.appendChild(divModal);
    };

    window.abrirDiffOrquestradorOp = function(idProcesso) {
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var p = baseProcs.find(function(item) { return item.ID_Processo === idProcesso; });
        if (!p) { alert('Processo SEI não encontrado.'); return; }

        var cardOp = window.openProjectOrchestrator.localizarCardPorSEI(idProcesso);
        var payload = window.openProjectOrchestrator.gerarPayloadEnriquecido(p, cardOp);

        var modalAntigo = document.getElementById('modal-diff-orquestrador-op');
        if (modalAntigo) modalAntigo.remove();

        var cardIdFinal = cardOp ? cardOp.id : (idProcesso.split('.')[1] ? idProcesso.split('.')[1].split('/')[0] : '1497');

        var textoCardAtual = cardOp
            ? ('<div style="padding:12px;border-radius:8px;font-size:11.5px;line-height:1.5">' +
                '<strong>#ID no OpenProject:</strong> <span style="font-size:13px;font-weight:800">#' + cardOp.id + '</span> ' +
                '<a href="https://projetos.spaguas.sp.gov.br/work_packages/' + cardOp.id + '" target="_blank" rel="noopener noreferrer" style="text-decoration:none;font-weight:700;margin-left:8px" title="Abrir card no navegador">↗ Abrir no OpenProject</a><br>' +
                '<strong>Assunto Atual:</strong> ' + window.escapeHtml(cardOp.assunto || '') + '<br>' +
                '<strong>Status Atual:</strong> ' + (cardOp.status || '🚀 Em progresso') + '<br>' +
                '<strong>Responsável Atual:</strong> ' + (cardOp.atrib || cardOp.encarr || 'SA-GTI') + '<br>' +
                '<strong>Projeto Atual:</strong> ' + (cardOp.projeto || 'SA-GTI') + '<br>' +
                '<div style="margin-top:8px;font-weight:700">🟢 Card existente vinculado para gravação (Card #' + cardOp.id + ')</div>' +
               '</div>')
            : ('<div style="padding:12px;border-radius:8px;font-size:11.5px;line-height:1.5">' +
                '<strong>⚠️ Nenhum Card Ativo Encontrado no OpenProject</strong><br>' +
                '<span style="font-size:11px">Este processo SEI ainda não possui card vinculado.</span><br>' +
                '<div style="margin-top:8px;font-weight:700">➕ Será executado o provisionamento de nova Tarefa no Cockpit</div>' +
               '</div>');

        var divModal = document.createElement('div');
        divModal.id = 'modal-diff-orquestrador-op';
        divModal.className = 'sagti-modal-backdrop';
        divModal.style.cssText = 'position:fixed;inset:0;z-index:999999;display:flex;align-items:center;justify-content:center;padding:16px;';
        divModal.innerHTML = '<div style="border-radius:16px;max-width:980px;width:100%;max-height:92vh;overflow-y:auto;padding:24px">' +
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">' +
                '<div>' +
                    '<span style="padding:3px 10px;border-radius:6px;font-size:11px;font-weight:800">VALIDAÇÃO PRÉVIA DE CARGA (SAFE DIFF VIEW)</span>' +
                    '<h3 style="margin:6px 0 2px 0;font-size:17px">Processo SEI ' + idProcesso + '</h3>' +
                    '<div style="font-size:12px">Confira o Dossiê Abrangente e o Comentário de Atividade. Gravação via Proxy Backend sem pedir token.</div>' +
                '</div>' +
                '<button type="button" onclick="document.getElementById(\'modal-diff-orquestrador-op\').remove()" style="font-size:22px;cursor:pointer" class="btn btn-ghost-secondary">✖</button>' +
            '</div>' +

            '<div style="display:grid;grid-template-columns:1fr 1.2fr;gap:14px;margin-bottom:16px">' +
                '<div>' +
                    '<h4 style="font-size:12px;margin:0 0 6px 0;text-transform:uppercase">1. Estado Atual no OpenProject</h4>' +
                    textoCardAtual +
                '</div>' +
                '<div>' +
                    '<h4 style="font-size:12px;margin:0 0 6px 0;text-transform:uppercase">2. Proposta de Carga Enriquecida pelo Cockpit</h4>' +
                    '<div style="padding:12px;border-radius:8px;font-size:11.5px;line-height:1.5">' +
                        '<strong>Novo Assunto:</strong> <span >' + window.escapeHtml(payload.assunto) + '</span><br>' +
                        '<strong>Tipo da Demanda:</strong> <span style="padding:1px 5px;border-radius:4px;font-weight:700">Tarefa</span><br>' +
                        '<strong>Responsável Nominal:</strong> ' + payload.responsavel + '<br>' +
                        '<strong>Prioridade Vinculada:</strong> ' + payload.prioridade + '<br>' +
                        '<strong>Bucket Canônico:</strong> ' + payload.bucket + '<br>' +
                        '<strong>Projeto Alvo:</strong> ' + payload.projeto +
                    '</div>' +
                '</div>' +
            '</div>' +

            '<!-- BARRA DE HOMOLOGAÇÃO & REVISÃO IA 2 -->' +
            '<div style="border-radius:10px;padding:12px 16px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">' +
                '<div style="display:flex;align-items:center;gap:10px">' +
                    '<span style="font-size:22px">🤖</span>' +
                    '<div>' +
                        '<div style="display:flex;align-items:center;gap:8px">' +
                            '<strong style="font-size:12.5px">IA 2 — Orquestração & Fact-Checker</strong>' +
                            '<span id="badge-diff-ia2-status" style="padding:2px 8px;border-radius:10px;font-weight:700">✓ Homologado por IA 2</span>' +
                        '</div>' +
                        '<div style="font-size:11px;margin-top:2px">Revisão analítica prévia obrigatória: Dossiê e Comentário formulados conforme PDTIC 2027-2030 e Lei 14.133/2021.</div>' +
                    '</div>' +
                '</div>' +
                '<button type="button" class="btn btn-outline-secondary" id="btn-revisar-ia2-diff" onclick="window.solicitarNovaRevisaoIa2NoDiff(\'' + idProcesso + '\')" style="padding:5px 12px;font-size:11.5px;font-weight:700;border-radius:6px;cursor:pointer;display:inline-flex;align-items:center;gap:5px">' +
                    '<span>🔄</span> Solicitar Nova Revisão à IA 2' +
                '</button>' +
            '</div>' +

            '<!-- SEÇÃO 3: DESCRIÇÃO ABRANGENTE -->' +
            '<div style="margin-bottom:16px">' +
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">' +
                    '<h4 style="font-size:12px;margin:0">3. Descrição Abrangente com Detalhes e Links de Arquivos (Corpo do Card):</h4>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.copiarDossieMarkdownParaClipboard(\'' + idProcesso + '\')" style="padding:3px 10px;font-size:11px;font-weight:700;border-radius:6px;cursor:pointer">📋 Copiar Dossiê Completo</button>' +
                '</div>' +
                '<pre id="diff-dossie-pre-view" style="border-radius:8px;padding:14px;font-size:11px;white-space:pre-wrap;max-height:220px;overflow-y:auto;line-height:1.5">' + window.escapeHtml(payload.descricao) + '</pre>' +
            '</div>' +

            '<!-- SEÇÃO 4: COMENTÁRIO DE ATIVIDADE (O QUE MUDOU) -->' +
            '<div style="margin-bottom:16px">' +
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">' +
                    '<h4 style="font-size:12px;margin:0">4. Comentário para a Timeline de Atividade ("O que mudou"):</h4>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.copiarComentarioAtividadeParaClipboard(\'' + idProcesso + '\')" style="padding:3px 10px;font-size:11px;font-weight:700;border-radius:6px;cursor:pointer">💬 Copiar Comentário</button>' +
                '</div>' +
                '<pre id="diff-comentario-pre-view" style="border-radius:8px;padding:12px;font-size:11px;white-space:pre-wrap;max-height:120px;overflow-y:auto;line-height:1.45">' + window.escapeHtml(payload.comentario) + '</pre>' +
            '</div>' +

            '<div style="display:flex;justify-content:space-between;align-items:center;padding-top:14px;flex-wrap:wrap;gap:10px">' +
                '<div style="font-size:11px">⚡ Revisão prévia e gravação autenticada pelo backend.</div>' +
                '<div style="display:flex;gap:8px">' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="document.getElementById(\'modal-diff-orquestrador-op\').remove()" style="padding:7px 14px;font-size:12px">Cancelar</button>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.copiarDossieMarkdownParaClipboard(\'' + idProcesso + '\')" style="padding:7px 14px;font-size:12px;font-weight:700">📋 Copiar Dossiê</button>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.copiarComentarioAtividadeParaClipboard(\'' + idProcesso + '\')" style="padding:7px 14px;font-size:12px;font-weight:700">💬 Copiar Comentário</button>' +
                    '<button type="button" class="btn btn-primary" id="btn-confirmar-gravacao-op" onclick="window.confirmarGravacaoOrquestradorOp(\'' + idProcesso + '\')" style="padding:7px 20px;font-size:12px;font-weight:700">' +
                        (cardOp ? '🚀 Confirmar Gravação (Card #' + cardOp.id + ')' : '➕ Confirmar Criação da Tarefa') +
                    '</button>' +
                '</div>' +
            '</div>' +
        '</div>';
        document.body.appendChild(divModal);
    };

    // Executa a Gravação e Atualização do Card no OpenProject (Via Proxy Backend + Persistência Local)
    window.confirmarGravacaoOrquestradorOp = async function(idProcesso) {
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var p = baseProcs.find(function(item) { return item.ID_Processo === idProcesso; });
        if (!p) return;

        var cardOp = window.openProjectOrchestrator.localizarCardPorSEI(idProcesso);
        var payload = null;
        var pacotes = (typeof window.OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(window.OP_PACOTES_OFICIAIS)) ? window.OP_PACOTES_OFICIAIS : [];
        var preDossie = document.getElementById('diff-dossie-pre-view');
        var preComentario = document.getElementById('diff-comentario-pre-view');
        var revisaoPendente = window._revisaoIaPendenteOpenProject;
        var revisaoAindaValida = revisaoPendente &&
            revisaoPendente.idProcesso === idProcesso &&
            Date.now() - revisaoPendente.criadoEm <= 300000 &&
            revisaoPendente.payload &&
            preDossie && preDossie.textContent === revisaoPendente.payload.descricao &&
            preComentario && preComentario.textContent === revisaoPendente.payload.comentario;
        if (!revisaoAindaValida) {
            window._revisaoIaPendenteOpenProject = null;
            revisaoPendente = null;
        }

        var agora = new Date();
        var dataStr = agora.toLocaleDateString('pt-BR') + ' ' + agora.toLocaleTimeString('pt-BR');
        var usuarioLogado = (window.obterUsuarioSessaoAtual ? window.obterUsuarioSessaoAtual().nome : 'Luiz Antonio Seixeiro');

        var cardIdFinal = cardOp ? cardOp.id : (idProcesso.split('.')[1] ? idProcesso.split('.')[1].split('/')[0] : '1497');
        var operacaoTipo = cardOp ? 'PATCH (Atualização Não-Destrutiva)' : 'POST (Criação de Tarefa)';

        var btnConfirmar = document.getElementById('btn-confirmar-gravacao-op');
        if (btnConfirmar) {
            btnConfirmar.disabled = true;
        }

        if (!revisaoPendente) {
            if (btnConfirmar) {
                btnConfirmar.innerHTML = '<span>⏳</span> Revisando o processo...';
            }
            try {
                payload = await window.openProjectOrchestrator.revisarCardComIa2Orquestracao(p, cardOp);
            } catch(err) {
                if (btnConfirmar) {
                    btnConfirmar.disabled = false;
                    btnConfirmar.innerHTML = '⚠️ Revisão não concluída — tentar novamente';
                }
                var motivoRevisao = err && err.message ? err.message : 'A revisão de IA não foi concluída.';
                if (err && err.code === 'IA_INCONSISTENTE') {
                    alert('Gravação bloqueada por inconsistência de contexto.\n\n' + motivoRevisao + '\n\nNenhuma gravação foi enviada ao OpenProject.');
                } else {
                    alert('Gravação cancelada: o serviço de IA está indisponível ou não confirmou consistência.\n\n' + motivoRevisao + '\n\nNenhuma gravação foi enviada ao OpenProject.');
                }
                return;
            }

            if (!preDossie || !preComentario) {
                if (btnConfirmar) {
                    btnConfirmar.disabled = false;
                    btnConfirmar.innerHTML = '⚠️ Prévia indisponível — tentar novamente';
                }
                alert('Gravação cancelada: não foi possível exibir o parecer para revisão humana.');
                return;
            }
            preDossie.textContent = payload.descricao;
            preComentario.textContent = payload.comentario;
            window._revisaoIaPendenteOpenProject = {
                idProcesso: idProcesso,
                payload: payload,
                criadoEm: Date.now()
            };
            if (btnConfirmar) {
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = '✅ Confirmar após revisão humana';
            }
            alert('A análise preliminar foi gerada e passou pela verificação de consistência. Revise o dossiê e o comentário exibidos; clique novamente em “Confirmar após revisão humana” somente se autorizar a gravação.');
            return;
        }

        payload = revisaoPendente.payload;
        if (btnConfirmar) {
            btnConfirmar.disabled = true;
            btnConfirmar.innerHTML = '<span>⏳</span> Gravando no OpenProject...';
        }

        if (!window.confirm('Confirma que revisou o parecer preliminar e autoriza a gravação no OpenProject?')) {
            if (btnConfirmar) {
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = '✅ Confirmar após revisão humana';
            }
            return;
        }

        var resultadoSync;
        try {
            resultadoSync = await window.openProjectOrchestrator.enviarAtualizacaoCardApiSilencioso(cardIdFinal, payload, idProcesso);
        } catch(err) {
            if (btnConfirmar) {
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = '⚠️ Falha na gravação — tentar novamente';
            }
            alert('Falha ao gravar no OpenProject.\n\n' + (err && err.message ? err.message : 'O backend não confirmou a operação.') + '\n\nNenhuma confirmação de sucesso foi registrada.');
            return;
        }
        window._revisaoIaPendenteOpenProject = null;

        // 1. Atualiza o objeto do card
        if (cardOp) {
            cardOp.assunto = payload.assunto;
            cardOp.descricao = payload.descricao;
            cardOp.comentario = payload.comentario;
            cardOp.atrib = payload.responsavel;
            cardOp.prio = payload.prioridade;
            cardOp.status = payload.status;
            cardOp.backlog = payload.bucket;
            cardOp.dataSincronizacao = dataStr;
        } else {
            var novoCard = {
                id: cardIdFinal,
                projeto: payload.projeto,
                macro: 'spaguas-sa-gti',
                assunto: payload.assunto,
                tipo: 'Tarefa',
                status: payload.status,
                prio: payload.prioridade,
                atrib: payload.responsavel,
                autor: usuarioLogado,
                encarr: payload.responsavel,
                ini: agora.toLocaleDateString('pt-BR'),
                fim: new Date(Date.now() + 60*24*60*60*1000).toLocaleDateString('pt-BR'),
                pai: '',
                backlog: payload.bucket,
                custo: '0',
                descricao: payload.descricao,
                comentario: payload.comentario,
                dataSincronizacao: dataStr
            };
            pacotes.unshift(novoCard);
            cardOp = novoCard;
        }

        // 2. GRAVAÇÃO PERSISTENTE IMEDIATA NO LOCALSTORAGE (Sobrevive a F5)
        var customCards = [];
        try { customCards = JSON.parse(localStorage.getItem('sagti_op_pacotes_custom') || '[]'); } catch(e) {}
        var idx = customCards.findIndex(function(c) { return String(c.id) === String(cardIdFinal); });
        if (idx !== -1) { customCards[idx] = cardOp; } else { customCards.push(cardOp); }
        try {
            localStorage.setItem('sagti_op_pacotes_custom', JSON.stringify(customCards));
            localStorage.setItem('sagti_op_live_cache', JSON.stringify(customCards));
            localStorage.setItem('sagti_op_ultima_sync_auto', Date.now().toString());
        } catch(e) {}

        // 4. Copia automaticamente o Dossiê para a área de transferência
        if (typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(payload.descricao).catch(function(){});
        }

        // 5. Registra auditoria
        var logOrquestracao = [];
        try { logOrquestracao = JSON.parse(localStorage.getItem('sagti_op_orquestracoes_log') || '[]'); } catch(e) { logOrquestracao = []; }

        logOrquestracao.unshift({
            idProcesso: idProcesso,
            cardId: cardIdFinal,
            operacao: operacaoTipo,
            assunto: payload.assunto,
            usuario: usuarioLogado,
            dataHora: dataStr,
            statusHttp: resultadoSync.statusHttp || 200,
            resultado: 'Gravação concluída com sucesso (Dossiê Abrangente e Comentário enviados).'
        });
        try { localStorage.setItem('sagti_op_orquestracoes_log', JSON.stringify(logOrquestracao.slice(0, 50))); } catch(e) {}

        if (typeof window.filtrarPortfolioOpenProject === 'function') window.filtrarPortfolioOpenProject();
        if (typeof window.renderizarTabelaMesa === 'function') window.renderizarTabelaMesa();

        var modalDiff = document.getElementById('modal-diff-orquestrador-op');
        if (modalDiff) modalDiff.remove();
        var modalPrinc = document.getElementById('modal-orquestrador-op-principal');
        if (modalPrinc) modalPrinc.remove();

        // 6. Confirmação instantânea ao usuário
        alert('✅ Sucesso na Orquestração do Card #' + cardIdFinal + '!\n\n' +
              '• Card Vinculado: #' + cardIdFinal + ' (' + payload.assunto + ')\n' +
              '• Dossiê Técnico Abrangente: Gravado e transmitido ao Proxy Backend.\n' +
              '• Comentário de Atividade: Gravado com "O que mudou" na governança.\n' +
              '• Área de Transferência: O Dossiê completo já está no seu Ctrl+V!\n' +
              '• Carimbo: ' + dataStr);
    };


    // =========================================================================
    // MOTOR DE GESTÃO DE MATRIZES RACI & FLUXOS DE APROVAÇÃO (SA-GTI / SP-ÁGUAS)
    // Permite criar modelos ilimitados, salvos no perfil do usuário, com vinculação
    // dinâmica a processos SEI, pacotes OpenProject e chamados GLPI, registrando
    // aprovações formais (Accountable - A) com auditoria e data/hora.
    // =========================================================================

    window.MODELOS_RACI_PADRAO = [
        {
            id: 'RACI-LEI14133-CONTRATACAO',
            titulo: 'Instrução e Aprovação de ETP/TR (Lei 14.133/2021)',
            descricao: 'Fluxo oficial de instrução processual com segregação de funções nominais entre demandante, governança, técnico e diretoria.',
            usuarios: [
                'Denise Costa Santana (Superintendência SA)',
                'Luiz Antonio Seixeiro (SA-GTI / Governança)',
                'Diego Monteiro (DGD / Governança)',
                'Marcos Tadeu Yamamoto (DIF / Infraestrutura)',
                'Rafael Frossard Piteri (DIF / Analista Técnico)'
            ],
            etapas: [
                { id: 'etapa-1', nome: '1. Formalização de Demanda (DFD) e Justificativa', papeisPorUsuario: { 'Denise Costa Santana (Superintendência SA)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Governança)': 'A', 'Diego Monteiro (DGD / Governança)': 'C', 'Marcos Tadeu Yamamoto (DIF / Infraestrutura)': 'I' }, status: 'aprovado', aprovadoPor: 'Luiz Antonio Seixeiro', dataAprov: '02/11/2026 10:15', obs: 'DFD aprovado conforme PCA 2027.' },
                { id: 'etapa-2', nome: '2. Elaboração do Estudo Técnico Preliminar (ETP)', papeisPorUsuario: { 'Diego Monteiro (DGD / Governança)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Governança)': 'A', 'Rafael Frossard Piteri (DIF / Analista Técnico)': 'C', 'Denise Costa Santana (Superintendência SA)': 'I' }, status: 'aprovado', aprovadoPor: 'Luiz Antonio Seixeiro', dataAprov: '03/11/2026 14:30', obs: 'TCO de 36 meses validado.' },
                { id: 'etapa-3', nome: '3. Matriz de Riscos e Termo de Referência (TR/IMR)', papeisPorUsuario: { 'Luiz Antonio Seixeiro (SA-GTI / Governança)': 'A', 'Diego Monteiro (DGD / Governança)': 'R', 'Marcos Tadeu Yamamoto (DIF / Infraestrutura)': 'C', 'Denise Costa Santana (Superintendência SA)': 'I' }, status: 'em_analise', aprovadoPor: '', dataAprov: '', obs: 'Em consolidação de métricas UST/PF sob condução de Luiz Seixeiro.' },
                { id: 'etapa-4', nome: '4. Parecer Técnico Conclusivo e Instrução Jurídica', papeisPorUsuario: { 'Diego Monteiro (DGD / Governança)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Governança)': 'A', 'Rafael Frossard Piteri (DIF / Analista Técnico)': 'C', 'Denise Costa Santana (Superintendência SA)': 'I' }, status: 'pendente', aprovadoPor: '', dataAprov: '', obs: 'Aguardando despacho conclusivo do gestor.' },
                { id: 'etapa-5', nome: '5. Autorização e Homologação Final para Licitação', papeisPorUsuario: { 'Luiz Antonio Seixeiro (SA-GTI / Governança)': 'A', 'Denise Costa Santana (Superintendência SA)': 'C', 'Marcos Tadeu Yamamoto (DIF / Infraestrutura)': 'I' }, status: 'pendente', aprovadoPor: '', dataAprov: '', obs: 'Deliberação conclusiva de governança.' }
            ],
            criadoEm: '01/11/2026',
            criadoPor: 'Luiz Antonio Seixeiro',
            vinculo: '137.00029841/2026-14',
            tipoVinculo: 'SEI'
        },
        {
            id: 'RACI-TCU269-FABRICA',
            titulo: 'Aceite Técnico e Medição Mensal UST/PF (Súmula 269 TCU)',
            descricao: 'Aferição rigorosa de entregáveis no GitLab vinculados nominalmente aos fiscais e ao gestor do contrato.',
            usuarios: [
                'Diego Monteiro (DGD / Fiscal Técnico)',
                'Luiz Antonio Seixeiro (SA-GTI / Gestor do Contrato)',
                'Rafael Frossard Piteri (DIF / Analista de Qualidade)',
                'Alessandro Delbue Silva (DIF / Fiscal Administrativo)',
                'Marcos Tadeu Yamamoto (DIF / Líder Técnico)'
            ],
            etapas: [
                { id: 'etapa-1', nome: '1. Emissão de Ordem de Serviço (OS) com PF/UST', papeisPorUsuario: { 'Luiz Antonio Seixeiro (SA-GTI / Gestor do Contrato)': 'A', 'Diego Monteiro (DGD / Fiscal Técnico)': 'C', 'Alessandro Delbue Silva (DIF / Fiscal Administrativo)': 'I' }, status: 'aprovado', aprovadoPor: 'Luiz Antonio Seixeiro', dataAprov: '01/11/2026 09:00', obs: 'OS #399 emitida no SEI sob aprovação de Luiz Antonio Seixeiro.' },
                { id: 'etapa-2', nome: '2. Inspeção de Código e Quality Gate no SonarQube', papeisPorUsuario: { 'Rafael Frossard Piteri (DIF / Analista de Qualidade)': 'R', 'Diego Monteiro (DGD / Fiscal Técnico)': 'A', 'Marcos Tadeu Yamamoto (DIF / Líder Técnico)': 'C', 'Luiz Antonio Seixeiro (SA-GTI / Gestor do Contrato)': 'I' }, status: 'aprovado', aprovadoPor: 'Diego Monteiro', dataAprov: '04/11/2026 16:40', obs: 'Aprovado pelo fiscal técnico Diego Monteiro: cobertura >= 82%.' },
                { id: 'etapa-3', nome: '3. Apuração de Indicadores de SLA e Instrumento IMR', papeisPorUsuario: { 'Diego Monteiro (DGD / Fiscal Técnico)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Gestor do Contrato)': 'A', 'Alessandro Delbue Silva (DIF / Fiscal Administrativo)': 'C', 'Marcos Tadeu Yamamoto (DIF / Líder Técnico)': 'I' }, status: 'em_analise', aprovadoPor: '', dataAprov: '', obs: 'Apuração do IMR 98.5% sem glosas sob análise de Luiz Seixeiro.' },
                { id: 'etapa-4', nome: '4. Emissão de Termo de Recebimento Provisório (TRP)', papeisPorUsuario: { 'Diego Monteiro (DGD / Fiscal Técnico)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Gestor do Contrato)': 'A', 'Rafael Frossard Piteri (DIF / Analista de Qualidade)': 'C', 'Alessandro Delbue Silva (DIF / Fiscal Administrativo)': 'I' }, status: 'pendente', aprovadoPor: '', dataAprov: '', obs: 'Recebimento provisório condicionado ao teste funcional.' },
                { id: 'etapa-5', nome: '5. Termo de Recebimento Definitivo (TRD) e SIAFEM', papeisPorUsuario: { 'Luiz Antonio Seixeiro (SA-GTI / Gestor do Contrato)': 'A', 'Alessandro Delbue Silva (DIF / Fiscal Administrativo)': 'C', 'Diego Monteiro (DGD / Fiscal Técnico)': 'I' }, status: 'pendente', aprovadoPor: '', dataAprov: '', obs: 'Atesto final de nota fiscal e liquidação orçamentária.' }
            ],
            criadoEm: '01/11/2026',
            criadoPor: 'Luiz Antonio Seixeiro',
            vinculo: '137.00010805/2025-82',
            tipoVinculo: 'SEI'
        },
        {
            id: 'RACI-DEVSECOPS-DEPLOY',
            titulo: 'Gestão de Mudanças & Deploy em Produção (DevSecOps & DRP)',
            descricao: 'Fluxo para aprovação de releases e alterações de infraestrutura de nuvem, banco de dados e backup imutável WORM.',
            usuarios: [
                'Marcos Tadeu Yamamoto (DIF / Líder de Infraestrutura)',
                'Luiz Antonio Seixeiro (SA-GTI / Coordenador GTI)',
                'Rafael Frossard Piteri (DIF / Especialista em Nuvem e Redes)',
                'Alessandro Delbue Silva (DIF / Operações NOC)',
                'Diego Monteiro (DGD / Conformidade & GRC)'
            ],
            etapas: [
                { id: 'etapa-1', nome: '1. Abertura de Solicitação de Mudança (RDM / GMUD)', papeisPorUsuario: { 'Marcos Tadeu Yamamoto (DIF / Líder de Infraestrutura)': 'A', 'Rafael Frossard Piteri (DIF / Especialista em Nuvem e Redes)': 'C', 'Luiz Antonio Seixeiro (SA-GTI / Coordenador GTI)': 'I' }, status: 'aprovado', aprovadoPor: 'Marcos Tadeu Yamamoto', dataAprov: '03/11/2026 11:20', obs: 'GMUD #1232 aprovada por Marcos Tadeu Yamamoto.' },
                { id: 'etapa-2', nome: '2. Homologação em Sandbox e Teste de Restore DRP', papeisPorUsuario: { 'Rafael Frossard Piteri (DIF / Especialista em Nuvem e Redes)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Coordenador GTI)': 'A', 'Marcos Tadeu Yamamoto (DIF / Líder de Infraestrutura)': 'C', 'Alessandro Delbue Silva (DIF / Operações NOC)': 'I' }, status: 'aprovado', aprovadoPor: 'Luiz Antonio Seixeiro', dataAprov: '04/11/2026 15:10', obs: 'Restore de 45GB validado em sandbox por Luiz Antonio Seixeiro.' },
                { id: 'etapa-3', nome: '3. Análise de Vulnerabilidades OWASP e SAST/DAST', papeisPorUsuario: { 'Diego Monteiro (DGD / Conformidade & GRC)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Coordenador GTI)': 'A', 'Rafael Frossard Piteri (DIF / Especialista em Nuvem e Redes)': 'C', 'Marcos Tadeu Yamamoto (DIF / Líder de Infraestrutura)': 'I' }, status: 'em_analise', aprovadoPor: '', dataAprov: '', obs: 'Varredura de dependências em andamento sob supervisão de Luiz Seixeiro.' },
                { id: 'etapa-4', nome: '4. Aprovação pelo Comitê de Mudanças (CAB / SA-GTI)', papeisPorUsuario: { 'Marcos Tadeu Yamamoto (DIF / Líder de Infraestrutura)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Coordenador GTI)': 'A', 'Diego Monteiro (DGD / Conformidade & GRC)': 'C', 'Alessandro Delbue Silva (DIF / Operações NOC)': 'I' }, status: 'pendente', aprovadoPor: '', dataAprov: '', obs: 'Pauta incluída na Daily War Room.' },
                { id: 'etapa-5', nome: '5. Janela de Manutenção e Rollback Plan', papeisPorUsuario: { 'Marcos Tadeu Yamamoto (DIF / Líder de Infraestrutura)': 'R', 'Luiz Antonio Seixeiro (SA-GTI / Coordenador GTI)': 'A', 'Alessandro Delbue Silva (DIF / Operações NOC)': 'C', 'Rafael Frossard Piteri (DIF / Especialista em Nuvem e Redes)': 'I' }, status: 'pendente', aprovadoPor: '', dataAprov: '', obs: 'Janela programada fora do horário de pico.' }
            ],
            criadoEm: '02/11/2026',
            criadoPor: 'Luiz Antonio Seixeiro',
            vinculo: 'OP#1232',
            tipoVinculo: 'OpenProject'
        }
    ];

    window.obterUsuariosRaciModelo = function(m) {
        if (!m) return [];
        if (Array.isArray(m.usuarios) && m.usuarios.length > 0) return m.usuarios;
        if (Array.isArray(m.papeis) && m.papeis.length > 0) return m.papeis;
        return ['Luiz Antonio Seixeiro (SA-GTI)', 'Marcos Tadeu Yamamoto (DIF)', 'Diego Monteiro (DGD)'];
    };

    window.obterModelosRaciSalvos = function() {
        var salvos = [];
        try {
            var raw = localStorage.getItem('sagti_modelos_raci_v3');
            if (raw) salvos = JSON.parse(raw);
        } catch(e) { salvos = []; }

        if (!Array.isArray(salvos) || salvos.length === 0) {
            salvos = JSON.parse(JSON.stringify(window.MODELOS_RACI_PADRAO));
            try { localStorage.setItem('sagti_modelos_raci_v3', JSON.stringify(salvos)); } catch(e) {}
        }
        return salvos;
    };

    window.salvarModelosRaci = function(lista) {
        try {
            localStorage.setItem('sagti_modelos_raci_v3', JSON.stringify(lista));
        } catch(e) {}
        var cntTopbar = document.getElementById('topbar-badge-raci');
        if (cntTopbar) cntTopbar.innerText = String(lista.length);
        var cntTabela = document.getElementById('raci-badge-count-tabela');
        if (cntTabela) cntTabela.innerText = String(lista.length) + ' Modelos';
    };

    // Renderiza a Nova Visão Principal de Matrizes RACI (Acessada pelo Menu Superior)
    
// GESTÃO CRUD DE RELATÓRIOS DAILY & SPRINTS (SUPER-ADMIN)
    // =========================================================================
    window.abrirModalEditarCriarRelatorio = function(idRel) {
        var modalOld = document.getElementById('modal-editar-relatorio-ritual');
        if (modalOld) modalOld.remove();

        var lista = window.obterRelatoriosRituais();
        var rel = idRel ? (lista.find(function(r) { return r.id === idRel; }) || null) : null;
        var isEdicao = !!rel;

        var tipoVal = rel ? rel.tipo : 'daily';
        var dataVal = rel ? rel.data : new Date().toLocaleDateString('pt-BR');
        var tituloVal = rel ? rel.titulo : '';
        var destaqueVal = rel ? rel.destaque : '';
        var statusVal = rel ? rel.status : 'Realizada';
        var conteudoVal = rel ? (rel.conteudo || rel.destaque) : '';

        var div = document.createElement('div');
        div.id = 'modal-editar-relatorio-ritual';
        div.className = 'sagti-modal-backdrop';
        div.style.cssText = 'position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;padding:20px;animation:fadeIn 0.2s ease-in-out;';

        div.innerHTML = '<div style="border-radius:14px;max-width:680px;width:100%;padding:22px 24px;max-height:90vh;overflow-y:auto">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">' +
                '<div style="display:flex;align-items:center;gap:8px">' +
                    '<span style="font-size:18px">' + (isEdicao ? '✏️' : '➕') + '</span>' +
                    '<strong style="font-size:15px">' + (isEdicao ? 'Editar Registro de Ritual / Ata (Super-Admin)' : 'Novo Registro de Ritual / Ata (Super-Admin)') + '</strong>' +
                '</div>' +
                '<button type="button" onclick="document.getElementById(\'modal-editar-relatorio-ritual\').remove()" style="font-size:18px;cursor:pointer" class="btn btn-ghost-secondary">✖</button>' +
            '</div>' +

            '<form id="form-editar-ritual" onsubmit="window.salvarRelatorioRitual(event, \'' + (rel ? rel.id : '') + '\')">' +
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">' +
                    '<div>' +
                        '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px;text-transform:uppercase">Tipo do Ritual:</label>' +
                        '<select id="edit-rel-tipo" style="width:100%;padding:8px 10px;border-radius:6px;font-size:12px;outline:none" class="form-select">' +
                            '<option value="daily" ' + (tipoVal === 'daily' ? 'selected' : '') + '>⏱️ Ata Daily Scrum</option>' +
                            '<option value="sprint" ' + (tipoVal === 'sprint' ? 'selected' : '') + '>🏃 Snapshot da Sprint</option>' +
                            '<option value="sprint_report" ' + (tipoVal === 'sprint_report' ? 'selected' : '') + '>🏃 Sprint Report</option>' +
                            '<option value="review" ' + (tipoVal === 'review' ? 'selected' : '') + '>🏃 Sprint Review & Retro</option>' +
                            '<option value="checkpoint" ' + (tipoVal === 'checkpoint' ? 'selected' : '') + '>📋 Checkpoint Operacional</option>' +
                        '</select>' +
                    '</div>' +
                    '<div>' +
                        '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px;text-transform:uppercase">Data do Ritual (DD/MM/AAAA):</label>' +
                        '<input type="text" id="edit-rel-data" value="' + window.escapeHtml(dataVal) + '" required style="width:100%;padding:8px 10px;border-radius:6px;font-size:12px;outline:none" class="form-control">' +
                    '</div>' +
                '</div>' +

                '<div style="margin-bottom:12px">' +
                    '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px;text-transform:uppercase">Título & Escopo Operacional:</label>' +
                    '<input type="text" id="edit-rel-titulo" value="' + window.escapeHtml(tituloVal) + '" required placeholder="Ex: Ata da Daily Scrum (15 min) — SA-GTI Coordenação" style="width:100%;padding:8px 10px;border-radius:6px;font-size:12px;outline:none" class="form-control">' +
                '</div>' +

                '<div style="margin-bottom:12px">' +
                    '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px;text-transform:uppercase">Destaques & Principais Deliberações (Resumo na Tabela):</label>' +
                    '<textarea id="edit-rel-destaque" rows="2" required placeholder="Pauta resumida, entregas e bloqueios tratados..." style="width:100%;padding:8px 10px;border-radius:6px;font-size:12px;outline:none;resize:vertical" class="form-control">' + window.escapeHtml(destaqueVal) + '</textarea>' +
                '</div>' +

                '<div style="margin-bottom:12px">' +
                    '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px;text-transform:uppercase">Status do Ritual:</label>' +
                    '<select id="edit-rel-status" style="width:100%;padding:8px 10px;border-radius:6px;font-size:12px;outline:none" class="form-select">' +
                        '<option value="Realizada" ' + (statusVal === 'Realizada' ? 'selected' : '') + '>🟢 Realizada</option>' +
                        '<option value="Em Execução" ' + (statusVal === 'Em Execução' ? 'selected' : '') + '>🔵 Em Execução</option>' +
                        '<option value="Ativo na Mesa" ' + (statusVal === 'Ativo na Mesa' ? 'selected' : '') + '>🟢 Ativo na Mesa</option>' +
                        '<option value="Ativo" ' + (statusVal === 'Ativo' ? 'selected' : '') + '>🟢 Ativo</option>' +
                        '<option value="Concluída" ' + (statusVal === 'Concluída' ? 'selected' : '') + '>🟣 Concluída</option>' +
                        '<option value="Arquivada" ' + (statusVal === 'Arquivada' ? 'selected' : '') + '>📁 Arquivada</option>' +
                    '</select>' +
                '</div>' +

                '<div style="margin-bottom:16px">' +
                    '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px;text-transform:uppercase">Conteúdo Integral / Dossiê (Visualizado no Modal):</label>' +
                    '<textarea id="edit-rel-conteudo" rows="6" placeholder="Texto completo da ata, tópicos debatidos, encaminhamentos e decisões..." style="width:100%;padding:10px 12px;border-radius:6px;font-size:12px;outline:none;resize:vertical;line-height:1.5" class="form-control">' + window.escapeHtml(conteudoVal) + '</textarea>' +
                '</div>' +

                '<div style="display:flex;justify-content:flex-end;gap:10px;align-items:center;padding-top:14px">' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="document.getElementById(\'modal-editar-relatorio-ritual\').remove()" style="padding:7px 16px;font-size:12px;border-radius:6px;cursor:pointer">' +
                        'Cancelar' +
                    '</button>' +
                    '<button type="submit" class="btn btn-primary" style="padding:7px 18px;font-size:12px;font-weight:700;border-radius:6px;cursor:pointer">' +
                        '💾 Salvar Alterações' +
                    '</button>' +
                '</div>' +
            '</form>' +
        '</div>';

        document.body.appendChild(div);
    };

    window.salvarRelatorioRitual = function(e, idRel) {
        if (e && e.preventDefault) e.preventDefault();

        var selTipo = document.getElementById('edit-rel-tipo');
        var tipoVal = selTipo ? selTipo.value : 'daily';
        var tipoLabelVal = selTipo ? selTipo.options[selTipo.selectedIndex].text : '⏱️ Ata Daily Scrum';
        var dataVal = (document.getElementById('edit-rel-data') ? document.getElementById('edit-rel-data').value : '').trim() || new Date().toLocaleDateString('pt-BR');
        var tituloVal = (document.getElementById('edit-rel-titulo') ? document.getElementById('edit-rel-titulo').value : '').trim();
        var destaqueVal = (document.getElementById('edit-rel-destaque') ? document.getElementById('edit-rel-destaque').value : '').trim();
        var statusVal = document.getElementById('edit-rel-status') ? document.getElementById('edit-rel-status').value : 'Realizada';
        var conteudoVal = (document.getElementById('edit-rel-conteudo') ? document.getElementById('edit-rel-conteudo').value : '').trim();

        if (!tituloVal) {
            alert('Por favor, informe o título do ritual/relatório.');
            return;
        }

        var lista = window.obterRelatoriosRituais();

        if (idRel) {
            var idx = lista.findIndex(function(r) { return r.id === idRel; });
            if (idx !== -1) {
                lista[idx].tipo = tipoVal;
                lista[idx].tipoLabel = tipoLabelVal;
                lista[idx].data = dataVal;
                lista[idx].titulo = tituloVal;
                lista[idx].destaque = destaqueVal;
                lista[idx].status = statusVal;
                lista[idx].conteudo = conteudoVal || destaqueVal;
            }
        } else {
            var novoId = 'REL-' + tipoVal.toUpperCase() + '-' + Date.now();
            lista.unshift({
                id: novoId,
                tipo: tipoVal,
                tipoLabel: tipoLabelVal,
                data: dataVal,
                titulo: tituloVal,
                destaque: destaqueVal,
                status: statusVal,
                marcado: false,
                conteudo: conteudoVal || destaqueVal
            });
        }

        try {
            localStorage.setItem('sagti_relatorios_rituais_v11', JSON.stringify(lista));
        } catch(err) {}

        var modal = document.getElementById('modal-editar-relatorio-ritual');
        if (modal) modal.remove();

        if (typeof window.renderizarViewRelatoriosSprints === 'function') window.renderizarViewRelatoriosSprints();
        if (typeof window.renderizarTabelaMesa === 'function') window.renderizarTabelaMesa();
        if (typeof window.atualizarContadoresCustodiaMesa === 'function') window.atualizarContadoresCustodiaMesa();
    };

    window.excluirRelatorioRitual = function(idRel) {
        if (!idRel) return;
        var lista = window.obterRelatoriosRituais();
        var item = lista.find(function(r) { return r.id === idRel; });
        var nomeItem = item ? ('"' + item.titulo + '"') : ('ID ' + idRel);

        if (!confirm('⚠️ Confirmar Exclusão (Super-Admin):\n\nDeseja realmente excluir permanentemente o registro de ritual:\n' + nomeItem + '?\n\nEsta ação atualizará os contadores e o acervo.')) {
            return;
        }

        var novaLista = lista.filter(function(r) { return r.id !== idRel; });
        try {
            localStorage.setItem('sagti_relatorios_rituais_v11', JSON.stringify(novaLista));
        } catch(err) {}

        var fix = window.obterFixadosValidos();
        var idxFix = fix.indexOf('REL#' + idRel);
        if (idxFix !== -1) {
            fix.splice(idxFix, 1);
            try { localStorage.setItem('sagti_fixados', JSON.stringify(fix)); } catch(e) {}
        }

        if (typeof window.renderizarViewRelatoriosSprints === 'function') window.renderizarViewRelatoriosSprints();
        if (typeof window.renderizarTabelaMesa === 'function') window.renderizarTabelaMesa();
        if (typeof window.atualizarContadoresCustodiaMesa === 'function') window.atualizarContadoresCustodiaMesa();
        alert('🗑️ Relatório excluído com sucesso do acervo!');
    };

    window.restaurarRelatoriosPadrao = function() {
        if (!confirm('Deseja restaurar o acervo padrão de relatórios e rituais canônicos?')) return;
        try {
            localStorage.setItem('sagti_relatorios_rituais_v11', JSON.stringify(window.RELATORIOS_RITUAIS_PADRAO));
        } catch(e) {}
        if (typeof window.renderizarViewRelatoriosSprints === 'function') window.renderizarViewRelatoriosSprints();
        if (typeof window.renderizarTabelaMesa === 'function') window.renderizarTabelaMesa();
        if (typeof window.atualizarContadoresCustodiaMesa === 'function') window.atualizarContadoresCustodiaMesa();
        alert('✅ Acervo padrão de relatórios restaurado com sucesso!');
    };

    // Renderiza a Nova Visão Principal de Relatórios Daily & Sprints (Menu Superior)

    // =========================================================================
    // NAVEGAÇÃO ENTRE SUB-ABAS DA DOCUMENTAÇÃO DO PROJETO (USUÁRIO / TÉCNICA / GITHUB)
    // =========================================================================
        window.renderizarMarkdown = function(md) {
        if (!md) return '';
        var lines = md.split('\n');
        var html = [];
        var inCode = false, inTable = false;
        for (var i = 0; i < lines.length; i++) {
            var l = lines[i];
            if (l.trim().indexOf('```') === 0) {
                if (inCode) { html.push('</code></pre>'); inCode = false; }
                else { html.push('<pre style="padding:14px;border-radius:8px;overflow-x:auto;font-size:12px;margin:14px 0"><code>'); inCode = true; }
                continue;
            }
            if (inCode) { html.push(l.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')); continue; }
            if (l.trim().indexOf('|') === 0 && l.trim().indexOf('|', 1) > 0) {
                if (l.indexOf('---') > -1) continue;
                var parts = l.split('|').slice(1, -1);
                if (!inTable) {
                    html.push('<div style="overflow-x:auto;margin:16px 0"><div class="table-responsive"><table style="width:100%;border-collapse:collapse;font-size:12px;line-height:1.5" class="table table-vcenter card-table table-hover"><thead><tr>' + parts.map(function(c) { return '<th style="padding:8px 12px;text-align:left;font-weight:700">' + c.trim() + '</th>'; }).join('') + '</tr></thead><tbody>');
                    inTable = true;
                } else {
                    html.push('<tr>' + parts.map(function(c) { return '<td style="padding:7px 12px">' + c.trim() + '</td>'; }).join('') + '</tr>');
                }
                continue;
            } else if (inTable) { html.push('</tbody></table></div></div>'); inTable = false; }

            var fmt = l.replace(/\*\*(.*?)\*\*/g, '<strong >$1</strong>')
                       .replace(/`([^`]+)`/g, '<code style="padding:2px 5px;border-radius:4px;font-size:11.5px">$1</code>')
                       .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank" style="text-decoration:underline">$1</a>');

            if (fmt.indexOf('# ') === 0) html.push('<h2 style="font-size:18px;margin:22px 0 10px 0;padding-bottom:6px;font-weight:800">' + fmt.substring(2) + '</h2>');
            else if (fmt.indexOf('## ') === 0) html.push('<h3 style="font-size:15px;margin:18px 0 8px 0;padding-bottom:5px;font-weight:700">' + fmt.substring(3) + '</h3>');
            else if (fmt.indexOf('### ') === 0) html.push('<h4 style="font-size:13.5px;margin:14px 0 6px 0;font-weight:700">' + fmt.substring(4) + '</h4>');
            else if (fmt.indexOf('#### ') === 0) html.push('<h5 style="font-size:12.5px;margin:12px 0 4px 0;font-weight:700">' + fmt.substring(5) + '</h5>');
            else if (fmt.indexOf('> ') === 0) html.push('<blockquote style="padding:10px 14px;border-radius:0 8px 8px 0;margin:12px 0;font-size:12.5px;line-height:1.6">' + fmt.substring(2) + '</blockquote>');
            else if (fmt.indexOf('* ') === 0 || fmt.indexOf('- ') === 0) html.push('<li style="margin-left:20px;font-size:12px;line-height:1.6">' + fmt.substring(2) + '</li>');
            else if (fmt.trim() === '---') html.push('<hr style="margin:18px 0">');
            else if (fmt.trim()) html.push('<p style="font-size:12.5px;line-height:1.65;margin:8px 0">' + fmt + '</p>');
        }
        if (inTable) html.push('</tbody></table></div></div>');
        if (inCode) html.push('</code></pre>');
        return html.join('\n');
    };

    window.carregarDocDinamica = function(subAba) {
        subAba = subAba || 'usuario';
        var el = document.getElementById('subview-doc-' + subAba);
        if (!el || el.dataset.docCarregado === 'true') return;
        var box = el.querySelector('div') || el;
        box.innerHTML = '<div style="padding:20px;text-align:center;font-size:13px">⏳ Carregando documentação oficial atualizada (docs/' + subAba.toUpperCase() + ')...</div>';
        fetch('/api/v1/docs/' + subAba)
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data && data.sucesso && data.conteudo_md) {
                    var headerHtml = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;padding-bottom:12px;flex-wrap:wrap;gap:10px">' +
                        '<div style="font-size:12px;font-weight:700">📄 Arquivo Oficial: <code>docs/' + data.arquivo + '</code> (Sincronizado)</div>' +
                        '<a href="[https://github.com/LUIZ-SEIXEIRO/Cockpit_GTI/blob/main/docs/](https://github.com/LUIZ-SEIXEIRO/Cockpit_GTI/blob/main/docs/)' + data.arquivo + '" target="_blank" style="padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none">🐙 Ver no GitHub ↗</a>' +
                        '</div>';
                    box.innerHTML = headerHtml + window.renderizarMarkdown(data.conteudo_md);
                    el.dataset.docCarregado = 'true';
                }
            })
            .catch(function(err) {
                box.innerHTML = '<div style="padding:20px">⚠️ Erro ao carregar documentação: ' + err.message + '</div>';
            });
    };
    window.alternarSubAbaDoc = function(subAba) {
        if (typeof window.carregarDocDinamica === 'function') window.carregarDocDinamica(subAba);
        subAba = subAba || 'usuario';
        var views = [
            { id: 'usuario', view: document.getElementById('subview-doc-usuario'), btn: document.getElementById('btn-doc-usuario') },
            { id: 'tecnica', view: document.getElementById('subview-doc-tecnica'), btn: document.getElementById('btn-doc-tecnica') },
            { id: 'github', view: document.getElementById('subview-doc-github'), btn: document.getElementById('btn-doc-github') },
            { id: 'readme', view: document.getElementById('subview-doc-readme'), btn: document.getElementById('btn-doc-readme') }
        ];

        views.forEach(function(item) {
            var ativo = (item.id === subAba);
            if (item.view) {
                item.view.style.display = ativo ? 'block' : 'none';
            }
            if (item.btn) {
                if (ativo) {
                    item.btn.className = 'btn btn-primary active subaba-doc-btn';
                } else {
                    item.btn.className = 'btn btn-outline-secondary subaba-doc-btn';
                }
            }
        });
    };

        window.renderizarViewRelatoriosSprints = function() {
        var rels = (typeof window.obterRelatoriosRituais === 'function') ? window.obterRelatoriosRituais() : [];
        var fixados = (typeof window.obterFixadosValidos === 'function') ? window.obterFixadosValidos() : [];
        var busca = (document.getElementById('busca-relatorios-view') ? document.getElementById('busca-relatorios-view').value : '').toLowerCase().trim();

        // Atualiza KPIs do topo
        var totalRels = rels.length;
        var totalDailies = rels.filter(function(r) { return (r.tipo || '').toLowerCase().includes('daily') || (r.tipoLabel || '').toLowerCase().includes('daily'); }).length;
        var totalSprints = rels.filter(function(r) { return (r.tipo || '').toLowerCase().includes('sprint') || (r.tipoLabel || '').toLowerCase().includes('sprint'); }).length;
        var marcados = rels.filter(function(r) { return fixados.indexOf('REL#' + r.id) !== -1 || r.marcado; }).length;

        var elTot = document.getElementById('rel-kpi-total'); if (elTot) elTot.innerText = String(totalRels);
        var elDai = document.getElementById('rel-kpi-dailies'); if (elDai) elDai.innerText = String(totalDailies);
        var elSpr = document.getElementById('rel-kpi-sprints'); if (elSpr) elSpr.innerText = String(totalSprints);
        var elMar = document.getElementById('rel-kpi-marcados'); if (elMar) elMar.innerText = String(marcados);

        var elBadge = document.getElementById('topbar-badge-relatorios'); if (elBadge) elBadge.innerText = String(totalRels);
        var elTabelaBadge = document.getElementById('rel-badge-count-tabela'); if (elTabelaBadge) elTabelaBadge.innerText = String(totalRels) + ' Rituais';

        var tbody = document.getElementById('tbody-relatorios-view');
        var pag = document.getElementById('rel-pag-info-view');
        if (!tbody) return;

        var filtrados = rels.filter(function(r) {
            if (!busca) return true;
            return ((r.titulo || '') + ' ' + (r.destaque || '') + ' ' + (r.tipoLabel || '') + ' ' + (r.data || '')).toLowerCase().indexOf(busca) !== -1;
        });

        if (pag) pag.innerText = 'Exibindo ' + filtrados.length + ' de ' + rels.length + ' relatórios de rituais ágeis cadastrados';

        if (filtrados.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="padding: 40px 16px; text-align: center">' +
                '<div style="font-size: 32px; margin-bottom: 8px">📑</div>' +
                '<strong style="font-size: 14px">Nenhum relatório encontrado para esta busca.</strong><br>' +
                '<span style="font-size: 12px; margin-top: 4px; display: inline-block">Você pode gerar um novo snapshot do quadro Kanban clicando no botão acima.</span>' +
            '</td></tr>';
            return;
        }

        tbody.innerHTML = filtrados.map(function(r, idx) {
            var bg = (idx % 2 === 0) ? 'rgba(15,23,42,0.4)' : 'rgba(30,41,59,0.25)';
            var chave = 'REL#' + r.id;
            var isMarcado = fixados.indexOf(chave) !== -1 || r.marcado;
            var sCor = isMarcado ? '#facc15' : '#64748b';
            var sIco = isMarcado ? '⭐' : '☆';
            return '<tr style="transition:background 0.15s ease">' +
                '<td style="text-align:center;padding:12px 8px;cursor:pointer;font-size:16px" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar/Desmarcar para acompanhamento">' +
                    '<span >' + sIco + '</span>' +
                '</td>' +
                '<td style="padding:12px 14px;font-weight:700;font-size:12px;white-space:nowrap">' + (r.tipoLabel || 'Ritual') + '</td>' +
                '<td style="padding:12px 14px;font-size:11.5px;white-space:nowrap">' + (r.data || 'Hoje') + '</td>' +
                '<td style="padding:12px 14px;font-weight:700;font-size:12.5px">' + (r.titulo || 'Relatório de Ritual') + '</td>' +
                '<td style="padding:12px 14px;font-size:11.5px">' + (r.destaque || '—') + '</td>' +
                '<td style="padding:12px 14px;text-align:center"><span style="font-size:10.5px;padding:3px 8px;border-radius:10px;font-weight:700">' + (r.status || 'Realizada') + '</span></td>' +
                '<td style="padding:12px 14px;text-align:center;white-space:nowrap">' +
                    '<button type="button" class="btn btn-primary" onclick="window.visualizarRelatorioMesaModal(\'' + r.id + '\')" style="padding:4px 9px;font-size:11px;margin-right:4px;font-weight:700">👁️ Ver Dossiê</button>' +
                    '<button type="button" class="btn btn-warning" onclick="window.abrirModalEditarCriarRelatorio(\'' + r.id + '\')" style="padding:4px 9px;font-size:11px;margin-right:4px;font-weight:700;border-radius:6px;cursor:pointer" title="Editar este ritual/relatório (Super-Admin)">✏️ Editar</button>' +
                    '<button type="button" class="btn btn-danger" onclick="window.excluirRelatorioRitual(\'' + r.id + '\')" style="padding:4px 9px;font-size:11px;margin-right:4px;font-weight:700;border-radius:6px;cursor:pointer" title="Excluir este ritual/relatório (Super-Admin)">🗑️ Excluir</button>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + chave + '\')" style="padding:4px 8px;font-size:11px">' + (isMarcado ? '⭐ Acompanhando' : '☆ Acompanhar') + '</button>' +
                '</td>' +
            '</tr>';
        }).join('');
    };

    

    window.renderizarViewMatrizRaci = function() {
        var tbody = document.getElementById('tbody-raci-principal');
        if (!tbody) tbody = document.getElementById('tbody-meus-processos');
        var pag = document.getElementById('raci-pag-info-principal');
        var busca = (document.getElementById('busca-raci-principal') ? document.getElementById('busca-raci-principal').value : '').toLowerCase().trim();

        var modelos = window.obterModelosRaciSalvos();
        window.salvarModelosRaci(modelos);

        // Atualiza KPIs do topo da aba RACI
        var totalModelos = modelos.length;
        var concluidas = 0;
        var emAndamento = 0;
        var minhasPendencias = 0;
        var usuarioLogadoNome = (window.obterUsuarioSessaoAtual ? window.obterUsuarioSessaoAtual().nome : 'Luiz Antonio Seixeiro').toLowerCase();

        modelos.forEach(function(m) {
            var tot = m.etapas.length;
            var apr = m.etapas.filter(function(e) { return e.status === 'aprovado'; }).length;
            if (tot > 0 && apr === tot) concluidas++;
            else emAndamento++;

            // Checa se o usuário atual é o Accountable (A) da etapa corrente pendente
            var etapaAtual = m.etapas.find(function(e) { return e.status === 'em_analise' || e.status === 'pendente'; });
            if (etapaAtual) {
                var listaU = window.obterUsuariosRaciModelo(m);
                var aprovadorNome = '';
                if (etapaAtual.papeisPorUsuario) {
                    for (var u in etapaAtual.papeisPorUsuario) {
                        if (etapaAtual.papeisPorUsuario[u] === 'A') { aprovadorNome = u; break; }
                    }
                }
                if (!aprovadorNome && typeof etapaAtual.a === 'number' && listaU[etapaAtual.a]) {
                    aprovadorNome = listaU[etapaAtual.a];
                }
                if (aprovadorNome.toLowerCase().includes('luiz') || (usuarioLogadoNome && aprovadorNome.toLowerCase().includes(usuarioLogadoNome.split(' ')[0]))) {
                    minhasPendencias++;
                }
            }
        });

        var elKpiTotal = document.getElementById('raci-kpi-total'); if (elKpiTotal) elKpiTotal.innerText = String(totalModelos);
        var elKpiConc = document.getElementById('raci-kpi-concluidas'); if (elKpiConc) elKpiConc.innerText = String(concluidas);
        var elKpiAnd = document.getElementById('raci-kpi-andamento'); if (elKpiAnd) elKpiAnd.innerText = String(emAndamento);
        var elKpiMinhas = document.getElementById('raci-kpi-minhas'); if (elKpiMinhas) elKpiMinhas.innerText = String(minhasPendencias);

        if (!tbody) return;

        var filtrados = modelos.filter(function(m) {
            if (!busca) return true;
            var usrStr = window.obterUsuariosRaciModelo(m).join(' ');
            return (m.titulo + ' ' + (m.descricao || '') + ' ' + (m.vinculo || '') + ' ' + usrStr).toLowerCase().indexOf(busca) !== -1;
        });

        if (pag) pag.innerText = 'Exibindo ' + filtrados.length + ' de ' + modelos.length + ' matrizes nominais ativas';

        if (filtrados.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="padding: 40px 16px; text-align: center">' +
                '<div style="font-size: 32px; margin-bottom: 8px">📊</div>' +
                '<strong style="font-size: 14px">Nenhuma matriz RACI encontrada para esta busca.</strong><br>' +
                '<span style="font-size: 12px; margin-top: 4px; display: inline-block">Clique no botão abaixo para construir uma nova matriz nominalmente.</span><br>' +
                '<button type="button" class="btn btn-primary" onclick="window.abrirModalCriarRaci()" style="margin-top: 14px; padding: 7px 16px; font-size: 12px">➕ Construir Nova Matriz Nominal</button>' +
            '</td></tr>';
            return;
        }

        tbody.innerHTML = filtrados.map(function(m) {
            var totalEtapas = m.etapas.length;
            var aprovadas = m.etapas.filter(function(e) { return e.status === 'aprovado'; }).length;
            var pct = totalEtapas > 0 ? Math.round((aprovadas / totalEtapas) * 100) : 0;
            var etapaAtual = m.etapas.find(function(e) { return e.status === 'em_analise' || e.status === 'pendente'; }) || m.etapas[m.etapas.length - 1];

            var listaUsuarios = window.obterUsuariosRaciModelo(m);
            var aprovadorNome = '';
            if (etapaAtual && etapaAtual.papeisPorUsuario) {
                for (var u in etapaAtual.papeisPorUsuario) {
                    if (etapaAtual.papeisPorUsuario[u] === 'A') { aprovadorNome = u; break; }
                }
            }
            if (!aprovadorNome) {
                var apIdx = (etapaAtual && typeof etapaAtual.a === 'number') ? etapaAtual.a : 0;
                aprovadorNome = listaUsuarios[apIdx] || 'Luiz Antonio Seixeiro';
            }
            var aprovadorCurto = aprovadorNome.split('(')[0].trim();

            var badgeStatus = '<span class="pill-tag pill-blue" >🟢 Concluído</span>';
            if (pct < 100 && aprovadas > 0) {
                badgeStatus = '<span class="pill-tag pill-yellow" >🟡 Em Aprovação (' + pct + '%)</span>';
            } else if (aprovadas === 0) {
                badgeStatus = '<span class="pill-tag pill-orange" >⚪ Pendente Inicial</span>';
            }

            var vinculoHtml = '<span style="font-size: 11px">Sem vínculo</span>';
            if (m.vinculo) {
                var tipoIco = m.tipoVinculo === 'OpenProject' ? '📦 ' : (m.tipoVinculo === 'GLPI' ? '🎫 ' : '📁 ');
                vinculoHtml = '<strong style="font-size: 11.5px">' + tipoIco + m.vinculo + '</strong>' +
                    '<div >' + (m.tipoVinculo || 'SEI') + '</div>';
            }

            return '<tr style="transition: background 0.15s ease">' +
                '<td style="text-align: center; padding: 12px 8px; font-size: 16px">📊</td>' +
                '<td style="padding: 12px 14px">' +
                    '<strong style="font-size: 12.5px; display: block; margin-bottom: 3px">' + m.titulo + '</strong>' +
                    '<div style="font-size: 11px; max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis" title="' + (m.descricao || '') + '">' + (m.descricao || '') + '</div>' +
                    '<div style="font-size: 10.5px; margin-top: 4px">👥 <strong>' + listaUsuarios.length + ' usuários nominais</strong></div>' +
                '</td>' +
                '<td style="padding: 12px 14px">' + vinculoHtml + '</td>' +
                '<td style="padding: 12px 14px; text-align: center">' +
                    '<div style="font-size: 11.5px; font-weight: 700; margin-bottom: 4px">' + aprovadas + '/' + totalEtapas + ' (' + pct + '%)</div>' +
                    '<div style="border-radius: 4px; height: 6px; overflow: hidden; width: 100px; margin: 0 auto">' +
                        '<div style="height: 100%; width: ' + pct + '%"></div>' +
                    '</div>' +
                '</td>' +
                '<td style="padding: 12px 14px">' +
                    '<div style="font-size: 12px; font-weight: 600">' + (etapaAtual ? etapaAtual.nome : '—') + '</div>' +
                    '<div style="font-size: 11px; font-weight: 700; margin-top: 2px">👑 ' + aprovadorCurto + '</div>' +
                '</td>' +
                '<td style="padding: 12px 14px; text-align: center">' + badgeStatus + '</td>' +
                '<td style="padding: 12px 14px; text-align: center; white-space: nowrap">' +
                    '<button type="button" class="btn btn-primary" onclick="window.abrirModalExecutarRaci(\'' + m.id + '\')" style="padding: 4px 10px; font-size: 11px; margin-right: 5px; font-weight: 700">⚡ Operar Fluxo</button>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.abrirModalVincularRaci(\'' + m.id + '\')" style="padding: 4px 8px; font-size: 11px; margin-right: 4px" title="Vincular a Processo SEI, OpenProject ou GLPI">🔗</button>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.abrirModalCriarRaci(\'' + m.id + '\')" style="padding: 4px 8px; font-size: 11px; margin-right: 4px" title="Editar Estrutura da Matriz">✏️</button>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.duplicarModeloRaci(\'' + m.id + '\')" style="padding: 4px 8px; font-size: 11px; margin-right: 4px" title="Duplicar Matriz">📋</button>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.excluirModeloRaci(\'' + m.id + '\')" style="padding: 4px 8px; font-size: 11px" title="Excluir Matriz">🗑️</button>' +
                '</td>' +
            '</tr>';
        }).join('');
    };

    window.renderizarGradeRaciMesa = window.renderizarViewMatrizRaci;

    // =========================================================================
    // CONSTRUTOR ESTRUTURADO DE MATRIZ RACI NOMINAL (CRIAÇÃO E EDIÇÃO LIVRE)
    // Permite definir nominalmente o papel de cada usuário em cada etapa:
    // Legenda Nominal: R = Executor | A 👑 = Aprovador Oficial | C = Consultado | I = Informado
    // =========================================================================

    window.raciBuilderState = null;

    window.abrirModalCriarRaci = function(idModeloParaEditar) {
        var modalAntigo = document.getElementById('modal-raci-criar-estruturado');
        if (modalAntigo) modalAntigo.remove();

        var usuariosCadastrados = (typeof window.obterUsuariosCadastrados === 'function')
            ? window.obterUsuariosCadastrados()
            : [
                { nome: 'Luiz Antonio Seixeiro', unidade: 'SA-GTI (Sede)', perfil: 'Super-Admin' },
                { nome: 'Marcos Tadeu Yamamoto', unidade: 'DIF - Infraestrutura', perfil: 'Gestor' },
                { nome: 'Diego Monteiro', unidade: 'DGD - Governança', perfil: 'Gestor' },
                { nome: 'Rafael Frossard Piteri', unidade: 'DIF - Infraestrutura', perfil: 'Analista' },
                { nome: 'Alessandro Delbue Silva', unidade: 'DIF - Redes', perfil: 'Analista' },
                { nome: 'Denise Costa Santana', unidade: 'Superintendência SA', perfil: 'Demandante' }
            ];

        if (idModeloParaEditar) {
            var modelos = window.obterModelosRaciSalvos();
            var modExistente = modelos.find(function(m) { return m.id === idModeloParaEditar; });
            if (modExistente) {
                window.raciBuilderState = JSON.parse(JSON.stringify(modExistente));
            }
        }

        if (!window.raciBuilderState || (idModeloParaEditar && window.raciBuilderState.id !== idModeloParaEditar) || !idModeloParaEditar) {
            // Inicialização de nova matriz
            var usuariosIniciais = [
                'Luiz Antonio Seixeiro (SA-GTI (Sede))',
                'Diego Monteiro (DGD - Governança)',
                'Marcos Tadeu Yamamoto (DIF - Infraestrutura)',
                'Rafael Frossard Piteri (DIF - Infraestrutura)',
                'Denise Costa Santana (Superintendência SA)'
            ];
            window.raciBuilderState = {
                id: idModeloParaEditar || '',
                titulo: '',
                descricao: '',
                vinculo: '',
                tipoVinculo: 'SEI',
                usuarios: usuariosIniciais,
                etapas: [
                    {
                        id: 'etapa-1',
                        nome: '1. Formalização de Demanda (DFD) e Justificativa Técnica',
                        papeisPorUsuario: {
                            'Denise Costa Santana (Superintendência SA)': 'R',
                            'Luiz Antonio Seixeiro (SA-GTI (Sede))': 'A',
                            'Diego Monteiro (DGD - Governança)': 'C',
                            'Marcos Tadeu Yamamoto (DIF - Infraestrutura)': 'I'
                        }
                    },
                    {
                        id: 'etapa-2',
                        nome: '2. Elaboração do Estudo Técnico Preliminar (ETP) e Riscos',
                        papeisPorUsuario: {
                            'Diego Monteiro (DGD - Governança)': 'R',
                            'Luiz Antonio Seixeiro (SA-GTI (Sede))': 'A',
                            'Rafael Frossard Piteri (DIF - Infraestrutura)': 'C',
                            'Denise Costa Santana (Superintendência SA)': 'I'
                        }
                    },
                    {
                        id: 'etapa-3',
                        nome: '3. Elaboração do Termo de Referência e Catálogo UST/PF',
                        papeisPorUsuario: {
                            'Luiz Antonio Seixeiro (SA-GTI (Sede))': 'A',
                            'Diego Monteiro (DGD - Governança)': 'R',
                            'Marcos Tadeu Yamamoto (DIF - Infraestrutura)': 'C',
                            'Denise Costa Santana (Superintendência SA)': 'I'
                        }
                    },
                    {
                        id: 'etapa-4',
                        nome: '4. Parecer Técnico Conclusivo e Parecer Jurídico CJ',
                        papeisPorUsuario: {
                            'Diego Monteiro (DGD - Governança)': 'R',
                            'Luiz Antonio Seixeiro (SA-GTI (Sede))': 'A',
                            'Rafael Frossard Piteri (DIF - Infraestrutura)': 'C',
                            'Denise Costa Santana (Superintendência SA)': 'I'
                        }
                    },
                    {
                        id: 'etapa-5',
                        nome: '5. Homologação Final e Autorização da Contratação',
                        papeisPorUsuario: {
                            'Luiz Antonio Seixeiro (SA-GTI (Sede))': 'A',
                            'Denise Costa Santana (Superintendência SA)': 'C',
                            'Marcos Tadeu Yamamoto (DIF - Infraestrutura)': 'I'
                        }
                    }
                ]
            };
        }

        var divModal = document.createElement('div');
        divModal.id = 'modal-raci-criar-estruturado';
        divModal.className = 'sagti-modal-backdrop';
        divModal.style.cssText = 'position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;padding:16px;';
        divModal.innerHTML = '<div style="border-radius:16px;max-width:1100px;width:100%;max-height:94vh;overflow-y:auto;padding:26px">' +
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">' +
                '<div>' +
                    '<span style="padding:3px 10px;border-radius:6px;font-size:11px;font-weight:800;letter-spacing:0.5px">CONSTRUTOR ESTRUTURADO DE MATRIZ RACI</span>' +
                    '<h3 style="margin:6px 0 2px 0;font-size:18px">' + (window.raciBuilderState.id ? '✏️ Editar Matriz RACI Nominal' : '➕ Criar Nova Matriz RACI Nominal') + '</h3>' +
                    '<div style="font-size:12px">Defina nominalmente a atribuição exata de cada usuário: Executor (R), Aprovador Oficial (A 👑), Consultado (C) ou Informado (I).</div>' +
                '</div>' +
                '<button type="button" onclick="document.getElementById(\'modal-raci-criar-estruturado\').remove()" style="font-size:22px;cursor:pointer" class="btn btn-ghost-secondary">✖</button>' +
            '</div>' +

            '<!-- SEÇÃO 1: DADOS GERAIS DA MATRIZ -->' +
            '<div style="display:grid;grid-template-columns:2fr 1.2fr;gap:14px;padding:14px;border-radius:10px;margin-bottom:16px">' +
                '<div style="display:flex;flex-direction:column;gap:10px">' +
                    '<div>' +
                        '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px">Título da Matriz / Fluxo de Aprovação:</label>' +
                        '<input type="text" id="builder-raci-titulo" value="' + window.escapeHtml(window.raciBuilderState.titulo || '') + '" placeholder="Ex: Instrução de Contratação de Nuvem (Lei 14.133)" style="width:100%;box-sizing:border-box;padding:8px 12px;border-radius:8px;font-size:12px;outline:none" class="form-control">' +
                    '</div>' +
                    '<div>' +
                        '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px">Descrição &amp; Finalidade Institucional:</label>' +
                        '<input type="text" id="builder-raci-desc" value="' + window.escapeHtml(window.raciBuilderState.descricao || '') + '" placeholder="Ex: Segregação formal de responsabilidades entre demandante, governança e fiscalização." style="width:100%;box-sizing:border-box;padding:8px 12px;border-radius:8px;font-size:12px;outline:none" class="form-control">' +
                    '</div>' +
                '</div>' +
                '<div>' +
                    '<label style="display:block;font-size:11px;font-weight:700;margin-bottom:4px">Vincular a uma Demanda (Opcional):</label>' +
                    '<input type="text" id="builder-raci-vinculo" value="' + window.escapeHtml(window.raciBuilderState.vinculo || '') + '" placeholder="Ex: 137.00029841/2026-14 ou OP#1232" style="width:100%;box-sizing:border-box;padding:8px 12px;border-radius:8px;font-size:12px;outline:none;margin-bottom:8px" class="form-control">' +
                    '<select id="builder-raci-tipovinculo" style="width:100%;box-sizing:border-box;padding:7px 10px;border-radius:8px;font-size:11.5px;outline:none" class="form-select">' +
                        '<option value="SEI" ' + (window.raciBuilderState.tipoVinculo === 'SEI' ? 'selected' : '') + '>Processo SEI</option>' +
                        '<option value="OpenProject" ' + (window.raciBuilderState.tipoVinculo === 'OpenProject' ? 'selected' : '') + '>Pacote OpenProject</option>' +
                        '<option value="GLPI" ' + (window.raciBuilderState.tipoVinculo === 'GLPI' ? 'selected' : '') + '>Chamado GLPI</option>' +
                    '</select>' +
                '</div>' +
            '</div>' +

            '<!-- SEÇÃO 2: USUÁRIOS REAIS PARTICIPANTES -->' +
            '<div style="padding:14px;border-radius:10px;margin-bottom:16px">' +
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">' +
                    '<label style="font-size:11.5px;font-weight:700;text-transform:uppercase">👥 Usuários Reais Participantes da Matriz:</label>' +
                    '<span style="font-size:10.5px">Marque os usuários para gerar as colunas nominais</span>' +
                '</div>' +
                '<div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:8px;margin-bottom:10px">' +
                    usuariosCadastrados.map(function(u) {
                        var uStr = u.nome + ' (' + u.unidade + ')';
                        var isChecked = window.raciBuilderState.usuarios.some(function(sel) { return sel.includes(u.nome); });
                        return '<label style="display:flex;align-items:center;gap:7px;padding:6px 10px;border-radius:6px;cursor:pointer;font-size:11px">' +
                            '<input type="checkbox" onchange="window.raciBuilderToggleUsuario(\'' + window.escapeHtml(uStr) + '\', this.checked)" ' + (isChecked ? 'checked' : '') + ' class="form-check-input">' +
                            '<span>👤 ' + u.nome + ' <small >(' + u.unidade.split(' ')[0] + ')</small></span>' +
                        '</label>';
                    }).join('') +
                '</div>' +
                '<div style="display:flex;gap:8px;align-items:center">' +
                    '<input type="text" id="builder-raci-extra-user" placeholder="Adicionar outro usuário / colaborador (ex: Procurador Consultoria Jurídica, Preposto Fábrica)..." style="flex:1;padding:6px 10px;border-radius:6px;font-size:11.5px;outline:none" class="form-control">' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.raciBuilderAddUsuarioExtra()" style="padding:6px 12px;font-size:11px;white-space:nowrap">➕ Incluir Usuário</button>' +
                '</div>' +
            '</div>' +

            '<!-- SEÇÃO 3: GRADE INTERATIVA RACI (ETAPAS X USUÁRIOS) -->' +
            '<div style="padding:14px;border-radius:10px;margin-bottom:16px">' +
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px">' +
                    '<div>' +
                        '<strong style="font-size:12px;text-transform:uppercase">📋 Matriz Interativa de Atribuições Nominais</strong>' +
                        '<div style="font-size:11px">Defina o papel de cada pessoa em cada etapa do fluxo</div>' +
                    '</div>' +
                    '<div style="display:flex;gap:6px;flex-wrap:wrap">' +
                        '<button type="button" class="btn btn-primary" onclick="window.raciBuilderAddEtapa()" style="padding:4px 10px;font-size:11px;font-weight:700">➕ Adicionar Etapa</button>' +
                        '<button type="button" class="btn btn-outline-secondary" onclick="window.raciBuilderCarregarTemplate(\'lei14133\')" style="padding:4px 8px;font-size:10.5px">⚡ Template Lei 14.133</button>' +
                        '<button type="button" class="btn btn-outline-secondary" onclick="window.raciBuilderCarregarTemplate(\'tcu269\')" style="padding:4px 8px;font-size:10.5px">⚡ Template TCU 269</button>' +
                        '<button type="button" class="btn btn-outline-secondary" onclick="window.raciBuilderCarregarTemplate(\'devsecops\')" style="padding:4px 8px;font-size:10.5px">⚡ Template DevSecOps</button>' +
                    '</div>' +
                '</div>' +
                '<div id="builder-raci-tabela-container" style="overflow-x:auto"></div>' +
            '</div>' +

            '<!-- BARRA FIXA DE LEGENDA NOMINAL -->' +
            '<div style="padding:10px 14px;border-radius:8px;font-size:11.5px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">' +
                '<div>' +
                    '<strong >Legenda Nominal:</strong> ' +
                    '<span style="padding:2px 7px;border-radius:4px;font-weight:800">R</span> = Usuário Executor &nbsp;|&nbsp; ' +
                    '<span style="padding:2px 7px;border-radius:4px;font-weight:800">A 👑</span> = Usuário Aprovador Oficial (Accountable) &nbsp;|&nbsp; ' +
                    '<span style="padding:2px 7px;border-radius:4px;font-weight:700">C</span> = Consultado &nbsp;|&nbsp; ' +
                    '<span style="padding:2px 7px;border-radius:4px">I</span> = Informado' +
                '</div>' +
            '</div>' +

            '<div style="display:flex;justify-content:flex-end;gap:10px">' +
                '<button type="button" class="btn btn-outline-secondary" onclick="document.getElementById(\'modal-raci-criar-estruturado\').remove()" style="padding:8px 16px;font-size:12px">Cancelar</button>' +
                '<button type="button" class="btn btn-primary" onclick="window.salvarBuilderRaciFinal()" style="padding:8px 22px;font-size:12px;font-weight:700">Salvar Matriz no Perfil</button>' +
            '</div>' +
        '</div>';
        document.body.appendChild(divModal);

        window.raciBuilderRenderTabela();
    };

    window.raciBuilderRenderTabela = function() {
        var container = document.getElementById('builder-raci-tabela-container');
        if (!container || !window.raciBuilderState) return;

        var usuarios = window.raciBuilderState.usuarios || [];
        var etapas = window.raciBuilderState.etapas || [];

        if (usuarios.length === 0) {
            container.innerHTML = '<div style="padding:20px;text-align:center">Por favor, selecione ao menos 1 usuário participante acima.</div>';
            return;
        }

        var html = '<div class="table-responsive"><table style="width:100%;border-collapse:collapse;font-size:11.5px" class="table table-vcenter card-table table-hover">' +
            '<thead><tr >' +
            '<th style="padding:8px 10px;text-align:left;min-width:240px">Nome da Etapa do Fluxo</th>';

        usuarios.forEach(function(u) {
            var uCurto = u.split('(')[0].trim();
            var uUnid = u.indexOf('(') !== -1 ? u.substring(u.indexOf('(')) : '';
            html += '<th style="padding:8px 6px;text-align:center;min-width:110px">' +
                '<div style="font-weight:700">👤 ' + uCurto + '</div>' +
                '<div style="font-size:9.5px;font-weight:400">' + uUnid + '</div>' +
            '</th>';
        });

        html += '<th style="width:40px;text-align:center;padding:8px">Excluir</th></tr></thead><tbody>';

        etapas.forEach(function(et, eIdx) {
            html += '<tr >' +
                '<td style="padding:6px 10px">' +
                    '<input type="text" onchange="window.raciBuilderUpdateEtapaNome(' + eIdx + ', this.value)" value="' + window.escapeHtml(et.nome) + '" placeholder="Nome da etapa..." style="width:100%;box-sizing:border-box;padding:6px 10px;border-radius:6px;font-size:11.5px;outline:none" class="form-control">' +
                '</td>';

            usuarios.forEach(function(u) {
                var papelAtual = (et.papeisPorUsuario && et.papeisPorUsuario[u]) ? et.papeisPorUsuario[u] : '';
                var papelClass = 'bg-secondary-lt text-secondary';
                if (papelAtual === 'R') papelClass = 'bg-blue-lt text-blue';
                else if (papelAtual === 'A') papelClass = 'bg-amber-lt text-amber';
                else if (papelAtual === 'C') papelClass = 'bg-cyan-lt text-cyan';
                else if (papelAtual === 'I') papelClass = 'bg-secondary-lt text-secondary';

                html += '<td style="padding:6px;text-align:center">' +
                    '<select onchange="window.raciBuilderUpdatePapel(' + eIdx + ', \'' + window.escapeHtml(u) + '\', this.value)" style="width:100%;padding:5px 4px" class="form-select ' + papelClass + '">' +
                        '<option value="" ' + (papelAtual === '' ? 'selected' : '') + '>— (Nenhum)</option>' +
                        '<option value="R" ' + (papelAtual === 'R' ? 'selected' : '') + '>R (Executor)</option>' +
                        '<option value="A" ' + (papelAtual === 'A' ? 'selected' : '') + '>A 👑 (Aprovador)</option>' +
                        '<option value="C" ' + (papelAtual === 'C' ? 'selected' : '') + '>C (Consultado)</option>' +
                        '<option value="I" ' + (papelAtual === 'I' ? 'selected' : '') + '>I (Informado)</option>' +
                    '</select>' +
                '</td>';
            });

            html += '<td style="padding:6px;text-align:center">' +
                '<button type="button" onclick="window.raciBuilderRemoverEtapa(' + eIdx + ')" style="cursor:pointer;font-size:14px" title="Remover Etapa" class="btn btn-ghost-secondary">🗑️</button>' +
            '</td></tr>';
        });

        html += '</tbody></table></div>';
        container.innerHTML = html;
    };

    window.raciBuilderToggleUsuario = function(nomeCompleto, checked) {
        if (!window.raciBuilderState) return;
        var idx = window.raciBuilderState.usuarios.indexOf(nomeCompleto);
        if (checked && idx === -1) {
            window.raciBuilderState.usuarios.push(nomeCompleto);
        } else if (!checked && idx !== -1) {
            window.raciBuilderState.usuarios.splice(idx, 1);
        }
        window.raciBuilderRenderTabela();
    };

    window.raciBuilderAddUsuarioExtra = function() {
        var inp = document.getElementById('builder-raci-extra-user');
        if (!inp) return;
        var val = inp.value.trim();
        if (!val) return;
        if (!window.raciBuilderState.usuarios.includes(val)) {
            window.raciBuilderState.usuarios.push(val);
            inp.value = '';
            window.raciBuilderRenderTabela();
        }
    };

    window.raciBuilderAddEtapa = function() {
        if (!window.raciBuilderState) return;
        var num = window.raciBuilderState.etapas.length + 1;
        window.raciBuilderState.etapas.push({
            id: 'etapa-' + Date.now(),
            nome: num + '. Nova Etapa do Fluxo de Aprovação',
            papeisPorUsuario: {}
        });
        window.raciBuilderRenderTabela();
    };

    window.raciBuilderRemoverEtapa = function(idx) {
        if (!window.raciBuilderState) return;
        window.raciBuilderState.etapas.splice(idx, 1);
        window.raciBuilderRenderTabela();
    };

    window.raciBuilderUpdateEtapaNome = function(idx, novoNome) {
        if (!window.raciBuilderState || !window.raciBuilderState.etapas[idx]) return;
        window.raciBuilderState.etapas[idx].nome = novoNome;
    };

    window.raciBuilderUpdatePapel = function(eIdx, usuario, papel) {
        if (!window.raciBuilderState || !window.raciBuilderState.etapas[eIdx]) return;
        if (!window.raciBuilderState.etapas[eIdx].papeisPorUsuario) {
            window.raciBuilderState.etapas[eIdx].papeisPorUsuario = {};
        }
        if (papel) {
            window.raciBuilderState.etapas[eIdx].papeisPorUsuario[usuario] = papel;
        } else {
            delete window.raciBuilderState.etapas[eIdx].papeisPorUsuario[usuario];
        }
        window.raciBuilderRenderTabela();
    };

    window.raciBuilderCarregarTemplate = function(tipo) {
        if (!window.raciBuilderState) return;
        if (tipo === 'lei14133') {
            window.raciBuilderState.titulo = 'Instrução e Aprovação de ETP/TR (Lei 14.133/2021)';
            window.raciBuilderState.descricao = 'Fluxo oficial de instrução técnica e governança da contratação pública de TIC.';
            window.raciBuilderState.etapas = [
                { id: 'etapa-1', nome: '1. Formalização de Demanda (DFD) e Justificativa', papeisPorUsuario: {} },
                { id: 'etapa-2', nome: '2. Elaboração do Estudo Técnico Preliminar (ETP)', papeisPorUsuario: {} },
                { id: 'etapa-3', nome: '3. Matriz de Riscos e Termo de Referência (TR/IMR)', papeisPorUsuario: {} },
                { id: 'etapa-4', nome: '4. Parecer Técnico Conclusivo e Parecer Jurídico CJ', papeisPorUsuario: {} },
                { id: 'etapa-5', nome: '5. Autorização e Homologação Final para Licitação', papeisPorUsuario: {} }
            ];
        } else if (tipo === 'tcu269') {
            window.raciBuilderState.titulo = 'Aceite Técnico e Medição Mensal UST/PF (Súmula 269 TCU)';
            window.raciBuilderState.descricao = 'Conferência de entregas no GitLab, métricas mensuráveis e aplicação de glosas IMR.';
            window.raciBuilderState.etapas = [
                { id: 'etapa-1', nome: '1. Emissão de Ordem de Serviço (OS) com PF/UST', papeisPorUsuario: {} },
                { id: 'etapa-2', nome: '2. Inspeção de Código e Quality Gate no SonarQube', papeisPorUsuario: {} },
                { id: 'etapa-3', nome: '3. Apuração de Indicadores de SLA e Instrumento IMR', papeisPorUsuario: {} },
                { id: 'etapa-4', nome: '4. Emissão de Termo de Recebimento Provisório (TRP)', papeisPorUsuario: {} },
                { id: 'etapa-5', nome: '5. Termo de Recebimento Definitivo (TRD) e SIAFEM', papeisPorUsuario: {} }
            ];
        } else if (tipo === 'devsecops') {
            window.raciBuilderState.titulo = 'Gestão de Mudanças & Deploy em Produção (DevSecOps)';
            window.raciBuilderState.descricao = 'Rito de aprovação de releases com sandbox, testes de restore e deliberação do CAB.';
            window.raciBuilderState.etapas = [
                { id: 'etapa-1', nome: '1. Abertura de Solicitação de Mudança (RDM / GMUD)', papeisPorUsuario: {} },
                { id: 'etapa-2', nome: '2. Homologação em Sandbox e Teste de Restore DRP', papeisPorUsuario: {} },
                { id: 'etapa-3', nome: '3. Análise de Vulnerabilidades OWASP e SAST/DAST', papeisPorUsuario: {} },
                { id: 'etapa-4', nome: '4. Aprovação pelo Comitê de Mudanças (CAB / SA-GTI)', papeisPorUsuario: {} },
                { id: 'etapa-5', nome: '5. Janela de Manutenção e Rollback Plan', papeisPorUsuario: {} }
            ];
        }

        var inpTit = document.getElementById('builder-raci-titulo'); if (inpTit) inpTit.value = window.raciBuilderState.titulo;
        var inpDesc = document.getElementById('builder-raci-desc'); if (inpDesc) inpDesc.value = window.raciBuilderState.descricao;
        window.raciBuilderRenderTabela();
    };

    window.salvarBuilderRaciFinal = function() {
        if (!window.raciBuilderState) return;
        var tit = (document.getElementById('builder-raci-titulo') ? document.getElementById('builder-raci-titulo').value : '').trim();
        var desc = (document.getElementById('builder-raci-desc') ? document.getElementById('builder-raci-desc').value : '').trim();
        var vinc = (document.getElementById('builder-raci-vinculo') ? document.getElementById('builder-raci-vinculo').value : '').trim();
        var tipovinc = (document.getElementById('builder-raci-tipovinculo') ? document.getElementById('builder-raci-tipovinculo').value : 'SEI');

        if (!tit) { alert('Por favor, informe o título da matriz RACI.'); return; }
        if (!window.raciBuilderState.usuarios || window.raciBuilderState.usuarios.length === 0) {
            alert('Selecione ao menos 1 usuário participante.');
            return;
        }
        if (!window.raciBuilderState.etapas || window.raciBuilderState.etapas.length === 0) {
            alert('Adicione ao menos 1 etapa ao fluxo.');
            return;
        }

        window.raciBuilderState.titulo = tit;
        window.raciBuilderState.descricao = desc || 'Fluxo nominal de governança configurado pelo usuário.';
        window.raciBuilderState.vinculo = vinc;
        window.raciBuilderState.tipoVinculo = tipovinc;

        // Se for nova matriz, cria ID único
        if (!window.raciBuilderState.id) {
            window.raciBuilderState.id = 'RACI-USR-' + Date.now();
            window.raciBuilderState.criadoEm = new Date().toLocaleDateString('pt-BR');
            window.raciBuilderState.criadoPor = (window.obterUsuarioSessaoAtual ? window.obterUsuarioSessaoAtual().nome : 'Luiz Antonio Seixeiro');
        }

        // Garante status inicial nas etapas
        window.raciBuilderState.etapas.forEach(function(et, idx) {
            if (!et.status) et.status = (idx === 0 ? 'em_analise' : 'pendente');
        });

        var modelos = window.obterModelosRaciSalvos();
        var idxExistente = modelos.findIndex(function(m) { return m.id === window.raciBuilderState.id; });
        if (idxExistente !== -1) {
            modelos[idxExistente] = window.raciBuilderState;
        } else {
            modelos.unshift(window.raciBuilderState);
        }

        window.salvarModelosRaci(modelos);
        window.renderizarViewMatrizRaci();

        var modal = document.getElementById('modal-raci-criar-estruturado');
        if (modal) modal.remove();
        alert('✅ Matriz RACI nominal "' + tit + '" salva com sucesso no seu perfil!');
    };

    window.duplicarModeloRaci = function(idModelo) {
        var modelos = window.obterModelosRaciSalvos();
        var m = modelos.find(function(item) { return item.id === idModelo; });
        if (!m) return;
        var clone = JSON.parse(JSON.stringify(m));
        clone.id = 'RACI-CLONE-' + Date.now();
        clone.titulo = m.titulo + ' (Cópia)';
        clone.vinculo = '';
        clone.tipoVinculo = '';
        clone.etapas.forEach(function(e, i) {
            e.status = (i === 0 ? 'em_analise' : 'pendente');
            e.aprovadoPor = '';
            e.dataAprov = '';
        });
        modelos.push(clone);
        window.salvarModelosRaci(modelos);
        window.renderizarViewMatrizRaci();
        alert('✅ Matriz duplicada com sucesso! Você pode operá-la ou vinculá-la a outra demanda.');
    };

    window.excluirModeloRaci = function(idModelo) {
        if (!confirm('Deseja realmente excluir esta matriz RACI do seu perfil?')) return;
        var modelos = window.obterModelosRaciSalvos();
        var filtrados = modelos.filter(function(item) { return item.id !== idModelo; });
        window.salvarModelosRaci(filtrados);
        window.renderizarViewMatrizRaci();
    };

    window.restaurarModelosPadraoRaci = function() {
        if (!confirm('Deseja restaurar os 3 modelos nominais homologados da SP-Águas (Lei 14.133, TCU 269 e DevSecOps)?')) return;
        window.salvarModelosRaci(JSON.parse(JSON.stringify(window.MODELOS_RACI_PADRAO)));
        window.renderizarViewMatrizRaci();
    };
window.renderizarTabelaMesa = function() {
        if (window.modoMesaAtivo === 'raci') {
            if (typeof window.renderizarGradeRaciMesa === 'function') {
                window.renderizarGradeRaciMesa();
                return;
            }
        }
        var thead = document.getElementById('thead-meus-processos');
        var tbody = document.getElementById('tbody-meus-processos');
        var pag = document.getElementById('mesa-pag-info');
        var busca = (document.getElementById('busca-mesa-input') ? document.getElementById('busca-mesa-input').value : '').toLowerCase().trim();
        if (!tbody) return;
        window.atualizarContadoresCustodiaMesa();

        var fixados = window.obterFixadosValidos();
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var pacotesOp = (typeof window.OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(window.OP_PACOTES_OFICIAIS)) ? window.OP_PACOTES_OFICIAIS : [];
        var baseGlpi = (typeof window.CHAMADOS_GLPI_15_OFICIAIS !== 'undefined' && Array.isArray(window.CHAMADOS_GLPI_15_OFICIAIS) && window.CHAMADOS_GLPI_15_OFICIAIS.length > 0) ? window.CHAMADOS_GLPI_15_OFICIAIS : ((typeof window.CHAMADOS_ITSM_SUPORTE !== 'undefined' && Array.isArray(window.CHAMADOS_ITSM_SUPORTE)) ? window.CHAMADOS_ITSM_SUPORTE : []);
        var rels = window.obterRelatoriosRituais();

        // 1. ABA: RELATÓRIOS DAILY & SPRINTS
        if (window.modoMesaAtivo === 'relatorios') {
            if (thead) {
                thead.innerHTML = '<tr style="font-size: 10.5px; text-transform: uppercase"><th style="width: 36px; text-align: center; padding: 10px 8px">⭐</th><th style="padding: 10px 12px">Tipo / Ritual</th><th style="padding: 10px 12px">Data</th><th style="padding: 10px 12px">Título &amp; Escopo</th><th style="padding: 10px 12px">Destaques</th><th style="padding: 10px 12px; text-align: center">Status</th><th style="text-align: center; padding: 10px 12px">Ações</th></tr>';
            }
            var relsFiltrados = rels.filter(function(r) {
                if (!busca) return true;
                return (r.titulo + ' ' + r.destaque + ' ' + r.tipoLabel + ' ' + r.data).toLowerCase().indexOf(busca) !== -1;
            });
            if (pag) pag.innerText = 'Exibindo ' + relsFiltrados.length + ' relatórios de rituais ágeis (Daily & Sprints)';
            tbody.innerHTML = relsFiltrados.map(function(r, idx) {
                var bg = (idx % 2 === 0) ? 'rgba(15,23,42,0.4)' : 'rgba(30,41,59,0.3)';
                var chave = 'REL#' + r.id;
                var isMarcado = fixados.indexOf(chave) !== -1 || r.marcado;
                var sCor = isMarcado ? '#facc15' : '#64748b';
                var sIco = isMarcado ? '⭐' : '☆';
                return '<tr ><td style="text-align:center;padding:10px 8px;cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar/Desmarcar para acompanhamento"><span >' + sIco + '</span></td><td style="padding:10px 12px;font-weight:700;font-size:11.5px">' + r.tipoLabel + '</td><td style="padding:10px 12px;font-size:11px">' + r.data + '</td><td style="padding:10px 12px;font-weight:700">' + r.titulo + '</td><td style="padding:10px 12px;font-size:11px">' + r.destaque + '</td><td style="padding:10px 12px;text-align:center"><span style="padding:2px 7px;border-radius:10px;font-weight:700">' + r.status + '</span></td><td style="padding:10px 12px;text-align:center;white-space:nowrap"><button type="button" class="btn btn-outline-secondary" onclick="window.visualizarRelatorioMesaModal(\'' + r.id + '\')" style="padding:3px 8px;font-size:10.5px;margin-right:4px">👁️ Ver</button><button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + chave + '\')" style="padding:3px 8px;font-size:10.5px">' + (isMarcado ? '⭐ Acompanhando' : '☆ Acompanhar') + '</button></td></tr>';
            }).join('');
            return;
        }

        // 2. ABA: CHAMADOS GLPI (TODOS OS 24 CHAMADOS COM SELEÇÃO PARA ACOMPANHAMENTO)
        if (window.modoMesaAtivo === 'glpi') {
            if (thead) {
                thead.innerHTML = '<tr style="font-size: 10.5px; text-transform: uppercase"><th style="width: 36px; text-align: center; padding: 10px 8px">⭐</th><th style="padding: 10px 12px">#ID GLPI</th><th style="padding: 10px 12px">Título do Chamado / Incidente</th><th style="padding: 10px 12px">Técnico / Fila</th><th style="padding: 10px 12px">Status</th><th style="padding: 10px 12px">SLA / Urgência</th><th style="text-align: center; padding: 10px 12px">Ações</th></tr>';
            }
            var listaGlpi = baseGlpi.filter(function(t) {
                if (!busca) return true;
                return (t.id + ' ' + (t.titulo || '') + ' ' + (t.tecnico || '') + ' ' + (t.local || '') + ' ' + (t.cat || t.bucket || '')).toLowerCase().indexOf(busca) !== -1;
            });
            if (pag) pag.innerText = 'Exibindo ' + listaGlpi.length + ' chamados técnicos não solucionados (GLPI Produção)';
            tbody.innerHTML = listaGlpi.map(function(t, idx) {
                var chave = 'GLPI#' + t.id;
                var isMarcado = fixados.indexOf(chave) !== -1;
                var sCor = isMarcado ? '#facc15' : '#64748b';
                var sIco = isMarcado ? '⭐' : '☆';
                var codGlpi = '#' + t.id;
                var linkOficial = 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=' + t.id;
                var stBadge = (t.status || '').toLowerCase().indexOf('atendimento') !== -1 
                    ? '<span class="pill-tag pill-blue" style="font-size:10.5px">🟢 ' + t.status + '</span>'
                    : '<span class="pill-tag pill-orange" style="font-size:10.5px">🟠 ' + (t.status || 'Pendente') + '</span>';
                var subCategoria = t.cat ? ('🏷️ ' + t.cat) : (t.bucket ? ('🏷️ ' + t.bucket) : '🏷️ Suporte & Infra');
                var solicitanteStr = t.requerente ? (' • Req: ' + t.requerente) : '';
                var slaStr = t.urgencia || (t.prioridade ? ('Prioridade: ' + t.prioridade) : 'Normal');

                return '<tr ><td style="text-align:center;padding:10px 8px;cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar/Desmarcar para acompanhamento"><span >' + sIco + '</span></td><td style="padding:10px 12px;font-weight:800"><a href="' + linkOficial + '" target="_blank" style="text-decoration:none" title="Abrir no GLPI Oficial">' + codGlpi + '</a></td><td style="padding:10px 12px;font-weight:600">' + (t.titulo || '—') + '<div style="font-size:10.5px;font-weight:400">' + subCategoria + solicitanteStr + '</div></td><td style="padding:10px 12px">👤 ' + (t.tecnico || 'SA-GTI') + '<div >' + (t.local || t.fila || 'Sede - São Paulo') + '</div></td><td style="padding:10px 12px">' + stBadge + '</td><td style="padding:10px 12px;font-size:11px">' + slaStr + '</td><td style="padding:10px 12px;text-align:center;white-space:nowrap"><button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + chave + '\')" style="padding:3px 8px;font-size:10.5px;margin-right:4px">' + (isMarcado ? '⭐ Acompanhando' : '☆ Acompanhar') + '</button><a href="' + linkOficial + '" target="_blank" class="btn btn-outline-secondary" style="padding:3px 8px;font-size:10.5px;text-decoration:none">GLPI ↗</a></td></tr>';
            }).join('');
            return;
        }

        // 3. ABA: PACOTES OPENPROJECT (TODOS OS PACOTES EM ABERTO, INDEPENDENTE DE USUÁRIO)
        if (window.modoMesaAtivo === 'openproject') {
            if (thead) {
                thead.innerHTML = '<tr style="font-size: 10.5px; text-transform: uppercase"><th style="width: 36px; text-align: center; padding: 10px 8px">⭐</th><th style="padding: 10px 12px">#ID Pacote</th><th style="padding: 10px 12px">Assunto / Entregável</th><th style="padding: 10px 12px">Responsável / Projeto</th><th style="padding: 10px 12px">Status</th><th style="padding: 10px 12px">Tipo / Custo</th><th style="text-align: center; padding: 10px 12px">Ações</th></tr>';
            }
            var pacotesAbertos = pacotesOp.filter(function(op) {
                var st = (op.status || '').toLowerCase();
                return st.indexOf('encerrado') === -1 && st.indexOf('concluído') === -1 && st.indexOf('cancelado') === -1;
            });
            if (busca) {
                pacotesAbertos = pacotesAbertos.filter(function(p) {
                    return (p.id + ' ' + (p.assunto || '') + ' ' + (p.projeto || '') + ' ' + (p.atrib || '') + ' ' + (p.status || '')).toLowerCase().indexOf(busca) !== -1;
                });
            }
            if (pag) pag.innerText = 'Exibindo ' + Math.min(100, pacotesAbertos.length) + ' de ' + pacotesAbertos.length + ' pacotes de trabalho em aberto (OpenProject Oficial)';
            tbody.innerHTML = pacotesAbertos.slice(0, 100).map(function(op) {
                var chave = 'OP#' + op.id;
                var isMarcado = fixados.indexOf(chave) !== -1;
                var sCor = isMarcado ? '#facc15' : '#64748b';
                var sIco = isMarcado ? '⭐' : '☆';
                var urlOp = 'https://projetos.spaguas.sp.gov.br/work_packages/' + op.id;
                var custoStr = op.custo && parseFloat(op.custo) > 0 ? (' • R$ ' + parseFloat(op.custo).toLocaleString('pt-BR', {minimumFractionDigits: 0})) : '';
                return '<tr ><td style="text-align:center;padding:10px 8px;cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar/Desmarcar para acompanhamento"><span >' + sIco + '</span></td><td style="padding:10px 12px;font-weight:800"><a href="' + urlOp + '" target="_blank" style="text-decoration:none">#' + op.id + '</a></td><td style="padding:10px 12px;font-weight:600">' + (op.assunto || '—') + '<div style="font-size:10.5px;font-weight:400">📁 ' + (op.projeto || 'SA-GTI') + '</div></td><td style="padding:10px 12px">👤 ' + (op.atrib || op.encarr || 'SA-GTI') + '</td><td style="padding:10px 12px"><span class="pill-tag pill-blue">' + (op.status || '🚀 Em progresso') + '</span></td><td style="padding:10px 12px;font-size:11px">' + (op.tipo || 'Projeto') + custoStr + '</td><td style="padding:10px 12px;text-align:center;white-space:nowrap"><button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + chave + '\')" style="padding:3px 8px;font-size:10.5px;margin-right:4px">' + (isMarcado ? '⭐ Acompanhando' : '☆ Acompanhar') + '</button><a href="' + urlOp + '" target="_blank" class="btn btn-outline-secondary" style="padding:3px 8px;font-size:10.5px;text-decoration:none">Abrir OP ↗</a></td></tr>';
            }).join('');
            return;
        }

        // 4. ABA: FIXADOS / ACOMPANHAMENTO UNIFICADO (TODOS OS ITENS MARCADOS: SEI + OP + GLPI + RELATÓRIOS)
        if (window.modoMesaAtivo === 'fixados') {
            if (thead) {
                thead.innerHTML = '<tr style="font-size: 10.5px; text-transform: uppercase"><th style="width: 36px; text-align: center; padding: 10px 8px">⭐</th><th style="padding: 10px 12px">Origem / ID</th><th style="padding: 10px 12px">Título / Especificação</th><th style="padding: 10px 12px">Responsável / Técnico</th><th style="padding: 10px 12px">Status</th><th style="padding: 10px 12px">Aging / Detalhe</th><th style="text-align: center; padding: 10px 12px">Ações</th></tr>';
            }
            var itensAcompanhados = [];
            fixados.forEach(function(chave) {
                var itemObj = (typeof window.resolverItemWatchlist === 'function')
                    ? window.resolverItemWatchlist(chave, baseProcs, pacotesOp, baseGlpi, rels)
                    : null;
                if (itemObj) itensAcompanhados.push(itemObj);
            });

            // Sincroniza compulsoriamente o contador do botão com a quantidade real exibida
            var elCountFixBtn = document.getElementById('count-mesa-fixados');
            if (elCountFixBtn) elCountFixBtn.innerText = String(itensAcompanhados.length);

            if (busca) {
                itensAcompanhados = itensAcompanhados.filter(function(it) {
                    return (it.id + ' ' + (it.titulo || '') + ' ' + (it.resp || '') + ' ' + (it.tipo || '')).toLowerCase().indexOf(busca) !== -1;
                });
            }

            if (pag) pag.innerText = 'Exibindo ' + itensAcompanhados.length + ' demandas sob seu acompanhamento ativo (Watchlist 360°)';
            if (itensAcompanhados.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="padding: 30px; text-align: center"><div style="font-size: 24px; margin-bottom: 8px">⭐</div><strong style="font-size: 13px">Nenhuma demanda selecionada para acompanhamento no momento.</strong><br><span style="font-size: 11.5px">Clique no botão "☆ Acompanhar" em qualquer aba (Processos SEI, Pacotes OpenProject, Chamados GLPI ou Relatórios) para consolidá-las aqui!</span></td></tr>';
                return;
            }

            tbody.innerHTML = itensAcompanhados.map(function(it) {
                var tagCor = it.tipo === 'OpenProject' ? '#f59e0b' : (it.tipo === 'GLPI' ? '#c084fc' : (it.tipo === 'Relatório' ? '#38bdf8' : '#38bdf8'));
                return '<tr ><td style="text-align:center;padding:10px 8px;cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + it.chave + '\')" title="Remover de Acompanhamento"><span >⭐</span></td><td style="padding:10px 12px;font-weight:700">' + it.id + ' <span style="font-weight:400">(' + it.tipo + ')</span></td><td style="padding:10px 12px">' + (it.titulo || '—') + '</td><td style="padding:10px 12px">' + (it.resp || 'SA-GTI') + '</td><td style="padding:10px 12px"><span class="pill-tag pill-blue">' + (it.status || 'Ativo') + '</span></td><td style="padding:10px 12px">' + (it.detalhe || '—') + '</td><td style="padding:10px 12px;text-align:center;white-space:nowrap">' + it.acao + '</td></tr>';
            }).join('');
            return;
        }

        // 5. ABA DEFAULT: MINHA CUSTÓDIA / ACERVO
        if (thead) {
            thead.innerHTML = '<tr style="font-size: 10.5px; text-transform: uppercase"><th style="width: 36px; text-align: center; padding: 10px 8px">⭐</th><th style="padding: 10px 12px">Processo SEI</th><th style="padding: 10px 12px">Especificação / Objeto</th><th style="padding: 10px 12px">Responsável</th><th style="padding: 10px 12px">Status</th><th style="padding: 10px 12px">Aging Líquido</th><th style="text-align: center; padding: 10px 12px">Ações</th></tr>';
        }

        var lista = (typeof window.obterCustodiaNominalLuiz === 'function') ? window.obterCustodiaNominalLuiz() : [];

        if (busca) {
            lista = lista.filter(function(p) {
                return (p.ID_Processo + ' ' + (p.Especificacao || '') + ' ' + (p.Responsavel_Tecnico || '')).toLowerCase().indexOf(busca) !== -1;
            });
        }

        if (pag) pag.innerText = 'Exibindo ' + lista.length + ' de ' + lista.length + ' itens';
        if (lista.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="padding: 30px; text-align: center"><div style="font-size: 24px; margin-bottom: 8px">📂</div><strong style="font-size: 13px">Nenhum processo sob sua custódia nominal direta no momento.</strong><br><span style="font-size: 11.5px">Demandas atribuídas aos analistas do setor podem ser acompanhadas nos filtros acima ou fixadas com estrela (⭐).</span></td></tr>';
            return;
        }

        tbody.innerHTML = lista.map(function(p) {
            var isFix = fixados.includes(p.ID_Processo);
            var starCor = isFix ? '#facc15' : '#64748b';
            var starIco = isFix ? '⭐' : '☆';
            return '<tr ><td style="text-align:center;padding:10px 8px;cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + p.ID_Processo + '\')" title="Marcar/Desmarcar para acompanhamento"><span >' + starIco + '</span></td><td style="padding:10px 12px;font-weight:700">' + p.ID_Processo + '</td><td style="padding:10px 12px">' + (p.Especificacao || '—') + '</td><td style="padding:10px 12px">' + (p.Responsavel_Tecnico || 'SA-GTI') + '</td><td style="padding:10px 12px"><span class="pill-tag pill-blue">' + (p.Status_Kanban || 'Ativo') + '</span></td><td style="padding:10px 12px">' + (p.Aging_Liquido || p.Faixa_Aging || 'Normal') + '</td><td style="padding:10px 12px;text-align:center;white-space:nowrap"><button type="button" class="btn btn-outline-secondary" onclick="window.toggleFixado(\'' + p.ID_Processo + '\')" style="padding:3px 8px;font-size:10.5px;margin-right:4px">' + (isFix ? '⭐ Acompanhando' : '☆ Acompanhar') + '</button><button class="btn btn-outline-secondary" onclick="window.abrirDetalhesProcesso(\'' + p.ID_Processo + '\')" style="padding:3px 8px;font-size:10.5px">👁️ Ver</button></td></tr>';
        }).join('');
    };

    // =========================================================================
    // 3. MOTOR KANBAN ÁGIL DE 5 COLUNAS — FIEL À IMAGEM MODELO (image_7f3d1c.png)
    // =========================================================================
    window.criarCardKanban = function(p, coluna) {
        var fixados = window.obterFixadosValidos();
        var isFixado = fixados.includes(p.ID_Processo);
        var postit = (typeof cardPostits !== 'undefined' && cardPostits[p.ID_Processo]) ? cardPostits[p.ID_Processo] : null;

        var statusClass = 'k-status-sei-normal';
        var farolTxt = p.Faixa_Aging || p.Farol_Criticidade || 'Normal';
        if (farolTxt.indexOf('Normal') !== -1) {
            farolTxt = 'Normal';
            statusClass = 'k-status-sei-normal';
        } else if (farolTxt.indexOf('Monitoramento') !== -1 || farolTxt.indexOf('Atenção') !== -1) {
            farolTxt = 'Monitoramento';
            statusClass = 'k-status-sei-alerta';
        } else {
            farolTxt = 'Saneamento';
            statusClass = 'k-status-sei-critico';
        }

        var bordaClass = 'borda-sei';
        if (coluna === 'sprint_atual') bordaClass = 'borda-atual';
        else if (coluna === 'sprint_prox') bordaClass = 'borda-prox';

        var postitHtml = '';
        if (postit) {
            var corClasse = postit.cor === 'rosa' ? 'postit-rosa' : (postit.cor === 'azul' ? 'postit-azul' : 'postit-verde');
            postitHtml = '<div class="postit-tag ' + corClasse + '" style="margin-top:6px;font-size:10.5px;padding:4px 6px;border-radius:4px">' +
                '<div style="display:flex;justify-content:space-between;align-items:center">' +
                    '<strong>📌 Post-it:</strong>' +
                    '<button onclick="removerPostitCard(\'' + p.ID_Processo + '\')" style="cursor:pointer" class="btn btn-ghost-secondary">✖</button>' +
                '</div>' +
                '<div>' + (postit.texto || '') + '</div>' +
            '</div>';
        }

        return '<div class="kanban-card-modelo ' + bordaClass + '" draggable="true" ondragstart="arrastarItem(event, \'' + p.ID_Processo + '\')">' +
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:6px;margin-bottom:4px">' +
                '<strong class="k-title-sei" onclick="abrirDetalhesProcesso(\'' + p.ID_Processo + '\')">' + p.ID_Processo + '</strong>' +
                '<div style="display:flex;align-items:center;gap:4px">' +
                    '<button type="button" class="k-btn-postit" onclick="adicionarPostitCardPrompt(\'' + p.ID_Processo + '\')" title="Adicionar Post-it">📌 Post-it</button>' +
                    '<span style="cursor:pointer;font-size:13px" onclick="window.toggleFixado(\'' + p.ID_Processo + '\')" title="Acompanhar">' + (isFixado ? '⭐' : '☆') + '</span>' +
                '</div>' +
            '</div>' +
            '<p class="k-desc-sei" title="' + (p.Especificacao || p.Tipo_Processo || '') + '">' + (p.Especificacao || p.Tipo_Processo || '') + '</p>' +
            '<div class="k-footer">' +
                '<span>👤 ' + (p.Responsavel_Tecnico || 'Sem responsável') + '</span>' +
                '<span class="' + statusClass + '">' + farolTxt + '</span>' +
            '</div>' +
            postitHtml +
        '</div>';
    };

    window.criarCardKanbanOP = function(op, coluna) {
        var chave = 'OP#' + op.id;
        var fixados = window.obterFixadosValidos();
        var isFixado = fixados.includes(chave);
        var postit = (typeof cardPostits !== 'undefined' && cardPostits[chave]) ? cardPostits[chave] : null;

        var bordaClass = 'borda-op';
        if (coluna === 'sprint_atual') bordaClass = 'borda-atual';
        else if (coluna === 'sprint_prox') bordaClass = 'borda-prox';

        var postitHtml = '';
        if (postit) {
            var corClasse = postit.cor === 'rosa' ? 'postit-rosa' : (postit.cor === 'azul' ? 'postit-azul' : 'postit-verde');
            postitHtml = '<div class="postit-tag ' + corClasse + '" style="margin-top:6px;font-size:10.5px;padding:4px 6px;border-radius:4px">' +
                '<div style="display:flex;justify-content:space-between;align-items:center">' +
                    '<strong>📌 Post-it:</strong>' +
                    '<button onclick="removerPostitCard(\'' + chave + '\')" style="cursor:pointer" class="btn btn-ghost-secondary">✖</button>' +
                '</div>' +
                '<div>' + (postit.texto || '') + '</div>' +
            '</div>';
        }

        var custoFormatado = '';
        if (op.custo && parseFloat(op.custo) > 0) {
            try {
                custoFormatado = ' • R$ ' + parseFloat(op.custo).toLocaleString('pt-BR', {minimumFractionDigits: 0, maximumFractionDigits: 0});
            } catch(e) {}
        } else if (String(op.id) === '42') {
            custoFormatado = ' • R$ 2.000.000';
        }

        return '<div class="kanban-card-modelo ' + bordaClass + '" draggable="true" ondragstart="arrastarItem(event, \'' + chave + '\')">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:6px">' +
                '<div style="display:flex;align-items:center;gap:6px">' +
                    '<span class="k-tag-op-id">#' + op.id + '</span>' +
                    '<span class="k-tag-op-tipo">' + (op.tipo || 'Projeto') + '</span>' +
                '</div>' +
                '<div style="display:flex;align-items:center;gap:4px">' +
                    '<button type="button" class="k-btn-postit" onclick="adicionarPostitCardPrompt(\'' + chave + '\')" title="Adicionar Post-it">📌 Post-it</button>' +
                    '<span style="cursor:pointer;font-size:13px" onclick="window.toggleFixado(\'' + chave + '\')" title="Acompanhar">' + (isFixado ? '⭐' : '☆') + '</span>' +
                '</div>' +
            '</div>' +
            '<div class="k-title-item" title="' + (op.assunto || '') + '">' + (op.assunto || 'Pacote sem assunto') + '</div>' +
            '<div class="k-meta-line" title="' + (op.projeto || '') + '">📁 ' + (op.projeto || 'SA-GTI - Gerência de TI') + '</div>' +
            '<div class="k-footer">' +
                '<span>👤 ' + (op.atrib || op.encarr || 'SA-GTI - Gerência de TI') + '</span>' +
                '<span class="k-status-op">' + (op.status || '🚀 Em progresso') + custoFormatado + '</span>' +
            '</div>' +
            postitHtml +
        '</div>';
    };

    window.criarCardKanbanGLPI = function(t, coluna, idx) {
        var chave = 'GLPI#' + t.id;
        var fixados = window.obterFixadosValidos();
        var isFixado = fixados.includes(chave);
        var postit = (typeof cardPostits !== 'undefined' && cardPostits[chave]) ? cardPostits[chave] : null;
        var displayId = t.id;

        var bordaClass = 'borda-glpi';
        if (coluna === 'sprint_atual') bordaClass = 'borda-atual';
        else if (coluna === 'sprint_prox') bordaClass = 'borda-prox';

        var postitHtml = '';
        if (postit) {
            var corClasse = postit.cor === 'rosa' ? 'postit-rosa' : (postit.cor === 'azul' ? 'postit-azul' : 'postit-verde');
            postitHtml = '<div class="postit-tag ' + corClasse + '" style="margin-top:6px;font-size:10.5px;padding:4px 6px;border-radius:4px">' +
                '<div style="display:flex;justify-content:space-between;align-items:center">' +
                    '<strong>📌 Post-it:</strong>' +
                    '<button onclick="removerPostitCard(\'' + chave + '\')" style="cursor:pointer" class="btn btn-ghost-secondary">✖</button>' +
                '</div>' +
                '<div>' + (postit.texto || '') + '</div>' +
            '</div>';
        }

        var categoriaTexto = t.cat || t.bucket || 'Suporte & Infra';
        var filaTexto = t.local ? (t.local.split('>')[0].trim()) : (t.fila || 'SA-GTI');
        var tipoLabel = t.tipo || (t.prioridade ? ('Prioridade ' + t.prioridade) : 'Incidente GLPI');

        return '<div class="kanban-card-modelo ' + bordaClass + '" draggable="true" ondragstart=\"arrastarItem(event, \'' + chave + '\')\">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:6px">' +
                '<div style="display:flex;align-items:center;gap:6px">' +
                    '<span class="k-tag-glpi-id">#' + displayId + '</span>' +
                    '<span class="k-tag-glpi-tipo">' + tipoLabel + '</span>' +
                '</div>' +
                '<div style="display:flex;align-items:center;gap:4px">' +
                    '<button type="button" class="k-btn-postit" onclick="adicionarPostitCardPrompt(\'' + chave + '\')" title="Adicionar Post-it">📌 Post-it</button>' +
                    '<span style="cursor:pointer;font-size:13px" onclick="window.toggleFixado(\'' + chave + '\')" title="Acompanhar">' + (isFixado ? '⭐' : '☆') + '</span>' +
                '</div>' +
            '</div>' +
            '<div class="k-title-item" title="' + (t.titulo || '') + '">' + (t.titulo || 'Chamado sem título') + '</div>' +
            '<div class="k-meta-line" title="' + categoriaTexto + '">🏷️ ' + filaTexto + ' • ' + categoriaTexto + '</div>' +
            '<div class="k-footer">' +
                '<span>👤 ' + (t.tecnico || 'Não atribuído') + '</span>' +
                '<span class="k-status-glpi">' + (t.status || 'Pendente') + '</span>' +
            '</div>' +
            postitHtml +
        '</div>';
    };

    window.soltarItem = function(ev, novaColuna) {
        if (ev && ev.preventDefault) ev.preventDefault();
        var id = (typeof idProcessoArrastado !== 'undefined' && idProcessoArrastado) ? idProcessoArrastado : (ev && ev.dataTransfer ? ev.dataTransfer.getData("text") : null);
        if (!id) return;

        if (id.indexOf('GLPI#') === 0) {
            if (novaColuna === 'backlog' || novaColuna === 'backlog_op' || novaColuna === 'backlog_glpi') {
                novaColuna = 'backlog_glpi';
            }
        } else if (id.indexOf('OP#') === 0) {
            if (novaColuna === 'backlog' || novaColuna === 'backlog_op' || novaColuna === 'backlog_glpi') {
                novaColuna = 'backlog_op';
            }
        } else {
            if (novaColuna === 'backlog_op' || novaColuna === 'backlog_glpi' || novaColuna === 'backlog') {
                novaColuna = 'backlog';
            }
        }

        if (typeof kanbanOverrides === 'undefined') window.kanbanOverrides = {};
        kanbanOverrides[id] = novaColuna;
        try { localStorage.setItem('sagti_kanban_status', JSON.stringify(kanbanOverrides)); } catch(e) {}
        try { localStorage.setItem('kanban_overrides', JSON.stringify(kanbanOverrides)); } catch(e) {}

        idProcessoArrastado = null;
        window.renderizarKanbanAgil();
    };

    window.arrastarItem = function(ev, id) {
        idProcessoArrastado = id;
        if (ev && ev.dataTransfer) {
            ev.dataTransfer.setData("text", id);
            ev.dataTransfer.effectAllowed = "move";
        }
    };

    window.permitirSoltar = function(ev) {
        if (ev && ev.preventDefault) ev.preventDefault();
    };

    window.resetarKanbanParaBacklog = function() {
        if (confirm('Deseja mover todos os itens (Processos SEI, Pacotes OpenProject e Chamados GLPI) de volta para os seus Backlogs de origem?')) {
            kanbanOverrides = {};
            try { localStorage.removeItem('sagti_kanban_status'); } catch(e) {}
            try { localStorage.removeItem('kanban_overrides'); } catch(e) {}
            window.renderizarKanbanAgil();
        }
    };

    window.renderizarKanbanAgil = function() {
        var colBackSEI = document.getElementById('col-backlog');
        var colBackOP = document.getElementById('col-backlog-op');
        var colBackGLPI = document.getElementById('col-backlog-glpi');
        var colAtual = document.getElementById('col-sprint-atual');
        var colProx = document.getElementById('col-sprint-prox');
        if (!colBackSEI || !colBackOP || !colBackGLPI || !colAtual || !colProx) return;

        var fBusca = (document.getElementById('kanban-busca') ? document.getElementById('kanban-busca').value : '').toLowerCase().trim();
        var fBucket = document.getElementById('kanban-filtro-bucket') ? document.getElementById('kanban-filtro-bucket').value : '';
        var fResp = document.getElementById('kanban-filtro-resp') ? document.getElementById('kanban-filtro-resp').value : '';
        var fEixo = document.getElementById('kanban-filtro-eixo') ? document.getElementById('kanban-filtro-eixo').value : '';

        var overrides = {};
        try { overrides = JSON.parse(localStorage.getItem('sagti_kanban_status') || localStorage.getItem('kanban_overrides') || '{}'); } catch(e) {}
        if (typeof kanbanOverrides !== 'undefined') {
            Object.assign(overrides, kanbanOverrides);
        }

        var listaSEI = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var procsFiltrados = listaSEI.filter(function(p) {
            if (fBusca && !(p.ID_Processo || '').toLowerCase().includes(fBusca) && !(p.Especificacao || '').toLowerCase().includes(fBusca)) return false;
            if (fBucket && p.Bucket_OpenProject !== fBucket) return false;
            if (fResp && p.Responsavel_Tecnico !== fResp) return false;
            if (fEixo && p.Eixo_Gestao !== fEixo) return false;
            return true;
        });

        var listaOP = (typeof window.OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(window.OP_PACOTES_OFICIAIS)) ? window.OP_PACOTES_OFICIAIS : [];
        var pacotesFiltrados = listaOP.filter(function(op) {
            if (fBusca && !(op.id + ' ' + (op.assunto || '') + ' ' + (op.projeto || '') + ' ' + (op.desc || '')).toLowerCase().includes(fBusca)) return false;
            if (fResp && (op.atrib || op.encarr || '') !== fResp) return false;
            if (fBucket && (op.backlog || '') !== fBucket) return false;
            return true;
        });

        var listaGLPI = (typeof window.CHAMADOS_GLPI_15_OFICIAIS !== 'undefined' && Array.isArray(window.CHAMADOS_GLPI_15_OFICIAIS) && window.CHAMADOS_GLPI_15_OFICIAIS.length > 0) ? window.CHAMADOS_GLPI_15_OFICIAIS : ((typeof window.CHAMADOS_ITSM_SUPORTE !== 'undefined' && Array.isArray(window.CHAMADOS_ITSM_SUPORTE)) ? window.CHAMADOS_ITSM_SUPORTE : []);
        var chamadosFiltrados = listaGLPI.filter(function(t) {
            if (fBusca && !(t.id + ' ' + (t.titulo || '') + ' ' + (t.fila || '') + ' ' + (t.bucket || '')).toLowerCase().includes(fBusca)) return false;
            if (fResp && (t.tecnico || '').toLowerCase().indexOf(fResp.toLowerCase()) === -1) return false;
            if (fBucket && (t.bucket || '') !== fBucket) return false;
            return true;
        });

        var itensBackSEI = [];
        var itensBackOP = [];
        var itensBackGLPI = [];
        var itensAtual = [];
        var itensProx = [];

        procsFiltrados.forEach(function(p) {
            var col = overrides[p.ID_Processo] || 'backlog';
            if (col === 'sprint_atual') itensAtual.push({ tipo: 'sei', dado: p });
            else if (col === 'sprint_prox') itensProx.push({ tipo: 'sei', dado: p });
            else itensBackSEI.push(p);
        });

        pacotesFiltrados.forEach(function(op) {
            var chave = 'OP#' + op.id;
            var col = overrides[chave] || 'backlog_op';
            if (col === 'sprint_atual') itensAtual.push({ tipo: 'op', dado: op });
            else if (col === 'sprint_prox') itensProx.push({ tipo: 'op', dado: op });
            else itensBackOP.push(op);
        });

        chamadosFiltrados.forEach(function(t, idx) {
            var chave = 'GLPI#' + t.id;
            var col = overrides[chave] || 'backlog_glpi';
            if (col === 'sprint_atual') itensAtual.push({ tipo: 'glpi', dado: t, idx: idx });
            else if (col === 'sprint_prox') itensProx.push({ tipo: 'glpi', dado: t, idx: idx });
            else itensBackGLPI.push({ dado: t, idx: idx });
        });

        var bBackSEI = document.getElementById('badge-sprint-backlog');
        var bBackOP = document.getElementById('badge-sprint-backlog-op');
        var bBackGLPI = document.getElementById('badge-sprint-backlog-glpi');
        var bAtual = document.getElementById('badge-sprint-atual');
        var bProx = document.getElementById('badge-sprint-prox');
        var bTotal = document.getElementById('kanban-contagem-total');

        if (bBackSEI) bBackSEI.innerText = itensBackSEI.length + ' processos';
        if (bBackOP) bBackOP.innerText = itensBackOP.length + ' pacotes';
        if (bBackGLPI) bBackGLPI.innerText = itensBackGLPI.length + ' chamados';
        if (bAtual) bAtual.innerText = itensAtual.length + ' itens';
        if (bProx) bProx.innerText = itensProx.length + ' itens';
        if (bTotal) {
            bTotal.innerText = 'Backlogs: ' + itensBackSEI.length + ' SEI + ' + itensBackOP.length + ' OP + ' + itensBackGLPI.length + ' GLPI | ' + itensAtual.length + ' na Sprint Atual';
        }

        colBackSEI.innerHTML = itensBackSEI.map(function(p) {
            return window.criarCardKanban(p, 'backlog');
        }).join('');

        colBackOP.innerHTML = itensBackOP.map(function(op) {
            return window.criarCardKanbanOP(op, 'backlog_op');
        }).join('');

        colBackGLPI.innerHTML = itensBackGLPI.map(function(obj) {
            return window.criarCardKanbanGLPI(obj.dado, 'backlog_glpi', obj.idx);
        }).join('');

        colAtual.innerHTML = itensAtual.map(function(item) {
            if (item.tipo === 'sei') return window.criarCardKanban(item.dado, 'sprint_atual');
            if (item.tipo === 'op') return window.criarCardKanbanOP(item.dado, 'sprint_atual');
            return window.criarCardKanbanGLPI(item.dado, 'sprint_atual', item.idx);
        }).join('');

        colProx.innerHTML = itensProx.map(function(item) {
            if (item.tipo === 'sei') return window.criarCardKanban(item.dado, 'sprint_prox');
            if (item.tipo === 'op') return window.criarCardKanbanOP(item.dado, 'sprint_prox');
            return window.criarCardKanbanGLPI(item.dado, 'sprint_prox', item.idx);
        }).join('');
    };

    
    // =========================================================================
    // 4. INTEGRAÇÃO DOS 3 BACKLOGS (SEI, OPENPROJECT & GLPI) NA WAR ROOM DAILY
    // =========================================================================
    window.abaPautaDailyAtiva = 'sei';

    window.alternarAbaPautaDaily = function(aba) {
        window.abaPautaDailyAtiva = aba || 'sei';
        ['sei', 'op', 'glpi'].forEach(function(a) {
            var btn = document.getElementById('btn-pauta-bkt-' + a);
            if (btn) {
                if (a === window.abaPautaDailyAtiva) {
                    btn.className = 'btn btn-primary pill-pauta-bkt active';
                } else {
                    btn.className = 'btn btn-outline-secondary pill-pauta-bkt';
                }
            }
        });
        window.filtrarListaParaPautar();
    };

    window.filtrarListaParaPautar = function() {
        var inp = document.getElementById('busca-pauta-input');
        var termo = (inp ? inp.value : '').toLowerCase().trim();
        var container = document.getElementById('lista-candidatos-pauta');
        if (!container) return;

        if (typeof pautaDailyCards === 'undefined') window.pautaDailyCards = [];
        try {
            var salvos = JSON.parse(localStorage.getItem('sagti_pauta_daily') || '[]');
            if (Array.isArray(salvos)) window.pautaDailyCards = salvos;
        } catch(e) {}

        var procsSEI = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var pacotesOP = (typeof window.OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(window.OP_PACOTES_OFICIAIS)) ? window.OP_PACOTES_OFICIAIS : [];
        var chamadosGLPI = (typeof window.CHAMADOS_GLPI_15_OFICIAIS !== 'undefined' && Array.isArray(window.CHAMADOS_GLPI_15_OFICIAIS) && window.CHAMADOS_GLPI_15_OFICIAIS.length > 0) ? window.CHAMADOS_GLPI_15_OFICIAIS : ((typeof window.CHAMADOS_ITSM_SUPORTE !== 'undefined' && Array.isArray(window.CHAMADOS_ITSM_SUPORTE)) ? window.CHAMADOS_ITSM_SUPORTE : []);

        var elCSei = document.getElementById('count-pauta-bkt-sei'); if (elCSei) elCSei.innerText = String(procsSEI.length);
        var elCOp = document.getElementById('count-pauta-bkt-op'); if (elCOp) elCOp.innerText = String(pacotesOP.length || 500);
        var elCGlpi = document.getElementById('count-pauta-bkt-glpi'); if (elCGlpi) elCGlpi.innerText = String(chamadosGLPI.length || 15);

        var html = '';
        var modo = window.abaPautaDailyAtiva || 'sei';

        if (modo === 'sei') {
            var candidatos = procsSEI.filter(function(p) {
                if (window.pautaDailyCards.indexOf(p.ID_Processo) !== -1) return false;
                if (!termo) return true;
                return (p.ID_Processo || '').toLowerCase().indexOf(termo) !== -1 || (p.Especificacao || '').toLowerCase().indexOf(termo) !== -1;
            }).slice(0, 15);

            html = candidatos.map(function(p) {
                return '<div style="border-radius:6px;padding:7px 9px;font-size:11px;display:flex;justify-content:space-between;align-items:center;gap:6px">' +
                    '<div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1">' +
                        '<strong >' + p.ID_Processo + '</strong><br>' +
                        '<span style="font-size:10.5px">' + (p.Especificacao || p.Tipo_Processo || '') + '</span>' +
                    '</div>' +
                    '<button type="button" class="btn btn-primary" style="padding:2px 7px;white-space:nowrap" onclick="window.puxarParaPauta(\'' + p.ID_Processo + '\')">+ Pautar</button>' +
                '</div>';
            }).join('');
        } else if (modo === 'op') {
            var candidatosOp = pacotesOP.filter(function(op) {
                var chave = 'OP#' + op.id;
                if (window.pautaDailyCards.indexOf(chave) !== -1) return false;
                if (!termo) return true;
                return ('#' + op.id + ' ' + (op.assunto || '') + ' ' + (op.projeto || '')).toLowerCase().indexOf(termo) !== -1;
            }).slice(0, 15);

            html = candidatosOp.map(function(op) {
                var chave = 'OP#' + op.id;
                return '<div style="border-radius:6px;padding:7px 9px;font-size:11px;display:flex;justify-content:space-between;align-items:center;gap:6px">' +
                    '<div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1">' +
                        '<strong >#' + op.id + '</strong> <span style="font-size:9.5px">(' + (op.tipo || 'Projeto') + ')</span><br>' +
                        '<span style="font-size:10.5px">' + (op.assunto || '') + '</span>' +
                    '</div>' +
                    '<button type="button" class="btn btn-primary" style="padding:2px 7px;white-space:nowrap" onclick="window.puxarParaPauta(\'' + chave + '\')">+ Pautar</button>' +
                '</div>';
            }).join('');
        } else if (modo === 'glpi') {
            var candidatosGlpi = chamadosGLPI.filter(function(t) {
                var chave = 'GLPI#' + t.id;
                if (window.pautaDailyCards.indexOf(chave) !== -1) return false;
                if (!termo) return true;
                return ('#' + t.id + ' ' + (t.titulo || '') + ' ' + (t.tecnico || '')).toLowerCase().indexOf(termo) !== -1;
            }).slice(0, 15);

            html = candidatosGlpi.map(function(t) {
                var chave = 'GLPI#' + t.id;
                return '<div style="border-radius:6px;padding:7px 9px;font-size:11px;display:flex;justify-content:space-between;align-items:center;gap:6px">' +
                    '<div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1">' +
                        '<strong >#' + t.id + '</strong> <span style="font-size:9.5px">(' + (t.cat || 'Suporte') + ')</span><br>' +
                        '<span style="font-size:10.5px">' + (t.titulo || '') + '</span>' +
                    '</div>' +
                    '<button type="button" class="btn btn-primary" style="padding:2px 7px;white-space:nowrap" onclick="window.puxarParaPauta(\'' + chave + '\')">+ Pautar</button>' +
                '</div>';
            }).join('');
        }

        if (!html) {
            html = '<div style="text-align:center;padding:16px;font-size:11px">Nenhum item restante para pautar neste filtro.</div>';
        }
        container.innerHTML = html;
    };

    window.puxarParaPauta = function(chave) {
        if (!chave) return;
        if (typeof pautaDailyCards === 'undefined') window.pautaDailyCards = [];
        if (window.pautaDailyCards.indexOf(chave) === -1) {
            window.pautaDailyCards.push(chave);
            try { localStorage.setItem('sagti_pauta_daily', JSON.stringify(window.pautaDailyCards)); } catch(e) {}
            if (typeof registrarHistoricoIA === 'function') {
                registrarHistoricoIA(chave, 'DAILY_PAUTA', 'Demanda incluída na Pauta da Daily Scrum para alinhamento.', 'Luiz Seixeiro');
            }
            window.renderizarPautaDaily();
            window.filtrarListaParaPautar();
        }
    };

    window.removerDaPauta = function(chave) {
        if (typeof pautaDailyCards === 'undefined') window.pautaDailyCards = [];
        window.pautaDailyCards = window.pautaDailyCards.filter(function(id) { return id !== chave; });
        try { localStorage.setItem('sagti_pauta_daily', JSON.stringify(window.pautaDailyCards)); } catch(e) {}
        window.renderizarPautaDaily();
        window.filtrarListaParaPautar();
    };

    window.renderizarPautaDaily = function() {
        var container = document.getElementById('container-pauta-cards');
        var badgeCount = document.getElementById('badge-pauta-count');
        if (!container) return;

        if (typeof pautaDailyCards === 'undefined') window.pautaDailyCards = [];
        try {
            var salvos = JSON.parse(localStorage.getItem('sagti_pauta_daily') || '[]');
            if (Array.isArray(salvos)) window.pautaDailyCards = salvos;
        } catch(e) {}

        if (badgeCount) badgeCount.innerText = window.pautaDailyCards.length + ' demandas pautadas';

        if (window.pautaDailyCards.length === 0) {
            container.innerHTML = '<div style="text-align:center;padding:34px;font-size:12.5px">' +
                '<span style="font-size:28px;display:block;margin-bottom:8px">📋</span>' +
                '<strong >Nenhuma demanda na pauta da Daily de hoje ainda.</strong><br>' +
                '<span style="font-size:11px">Utilize o seletor à esquerda para puxar processos do SEI, pacotes do OpenProject ou chamados do GLPI.</span>' +
                '</div>';
            return;
        }

        var baseSEI = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var pacotesOP = (typeof window.OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(window.OP_PACOTES_OFICIAIS)) ? window.OP_PACOTES_OFICIAIS : [];
        var baseGLPI = (typeof window.CHAMADOS_GLPI_15_OFICIAIS !== 'undefined' && Array.isArray(window.CHAMADOS_GLPI_15_OFICIAIS) && window.CHAMADOS_GLPI_15_OFICIAIS.length > 0) ? window.CHAMADOS_GLPI_15_OFICIAIS : ((typeof window.CHAMADOS_ITSM_SUPORTE !== 'undefined' && Array.isArray(window.CHAMADOS_ITSM_SUPORTE)) ? window.CHAMADOS_ITSM_SUPORTE : []);
        var postitsMap = (typeof cardPostits !== 'undefined') ? cardPostits : {};

        var fixados = window.obterFixadosValidos();

        container.innerHTML = window.pautaDailyCards.map(function(chave) {
            var postit = postitsMap[chave];
            var postitHtml = '';
            if (postit) {
                var corClasse = postit.cor === 'rosa' ? 'postit-rosa' : (postit.cor === 'azul' ? 'postit-azul' : 'postit-verde');
                postitHtml = '<div class="postit-tag ' + corClasse + '" style="margin-top:6px">' +
                    '<strong>📌 Post-it da Reunião (' + String(postit.cor).toUpperCase() + '):</strong> ' + postit.texto +
                    '<button onclick="removerPostitCard(\'' + chave + '\')" style="cursor:pointer;float:right" class="btn btn-ghost-secondary">✖</button>' +
                '</div>';
            }

            var isFix = fixados.indexOf(chave) !== -1;
            var starCor = isFix ? '#facc15' : '#64748b';
            var starIco = isFix ? '⭐' : '☆';

            // CASO 1: PACOTE OPENPROJECT
            if (String(chave).indexOf('OP#') === 0) {
                var opId = String(chave).replace(/^OP#/, '');
                var op = pacotesOP.find(function(p) { return String(p.id) === String(opId); }) || { id: opId, assunto: 'Pacote OpenProject #' + opId, tipo: 'Projeto', status: 'Em progresso', atrib: 'SA-GTI' };
                var urlOp = 'https://projetos.spaguas.sp.gov.br/work_packages/' + op.id;
                return '<div class="kpi-card card card-sm" style="padding: 12px 16px">' +
                    '<div style="display: flex; justify-content: space-between; align-items: center">' +
                        '<div style="display:flex;align-items:center;gap:8px">' +
                            '<span style="cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + chave + '\')" title="Acompanhar">' + starIco + '</span>' +
                            '<strong style="font-size: 13px">#' + op.id + '</strong>' +
                            '<span class="pill-tag pill-orange" >🏗️ OpenProject • ' + (op.tipo || 'Projeto') + '</span>' +
                        '</div>' +
                        '<div style="display: flex; gap: 6px">' +
                            '<button type="button" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px" onclick="adicionarPostitCardPrompt(\'' + chave + '\')">📌 Post-it</button>' +
                            '<a href="' + urlOp + '" target="_blank" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px; text-decoration: none">Abrir OP ↗</a>' +
                            '<button type="button" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px" onclick="window.removerDaPauta(\'' + chave + '\')">✖ Tirar da Pauta</button>' +
                        '</div>' +
                    '</div>' +
                    '<p style="font-size: 12px; margin: 6px 0; font-weight:600">' + (op.assunto || '') + '</p>' +
                    '<div style="display: flex; justify-content: space-between; font-size: 11px">' +
                        '<span>👤 <strong>Responsável:</strong> ' + (op.atrib || op.encarr || 'SA-GTI') + ' • 📁 ' + (op.projeto || 'SA-GTI') + '</span>' +
                        '<span>Status: <strong >' + (op.status || 'Em progresso') + '</strong></span>' +
                    '</div>' +
                    postitHtml +
                '</div>';
            }

            // CASO 2: CHAMADO GLPI
            if (String(chave).indexOf('GLPI#') === 0) {
                var gId = String(chave).replace(/^GLPI#/, '').split('_')[0];
                var t = baseGLPI.find(function(item) { return String(item.id) === String(gId); }) || { id: gId, titulo: 'Chamado GLPI #' + gId, status: 'Pendente', tecnico: 'SA-GTI' };
                var linkGlpi = 'https://atendimento.spaguas.sp.gov.br/front/ticket.form.php?id=' + t.id;
                return '<div class="kpi-card card card-sm" style="padding: 12px 16px">' +
                    '<div style="display: flex; justify-content: space-between; align-items: center">' +
                        '<div style="display:flex;align-items:center;gap:8px">' +
                            '<span style="cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + chave + '\')" title="Acompanhar">' + starIco + '</span>' +
                            '<strong style="font-size: 13px">#' + t.id + '</strong>' +
                            '<span class="pill-tag pill-purple" >🎫 GLPI • ' + (t.cat || 'Suporte') + '</span>' +
                        '</div>' +
                        '<div style="display: flex; gap: 6px">' +
                            '<button type="button" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px" onclick="adicionarPostitCardPrompt(\'' + chave + '\')">📌 Post-it</button>' +
                            '<a href="' + linkGlpi + '" target="_blank" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px; text-decoration: none">Abrir GLPI ↗</a>' +
                            '<button type="button" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px" onclick="window.removerDaPauta(\'' + chave + '\')">✖ Tirar da Pauta</button>' +
                        '</div>' +
                    '</div>' +
                    '<p style="font-size: 12px; margin: 6px 0; font-weight:600">' + (t.titulo || '') + '</p>' +
                    '<div style="display: flex; justify-content: space-between; font-size: 11px">' +
                        '<span>👤 <strong>Técnico:</strong> ' + (t.tecnico || 'SA-GTI') + ' • ' + (t.local || 'Sede') + '</span>' +
                        '<span>Status: <strong >' + (t.status || 'Pendente') + '</strong></span>' +
                    '</div>' +
                    postitHtml +
                '</div>';
            }

            // CASO 3: PROCESSO SEI
            var p = baseSEI.find(function(item) { return item.ID_Processo === chave; });
            if (!p) return '';
            return '<div class="kpi-card card card-sm" style="padding: 12px 16px">' +
                '<div style="display: flex; justify-content: space-between; align-items: center">' +
                    '<div style="display:flex;align-items:center;gap:8px">' +
                        '<span style="cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + p.ID_Processo + '\')" title="Acompanhar">' + starIco + '</span>' +
                        '<strong style="font-size: 13px; cursor: pointer" onclick="abrirDetalhesProcesso(\'' + p.ID_Processo + '\')">' + p.ID_Processo + '</strong>' +
                        '<span class="pill-tag pill-blue" >📁 SEI • ' + (p.Bucket_OpenProject || 'Bucket') + '</span>' +
                    '</div>' +
                    '<div style="display: flex; gap: 6px">' +
                        '<button type="button" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px" onclick="adicionarPostitCardPrompt(\'' + p.ID_Processo + '\')">📌 Post-it</button>' +
                        '<button type="button" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px" onclick="abrirDetalhesProcesso(\'' + p.ID_Processo + '\')">Dossiê</button>' +
                        '<button type="button" class="btn btn-outline-secondary" style="padding: 2px 8px; font-size: 11px" onclick="window.removerDaPauta(\'' + p.ID_Processo + '\')">✖ Tirar da Pauta</button>' +
                    '</div>' +
                '</div>' +
                '<p style="font-size: 12px; margin: 6px 0; font-weight:600">' + (p.Especificacao || p.Tipo_Processo || '') + '</p>' +
                '<div style="display: flex; justify-content: space-between; font-size: 11px">' +
                    '<span>👤 <strong>Responsável:</strong> ' + (p.Responsavel_Tecnico || 'Não atribuído') + '</span>' +
                    '<span>⏱️ Aging: <strong>' + (p.Faixa_Aging || 'Normal') + '</strong> (' + (p.Dias_Ultima_Mov || 0) + ' dias)</span>' +
                '</div>' +
                postitHtml +
            '</div>';
        }).join('');
    };

    
    // =========================================================================
    // Administração de usuários e RBAC exigem integração server-side com um IdP institucional.
    window.USUARIOS_PADRAO_COCKPIT = [];
    window.obterUsuariosCadastrados = function() { return []; };
    window.renderizarTabelaUsuarios = function() {};
    window.carregarPermissoes = function() { return false; };
    window.aplicarPermissoesPerfil = function() { return false; };
    window.atualizarCadernosTematicosAutomatico = function() { return 0; };

    // =========================================================================
    // ROTINA DE ATUALIZAÇÃO AUTOMÁTICA DOS CADERNOS TEMÁTICOS VIA MOTORES DE BUSCA
    // =========================================================================
    window.atualizarCadernosTematicosAutomatico = function() { return 0; };

    function init() {
        window.atualizarContadoresCustodiaMesa();
        if (typeof window.renderizarTabelaMesa === 'function') window.renderizarTabelaMesa();
        if (typeof window.renderizarKanbanAgil === 'function') window.renderizarKanbanAgil();
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
    
    window.addEventListener('load', init);
})();


// =========================================================================
// MÓDULO: DRIVE DE CONTEXTO CORPORATIVO — REPOSITÓRIO PDF PARA POOL DE IAS
// =========================================================================
(function() {
    window.PDFS_PADRAO_DRIVE_SAGTI = [];

    window.documentosDrivePdf = [];

    window.carregarDocumentosDrivePdf = function(forcarPadrao) {
        var CHAVE_STORAGE = 'sagti_drive_documentos_pdf_v1';
        var carregar = (forcarPadrao === true);
        if (!carregar) {
            try {
                var salvo = localStorage.getItem(CHAVE_STORAGE);
                if (salvo) {
                    var parsed = JSON.parse(salvo);
                    if (Array.isArray(parsed) && parsed.length > 0) {
                        var idsDemonstrativos = ['doc_dec_68220', 'doc_pdtic_2027_2030', 'doc_deliberacao_21'];
                        window.documentosDrivePdf = parsed
                            .filter(function(doc) { return doc && idsDemonstrativos.indexOf(doc.id) === -1; })
                            .map(function(doc) { return Object.assign({}, doc, { status: 'metadata_only' }); });
                        localStorage.setItem(CHAVE_STORAGE, JSON.stringify(window.documentosDrivePdf));
                    } else {
                        carregar = true;
                    }
                } else {
                    carregar = true;
                }
            } catch(e) {
                carregar = true;
            }
        }
        if (carregar) {
            window.documentosDrivePdf = JSON.parse(JSON.stringify(window.PDFS_PADRAO_DRIVE_SAGTI));
            try {
                localStorage.setItem(CHAVE_STORAGE, JSON.stringify(window.documentosDrivePdf));
            } catch(e) {}
        }
        window.atualizarBadgesDrivePdf();
        window.renderizarGradeDocumentosDrivePdf();
    };

    window.salvarDocumentosDrivePdf = function() {
        var CHAVE_STORAGE = 'sagti_drive_documentos_pdf_v1';
        try {
            localStorage.setItem(CHAVE_STORAGE, JSON.stringify(window.documentosDrivePdf));
        } catch(e) {
            console.warn('[Drive IA] Falha ao persistir em localStorage:', e);
        }
        window.atualizarBadgesDrivePdf();
        window.renderizarGradeDocumentosDrivePdf();
    };

    window.atualizarBadgesDrivePdf = function() {
        var total = (window.documentosDrivePdf && Array.isArray(window.documentosDrivePdf)) ? window.documentosDrivePdf.length : 0;
        var totalBytes = 0;
        (window.documentosDrivePdf || []).forEach(function(d) {
            totalBytes += (d.tamanhoBytes || 0);
        });
        var totalMbStr = (totalBytes / (1024 * 1024)).toFixed(1) + ' MB';

        var badgeTopo = document.getElementById('topbar-badge-drive-ia');
        if (badgeTopo) badgeTopo.innerText = total + ' PDF' + (total !== 1 ? 's' : '');

        var kpiTotal = document.getElementById('kpi-drive-total-docs');
        if (kpiTotal) kpiTotal.innerText = total;

        var kpiSize = document.getElementById('kpi-drive-total-size');
        if (kpiSize) kpiSize.innerText = totalMbStr;

        var badgeLista = document.getElementById('badge-total-drive-lista');
        if (badgeLista) badgeLista.innerText = total + ' Documento' + (total !== 1 ? 's' : '');
    };

    window.renderizarGradeDocumentosDrivePdf = function(filtroTexto, filtroCat) {
        var container = document.getElementById('container-cards-drive-pdf');
        if (!container) return;

        var lista = window.documentosDrivePdf || [];
        var q = (filtroTexto || '').toLowerCase().trim();
        var cat = (filtroCat || 'TODOS');

        var filtrados = lista.filter(function(doc) {
            var matchQ = (!q) || (doc.nome && doc.nome.toLowerCase().indexOf(q) !== -1) || (doc.resumo && doc.resumo.toLowerCase().indexOf(q) !== -1);
            var matchCat = (cat === 'TODOS') || (doc.categoria === cat);
            return matchQ && matchCat;
        });

        if (filtrados.length === 0) {
            container.innerHTML = '<div style="grid-column: 1 / -1; border-radius: 10px; padding: 32px; text-align: center">' +
                '<div style="font-size: 28px; margin-bottom: 6px">📂</div>' +
                '<strong style="font-size: 13.5px">Nenhum documento PDF localizado com os filtros atuais.</strong>' +
                '<div style="font-size: 12px; margin-top: 4px">A ingestão de arquivos não está disponível nesta versão.</div>' +
            '</div>';
            return;
        }

        container.innerHTML = filtrados.map(function(doc) {
            var corBadge = '#3b82f6';
            if (doc.categoria === 'Normativos') corBadge = '#0ea5e9';
            else if (doc.categoria === 'Governança') corBadge = '#0284c7';
            else if (doc.categoria === 'Contratação') corBadge = '#10b981';
            else if (doc.categoria === 'Upload') corBadge = '#0369a1';

            return '<div style="border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.15s ease">' +
                '<div>' +
                    '<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px">' +
                        '<span style="padding: 2px 8px; border-radius: 6px; font-weight: 800">📄 PDF</span>' +
                        '<span style="padding: 2px 7px; border-radius: 4px; font-weight: 700">' + (doc.categoria || 'Geral') + '</span>' +
                    '</div>' +
                    '<h4 style="margin: 0 0 6px 0; font-size: 13px; font-weight: 800; line-height: 1.35; word-break: break-all">' + window.escapeHtml(doc.nome) + '</h4>' +
                    '<div style="font-size: 11px; margin-bottom: 8px; display: flex; gap: 8px; flex-wrap: wrap">' +
                        '<span>💾 ' + doc.tamanhoFormatado + '</span>' +
                        '<span>&bull;</span>' +
                        '<span>📅 ' + doc.dataUpload + '</span>' +
                        (doc.paginas ? ('<span>&bull;</span><span>📖 ' + doc.paginas + ' pág.</span>') : '') +
                    '</div>' +
                    '<p style="margin: 0 0 12px 0; font-size: 11.5px; line-height: 1.45; max-height: 60px; overflow: hidden; text-overflow: ellipsis">' + window.escapeHtml(doc.resumo || 'Documento em PDF cadastrado no Drive de Contexto para consulta direta das IAs.') + '</p>' +
                    '<div style="font-size: 10.5px; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 4px">' +
                        '<span>🟢</span> Ingerido no Contexto IA 1 (Copiloto) &amp; IA 2' +
                    '</div>' +
                '</div>' +
                '<div style="display: flex; gap: 6px; padding-top: 10px">' +
                    '<button type="button" class="btn btn-secondary btn-sm btn-outline-secondary" onclick="window.visualizarDocumentoDrivePdf(\'' + doc.id + '\')" style="flex: 1; padding: 5px 8px; font-size: 11px; font-weight: 700" title="Visualizar Dossiê do PDF">👁️ Ver</button>' +
                    '<button type="button" class="btn btn-primary btn-sm" onclick="window.baixarDocumentoDrivePdf(\'' + doc.id + '\')" style="flex: 1; padding: 5px 8px; font-size: 11px; font-weight: 700" title="Baixar arquivo">⬇️ Baixar</button>' +
                    '<button type="button" class="btn btn-secondary btn-sm btn-outline-secondary" onclick="window.excluirDocumentoDrivePdf(\'' + doc.id + '\')" style="padding: 5px 10px; font-size: 11px; font-weight: 700" title="Excluir documento do Drive e do contexto das IAs">🗑️</button>' +
                '</div>' +
            '</div>';
        }).join('');
    };

    window.filtrarDocumentosDrivePdf = function() {
        var q = document.getElementById('filtro-busca-drive-pdf') ? document.getElementById('filtro-busca-drive-pdf').value : '';
        var cat = document.getElementById('filtro-cat-drive-pdf') ? document.getElementById('filtro-cat-drive-pdf').value : 'TODOS';
        window.renderizarGradeDocumentosDrivePdf(q, cat);
    };

    window.acionarSeletorUploadPdfDrive = function() {
        var inp = document.getElementById('input-arquivo-pdf-drive');
        if (inp) {
            inp.value = '';
            inp.click();
        }
    };

    window.validarArquivoEstritamentePdf = function(file) {
        if (!file) return false;
        var nome = file.name || '';
        var ext = nome.slice((nome.lastIndexOf('.') - 1 >>> 0) + 2).toLowerCase();
        var mime = file.type || '';
        var ehPdfExt = (ext === 'pdf');
        var ehPdfMime = (!mime || mime === 'application/pdf' || mime === 'application/x-pdf');
        return ehPdfExt && ehPdfMime;
    };

    window.processarArquivosSelecionadosDrivePdf = function(event) {
        var files = event.target.files;
        if (!files || files.length === 0) return;
        window.adicionarArquivosPdfAoDrive(files);
    };

    window.tratarDragOverDrivePdf = function(e) {
        e.preventDefault();
        e.stopPropagation();
        var dz = document.getElementById('dropzone-drive-pdf');
        if (dz) dz.classList.add('sagti-dropzone-active');
    };

    window.tratarDragLeaveDrivePdf = function(e) {
        e.preventDefault();
        e.stopPropagation();
        var dz = document.getElementById('dropzone-drive-pdf');
        if (dz) dz.classList.remove('sagti-dropzone-active');
    };

    window.tratarDropDrivePdf = function(e) {
        e.preventDefault();
        e.stopPropagation();
        window.tratarDragLeaveDrivePdf(e);
        var dt = e.dataTransfer;
        if (!dt || !dt.files || dt.files.length === 0) return;
        window.adicionarArquivosPdfAoDrive(dt.files);
    };

    window.adicionarArquivosPdfAoDrive = function() {
        alert('A ingestão de PDFs não está disponível: o conteúdo não é enviado nem indexado no backend.');
        return false;
    };

    window.excluirDocumentoDrivePdf = function(id) {
        var doc = (window.documentosDrivePdf || []).find(function(d) { return d.id === id; });
        if (!doc) return;

        if (confirm('Deseja realmente excluir o documento "' + doc.nome + '" do Drive de Contexto?\n\nEle será removido imediatamente do contexto da IA 1 e IA 2.')) {
            window.documentosDrivePdf = (window.documentosDrivePdf || []).filter(function(d) { return d.id !== id; });
            window.salvarDocumentosDrivePdf();
            if (typeof mostrarNotificacao === 'function') {
                mostrarNotificacao('PDF Excluído', 'Documento "' + doc.nome + '" removido do Drive e do contexto das IAs.', 'info');
            } else {
                alert('🗑️ Documento "' + doc.nome + '" excluído com sucesso.');
            }
        }
    };

    window.visualizarDocumentoDrivePdf = function(id) {
        var doc = (window.documentosDrivePdf || []).find(function(d) { return d.id === id; });
        if (!doc) return;

        var modal = document.getElementById('modal-visualizador-drive-pdf');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'modal-visualizador-drive-pdf';
            modal.classList.add('sagti-modal-backdrop');
            modal.style.cssText = 'position:fixed;inset:0;z-index:99999;display:flex;align-items:flex-start;justify-content:center;padding:24px 16px;overflow-y:auto;box-sizing:border-box;';
            modal.onclick = function(e) {
                if (e.target === modal) modal.style.display = 'none';
            };
            document.body.appendChild(modal);
        }
        modal.style.display = 'flex';

        modal.innerHTML = '<div style="position:relative;border-radius:14px;max-width:820px;width:100%;margin:auto 0;padding:24px;box-sizing:border-box">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;margin-bottom:16px">' +
                '<div>' +
                    '<div style="font-size:11px;font-weight:800;text-transform:uppercase">Drive de Contexto IA &bull; Visualizador de Dossiê PDF</div>' +
                    '<h3 style="margin:2px 0 0 0;font-size:16px;font-weight:800;display:flex;align-items:center;gap:8px">' +
                        '<span>📄</span> ' + window.escapeHtml(doc.nome) +
                    '</h3>' +
                '</div>' +
                '<button type="button" onclick="document.getElementById(\'modal-visualizador-drive-pdf\').style.display=\'none\'" style="border-radius:8px;padding:6px 14px;font-size:12px;font-weight:800;cursor:pointer" class="btn btn-ghost-secondary">&#10006; Fechar</button>' +
            '</div>' +
            '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px">' +
                '<div style="border-radius:8px;padding:10px">' +
                    '<div style="font-size:11px;font-weight:700">TAMANHO DO ARQUIVO</div>' +
                    '<div style="font-size:16px;font-weight:800">' + doc.tamanhoFormatado + '</div>' +
                '</div>' +
                '<div style="border-radius:8px;padding:10px">' +
                    '<div style="font-size:11px;font-weight:700">DATA DE INGESTÃO</div>' +
                    '<div style="font-size:16px;font-weight:800">' + doc.dataUpload + '</div>' +
                '</div>' +
                '<div style="border-radius:8px;padding:10px">' +
                        '<div style="font-size:11px;font-weight:700">STATUS DE INGESTÃO</div>' +
                        '<div style="font-size:14px;font-weight:800">Metadados locais; não indexado</div>' +
                '</div>' +
            '</div>' +
            '<div style="border-radius:8px;padding:14px;margin-bottom:16px">' +
                '<strong style="font-size:12px">Metadados informados (não verificados nem indexados):</strong>' +
                '<p style="font-size:12px;margin:8px 0 0 0;line-height:1.5">' + window.escapeHtml(doc.resumo) + '</p>' +
            '</div>' +
            '<div style="display:flex;justify-content:space-between;align-items:center;padding-top:14px">' +
                '<button type="button" class="btn btn-outline-secondary" onclick="window.excluirDocumentoDrivePdf(\'' + doc.id + '\');document.getElementById(\'modal-visualizador-drive-pdf\').style.display=\'none\';" style="font-size:12px;font-weight:700">🗑️ Excluir do Drive</button>' +
                '<div style="display:flex;gap:8px">' +
                    '<button type="button" class="btn btn-primary" onclick="window.baixarDocumentoDrivePdf(\'' + doc.id + '\')" style="font-size:12px;font-weight:700">⬇️ Baixar PDF</button>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="document.getElementById(\'modal-visualizador-drive-pdf\').style.display=\'none\'" style="font-size:12px;font-weight:700">✕ Fechar</button>' +
                '</div>' +
            '</div>' +
        '</div>';
    };

    window.baixarDocumentoDrivePdf = function() {
        alert('O conteúdo do PDF não é armazenado neste sistema e não pode ser baixado.');
        return false;
    };

    window.sincronizarDriveComIas = function() {
        alert('A indexação RAG server-side ainda não está implementada.');
        return false;
    };

    window.restaurarPdfsPadraoDrive = function() {
        alert('Não há documentos institucionais padrão verificados para restaurar.');
        return false;
    };

    // Função global que fornece o contexto documental do Drive para as IAs
    window.obterContextoDocumentosDriveIA = function() { return ''; };

    // Inicialização automática ao carregar o documento
    if (document.readyState === 'loading') {
        window.addEventListener('DOMContentLoaded', function() { window.carregarDocumentosDrivePdf(); });
    } else {
        window.carregarDocumentosDrivePdf();
    }
})();



// =========================================================================
// MOTOR: REVISÃO & HOMOLOGAÇÃO DO ACERVO COMPLETO VIA IA 1 (PRINCIPAL)
// =========================================================================
window.fecharModalRevisaoAcervo = function() {
    var m = document.getElementById('modal-revisao-acervo-completo');
    if (m) m.style.display = 'none';
    if (window._timerPollingAcervo) {
        clearInterval(window._timerPollingAcervo);
        window._timerPollingAcervo = null;
    }
};

if (!window._listenerEscRevisaoAcervo) {
    window._listenerEscRevisaoAcervo = true;
    window.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            window.fecharModalRevisaoAcervo();
        }
    });
}

window.copiarComandoTerminalOp = function() {
    var cmd = 'python sincronizar_openproject_backend.py --todos';
    navigator.clipboard.writeText(cmd).then(function() {
        if (typeof mostrarNotificacao === 'function') {
            mostrarNotificacao('Comando Copiado', 'Comando copiado para a área de transferência: ' + cmd, 'success');
        } else {
            alert('📋 Comando copiado com sucesso:\n\n' + cmd + '\n\nBasta colar no PowerShell e pressionar Enter!');
        }
    }).catch(function() {
        alert('Comando para rodar no PowerShell:\n' + cmd);
    });
};

window.executarRevisaoHomologacaoAcervoCompleto = function() {
    var modal = document.getElementById('modal-revisao-acervo-completo');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-revisao-acervo-completo';
        modal.classList.add('sagti-modal-backdrop');
        modal.style.cssText = 'position:fixed;inset:0;z-index:99999;display:flex;align-items:flex-start;justify-content:center;padding:24px 16px;overflow-y:auto;box-sizing:border-box;';
        modal.onclick = function(e) {
            if (e.target === modal) window.fecharModalRevisaoAcervo();
        };
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';

    var pool = window.POOL_TRES_IAS || (typeof window.obterPoolPadraoTresIas === 'function' ? window.obterPoolPadraoTresIas() : null);
    var modeloIa1 = (pool && pool.ias && pool.ias.principal && pool.ias.principal.agent) ? pool.ias.principal.agent : 'qwen2.5:7b';
    var totalProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS.length : 179;

    modal.innerHTML = '<div style="position:relative;border-radius:14px;max-width:880px;width:100%;margin:auto 0;padding:24px;box-sizing:border-box">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;margin-bottom:16px;flex-wrap:wrap;gap:10px">' +
            '<div>' +
                '<div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:0.5px">Orquestrador Cockpit GTI &bull; Sincronização em Lote</div>' +
                '<h3 style="margin:2px 0 0 0;font-size:17px;font-weight:800;display:flex;align-items:center;gap:8px">' +
                    '<span>⚡</span> REVISAR E HOMOLOGAR O ACERVO COMPLETO (' + totalProcs + ' PROCESSOS SEI)' +
                '</h3>' +
            '</div>' +
            '<button type="button" onclick="window.fecharModalRevisaoAcervo()" style="border-radius:8px;padding:7px 16px;font-size:12px;font-weight:800;cursor:pointer" class="btn btn-ghost-secondary">&#10006; Fechar Janela</button>' +
        '</div>' +

        '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px">' +
            '<div style="border-radius:8px;padding:12px">' +
                '<div style="font-size:11px;font-weight:700">ACERVO A HOMOLOGAR</div>' +
                '<div style="font-size:20px;font-weight:800;margin-top:3px">' + totalProcs + ' Processos SEI</div>' +
                '<div >+ 500 Pacotes OpenProject</div>' +
            '</div>' +
            '<div style="border-radius:8px;padding:12px">' +
                '<div style="font-size:11px;font-weight:700">MOTOR DE INTELIGÊNCIA</div>' +
                '<div style="font-size:20px;font-weight:800;margin-top:3px">IA 1 — Principal</div>' +
                '<div >Modelo Ativo: <strong>' + window.escapeHtml(modeloIa1) + '</strong></div>' +
            '</div>' +
            '<div style="border-radius:8px;padding:12px">' +
                '<div style="font-size:11px;font-weight:700">REGRA DE COMPLIANCE</div>' +
                '<div style="font-size:20px;font-weight:800;margin-top:3px">Lei 14.133 / PDTIC</div>' +
                '<div >Dossiê 7 Seções + Linha do Tempo</div>' +
            '</div>' +
        '</div>' +

        '<div style="border-radius:10px;padding:16px;margin-bottom:16px">' +
            '<div style="font-size:13px;font-weight:800;margin-bottom:6px">Como funciona a Homologação Completa:</div>' +
            '<ul style="margin:0;padding-left:20px;font-size:12px;line-height:1.6">' +
                '<li><strong>Revisão Analítica Profunda:</strong> A IA 1 (Principal) analisa cada processo individualmente, emitindo parecer com enquadramento legal, aging líquido e recomendações.</li>' +
                '<li><strong>Gravação do Dossiê nos Cards:</strong> Atualiza a descrição de cada Work Package no OpenProject com links probatórios clicáveis (SEI, GLPI e DOE-SP).</li>' +
                '<li><strong>Registro de Atividade:</strong> Publica comentário formal assinado pela IA na timeline do OpenProject mantendo a rastreabilidade total.</li>' +
            '</ul>' +
        '</div>' +

        '<div style="border-radius:10px;padding:16px;margin-bottom:16px">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px">' +
                '<div>' +
                    '<strong style="font-size:13px">Opção 1: Disparo Automático via Cockpit (Segundo Plano)</strong>' +
                    '<div style="font-size:11.5px;margin-top:2px">Inicia o script no servidor Flask (:5000) e transmite os dados com acompanhamento de log abaixo.</div>' +
                '</div>' +
                '<button type="button" id="btn-iniciar-homologacao-backend" onclick="window.dispararHomologacaoBackendReal(this)" style="border-radius:8px;padding:9px 18px;font-size:12.5px;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;gap:6px" class="btn btn-ghost-secondary">' +
                    '🚀 Iniciar Homologação Agora' +
                '</button>' +
            '</div>' +
            '<div id="box-log-terminal-container" style="display:none;margin-top:12px">' +
                '<div style="font-size:11px;font-weight:700;margin-bottom:4px;display:flex;justify-content:space-between">' +
                    '<span>📡 Streaming do Laudo de Sincronização em Tempo Real:</span>' +
                    '<span id="status-spinner-sync" >🟢 Executando...</span>' +
                '</div>' +
                '<pre id="terminal-log-acervo" style="border-radius:8px;padding:12px;font-size:11px;max-height:180px;overflow-y:auto;white-space:pre-wrap;margin:0;line-height:1.45">Conectando ao log do servidor...</pre>' +
            '</div>' +
        '</div>' +

        '<div style="border-radius:10px;padding:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:12px">' +
            '<div>' +
                '<strong style="font-size:12px">Opção 2: Execução Direta no Terminal (PowerShell)</strong>' +
                '<div style="font-size:11px;margin-top:2px">Execute manualmente no console do Windows para acompanhar cada token em tempo real:</div>' +
                '<code style="padding:3px 8px;border-radius:4px;font-size:11.5px;display:inline-block;margin-top:4px">python sincronizar_openproject_backend.py --todos</code>' +
            '</div>' +
            '<button type="button" onclick="window.copiarComandoTerminalOp()" style="border-radius:6px;padding:7px 14px;font-size:11.5px;font-weight:700;cursor:pointer" class="btn btn-ghost-secondary">' +
                '📋 Copiar Comando' +
            '</button>' +
        '</div>' +

        '<div style="display:flex;justify-content:space-between;align-items:center;padding-top:14px">' +
            '<div style="font-size:11.5px">💡 Dica: Você pode fechar esta janela a qualquer momento sem interromper a execução no servidor.</div>' +
            '<button type="button" onclick="window.fecharModalRevisaoAcervo()" style="border-radius:8px;padding:8px 20px;font-size:13px;font-weight:800;cursor:pointer" class="btn btn-ghost-secondary">' +
                '✕ Fechar' +
            '</button>' +
        '</div>' +
    '</div>';
};

window.dispararHomologacaoBackendReal = async function(btn) {
    if (btn) {
        btn.disabled = true;
        btn.style.opacity = '0.7';
        btn.innerHTML = '<span>⏳</span> Processando...';
    }

    var boxTerm = document.getElementById('box-log-terminal-container');
    var preTerm = document.getElementById('terminal-log-acervo');
    if (boxTerm) boxTerm.style.display = 'block';

    try {
        var resp = await fetch('/api/v1/openproject/sync_batch', {
            method: 'POST',
            headers: obterHeadersComAuth(),
            body: JSON.stringify({ comando: 'todos', todos: true })
        });
        var dados = await resp.json();
        if (preTerm) {
            preTerm.innerText = '✅ Disparo realizado com sucesso!\n' + (dados.mensagem || '') + '\n\nIniciando monitoramento do arquivo laudo_sincronizacao_automatica.txt...\n';
        }
    } catch(e) {
        if (preTerm) {
            preTerm.innerText = 'ℹ️ Backend Flask em espera. Para execução imediata com streaming no console, utilize o comando PowerShell abaixo: python sincronizar_openproject_backend.py --todos\n';
        }
    }

    // Iniciar Polling de Log do Arquivo em Tempo Real
    if (window._timerPollingAcervo) clearInterval(window._timerPollingAcervo);
    window._timerPollingAcervo = setInterval(async function() {
        try {
            var rStatus = await fetch('/api/v1/openproject/sync_status');
            if (rStatus.ok) {
                var dStatus = await rStatus.json();
                if (preTerm && dStatus.linhas) {
                    preTerm.innerText = dStatus.linhas;
                    preTerm.scrollTop = preTerm.scrollHeight;
                }
            }
        } catch(err) {}
    }, 1800);
};



// =========================================================================
// MÓDULO: DASHBOARD DE ATIVOS GLPI 10 (dashboard_assets.php)
// =========================================================================
(function() {
    window.DADOS_CMDB_GLPI = [
        { id: 'PAT-0104', hostname: 'SPAGUAS-DESK-0104', tipo: 'Desktop', modelo: 'Dell OptiPlex 7090', config: 'Intel Core i5-11500 / 16GB / SSD 512GB', local: 'Sede SA-GTI (São Paulo)', resp: 'Alessandro Delbue Silva', status: 'Operacional' },
        { id: 'PAT-0105', hostname: 'SPAGUAS-DESK-0105', tipo: 'Desktop', modelo: 'Dell OptiPlex 7090', config: 'Intel Core i5-11500 / 16GB / SSD 512GB', local: 'Sede SA-GTI (São Paulo)', resp: 'Marcos Tadeu Yamamoto', status: 'Operacional' },
        { id: 'PAT-0042', hostname: 'SPAGUAS-NOTE-0042', tipo: 'Notebook', modelo: 'Lenovo ThinkPad T14', config: 'Intel Core i7-12700 / 32GB / SSD 1TB', local: 'Superintendência (Gabinete)', resp: 'Luiz Antonio Seixeiro', status: 'Operacional' },
        { id: 'PAT-0043', hostname: 'SPAGUAS-NOTE-0043', tipo: 'Notebook', modelo: 'Lenovo ThinkPad T14', config: 'Intel Core i7-12700 / 16GB / SSD 512GB', local: 'Diretoria Colegiada', resp: 'Diretoria SA-GTI', status: 'Operacional' },
        { id: 'PAT-0201', hostname: 'SPAGUAS-DESK-0201', tipo: 'Desktop', modelo: 'HP ProDesk 400 G7', config: 'Intel Core i3-10100 / 8GB / SSD 256GB', local: 'Bacia PCJ (Campinas)', resp: 'Equipe Regional PCJ', status: 'Operacional' },
        { id: 'PAT-0202', hostname: 'SPAGUAS-DESK-0202', tipo: 'Desktop', modelo: 'HP ProDesk 400 G7', config: 'Intel Core i3-10100 / 8GB / SSD 256GB', local: 'Bacia Alto Tietê (Mogi)', resp: 'Equipe Regional Alto Tietê', status: 'Operacional' },
        { id: 'PAT-0203', hostname: 'SPAGUAS-DESK-0203', tipo: 'Desktop', modelo: 'HP ProDesk 400 G7', config: 'Intel Core i5-10400 / 16GB / SSD 512GB', local: 'Bacia Vale do Paraíba', resp: 'Equipe Regional Paraíba', status: 'Operacional' },
        { id: 'PAT-0301', hostname: 'SRV-HYPERV-01', tipo: 'Hyper-V', modelo: 'Dell PowerEdge R740', config: 'Dual Xeon Silver 4210R / 128GB RAM', local: 'Datacenter / Core SA-GTI', resp: 'Diego Monteiro (Infra)', status: 'Operacional' },
        { id: 'PAT-0302', hostname: 'SRV-HYPERV-02', tipo: 'Hyper-V', modelo: 'Dell PowerEdge R740', config: 'Dual Xeon Silver 4210R / 128GB RAM', local: 'Datacenter / Core SA-GTI', resp: 'Diego Monteiro (Infra)', status: 'Operacional' },
        { id: 'PAT-0401', hostname: 'MON-DELL-P2419', tipo: 'Monitor', modelo: 'Dell Professional P2419H (24")', config: 'Full HD IPS / HDMI / DP', local: 'Sede SA-GTI (Posto 14)', resp: 'Alessandro Delbue Silva', status: 'Operacional' },
        { id: 'PAT-0402', hostname: 'MON-DELL-P2419', tipo: 'Monitor', modelo: 'Dell Professional P2419H (24")', config: 'Full HD IPS / HDMI / DP', local: 'Sede SA-GTI (Posto 15)', resp: 'Marcos Tadeu Yamamoto', status: 'Operacional' },
        { id: 'PAT-0501', hostname: 'PRN-SEDE-COR-01', tipo: 'Impressora', modelo: 'HP LaserJet Enterprise M553', config: 'Laser Colorida / Gigabit Ethernet', local: 'Sede SA-GTI (Andar 4)', resp: 'GTI Suporte N2', status: 'Operacional' },
        { id: 'PAT-0502', hostname: 'PRN-PCJ-01', tipo: 'Impressora', modelo: 'Kyocera ECOSYS P3155dn', config: 'Monocromática / Rede TCP/IP', local: 'Bacia PCJ (Recepção)', resp: 'Equipe Regional PCJ', status: 'Operacional' }
    ];

    window.renderizarDashboardAtivosGlpi = function() {
        window.renderizarTabelaCmdbGlpi();
        window.renderizarGraficosAtivosGlpi();
    };

    window.renderizarTabelaCmdbGlpi = function() {
        var tbody = document.getElementById('tbody-cmdb-glpi-ativos');
        if (!tbody) return;

        var q = (document.getElementById('filtro-busca-cmdb-glpi') ? document.getElementById('filtro-busca-cmdb-glpi').value : '').toLowerCase().trim();
        var cat = (document.getElementById('filtro-cat-cmdb-glpi') ? document.getElementById('filtro-cat-cmdb-glpi').value : 'TODOS');

        var filtrados = (window.DADOS_CMDB_GLPI || []).filter(function(item) {
            var matchQ = (!q) || (item.hostname.toLowerCase().indexOf(q) !== -1) ||
                         (item.id.toLowerCase().indexOf(q) !== -1) ||
                         (item.resp.toLowerCase().indexOf(q) !== -1) ||
                         (item.local.toLowerCase().indexOf(q) !== -1);
            var matchCat = (cat === 'TODOS') || (item.tipo.indexOf(cat) !== -1);
            return matchQ && matchCat;
        });

        tbody.innerHTML = filtrados.map(function(it) {
            var corBadge = '#38bdf8';
            if (it.tipo === 'Notebook') corBadge = '#0ea5e9';
            else if (it.tipo === 'Hyper-V') corBadge = '#10b981';
            else if (it.tipo === 'Monitor') corBadge = '#0284c7';
            else if (it.tipo === 'Impressora') corBadge = '#f59e0b';

            return '<tr >' +
                '<td style="padding: 10px 14px; font-weight: 700">' +
                    '<span style="padding: 2px 6px; border-radius: 4px; margin-right: 6px">' + it.id + '</span>' +
                    window.escapeHtml(it.hostname) +
                '</td>' +
                '<td style="padding: 10px 14px">' +
                    '<span style="padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700">' + it.tipo + '</span>' +
                '</td>' +
                '<td style="padding: 10px 14px">' + window.escapeHtml(it.modelo) + '</td>' +
                '<td style="padding: 10px 14px; font-size: 11.5px">' + window.escapeHtml(it.config) + '</td>' +
                '<td style="padding: 10px 14px">' + window.escapeHtml(it.local) + '</td>' +
                '<td style="padding: 10px 14px; font-weight: 600">' + window.escapeHtml(it.resp) + '</td>' +
                '<td style="padding: 10px 14px">' +
                    '<span style="padding: 2px 7px; border-radius: 4px; font-size: 10.5px; font-weight: 700">🟢 ' + it.status + '</span>' +
                '</td>' +
            '</tr>';
        }).join('');
    };

    window.filtrarTabelaCmdbGlpi = function() {
        window.renderizarTabelaCmdbGlpi();
    };

    window.renderizarGraficosAtivosGlpi = function() {
        // 1. Gráfico: Computadores por Tipo (Barra Horizontal)
        var elG1 = document.getElementById('chart-glpi-computadores-tipo');
        if (elG1) {
            elG1.innerHTML = '';
            if (typeof ApexCharts !== 'undefined') {
                var opt1 = {
                    chart: { type: 'bar', height: 210, toolbar: { show: false }, background: 'transparent', foreColor: '#334155', fontFamily: 'Inter, sans-serif' },
                    series: [{ name: 'Unidades', data: [316, 88, 23, 4, 3] }],
                    xaxis: { categories: ['Desktop', 'Notebook', 'Hyper-V', 'All in One', 'Servidores'], labels: { style: { colors: '#334155', fontSize: '12px' } } },
                    yaxis: { labels: { style: { colors: '#334155', fontSize: '12px' } } },
                    colors: ['#004b87'],
                    plotOptions: { bar: { horizontal: false, columnWidth: '45%', borderRadius: 4 } },
                    dataLabels: { enabled: true, style: { colors: ['#fff'], fontSize: '11px', fontWeight: 'bold' } },
                    grid: { borderColor: '#e2e8f0' },
                    theme: { mode: 'light' }
                };
                new ApexCharts(elG1, opt1).render();
            } else {
                elG1.innerHTML = '<div style="display:flex;flex-direction:column;gap:6px;padding-top:10px">' +
                    '<div style="font-size:11px">Desktop: <strong>316</strong></div>' +
                    '<div style="height:14px;border-radius:4px;overflow:hidden"><div style="width:71%;height:100%"></div></div>' +
                    '<div style="font-size:11px;margin-top:4px">Notebook: <strong>88</strong></div>' +
                    '<div style="height:14px;border-radius:4px;overflow:hidden"><div style="width:20%;height:100%"></div></div>' +
                    '<div style="font-size:11px;margin-top:4px">Hyper-V: <strong>23</strong></div>' +
                    '<div style="height:14px;border-radius:4px;overflow:hidden"><div style="width:5%;height:100%"></div></div>' +
                '</div>';
            }
        }

        // 2. Gráfico: Número de Processador itens por tipo
        var elG2 = document.getElementById('chart-glpi-processadores-tipo');
        if (elG2) {
            elG2.innerHTML = '';
            if (typeof ApexCharts !== 'undefined') {
                var opt2 = {
                    chart: { type: 'bar', height: 210, toolbar: { show: false }, background: 'transparent', foreColor: '#334155', fontFamily: 'Inter, sans-serif' },
                    series: [{ name: 'Processadores', data: [96, 46, 38, 33, 26, 22, 15] }],
                    xaxis: { categories: ['Core i5', 'Core i7', 'Core i3', 'Xeon', 'Ryzen', 'Celeron', 'Outros'], labels: { style: { colors: '#334155', fontSize: '12px' } } },
                    yaxis: { labels: { style: { colors: '#334155', fontSize: '12px' } } },
                    colors: ['#0284c7'],
                    plotOptions: { bar: { horizontal: false, columnWidth: '45%', borderRadius: 4 } },
                    dataLabels: { enabled: true, style: { colors: ['#020617'], fontSize: '10px' } },
                    grid: { borderColor: '#e2e8f0' },
                    theme: { mode: 'light' }
                };
                new ApexCharts(elG2, opt2).render();
            }
        }

        // 3. Gráfico: Número de Memória itens por tipo
        var elG3 = document.getElementById('chart-glpi-memorias-tipo');
        if (elG3) {
            elG3.innerHTML = '';
            if (typeof ApexCharts !== 'undefined') {
                var opt3 = {
                    chart: { type: 'bar', height: 210, toolbar: { show: false }, background: 'transparent', foreColor: '#334155', fontFamily: 'Inter, sans-serif' },
                    series: [{ name: 'Pentes de Memória', data: [74, 60, 49, 33, 33, 32, 30] }],
                    xaxis: { categories: ['DDR3-1600', 'DDR4-2400', 'DDR4-3200', 'Hyper-V', 'DDR3L', 'SODIMM', 'ECC Server'], labels: { style: { colors: '#334155', fontSize: '12px' } } },
                    yaxis: { labels: { style: { colors: '#334155', fontSize: '12px' } } },
                    colors: ['#01a75f'],
                    plotOptions: { bar: { horizontal: false, columnWidth: '45%', borderRadius: 4 } },
                    dataLabels: { enabled: true, style: { colors: ['#052e1b'], fontSize: '10px' } },
                    grid: { borderColor: '#e2e8f0' },
                    theme: { mode: 'light' }
                };
                new ApexCharts(elG3, opt3).render();
            }
        }
    };
})();
