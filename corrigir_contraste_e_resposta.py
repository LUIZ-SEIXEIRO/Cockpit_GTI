import os

files_to_check = [
    'painel.html',
    os.path.join('frontend', 'painel.html'),
    r'C:\Cockpit_GTI\painel.html',
    r'C:\Cockpit_GTI\frontend\painel.html'
]

targets = []
seen = set()
for p in files_to_check:
    norm = os.path.normpath(os.path.abspath(p))
    if os.path.exists(norm) and norm not in seen:
        seen.add(norm)
        targets.append(norm)

js_melhorias_chat = r'''<script id="script-melhorias-esteira-ia-v11">
(function() {
    window.abaContextoChatAtiva = 'fixados';

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
            'daily_warroom': 'daily_warroom',
            'gestao_agil': 'daily_warroom',
            'auditoria': 'daily_warroom',
            'configuracoes': 'configuracoes'
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
                'background:linear-gradient(135deg,#002d5a 0%,#0544cf 100%);' +
                'display:flex;align-items:center;justify-content:center;' +
                'color:white;font-size:15px;flex-shrink:0;">🤖</div>' +
                '<div style="background:rgba(30,41,59,0.9);border:1px solid rgba(255,255,255,0.1);' +
                'padding:14px 18px;border-radius:4px 14px 14px 14px;' +
                'font-size:13px;color:#f1f5f9;line-height:1.65;box-shadow:0 4px 12px rgba(0,0,0,0.2);">' +
                'Conversa reiniciada com sucesso, Luiz! Contexto limpo.<br><br>' +
                'Estou pronto para uma nova tarefa. Você pode escolher uma das sugestões abaixo, ' +
                'clicar em qualquer demanda do painel ao lado ou digitar livremente sua instrução.<br><br>' +
                'Como deseja prosseguir agora?' +
                '</div></div>';
            chat.scrollTop = 0;
        }
    };
    window.reiniciarChatEsteira = window.reiniciarConversaChat;

    // 3. Painel Lateral de Contexto Operacional com Alto Contraste Dark V11
    window.alternarAbaContextoChat = function(aba) {
        window.abaContextoChatAtiva = aba || 'fixados';
        var abas = ['fixados', 'sei', 'op'];
        abas.forEach(function(a) {
            var btn = document.getElementById('btn-ctx-' + a);
            if (btn) {
                if (a === window.abaContextoChatAtiva) {
                    btn.className = 'btn btn-primary pill-contexto-chat active';
                    btn.style.setProperty('background', 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)', 'important');
                    btn.style.setProperty('color', '#ffffff', 'important');
                    btn.style.setProperty('font-weight', '700', 'important');
                    btn.style.setProperty('border', '1px solid rgba(56,189,248,0.6)', 'important');
                } else {
                    btn.className = 'btn btn-secondary pill-contexto-chat';
                    btn.style.setProperty('background', 'rgba(255,255,255,0.06)', 'important');
                    btn.style.setProperty('color', '#cbd5e1', 'important');
                    btn.style.setProperty('font-weight', '600', 'important');
                    btn.style.setProperty('border', '1px solid rgba(255,255,255,0.12)', 'important');
                }
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
            window.enviarMensagemChatUnificado();
        }
    };

    window.consultarPacoteOpComIa = function(idOp, assunto) {
        var textoPrompt = 'Como está o status e entregáveis do pacote OpenProject #' + idOp +
            ' (' + (assunto || 'Iniciativa SA-GTI') + ')? Apresente o resumo executivo e próximos passos.';
        var inp = document.getElementById('chat-input');
        if (inp) {
            inp.value = textoPrompt;
            window.enviarMensagemChatUnificado();
        }
    };

    window.renderizarListaContextoChat = function() {
        var container = document.getElementById('lista-contexto-chat-container');
        if (!container) return;

        var busca = (document.getElementById('busca-contexto-chat') ?
                     document.getElementById('busca-contexto-chat').value : '').toLowerCase().trim();
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var fixados = [];
        try { fixados = JSON.parse(localStorage.getItem('sagti_fixados') || '[]'); } catch(e) { fixados = []; }

        var elCFix = document.getElementById('chat-count-fixados');
        if (elCFix) elCFix.innerText = fixados.length;
        var elCSei = document.getElementById('chat-count-sei');
        if (elCSei) elCSei.innerText = baseProcs.length;

        var pacotesOpLuiz = [
            { id: '1185', assunto: 'PDTIC-E1-I01 - Backup corporativo e recuperação',
              tipo: 'Iniciativa PDTIC', status: 'Em progresso' },
            { id: '1231', assunto: 'Track 1 (Operação Atual) — Sustentação de Contratos',
              tipo: 'Fase / Track', status: 'Em progresso' },
            { id: '1232', assunto: 'Track 2: Renegociação e Readequação Contratual',
              tipo: 'Fase / Track', status: 'Em progresso' },
            { id: '1233', assunto: 'Configuração e Métricas do Portfólio',
              tipo: 'Tarefa', status: 'Concluído' }
        ];
        var elCOp = document.getElementById('chat-count-op');
        if (elCOp) elCOp.innerText = pacotesOpLuiz.length;

        var modo = window.abaContextoChatAtiva || 'fixados';
        var html = '';

        if (modo === 'fixados') {
            var procsFix = baseProcs.filter(function(p) { return fixados.indexOf(p.ID_Processo) !== -1; });
            if (busca) {
                procsFix = procsFix.filter(function(p) {
                    var s = (p.ID_Processo + ' ' + (p.Especificacao || '')).toLowerCase();
                    return s.indexOf(busca) !== -1;
                });
            }
            if (procsFix.length === 0) {
                html = '<div style="text-align:center;padding:28px 10px;color:#94a3b8;font-size:11.5px;">' +
                    '<span style="font-size:26px;display:block;margin-bottom:8px;">⭐</span>' +
                    '<strong style="color:#f1f5f9;">Nenhum processo fixado ainda.</strong><br>' +
                    '<span style="font-size:10.5px;color:#94a3b8;">' +
                    'Clique na estrela ao lado de qualquer processo no Acervo SEI para fixá-lo aqui.</span></div>';
            } else {
                procsFix.forEach(function(p) {
                    html += '<div style="background:rgba(30,41,59,0.75);border:1px solid rgba(255,255,255,0.08);' +
                        'border-left:3px solid #f59e0b;border-radius:8px;padding:9px 11px;display:flex;' +
                        'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                        '<strong style="font-family:monospace;font-size:11.5px;color:#38bdf8;">' + p.ID_Processo + '</strong>' +
                        '<span style="font-size:9.5px;background:rgba(245,158,11,0.2);color:#fbbf24;' +
                        'border:1px solid rgba(245,158,11,0.3);padding:1px 6px;border-radius:4px;font-weight:700;">' +
                        '⭐ Fixado</span></div>' +
                        '<div style="font-size:11.5px;color:#e2e8f0;white-space:nowrap;overflow:hidden;' +
                        'text-overflow:ellipsis;" title="' + (p.Especificacao || '') + '">' +
                        (p.Especificacao || 'Demanda TIC') + '</div>' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                        '<span style="font-size:10.5px;color:#94a3b8;">' + (p.Responsavel_Tecnico || 'SA-GTI') + '</span>' +
                        '<button type="button" class="btn btn-secondary" onclick="window.consultarProcessoComIa(\'' +
                        p.ID_Processo + '\', \'' + window.escapeHtml(p.Especificacao || '') + '\')" ' +
                        'style="padding:3px 8px;font-size:10.5px;background:rgba(56,189,248,0.18);' +
                        'border:1px solid rgba(56,189,248,0.4);color:#38bdf8;border-radius:4px;' +
                        'font-weight:700;cursor:pointer;">Consultar IA 💬</button>' +
                        '</div></div>';
                });
            }
        } else if (modo === 'sei') {
            var procsSei = baseProcs;
            if (busca) {
                procsSei = procsSei.filter(function(p) {
                    var s = (p.ID_Processo + ' ' + (p.Especificacao || '') + ' ' + (p.Responsavel_Tecnico || '')).toLowerCase();
                    return s.indexOf(busca) !== -1;
                });
            }
            procsSei.slice(0, 50).forEach(function(p) {
                var isFix = fixados.indexOf(p.ID_Processo) !== -1;
                html += '<div style="background:rgba(30,41,59,0.75);border:1px solid rgba(255,255,255,0.08);' +
                    'border-left:3px solid #0284c7;border-radius:8px;padding:9px 11px;display:flex;' +
                    'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                    '<strong style="font-family:monospace;font-size:11.5px;color:#38bdf8;">' + p.ID_Processo + '</strong>' +
                    (isFix ? '<span style="font-size:10px;color:#f59e0b;">⭐</span>' : '') + '</div>' +
                    '<div style="font-size:11.5px;color:#e2e8f0;white-space:nowrap;overflow:hidden;' +
                    'text-overflow:ellipsis;" title="' + (p.Especificacao || '') + '">' +
                    (p.Especificacao || 'Demanda TIC') + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                    '<span style="font-size:10.5px;color:#94a3b8;">' +
                    (p.Bucket_OpenProject ? p.Bucket_OpenProject.split('.')[0] : 'SA-GTI') + '</span>' +
                    '<button type="button" class="btn btn-secondary" onclick="window.consultarProcessoComIa(\'' +
                    p.ID_Processo + '\', \'' + window.escapeHtml(p.Especificacao || '') + '\')" ' +
                    'style="padding:3px 8px;font-size:10.5px;background:rgba(56,189,248,0.18);' +
                    'border:1px solid rgba(56,189,248,0.4);color:#38bdf8;border-radius:4px;' +
                    'font-weight:700;cursor:pointer;">Consultar IA 💬</button>' +
                    '</div></div>';
            });
            if (procsSei.length > 50) {
                html += '<div style="text-align:center;padding:8px;font-size:11px;color:#94a3b8;">' +
                        'Exibindo primeiros 50 processos. Use o filtro acima para refinar.</div>';
            }
        } else if (modo === 'op') {
            pacotesOpLuiz.forEach(function(p) {
                html += '<div style="background:rgba(30,41,59,0.75);border:1px solid rgba(255,255,255,0.08);' +
                    'border-left:3px solid #10b981;border-radius:8px;padding:9px 11px;display:flex;' +
                    'flex-direction:column;gap:5px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;">' +
                    '<strong style="font-family:monospace;font-size:11.5px;color:#34d399;">#' + p.id + '</strong>' +
                    '<span style="font-size:9.5px;background:rgba(16,185,129,0.2);color:#4ade80;' +
                    'border:1px solid rgba(16,185,129,0.3);padding:1px 6px;border-radius:4px;font-weight:700;">' +
                    p.status + '</span></div>' +
                    '<div style="font-size:11.5px;color:#e2e8f0;font-weight:600;white-space:nowrap;' +
                    'overflow:hidden;text-overflow:ellipsis;" title="' + p.assunto + '">' + p.assunto + '</div>' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px;">' +
                    '<span style="font-size:10.5px;color:#94a3b8;">' + p.tipo + '</span>' +
                    '<button type="button" class="btn btn-secondary" onclick="window.consultarPacoteOpComIa(\'' +
                    p.id + '\', \'' + window.escapeHtml(p.assunto) + '\')" ' +
                    'style="padding:3px 8px;font-size:10.5px;background:rgba(56,189,248,0.18);' +
                    'border:1px solid rgba(56,189,248,0.4);color:#38bdf8;border-radius:4px;' +
                    'font-weight:700;cursor:pointer;">Consultar IA 💬</button>' +
                    '</div></div>';
            });
        }

        container.innerHTML = html;
    };

    // 4. Mecanismo Anti-Travamento (Timeout rápido de 3.5s + Fallback determinístico garantido)
    window.enviarMensagemChatUnificado = async function() {
        var input = document.getElementById('chat-input');
        var txt = input ? input.value.trim() : '';
        var msgContainer = document.getElementById('chat-messages');
        if (!txt && (!window.arquivosAnexados || window.arquivosAnexados.length === 0)) return;

        var anexosHtml = '';
        if (window.arquivosAnexados && window.arquivosAnexados.length > 0) {
            var nomes = window.arquivosAnexados.map(function(a) { return window.escapeHtml(a.name); }).join(', ');
            anexosHtml = '<div style="margin-bottom:4px;font-size:11px;background:rgba(255,255,255,0.25);' +
                         'padding:4px 8px;border-radius:4px;">📎 <strong>Anexo(s):</strong> ' + nomes + '</div>';
            window.arquivosAnexados = [];
            if (typeof window.renderizarAnexosChips === 'function') window.renderizarAnexosChips();
        }

        msgContainer.innerHTML += '<div style="background:linear-gradient(135deg, #0284c7 0%, #0369a1 100%);' +
            'color:white;padding:11px 16px;border-radius:14px 14px 4px 14px;font-size:13px;align-self:flex-end;' +
            'max-width:82%;box-shadow:0 4px 12px rgba(2,132,199,0.3);line-height:1.5;">' +
            anexosHtml +
            '<div>' + window.escapeHtml(txt) + '</div></div>';
        if (input) input.value = '';
        msgContainer.scrollTop = msgContainer.scrollHeight;

        var poolAtivo = (typeof window.lerPoolTresIasAoVivo === 'function') ?
                        window.lerPoolTresIasAoVivo() : { ias: {} };
        var slotPrevisto = (typeof window.escolherSlotIaParaConsulta === 'function') ?
                           window.escolherSlotIaParaConsulta(txt) : 'orquestracao';
        var agPrevisto = (poolAtivo.ias && poolAtivo.ias[slotPrevisto] && poolAtivo.ias[slotPrevisto].agent) || 'IA Pessoal';

        var typingId = 'typing-' + Date.now();
        msgContainer.innerHTML += '<div id="' + typingId + '" ' +
            'style="background:rgba(30,41,59,0.9);border:1px solid rgba(255,255,255,0.1);' +
            'padding:10px 14px;border-radius:4px 14px 14px 14px;font-size:12px;color:#94a3b8;' +
            'align-self:flex-start;max-width:70%;display:flex;align-items:center;gap:8px;">' +
            '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#10b981;"></span>' +
            '<span>Pensando...</span></div>';
        msgContainer.scrollTop = msgContainer.scrollHeight;

        var ctx = null;
        var htmlAutomacao = '';
        var resultadoLlm = null;

        try {
            ctx = window.coletarContextoTotalSistemas(txt);
        } catch (eCtx) {
            ctx = { sinteseDeterministica: 'Base processual e normativa SA-GTI consultada.' };
        }

        try {
            var timeoutAuto = new Promise(function(resolve) { setTimeout(function() { resolve(''); }, 1200); });
            htmlAutomacao = await Promise.race([window.executarGatilhoAutomacaoChat(txt), timeoutAuto]);
        } catch (eAuto) {
            htmlAutomacao = '';
        }

        try {
            var timeoutLlm = new Promise(function(resolve) { setTimeout(function() { resolve(null); }, 4000); });
            resultadoLlm = await Promise.race([window.chamarNewApiClosedWorld(txt, ctx), timeoutLlm]);
        } catch (eLlm) {
            resultadoLlm = null;
        }

        var elTyping = document.getElementById(typingId);
        if (elTyping) elTyping.remove();

        window.historicoMensagensChat.push({ role: 'user', content: txt });
        if (resultadoLlm && resultadoLlm.texto) {
            window.historicoMensagensChat.push({ role: 'assistant', content: resultadoLlm.texto });
        } else {
            var resumoLimpo = String(ctx.sinteseDeterministica || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
            window.historicoMensagensChat.push({ role: 'assistant', content: resumoLimpo.slice(0, 350) });
        }

        var respostaFinalHtml = window.gerarBlocoDadosVerificados(
            txt, ctx, window.modeloDetectadoNewApi || agPrevisto, resultadoLlm, htmlAutomacao
        );

        msgContainer.innerHTML += '<div style="align-self:flex-start;width:100%;">' + respostaFinalHtml + '</div>';
        msgContainer.scrollTop = msgContainer.scrollHeight;
    };
    window.enviarMensagemChat = window.enviarMensagemChatUnificado;

    function aplicarEstilosDarkV11() {
        var gridChat = document.getElementById('grid-layout-chat-ia');
        if (gridChat) {
            gridChat.style.display = 'grid';
            gridChat.style.gridTemplateColumns = '320px 1fr';
            gridChat.style.gap = '14px';
        }

        var divLateral = document.getElementById('painel-contexto-operacional-chat');
        if (!divLateral && gridChat) {
            divLateral = document.createElement('div');
            divLateral.id = 'painel-contexto-operacional-chat';
            divLateral.className = 'chart-card';
            divLateral.style.cssText = 'height:100%;display:flex;flex-direction:column;padding:0;' +
                'overflow:hidden;background:rgba(15,23,42,0.85);backdrop-filter:blur(16px);' +
                'border:1px solid rgba(255,255,255,0.1);border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.3);';
            divLateral.innerHTML = '<div style="padding:12px 14px;background:rgba(15,23,42,0.95);' +
                'border-bottom:1px solid rgba(255,255,255,0.08);' +
                'display:flex;justify-content:space-between;align-items:center;">' +
                '<div><strong style="font-size:12.5px;color:#ffffff;display:flex;align-items:center;gap:6px;">' +
                '<span>📁</span> Contexto &amp; Demandas Rápidas</strong>' +
                '<div style="font-size:10.5px;color:#94a3b8;">Clique para consultar com a IA</div></div></div>' +
                '<div style="display:flex;gap:5px;padding:8px 10px;background:rgba(2,6,23,0.6);' +
                'border-bottom:1px solid rgba(255,255,255,0.08);">' +
                '<button type="button" class="btn btn-primary pill-contexto-chat active" id="btn-ctx-fixados" ' +
                'onclick="window.alternarAbaContextoChat(\'fixados\')" ' +
                'style="flex:1;padding:5px 6px;font-size:10.5px;border-radius:6px;font-weight:700;">' +
                '⭐ Fixados (<span id="chat-count-fixados">0</span>)</button>' +
                '<button type="button" class="btn btn-secondary pill-contexto-chat" id="btn-ctx-sei" ' +
                'onclick="window.alternarAbaContextoChat(\'sei\')" ' +
                'style="flex:1;padding:5px 6px;font-size:10.5px;border-radius:6px;font-weight:600;">' +
                '📂 Acervo (<span id="chat-count-sei">179</span>)</button>' +
                '<button type="button" class="btn btn-secondary pill-contexto-chat" id="btn-ctx-op" ' +
                'onclick="window.alternarAbaContextoChat(\'op\')" ' +
                'style="flex:1;padding:5px 6px;font-size:10.5px;border-radius:6px;font-weight:600;">' +
                '📦 OpenProj (<span id="chat-count-op">4</span>)</button>' +
                '</div>' +
                '<div style="padding:8px 10px;border-bottom:1px solid rgba(255,255,255,0.08);' +
                'background:rgba(15,23,42,0.7);">' +
                '<input type="text" id="busca-contexto-chat" placeholder="🔍 Filtrar lista..." ' +
                'oninput="window.renderizarListaContextoChat()" ' +
                'style="width:100%;box-sizing:border-box;padding:6px 10px;border-radius:6px;' +
                'border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.06);' +
                'color:#ffffff;font-size:11.5px;outline:none;">' +
                '</div>' +
                '<div id="lista-contexto-chat-container" ' +
                'style="flex:1;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:6px;' +
                'background:rgba(11,19,43,0.5);"></div>';

            gridChat.insertBefore(divLateral, gridChat.firstChild);
            window.renderizarListaContextoChat();
        } else if (divLateral) {
            divLateral.style.cssText = 'height:100%;display:flex;flex-direction:column;padding:0;' +
                'overflow:hidden;background:rgba(15,23,42,0.85);backdrop-filter:blur(16px);' +
                'border:1px solid rgba(255,255,255,0.1);border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.3);';
            window.renderizarListaContextoChat();
        }

        // Estiliza o Card de Chat na direita para Dark Theme V11 impecável
        var chatCard = document.querySelector('#grid-layout-chat-ia .chart-card:last-child');
        if (chatCard) {
            chatCard.style.cssText = 'height:100%;display:flex;flex-direction:column;padding:0;overflow:hidden;' +
                'background:rgba(15,23,42,0.85);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.1);' +
                'border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.3);';

            var headerChat = chatCard.querySelector('div:first-child');
            if (headerChat) {
                headerChat.style.cssText = 'padding:12px 18px;background:rgba(15,23,42,0.95);' +
                    'border-bottom:1px solid rgba(255,255,255,0.08);display:flex;' +
                    'justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;';

                var txtBox = headerChat.querySelector('div:first-child');
                if (txtBox) {
                    var strTit = txtBox.querySelector('strong');
                    if (strTit) strTit.style.cssText = 'font-size:14px;color:#ffffff;display:block;';
                    var strSub = txtBox.querySelector('div');
                    if (strSub) strSub.style.cssText = 'font-size:11.5px;color:#94a3b8;margin-top:2px;';
                }

                var containerBotoes = headerChat.querySelector('div:last-child');
                if (containerBotoes && !document.getElementById('btn-header-reiniciar-chat')) {
                    var btnReiniciar = document.createElement('button');
                    btnReiniciar.type = 'button';
                    btnReiniciar.id = 'btn-header-reiniciar-chat';
                    btnReiniciar.className = 'btn btn-secondary';
                    btnReiniciar.setAttribute('onclick', 'window.reiniciarConversaChat()');
                    btnReiniciar.style.cssText = 'padding:6px 12px;font-size:11px;background:rgba(239,68,68,0.18);' +
                        'border:1px solid rgba(239,68,68,0.4);color:#fca5a5;font-weight:700;cursor:pointer;' +
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
                barraSugestoes.style.cssText = 'display:flex;gap:8px;overflow-x:auto;padding:10px 14px;' +
                    'background:rgba(15,23,42,0.92);border-top:1px solid rgba(255,255,255,0.08);align-items:center;';

                if (!document.getElementById('btn-sugestao-iniciar-doc')) {
                    var btnDoc = document.createElement('button');
                    btnDoc.type = 'button';
                    btnDoc.id = 'btn-sugestao-iniciar-doc';
                    btnDoc.className = 'btn btn-secondary pill-tag';
                    btnDoc.style.cssText = 'padding:5px 12px;font-size:11px;cursor:pointer;border-radius:14px;' +
                        'background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);' +
                        'color:#e2e8f0;font-weight:600;white-space:nowrap;';
                    btnDoc.innerHTML = '📄 Iniciar Documentação (DFD/ETP/TR)';
                    var pDoc = 'Quero iniciar a elaboração de uma nova documentação técnica de TIC ' +
                               '(DFD, ETP ou Termo de Referência pela Lei 14.133/2021). ' +
                               'Qual o passo a passo e modelo recomendado?';
                    btnDoc.onclick = function() { window.dispararPerguntaDireta(pDoc); };

                    var btnProc = document.createElement('button');
                    btnProc.type = 'button';
                    btnProc.id = 'btn-sugestao-iniciar-proc';
                    btnProc.className = 'btn btn-secondary pill-tag';
                    btnProc.style.cssText = 'padding:5px 12px;font-size:11px;cursor:pointer;border-radius:14px;' +
                        'background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);' +
                        'color:#e2e8f0;font-weight:600;white-space:nowrap;';
                    btnProc.innerHTML = '📂 Iniciar Processo SEI';
                    var pProc = 'Preciso iniciar a instrução de um novo processo administrativo no SEI-SP ' +
                                'para a SA-GTI. Quais documentos e justificativas iniciais são obrigatórios?';
                    btnProc.onclick = function() { window.dispararPerguntaDireta(pProc); };

                    var btnRev = document.createElement('button');
                    btnRev.type = 'button';
                    btnRev.id = 'btn-sugestao-revisar';
                    btnRev.className = 'btn btn-secondary pill-tag';
                    btnRev.style.cssText = 'padding:5px 12px;font-size:11px;cursor:pointer;border-radius:14px;' +
                        'background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);' +
                        'color:#e2e8f0;font-weight:600;white-space:nowrap;';
                    btnRev.innerHTML = '🔍 Revisar em Andamento';
                    var pRev = 'Quero revisar uma minuta de documento técnico ou processo que já está em andamento ' +
                               'para verificar conformidade com as regras da autarquia e apontar melhorias.';
                    btnRev.onclick = function() { window.dispararPerguntaDireta(pRev); };

                    barraSugestoes.appendChild(btnDoc);
                    barraSugestoes.appendChild(btnProc);
                    barraSugestoes.appendChild(btnRev);
                }
            }

            var inputBar = document.querySelector('#view-esteira_ia div[style*="padding: 12px 18px; background: #ffffff;"]');
            if (inputBar) {
                inputBar.style.cssText = 'padding:12px 18px;background:rgba(15,23,42,0.95);' +
                    'border-top:1px solid rgba(255,255,255,0.08);display:flex;gap:8px;align-items:center;';
                var inp = document.getElementById('chat-input');
                if (inp) {
                    inp.style.cssText = 'flex:1;padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.15);' +
                        'background:rgba(255,255,255,0.06);color:#ffffff;font-size:12.5px;outline:none;';
                }
            }
        }
    }

    aplicarEstilosDarkV11();
    document.addEventListener('DOMContentLoaded', aplicarEstilosDarkV11);
    window.addEventListener('load', aplicarEstilosDarkV11);
    setInterval(function() {
        if (window.currentTab === 'esteira_ia') {
            aplicarEstilosDarkV11();
        }
    }, 1200);
})();
</script>'''

for filepath in targets:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    orig_len = len(text)
    idx_existing = text.find('<script id="script-melhorias-esteira-ia-v11">')
    if idx_existing != -1:
        idx_end = text.find('</script>', idx_existing)
        if idx_end != -1:
            text = text[:idx_existing] + js_melhorias_chat + text[idx_end + len('</script>'):]
    else:
        idx_body = text.rfind('</body>')
        if idx_body != -1:
            text = text[:idx_body] + '\n' + js_melhorias_chat + '\n' + text[idx_body:]
        else:
            text = text + '\n' + js_melhorias_chat

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"[OK] Contraste Dark V11 e Anti-Travamento aplicados em: {filepath} ({orig_len} -> {len(text)} bytes)")
