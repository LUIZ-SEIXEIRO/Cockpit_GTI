(function() {
    window.abaContextoChatAtiva = 'custodia';

    // 1. Correção do conflito de chamada na Sidebar
    var origSwitchTab = window.switchTab;
    window.switchTab = function(tabId) {
        if (!tabId) tabId = 'dashboards';
        var mapaEixoSidebar = {
            'dashboards': 'dashboards',
            'visao_estrategica': 'dashboards',
            'portfolio_openproject': 'dashboards',
            'tracks_sagti': 'dashboards',
            'pdtic_eixos': 'dashboards',
            'gestao_glpi': 'dashboards',
            'mesa_trabalho': 'mesa_trabalho',
            'consulta': 'mesa_trabalho',
            'esteira_ia': 'mesa_trabalho',
            'cadernos': 'mesa_trabalho',
            'matriz_raci': 'mesa_trabalho',
            'relatorios_sprints': 'mesa_trabalho',
            'drive_contexto_ia': 'mesa_trabalho',
            'daily_warroom': 'daily_warroom',
            'gestao_agil': 'daily_warroom',
            'auditoria': 'dashboards',
            'configuracoes': 'configuracoes',
            'documentacao': 'documentacao'
        };
        var tabPaiSidebar = mapaEixoSidebar[tabId] || tabId;

        if (typeof origSwitchTab === 'function') {
            origSwitchTab(tabId);
        }

        document.querySelectorAll('#sidebar .nav-item').forEach(function(el) {
            if (el.getAttribute('data-tab') === tabPaiSidebar) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });
    };

    // 2. Botão de Reinício Rápido de Conversa
    window.reiniciarConversaChat = function() {
        window.historicoMensagensChat = [];
        window.arquivosAnexados = [];
        if (typeof window.renderizarAnexosChips === 'function') {
            window.renderizarAnexosChips();
        }

        var chat = document.getElementById('chat-messages');
        var input = document.getElementById('chat-input');
        if (input) {
            input.value = '';
            input.focus();
        }

        if (chat) {
            chat.innerHTML = '<div style="display:flex;gap:12px;max-width:88%;align-self:flex-start;">' +
                '<div style="width:34px;height:34px;border-radius:50%;' +
                'background:var(--sagti-accent);' +
                'display:flex;align-items:center;justify-content:center;' +
                'color:white;font-size:15px;flex-shrink:0;">🤖</div>' +
                '<div style="background:var(--sagti-surface-alt);border:1px solid rgba(255,255,255,0.1);' +
                'padding:14px 18px;border-radius:4px 14px 14px 14px;' +
                'font-size:13px;color:#f1f5f9;line-height:1.65;box-shadow:0 4px 14px rgba(0,0,0,0.3);">' +
                '<strong>Olá, Luiz! Tudo bem? Sou sua IA pessoal aqui na SA-GTI.</strong><br><br>' +
                'Você pode conversar comigo livremente para resolver qualquer assunto do seu dia a dia — ' +
                'seja para redigir um e-mail, estruturar um despacho ou documento, organizar suas prioridades da semana, ' +
                'destrinchar uma dúvida técnica ou consultar de forma simples o andamento das nossas demandas ' +
                '(contando com toda a nossa base consolidada do SEI, GLPI e OpenProject nos bastidores).<br><br>' +
                '<em>Como posso te ajudar agora?</em>' +
                '</div></div>';
            chat.scrollTop = 0;
        }
    };
    window.reiniciarChatEsteira = window.reiniciarConversaChat;

    // 3. Alternância Unificada de Abas de Contexto na IA (Espelhando a Mesa de Trabalho)
    window.alternarAbaContextoChat = function(aba) {
        window.abaContextoChatAtiva = aba || 'custodia';
        var sel = document.getElementById('select-contexto-chat');
        if (sel && sel.value !== window.abaContextoChatAtiva) {
            sel.value = window.abaContextoChatAtiva;
        }
        var abas = ['custodia', 'fixados', 'op', 'glpi', 'relatorios', 'acervo'];
        abas.forEach(function(a) {
            var btn = document.getElementById('btn-ctx-' + a);
            if (btn) {
                btn.className = (a === window.abaContextoChatAtiva)
                    ? 'btn btn-primary pill-contexto-chat active'
                    : 'btn btn-secondary pill-contexto-chat';
            }
        });
        window.renderizarListaContextoChat();
    };

    window.consultarProcessoComIa = function(sei, especificacao) {
        var textoPrompt = 'Por favor, analise a situação do processo SEI ' + sei +
            ' (' + (especificacao || 'Demanda TIC') + ') detalhando objeto, prazos, estágio e riscos.';
        var inp = document.getElementById('chat-input');
        if (inp) {
            inp.value = textoPrompt;
            if (typeof window.enviarMensagemChatUnificado === 'function') window.enviarMensagemChatUnificado();
        }
    };

    window.consultarPacoteOpComIa = function(idOp, assunto) {
        var textoPrompt = 'Como está o status e entregáveis do pacote OpenProject #' + idOp +
            ' (' + (assunto || 'Iniciativa SA-GTI') + ')? Apresente o resumo executivo e próximos passos.';
        var inp = document.getElementById('chat-input');
        if (inp) {
            inp.value = textoPrompt;
            if (typeof window.enviarMensagemChatUnificado === 'function') window.enviarMensagemChatUnificado();
        }
    };

    window.consultarChamadoGlpiComIa = function(idGlpi, titulo) {
        var textoPrompt = 'Por favor, avalie o chamado GLPI ' + idGlpi + ' (' + (titulo || 'Incidente ITSM') + '), informando SLA, causa raiz e ação de suporte recomendada.';
        var inp = document.getElementById('chat-input');
        if (inp) {
            inp.value = textoPrompt;
            if (typeof window.enviarMensagemChatUnificado === 'function') window.enviarMensagemChatUnificado();
        }
    };

    
    window.consultarRaciComIa = function(titulo, vinculo) {
        var textoPrompt = 'Por favor, analise a Matriz RACI e o Fluxo de Aprovação "' + titulo + '"' +
            (vinculo ? (' vinculado à demanda ' + vinculo) : '') +
            ', avaliando conformidade com a segregação de funções, papéis de Accountable (A) e próximos passos para homologação formal.';
        var inp = document.getElementById('chat-input') || document.getElementById('drawer-chat-input');
        if (inp) {
            inp.value = textoPrompt;
            inp.focus();
            if (typeof window.enviarMensagemChatUnificado === 'function') {
                window.enviarMensagemChatUnificado();
            }
        }
    };

    window.consultarRelatorioRitualComIa = function(titulo, tipo) {
        var textoPrompt = 'Com base no relatório de ritual "' + titulo + '" (' + tipo + '), sintetize os principais pontos de atenção, impedimentos e deliberações para a gestão da SA-GTI.';
        var inp = document.getElementById('chat-input');
        if (inp) {
            inp.value = textoPrompt;
            if (typeof window.enviarMensagemChatUnificado === 'function') window.enviarMensagemChatUnificado();
        }
    };

    window.renderizarListaContextoChat = function() {
        var container = document.getElementById('lista-contexto-chat-container');
        if (!container) return;

        var busca = (document.getElementById('busca-contexto-chat') ?
                     document.getElementById('busca-contexto-chat').value : '').toLowerCase().trim();
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var procsCustodia = (typeof window.obterCustodiaNominalLuiz === 'function') ? window.obterCustodiaNominalLuiz() : [];
        var fixados = (typeof window.obterFixadosValidos === 'function') ? window.obterFixadosValidos() : [];
        var listaOp = (typeof window.OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(window.OP_PACOTES_OFICIAIS)) ? window.OP_PACOTES_OFICIAIS : [];
        var pacotesOpAbertos = listaOp.filter(function(op) {
            var st = (op.status || '').toLowerCase();
            return st.indexOf('encerrado') === -1 && st.indexOf('concluído') === -1 && st.indexOf('cancelado') === -1;
        });
        var listaGlpi = (typeof window.CHAMADOS_GLPI_15_OFICIAIS !== 'undefined' && Array.isArray(window.CHAMADOS_GLPI_15_OFICIAIS) && window.CHAMADOS_GLPI_15_OFICIAIS.length > 0) ? window.CHAMADOS_GLPI_15_OFICIAIS : ((typeof window.CHAMADOS_ITSM_SUPORTE !== 'undefined' && Array.isArray(window.CHAMADOS_ITSM_SUPORTE)) ? window.CHAMADOS_ITSM_SUPORTE : []);
        var relatoriosRituais = (typeof window.obterRelatoriosRituais === 'function') ? window.obterRelatoriosRituais() : [];

        // Atualiza dinamicamente as legendas da Lista Suspensa (Select)
        var selCtx = document.getElementById('select-contexto-chat');
        if (selCtx) {
            var optCust = selCtx.querySelector('option[value="custodia"]');
            if (optCust) optCust.innerText = '📌 Minha Custódia (' + procsCustodia.length + ' processos)';
            var optFix = selCtx.querySelector('option[value="fixados"]');
            if (optFix) optFix.innerText = '⭐ Fixados / Acompanhamento (' + fixados.length + ')';
            var optOp = selCtx.querySelector('option[value="op"]');
            if (optOp) optOp.innerText = '📦 Pacotes OpenProject (500)';
            var optGlpi = selCtx.querySelector('option[value="glpi"]');
            if (optGlpi) optGlpi.innerText = '🎫 Chamados GLPI 10 (' + listaGlpi.length + ' não solucionados)';
            var optRel = selCtx.querySelector('option[value="relatorios"]');
            if (optRel) optRel.innerText = '📑 Relatórios Daily & Sprints (' + relatoriosRituais.length + ' rituais)';
            var optAcervo = selCtx.querySelector('option[value="acervo"]');
            if (optAcervo) optAcervo.innerText = '📚 Acervo Probatório SEI (' + baseProcs.length + ' autos)';
        }

        var modo = window.abaContextoChatAtiva || 'custodia';
        var html = '';

        // 1. MODO: MINHA CUSTÓDIA
        if (modo === 'custodia') {
            var listaCust = procsCustodia;
            if (busca) {
                listaCust = listaCust.filter(function(p) {
                    return (p.ID_Processo + ' ' + (p.Especificacao || '') + ' ' + (p.Responsavel_Tecnico || '')).toLowerCase().indexOf(busca) !== -1;
                });
            }
            if (listaCust.length === 0) {
                html = '<div style="text-align:center;padding:28px 10px;color:#94a3b8;font-size:11.5px;">' +
                    '<span style="font-size:26px;display:block;margin-bottom:8px;">📌</span>' +
                    '<strong style="color:#f1f5f9;">Nenhum processo sob sua custódia nominal direta.</strong><br>' +
                    '<span style="font-size:10.5px;color:#94a3b8;">' +
                    'Selecione outra opção na lista suspensa acima para consultar demandas do SEI, OpenProject, GLPI ou Relatórios.</span></div>';
            } else {
                listaCust.forEach(function(p) {
                    var isFix = fixados.indexOf(p.ID_Processo) !== -1;
                    html += '<div style="background:var(--sagti-surface-alt);border:1px solid rgba(255,255,255,0.08);' +
                        'border-left:3px solid #38bdf8;border-radius:8px;padding:9px 11px;display:flex;' +
                        'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                            '<div style="display:flex;align-items:center;gap:6px;">' +
                                '<strong style="font-family:monospace;font-size:11.5px;color:var(--sagti-accent);">' + p.ID_Processo + '</strong>' +
                                '<span style="font-size:9.5px;background:rgba(56,189,248,0.2);color:var(--sagti-accent);padding:1px 5px;border-radius:4px;font-weight:700;">' + (p.Status_OpenProject || '🚀 Em progresso') + '</span>' +
                            '</div>' +
                            '<span style="cursor:pointer;font-size:14px;color:' + (isFix ? '#facc15' : '#64748b') + ';" onclick="window.toggleFixado(\'' + p.ID_Processo + '\')" title="Marcar/Desmarcar Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                        '</div>' +
                        '<div style="font-size:11.5px;color:var(--sagti-text);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="' + (p.Especificacao || '') + '">' + (p.Especificacao || 'Processo sob custódia') + '</div>' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                            '<span style="font-size:10.5px;color:#94a3b8;">Aging: ' + (p.Faixa_Aging || 'Normal') + ' (' + (p.Dias_Ultima_Mov || 0) + 'd)</span>' +
                            '<button type="button" class="btn btn-secondary" onclick="window.consultarProcessoComIa(\'' + p.ID_Processo + '\', \'' + window.escapeHtml(p.Especificacao || '') + '\')" style="padding:3px 8px;font-size:10.5px;background:rgba(56,189,248,0.18);border:1px solid rgba(56,189,248,0.4);color:var(--sagti-accent);border-radius:4px;font-weight:700;cursor:pointer;">Consultar IA 💬</button>' +
                        '</div></div>';
                });
            }
        }

        // 2. MODO: FIXADOS / ACOMPANHAMENTO (RESOLVEDOR UNIFICADO)
        else if (modo === 'fixados') {
            var itensAcompanhados = [];
            fixados.forEach(function(chave) {
                var itemObj = (typeof window.resolverItemWatchlist === 'function')
                    ? window.resolverItemWatchlist(chave, baseProcs, pacotesOpAbertos, listaGlpi, relatoriosRituais)
                    : null;
                if (itemObj) itensAcompanhados.push(itemObj);
            });

            if (busca) {
                itensAcompanhados = itensAcompanhados.filter(function(it) {
                    return (it.id + ' ' + (it.titulo || '') + ' ' + (it.resp || '') + ' ' + (it.tipo || '')).toLowerCase().indexOf(busca) !== -1;
                });
            }

            if (itensAcompanhados.length === 0) {
                html = '<div style="text-align:center;padding:28px 10px;color:#94a3b8;font-size:11.5px;">' +
                    '<span style="font-size:26px;display:block;margin-bottom:8px;">⭐</span>' +
                    '<strong style="color:#f1f5f9;">Nenhum item marcado para acompanhamento.</strong><br>' +
                    '<span style="font-size:10.5px;color:#94a3b8;">' +
                    'Marque a estrela (⭐ Acompanhar) em qualquer processo SEI, pacote OpenProject, chamado GLPI ou relatório daily para acompanhá-lo aqui!</span></div>';
            } else {
                itensAcompanhados.forEach(function(it) {
                    var bordaCor = it.tipo === 'OpenProject' ? '#f59e0b' : (it.tipo === 'GLPI' ? '#c084fc' : (it.tipo === 'Relatório' ? '#38bdf8' : '#0ea5e9'));
                    var btnIaAction = '';
                    if (it.tipo === 'SEI') {
                        btnIaAction = '<button type="button" class="btn btn-secondary" onclick="window.consultarProcessoComIa(\'' + it.id + '\', \'' + window.escapeHtml(it.titulo || '') + '\')" style="padding:3px 8px;font-size:10.5px;background:rgba(56,189,248,0.18);border:1px solid rgba(56,189,248,0.4);color:var(--sagti-accent);border-radius:4px;font-weight:700;cursor:pointer;">Consultar IA 💬</button>';
                    } else if (it.tipo === 'OpenProject') {
                        btnIaAction = '<button type="button" class="btn btn-secondary" onclick="window.consultarPacoteOpComIa(\'' + it.id.replace('#','') + '\', \'' + window.escapeHtml(it.titulo || '') + '\')" style="padding:3px 8px;font-size:10.5px;background:rgba(245,158,11,0.18);border:1px solid rgba(245,158,11,0.4);color:#fbbf24;border-radius:4px;font-weight:700;cursor:pointer;">Consultar IA 💬</button>';
                    } else if (it.tipo === 'GLPI') {
                        btnIaAction = '<button type="button" class="btn btn-secondary" onclick="window.consultarChamadoGlpiComIa(\'' + it.id + '\', \'' + window.escapeHtml(it.titulo || '') + '\')" style="padding:3px 8px;font-size:10.5px;background:rgba(139,92,246,0.18);border:1px solid rgba(139,92,246,0.4);color:#c084fc;border-radius:4px;font-weight:700;cursor:pointer;">Consultar IA 💬</button>';
                    } else {
                        btnIaAction = '<button type="button" class="btn btn-secondary" onclick="window.consultarRelatorioRitualComIa(\'' + window.escapeHtml(it.titulo || '') + '\', \'' + (it.resp || '') + '\')" style="padding:3px 8px;font-size:10.5px;background:rgba(56,189,248,0.18);border:1px solid rgba(56,189,248,0.4);color:var(--sagti-accent);border-radius:4px;font-weight:700;cursor:pointer;">Consultar IA 💬</button>';
                    }

                    html += '<div style="background:var(--sagti-surface-alt);border:1px solid rgba(255,255,255,0.08);' +
                        'border-left:3px solid ' + bordaCor + ';border-radius:8px;padding:9px 11px;display:flex;' +
                        'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                        '<strong style="font-family:monospace;font-size:11.5px;color:var(--sagti-accent);">' + it.id + ' <span style="font-size:10px;color:#94a3b8;font-weight:400;">(' + it.tipo + ')</span></strong>' +
                        '<span style="cursor:pointer;font-size:13px;color:#facc15;" onclick="window.toggleFixado(\'' + it.chave + '\')" title="Remover de Acompanhamento">⭐</span></div>' +
                        '<div style="font-size:11.5px;color:var(--sagti-text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="' + (it.titulo || '') + '">' + (it.titulo || 'Demanda TIC') + '</div>' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                        '<span style="font-size:10.5px;color:#94a3b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:180px;">' + (it.resp || it.detalhe || 'SA-GTI') + '</span>' +
                        btnIaAction +
                        '</div></div>';
                });
            }
        }

        // 3. MODO: PACOTES OPENPROJECT
        else if (modo === 'op') {
            var pacotesFiltrados = pacotesOpAbertos;
            if (busca) {
                pacotesFiltrados = pacotesFiltrados.filter(function(p) {
                    return (p.id + ' ' + (p.assunto || '') + ' ' + (p.projeto || '') + ' ' + (p.atrib || '') + ' ' + (p.status || '')).toLowerCase().indexOf(busca) !== -1;
                });
            }
            pacotesFiltrados.slice(0, 100).forEach(function(p) {
                var chave = 'OP#' + p.id;
                var isFix = fixados.indexOf(chave) !== -1;
                html += '<div style="background:var(--sagti-surface-alt);border:1px solid rgba(255,255,255,0.08);' +
                    'border-left:3px solid #f59e0b;border-radius:8px;padding:9px 11px;display:flex;' +
                    'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                    '<div style="display:flex;align-items:center;gap:6px;">' +
                        '<strong style="font-family:monospace;font-size:11.5px;color:#f59e0b;">#' + p.id + '</strong>' +
                        '<span style="font-size:9.5px;background:#e0f2fe;color:#0369a1;padding:1px 5px;border-radius:4px;font-weight:700;">' + (p.tipo || 'Projeto') + '</span>' +
                    '</div>' +
                    '<span style="cursor:pointer;font-size:14px;color:' + (isFix ? '#facc15' : '#64748b') + ';" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar para Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                    '</div>' +
                    '<div style="font-size:11.5px;color:var(--sagti-text);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="' + (p.assunto || '') + '">' + (p.assunto || '') + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                    '<span style="font-size:10.5px;color:#94a3b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:180px;">👤 ' + (p.atrib || p.encarr || 'SA-GTI') + '</span>' +
                    '<button type="button" class="btn btn-secondary" onclick="window.consultarPacoteOpComIa(\'' +
                    p.id + '\', \'' + window.escapeHtml(p.assunto || '') + '\')" ' +
                    'style="padding:3px 8px;font-size:10.5px;background:rgba(245,158,11,0.18);' +
                    'border:1px solid rgba(245,158,11,0.4);color:#fbbf24;border-radius:4px;' +
                    'font-weight:700;cursor:pointer;">Consultar IA 💬</button>' +
                    '</div></div>';
            });
            if (pacotesFiltrados.length > 100) {
                html += '<div style="text-align:center;padding:8px;font-size:11px;color:#94a3b8;">' +
                        'Exibindo primeiros 100 pacotes de ' + pacotesFiltrados.length + ' em aberto. Use o campo de busca para refinar.</div>';
            }
        }

        // 4. MODO: CHAMADOS GLPI
        else if (modo === 'glpi') {
            var glpiFiltrados = listaGlpi;
            if (busca) {
                glpiFiltrados = glpiFiltrados.filter(function(t) {
                    return (t.id + ' ' + (t.titulo || '') + ' ' + (t.tecnico || '') + ' ' + (t.fila || '') + ' ' + (t.bucket || '')).toLowerCase().indexOf(busca) !== -1;
                });
            }
            glpiFiltrados.forEach(function(t) {
                var chave = 'GLPI#' + t.id;
                var isFix = fixados.indexOf(chave) !== -1;
                var codGlpi = '#' + t.id;
                html += '<div style="background:var(--sagti-surface-alt);border:1px solid rgba(255,255,255,0.08);' +
                    'border-left:3px solid #0284c7;border-radius:8px;padding:9px 11px;display:flex;' +
                    'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                    '<div style="display:flex;align-items:center;gap:6px;">' +
                        '<strong style="font-family:monospace;font-size:11.5px;color:#c084fc;">' + codGlpi + '</strong>' +
                        '<span style="font-size:9.5px;background:rgba(239,68,68,0.2);color:#fca5a5;padding:1px 5px;border-radius:4px;font-weight:700;">' + (t.status || 'Pendente') + '</span>' +
                    '</div>' +
                    '<span style="cursor:pointer;font-size:14px;color:' + (isFix ? '#facc15' : '#64748b') + ';" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar para Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                    '</div>' +
                    '<div style="font-size:11.5px;color:var(--sagti-text);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="' + (t.titulo || '') + '">' + (t.titulo || '') + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                    '<span style="font-size:10.5px;color:#94a3b8;">👤 ' + (t.tecnico || 'SA-GTI') + '</span>' +
                    '<button type="button" class="btn btn-secondary" onclick="window.consultarChamadoGlpiComIa(\'' +
                    codGlpi + '\', \'' + window.escapeHtml(t.titulo || '') + '\')" ' +
                    'style="padding:3px 8px;font-size:10.5px;background:rgba(139,92,246,0.18);' +
                    'border:1px solid rgba(139,92,246,0.4);color:#c084fc;border-radius:4px;' +
                    'font-weight:700;cursor:pointer;">Consultar IA 💬</button>' +
                    '</div></div>';
            });
        }

        // 5. MODO: RELATÓRIOS DAILY & SPRINTS
        else if (modo === 'relatorios') {
            var relFiltrados = relatoriosRituais;
            if (busca) {
                relFiltrados = relFiltrados.filter(function(r) {
                    return (r.titulo + ' ' + r.destaque + ' ' + r.tipoLabel + ' ' + r.data).toLowerCase().indexOf(busca) !== -1;
                });
            }
            relFiltrados.forEach(function(r) {
                var chave = 'REL#' + r.id;
                var isFix = fixados.indexOf(chave) !== -1 || r.marcado;
                html += '<div style="background:var(--sagti-surface-alt);border:1px solid rgba(255,255,255,0.08);' +
                    'border-left:3px solid #38bdf8;border-radius:8px;padding:9px 11px;display:flex;' +
                    'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                    '<strong style="font-size:11px;color:var(--sagti-accent);font-weight:700;">' + r.tipoLabel + '</strong>' +
                    '<span style="cursor:pointer;font-size:14px;color:' + (isFix ? '#facc15' : '#64748b') + ';" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar para Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                    '</div>' +
                    '<div style="font-size:11.5px;color:var(--sagti-text);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="' + r.titulo + '">' + r.titulo + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                    '<span style="font-size:10.5px;color:#34d399;font-weight:700;">' + r.status + ' • ' + r.data + '</span>' +
                    '<button type="button" class="btn btn-secondary" onclick="window.consultarRelatorioRitualComIa(\'' +
                    window.escapeHtml(r.titulo) + '\', \'' + r.tipoLabel + '\')" ' +
                    'style="padding:3px 8px;font-size:10.5px;background:rgba(56,189,248,0.18);' +
                    'border:1px solid rgba(56,189,248,0.4);color:var(--sagti-accent);border-radius:4px;' +
                    'font-weight:700;cursor:pointer;">Consultar IA 💬</button>' +
                    '</div></div>';
            });
        }

        // 6. MODO: ACERVO PROBATÓRIO SEI COMPLETO (179 PROCESSOS)
        else if (modo === 'acervo') {
            var acervoFiltrado = baseProcs;
            if (busca) {
                acervoFiltrado = acervoFiltrado.filter(function(p) {
                    return (p.ID_Processo + ' ' + (p.Especificacao || '') + ' ' + (p.Responsavel_Tecnico || '')).toLowerCase().indexOf(busca) !== -1;
                });
            }
            acervoFiltrado.slice(0, 100).forEach(function(p) {
                var isFix = fixados.indexOf(p.ID_Processo) !== -1;
                html += '<div style="background:var(--sagti-surface-alt);border:1px solid rgba(255,255,255,0.08);' +
                    'border-left:3px solid #0284c7;border-radius:8px;padding:9px 11px;display:flex;' +
                    'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                        '<div style="display:flex;align-items:center;gap:6px;">' +
                            '<strong style="font-family:monospace;font-size:11.5px;color:var(--sagti-accent);">' + p.ID_Processo + '</strong>' +
                            '<span style="font-size:9.5px;background:rgba(2,132,199,0.2);color:var(--sagti-accent);padding:1px 5px;border-radius:4px;font-weight:700;">' + (p.Responsavel_Tecnico || 'SA-GTI') + '</span>' +
                        '</div>' +
                        '<span style="cursor:pointer;font-size:14px;color:' + (isFix ? '#facc15' : '#64748b') + ';" onclick="window.toggleFixado(\'' + p.ID_Processo + '\')" title="Marcar para Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                    '</div>' +
                    '<div style="font-size:11.5px;color:var(--sagti-text);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="' + (p.Especificacao || '') + '">' + (p.Especificacao || 'Processo SEI') + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                        '<span style="font-size:10.5px;color:#94a3b8;">Aging: ' + (p.Faixa_Aging || 'Normal') + ' (' + (p.Dias_Ultima_Mov || 0) + 'd)</span>' +
                        '<button type="button" class="btn btn-secondary" onclick="window.consultarProcessoComIa(\'' + p.ID_Processo + '\', \'' + window.escapeHtml(p.Especificacao || '') + '\')" style="padding:3px 8px;font-size:10.5px;background:rgba(2,132,199,0.18);border:1px solid rgba(2,132,199,0.4);color:var(--sagti-accent);border-radius:4px;font-weight:700;cursor:pointer;">Consultar IA 💬</button>' +
                    '</div></div>';
            });
            if (acervoFiltrado.length > 100) {
                html += '<div style="text-align:center;padding:8px;font-size:11px;color:#94a3b8;">Exibindo primeiros 100 processos de ' + acervoFiltrado.length + '. Use a busca acima para filtrar.</div>';
            }
        }

        container.innerHTML = html;
    };

    // 4. Injeção Dinâmica do Painel de Contexto com as 5 Pílulas idênticas à Mesa
    function configurarPainelContextoIaUnificado() {
        var gridChat = document.getElementById('grid-layout-chat-ia');
        if (!gridChat) return;

        gridChat.style.display = 'grid';
        gridChat.style.gridTemplateColumns = '340px 1fr';
        gridChat.style.gap = '16px';

        var divLateral = document.getElementById('painel-contexto-operacional-chat');
        if (!divLateral) {
            divLateral = document.createElement('div');
            divLateral.id = 'painel-contexto-operacional-chat';
            divLateral.className = 'chart-card';
            gridChat.insertBefore(divLateral, gridChat.firstChild);
        }

        divLateral.style.cssText = 'height:100%;display:flex;flex-direction:column;padding:0;' +
            'overflow:hidden;background:var(--sagti-surface-alt);' +
            'border:1px solid rgba(255,255,255,0.1);border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.3);';

        divLateral.innerHTML = '<div style="padding:12px 14px;background:var(--sagti-surface-alt);' +
            'border-bottom:1px solid rgba(255,255,255,0.08);' +
            'display:flex;justify-content:space-between;align-items:center;">' +
            '<div><strong style="font-size:12.5px;color:var(--sagti-text);display:flex;align-items:center;gap:6px;">' +
            '<span>📁</span> Contexto &amp; Demandas Rápidas</strong>' +
            '<div style="font-size:10.5px;color:#94a3b8;">Clique para consultar com a IA</div></div></div>' +
            '<div style="padding:10px 12px;background:rgba(2,6,23,0.65);border-bottom:1px solid rgba(255,255,255,0.08);' +
            'display:flex;flex-direction:column;gap:6px;">' +
            '<label for="select-contexto-chat" style="font-size:10.5px;color:#94a3b8;font-weight:700;' +
            'text-transform:uppercase;letter-spacing:0.5px;display:flex;align-items:center;gap:5px;">' +
            '<span>🎯</span> Base de Contexto Operacional:' +
            '</label>' +
            '<select id="select-contexto-chat" onchange="window.alternarAbaContextoChat(this.value)" ' +
            'style="width:100%;box-sizing:border-box;padding:8px 12px;border-radius:8px;' +
            'border:1px solid rgba(56,189,248,0.35);background:var(--sagti-surface-alt);color:var(--sagti-text);' +
            'font-size:12px;font-weight:700;outline:none;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.3);">' +
            '<option value="custodia" selected>📌 Minha Custódia (2 processos)</option>' +
            '<option value="fixados">⭐ Fixados / Acompanhamento</option>' +
            '<option value="op">📦 Pacotes OpenProject (500)</option>' +
            '<option value="glpi">🎫 Chamados GLPI 10 (15 chamados)</option>' +
            '<option value="relatorios">📑 Relatórios Daily &amp; Sprints (5 rituais)</option>' +
            '<option value="acervo">📚 Acervo Probatório SEI (179 autos)</option>' +
            '</select>' +
            '</div>' +
            '<div style="padding:8px 10px;border-bottom:1px solid rgba(255,255,255,0.08);' +
            'background:var(--sagti-surface-alt);">' +
            '<input type="text" id="busca-contexto-chat" placeholder="🔍 Filtrar nesta base..." ' +
            'oninput="window.renderizarListaContextoChat()" ' +
            'style="width:100%;box-sizing:border-box;padding:6px 10px;border-radius:6px;' +
            'border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.06);' +
            'color:var(--sagti-text);font-size:11.5px;outline:none;">' +
            '</div>' +
            '<div id="lista-contexto-chat-container" ' +
            'style="flex:1;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:6px;' +
            'background:rgba(11,19,43,0.5);"></div>';

        // Estiliza o Card de Chat na direita para Dark Theme V11 impecável
        var chatCard = document.querySelector('#grid-layout-chat-ia .chart-card:last-child');
        if (chatCard) {
            chatCard.style.cssText = 'height:100%;display:flex;flex-direction:column;padding:0;overflow:hidden;' +
                'background:var(--sagti-surface-alt);border:1px solid rgba(255,255,255,0.1);' +
                'border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.3);';

            var headerChat = chatCard.querySelector('div:first-child');
            if (headerChat) {
                headerChat.style.cssText = 'padding:12px 18px;background:var(--sagti-surface-alt);' +
                    'border-bottom:1px solid rgba(255,255,255,0.08);display:flex;' +
                    'justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;';

                var txtBox = headerChat.querySelector('div:first-child');
                if (txtBox) {
                    var strTit = txtBox.querySelector('strong');
                    if (strTit) strTit.style.cssText = 'font-size:14px;color:var(--sagti-text);display:block;';
                    var strSub = txtBox.querySelector('div');
                    if (strSub) strSub.style.cssText = 'font-size:11.5px;color:#94a3b8;margin-top:2px;';
                }

                var containerBotoes = headerChat.querySelector('div[style*="display: flex; gap: 8px;"]');
                if (containerBotoes && !document.getElementById('btn-reiniciar-chat-v11')) {
                    var btnReiniciar = document.createElement('button');
                    btnReiniciar.id = 'btn-reiniciar-chat-v11';
                    btnReiniciar.className = 'btn btn-secondary';
                    btnReiniciar.onclick = window.reiniciarConversaChat;
                    btnReiniciar.style.cssText = 'padding:5px 12px;font-size:11.5px;background:rgba(239,68,68,0.16);' +
                        'border:1px solid rgba(239,68,68,0.35);color:#fca5a5;font-weight:700;cursor:pointer;' +
                        'display:inline-flex;align-items:center;gap:5px;border-radius:6px;';
                    btnReiniciar.innerHTML = '<span>🔄</span> Reiniciar Conversa';
                    containerBotoes.insertBefore(btnReiniciar, containerBotoes.firstChild);
                }
            }

            var msgContainer = document.getElementById('chat-messages');
            if (msgContainer) {
                msgContainer.style.cssText = 'flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;' +
                    'gap:14px;background:rgba(11,19,43,0.5);';
            }

            var barraSugestoes = document.querySelector('#view-esteira_ia div[style*="overflow-x: auto; padding: 8px 14px;"]');
            if (barraSugestoes) {
                barraSugestoes.style.cssText = 'overflow-x:auto;padding:8px 14px;background:var(--sagti-surface-alt);' +
                    'border-top:1px solid rgba(255,255,255,0.08);display:flex;gap:8px;align-items:center;' +
                    'font-size:11.5px;color:#94a3b8;white-space:nowrap;';
            }

            var footerChat = document.querySelector('#view-esteira_ia div[style*="border-top: 1px solid #e2e8f0; padding: 12px 18px;"]');
            if (footerChat) {
                footerChat.style.cssText = 'border-top:1px solid rgba(255,255,255,0.08);padding:12px 18px;' +
                    'background:var(--sagti-surface-alt);';

                var inputChat = document.getElementById('chat-input');
                if (inputChat) {
                    inputChat.style.cssText = 'flex:1;border:1px solid rgba(255,255,255,0.14);' +
                        'background:rgba(255,255,255,0.06);color:var(--sagti-text);border-radius:8px;' +
                        'padding:10px 14px;font-size:12.5px;outline:none;';
                }

                var btnEnviar = footerChat.querySelector('button.btn-primary');
                if (btnEnviar) {
                    btnEnviar.style.cssText = 'padding:10px 18px;font-size:12.5px;font-weight:700;' +
                        'background:var(--sagti-accent);' +
                        'border:1px solid rgba(56,189,248,0.5);border-radius:8px;cursor:pointer;' +
                        'box-shadow:0 4px 14px rgba(14,165,233,0.35);color:var(--sagti-text);';
                }
            }
        }

        window.renderizarListaContextoChat();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', configurarPainelContextoIaUnificado);
    } else {
        configurarPainelContextoIaUnificado();
    }
    window.addEventListener('load', configurarPainelContextoIaUnificado);
    window.addEventListener('hashchange', function() {
        if (window.location.hash.indexOf('esteira') !== -1) {
            setTimeout(configurarPainelContextoIaUnificado, 50);
        }
    });
})();
