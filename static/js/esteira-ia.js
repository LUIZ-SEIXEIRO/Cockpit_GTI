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
            chat.innerHTML = '<div class="d-flex gap-3 align-items-start">' +
                '<div class="avatar bg-primary-lt text-primary">🤖</div>' +
                '<div class="card card-body">' +
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
                html = '<div style="text-align:center;padding:28px 10px;font-size:11.5px">' +
                    '<span style="font-size:26px;display:block;margin-bottom:8px">📌</span>' +
                    '<strong >Nenhum processo sob sua custódia nominal direta.</strong><br>' +
                    '<span style="font-size:10.5px">' +
                    'Selecione outra opção na lista suspensa acima para consultar demandas do SEI, OpenProject, GLPI ou Relatórios.</span></div>';
            } else {
                listaCust.forEach(function(p) {
                    var isFix = fixados.indexOf(p.ID_Processo) !== -1;
                    html += '<div class="card card-sm" style="display:flex;flex-direction:column;gap:5px">' +
                        '<div style="display:flex;justify-content:space-between;align-items:center">' +
                            '<div style="display:flex;align-items:center;gap:6px">' +
                                '<strong style="font-size:11.5px">' + p.ID_Processo + '</strong>' +
                                '<span style="font-size:9.5px;padding:1px 5px;border-radius:4px;font-weight:700">' + (p.Status_OpenProject || '🚀 Em progresso') + '</span>' +
                            '</div>' +
                            '<span style="cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + p.ID_Processo + '\')" title="Marcar/Desmarcar Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                        '</div>' +
                        '<div style="font-size:11.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="' + (p.Especificacao || '') + '">' + (p.Especificacao || 'Processo sob custódia') + '</div>' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px">' +
                            '<span style="font-size:10.5px">Aging: ' + (p.Faixa_Aging || 'Normal') + ' (' + (p.Dias_Ultima_Mov || 0) + 'd)</span>' +
                            '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarProcessoComIa(\'' + p.ID_Processo + '\', \'' + window.escapeHtml(p.Especificacao || '') + '\')" style="padding:3px 8px;font-size:10.5px;border-radius:4px;font-weight:700;cursor:pointer">Consultar IA 💬</button>' +
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
                html = '<div style="text-align:center;padding:28px 10px;font-size:11.5px">' +
                    '<span style="font-size:26px;display:block;margin-bottom:8px">⭐</span>' +
                    '<strong >Nenhum item marcado para acompanhamento.</strong><br>' +
                    '<span style="font-size:10.5px">' +
                    'Marque a estrela (⭐ Acompanhar) em qualquer processo SEI, pacote OpenProject, chamado GLPI ou relatório daily para acompanhá-lo aqui!</span></div>';
            } else {
                itensAcompanhados.forEach(function(it) {
                    var btnIaAction = '';
                    if (it.tipo === 'SEI') {
                        btnIaAction = '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarProcessoComIa(\'' + it.id + '\', \'' + window.escapeHtml(it.titulo || '') + '\')" style="padding:3px 8px;font-size:10.5px;border-radius:4px;font-weight:700;cursor:pointer">Consultar IA 💬</button>';
                    } else if (it.tipo === 'OpenProject') {
                        btnIaAction = '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarPacoteOpComIa(\'' + it.id.replace('#','') + '\', \'' + window.escapeHtml(it.titulo || '') + '\')" style="padding:3px 8px;font-size:10.5px;border-radius:4px;font-weight:700;cursor:pointer">Consultar IA 💬</button>';
                    } else if (it.tipo === 'GLPI') {
                        btnIaAction = '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarChamadoGlpiComIa(\'' + it.id + '\', \'' + window.escapeHtml(it.titulo || '') + '\')" style="padding:3px 8px;font-size:10.5px;border-radius:4px;font-weight:700;cursor:pointer">Consultar IA 💬</button>';
                    } else {
                        btnIaAction = '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarRelatorioRitualComIa(\'' + window.escapeHtml(it.titulo || '') + '\', \'' + (it.resp || '') + '\')" style="padding:3px 8px;font-size:10.5px;border-radius:4px;font-weight:700;cursor:pointer">Consultar IA 💬</button>';
                    }

                    html += '<div class="card card-sm" style="display:flex;flex-direction:column;gap:5px">' +
                        '<div style="display:flex;justify-content:space-between;align-items:center">' +
                        '<strong style="font-size:11.5px">' + it.id + ' <span style="font-weight:400">(' + it.tipo + ')</span></strong>' +
                        '<span style="cursor:pointer;font-size:13px" onclick="window.toggleFixado(\'' + it.chave + '\')" title="Remover de Acompanhamento">⭐</span></div>' +
                        '<div style="font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="' + (it.titulo || '') + '">' + (it.titulo || 'Demanda TIC') + '</div>' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px">' +
                        '<span style="font-size:10.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:180px">' + (it.resp || it.detalhe || 'SA-GTI') + '</span>' +
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
                html += '<div class="card card-sm" style="display:flex;flex-direction:column;gap:5px">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center">' +
                    '<div style="display:flex;align-items:center;gap:6px">' +
                        '<strong style="font-size:11.5px">#' + p.id + '</strong>' +
                        '<span style="font-size:9.5px;padding:1px 5px;border-radius:4px;font-weight:700">' + (p.tipo || 'Projeto') + '</span>' +
                    '</div>' +
                    '<span style="cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar para Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                    '</div>' +
                    '<div style="font-size:11.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="' + (p.assunto || '') + '">' + (p.assunto || '') + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px">' +
                    '<span style="font-size:10.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:180px">👤 ' + (p.atrib || p.encarr || 'SA-GTI') + '</span>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarPacoteOpComIa(\'' +
                    p.id + '\', \'' + window.escapeHtml(p.assunto || '') + '\')" ' +
                    'style="padding:3px 8px;font-size:10.5px;' +
                    'border:1px solid rgba(245,158,11,0.4);border-radius:4px;' +
                    'font-weight:700;cursor:pointer">Consultar IA 💬</button>' +
                    '</div></div>';
            });
            if (pacotesFiltrados.length > 100) {
                html += '<div style="text-align:center;padding:8px;font-size:11px">' +
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
                html += '<div class="card card-sm" style="display:flex;flex-direction:column;gap:5px">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center">' +
                    '<div style="display:flex;align-items:center;gap:6px">' +
                        '<strong style="font-size:11.5px">' + codGlpi + '</strong>' +
                        '<span style="font-size:9.5px;padding:1px 5px;border-radius:4px;font-weight:700">' + (t.status || 'Pendente') + '</span>' +
                    '</div>' +
                    '<span style="cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar para Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                    '</div>' +
                    '<div style="font-size:11.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="' + (t.titulo || '') + '">' + (t.titulo || '') + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px">' +
                    '<span style="font-size:10.5px">👤 ' + (t.tecnico || 'SA-GTI') + '</span>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarChamadoGlpiComIa(\'' +
                    codGlpi + '\', \'' + window.escapeHtml(t.titulo || '') + '\')" ' +
                    'style="padding:3px 8px;font-size:10.5px;' +
                    'border:1px solid rgba(139,92,246,0.4);border-radius:4px;' +
                    'font-weight:700;cursor:pointer">Consultar IA 💬</button>' +
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
                html += '<div class="card card-sm" style="display:flex;flex-direction:column;gap:5px">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center">' +
                    '<strong style="font-size:11px;font-weight:700">' + r.tipoLabel + '</strong>' +
                    '<span style="cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + chave + '\')" title="Marcar para Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                    '</div>' +
                    '<div style="font-size:11.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="' + r.titulo + '">' + r.titulo + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px">' +
                    '<span style="font-size:10.5px;font-weight:700">' + r.status + ' • ' + r.data + '</span>' +
                    '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarRelatorioRitualComIa(\'' +
                    window.escapeHtml(r.titulo) + '\', \'' + r.tipoLabel + '\')" ' +
                    'style="padding:3px 8px;font-size:10.5px;' +
                    'border:1px solid rgba(56,189,248,0.4);border-radius:4px;' +
                    'font-weight:700;cursor:pointer">Consultar IA 💬</button>' +
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
                html += '<div class="card card-sm" style="display:flex;flex-direction:column;gap:5px">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center">' +
                        '<div style="display:flex;align-items:center;gap:6px">' +
                            '<strong style="font-size:11.5px">' + p.ID_Processo + '</strong>' +
                            '<span style="font-size:9.5px;padding:1px 5px;border-radius:4px;font-weight:700">' + (p.Responsavel_Tecnico || 'SA-GTI') + '</span>' +
                        '</div>' +
                        '<span style="cursor:pointer;font-size:14px" onclick="window.toggleFixado(\'' + p.ID_Processo + '\')" title="Marcar para Acompanhamento">' + (isFix ? '⭐' : '☆') + '</span>' +
                    '</div>' +
                    '<div style="font-size:11.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="' + (p.Especificacao || '') + '">' + (p.Especificacao || 'Processo SEI') + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px">' +
                        '<span style="font-size:10.5px">Aging: ' + (p.Faixa_Aging || 'Normal') + ' (' + (p.Dias_Ultima_Mov || 0) + 'd)</span>' +
                        '<button type="button" class="btn btn-outline-secondary" onclick="window.consultarProcessoComIa(\'' + p.ID_Processo + '\', \'' + window.escapeHtml(p.Especificacao || '') + '\')" style="padding:3px 8px;font-size:10.5px;border-radius:4px;font-weight:700;cursor:pointer">Consultar IA 💬</button>' +
                    '</div></div>';
            });
            if (acervoFiltrado.length > 100) {
                html += '<div style="text-align:center;padding:8px;font-size:11px">Exibindo primeiros 100 processos de ' + acervoFiltrado.length + '. Use a busca acima para filtrar.</div>';
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

        divLateral.classList.add('card', 'd-flex', 'flex-column', 'h-100', 'overflow-hidden');

        divLateral.innerHTML = '<div class="card-header d-flex justify-content-between align-items-center">' +
            '<div><strong class="card-title d-flex align-items-center gap-2">' +
            '<span>📁</span> Contexto &amp; Demandas Rápidas</strong>' +
            '<div class="small text-secondary">Clique para consultar com a IA</div></div></div>' +
            '<div class="card-body d-flex flex-column gap-2">' +
            '<label for="select-contexto-chat" style="font-size:10.5px;font-weight:700;' +
            'text-transform:uppercase;letter-spacing:0.5px;display:flex;align-items:center;gap:5px">' +
            '<span>🎯</span> Base de Contexto Operacional:' +
            '</label>' +
            '<select id="select-contexto-chat" onchange="window.alternarAbaContextoChat(this.value)" ' +
            'class="form-select">' +
            '<option value="custodia" selected>📌 Minha Custódia (2 processos)</option>' +
            '<option value="fixados">⭐ Fixados / Acompanhamento</option>' +
            '<option value="op">📦 Pacotes OpenProject (500)</option>' +
            '<option value="glpi">🎫 Chamados GLPI 10 (15 chamados)</option>' +
            '<option value="relatorios">📑 Relatórios Daily &amp; Sprints (5 rituais)</option>' +
            '<option value="acervo">📚 Acervo Probatório SEI (179 autos)</option>' +
            '</select>' +
            '</div>' +
            '<div class="p-2">' +
            '<input type="text" id="busca-contexto-chat" placeholder="🔍 Filtrar nesta base..." ' +
            'oninput="window.renderizarListaContextoChat()" ' +
            'class="form-control">' +
            '</div>' +
            '<div id="lista-contexto-chat-container" ' +
            'class="d-flex flex-column flex-fill overflow-auto gap-2"></div>';

        // Apply Tabler structure to the chat panel and its controls.
        var chatCard = document.querySelector('#grid-layout-chat-ia .chart-card:last-child');
        if (chatCard) {
            chatCard.classList.add('card', 'd-flex', 'flex-column', 'h-100');

            var headerChat = chatCard.querySelector('div:first-child');
            if (headerChat) {
                headerChat.classList.add('card-header', 'd-flex', 'justify-content-between', 'align-items-center', 'flex-wrap', 'gap-2');

                var txtBox = headerChat.querySelector('div:first-child');
                if (txtBox) {
                    var strTit = txtBox.querySelector('strong');
                    if (strTit) strTit.classList.add('card-title');
                    var strSub = txtBox.querySelector('div');
                    if (strSub) strSub.classList.add('text-secondary');
                }

                var containerBotoes = headerChat.querySelector('div[style*="display: flex; gap: 8px;"]');
                if (containerBotoes && !document.getElementById('btn-reiniciar-chat-v11')) {
                    var btnReiniciar = document.createElement('button');
                    btnReiniciar.id = 'btn-reiniciar-chat-v11';
                    btnReiniciar.className = 'btn btn-outline-danger btn-sm';
                    btnReiniciar.onclick = window.reiniciarConversaChat;
                    btnReiniciar.innerHTML = '<span>🔄</span> Reiniciar Conversa';
                    containerBotoes.insertBefore(btnReiniciar, containerBotoes.firstChild);
                }
            }

            var msgContainer = document.getElementById('chat-messages');
            if (msgContainer) {
                msgContainer.classList.add('card-body', 'd-flex', 'flex-column', 'flex-fill', 'overflow-auto', 'gap-3');
            }

            var barraSugestoes = document.querySelector('#view-esteira_ia div[style*="overflow-x: auto; padding: 8px 14px;"]');
            if (barraSugestoes) {
                barraSugestoes.classList.add('card-footer', 'd-flex', 'align-items-center', 'gap-2', 'overflow-auto');
            }

            var inputChat = document.getElementById('chat-input');
            var footerChat = inputChat && inputChat.parentElement;
            if (footerChat) {
                footerChat.classList.add('card-footer', 'd-flex', 'align-items-center', 'gap-2');
                if (inputChat) {
                    inputChat.classList.add('flex-fill');
                }

                var btnEnviar = footerChat.querySelector('button.btn-primary');
                if (btnEnviar) {
                    btnEnviar.classList.add('btn-primary');
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
