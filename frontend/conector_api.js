/**
 * Cockpit GTI — Conector Oficial de Telemetria e Navegação em 5 Pilares Consolidados
 * SP-Águas SA-GTI
 */
(function () {
    // 1. ROTEADOR DE NAVEGAÇÃO E PERSISTÊNCIA DE ABA (HASH #tab)
    window.rotearAba = function (tabId) {
        if (!tabId) tabId = 'dashboards';

        // Redirecionamento transparente de fixados para a Mesa de Trabalho
        if (tabId === 'fixados') {
            tabId = 'mesa_trabalho';
            setTimeout(function() {
                var elF = document.getElementById('tbody-fixados');
                if (elF && elF.scrollIntoView) elF.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }

        if (window.location.hash !== '#' + tabId) {
            window.location.hash = '#' + tabId;
        }

        if (typeof window.switchTab === 'function') {
            try {
                window.switchTab(tabId);
            } catch (e) {
                console.warn('Aviso switchTab:', e);
            }
        }

        document.querySelectorAll('.sidebar-menu .nav-item').forEach(function (el) {
            if (el.getAttribute('data-tab') === tabId) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });

        var mainEl = document.getElementById('main') || document.querySelector('.content-scroll');
        if (mainEl) mainEl.scrollTop = 0;
    };

    // 2. MENU LATERAL EM 5 PILARES (14 TELAS COESAS)
    function aplicarMenu5Pilares() {
        var sidebarMenu = document.querySelector('.sidebar-menu');
        if (!sidebarMenu) return;

        var htmlMenu = [
            '<div class="menu-category">1. VISÃO EXECUTIVA &amp; LIDERANÇA</div>',
            '<div class="nav-item active" data-tab="dashboards" onclick="window.rotearAba(\'dashboards\')">',
            '    <div class="nav-item-left">&#128202; <span>Central de Dashboards 360°</span></div>',
            '    <span class="nav-badge">360°</span>',
            '</div>',
            '<div class="nav-item" data-tab="visao_estrategica" onclick="window.rotearAba(\'visao_estrategica\')">',
            '    <div class="nav-item-left">&#127919; <span>Faróis de Criticidade &amp; Prazos</span></div>',
            '    <span class="nav-badge">87</span>',
            '</div>',
            '<div class="nav-item" data-tab="portfolio_openproject" onclick="window.rotearAba(\'portfolio_openproject\')">',
            '    <div class="nav-item-left">&#127959;&#65039; <span>Portfólio Geral OpenProject</span></div>',
            '    <span class="nav-badge" style="background:#10b981; color:#fff;">500</span>',
            '</div>',

            '<div class="menu-category">2. GESTÃO DE TIC &amp; CONTRATOS</div>',
            '<div class="nav-item" data-tab="tracks_sagti" onclick="window.rotearAba(\'tracks_sagti\')">',
            '    <div class="nav-item-left">&#9889; <span>Tracks 1 &amp; 2 (Operação &amp; Contratos)</span></div>',
            '    <span class="nav-badge" style="background:#0544cf; color:#fff;">97</span>',
            '</div>',
            '<div class="nav-item" data-tab="pdtic_eixos" onclick="window.rotearAba(\'pdtic_eixos\')">',
            '    <div class="nav-item-left">&#129517; <span>Governança PDTIC 2027-2030 &amp; KPIs</span></div>',
            '    <span class="nav-badge" style="background:#6366f1; color:#fff;">35</span>',
            '</div>',
            '<div class="nav-item" data-tab="gestao_glpi" onclick="window.rotearAba(\'gestao_glpi\')">',
            '    <div class="nav-item-left">&#127915; <span>Atendimento GLPI 10 (ITSM)</span></div>',
            '    <span class="nav-badge" style="background:#0284c7; color:#fff;">203</span>',
            '</div>',
            '<div class="nav-item" data-tab="consulta" onclick="window.rotearAba(\'consulta\')">',
            '    <div class="nav-item-left">&#128194; <span>Acervo Probatório SEI-SP</span></div>',
            '    <span class="nav-badge">179</span>',
            '</div>',

            '<div class="menu-category">3. OPERAÇÃO ÁGIL &amp; RITUAIS</div>',
            '<div class="nav-item" data-tab="mesa_trabalho" onclick="window.rotearAba(\'mesa_trabalho\')">',
            '    <div class="nav-item-left">&#128421;&#65039; <span>Mesa de Trabalho Operacional</span></div>',
            '    <span class="nav-badge" style="background:#00a859; color:white;">Demandas</span>',
            '</div>',
            '<div class="nav-item" data-tab="gestao_agil" onclick="window.rotearAba(\'gestao_agil\')">',
            '    <div class="nav-item-left">&#128203; <span>Sprint Planning &amp; Kanban</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="daily_warroom" onclick="window.rotearAba(\'daily_warroom\')">',
            '    <div class="nav-item-left">&#9201;&#65039; <span>War Room Daily Scrum</span></div>',
            '</div>',

            '<div class="menu-category">4. INTELIGÊNCIA &amp; CONFORMIDADE</div>',
            '<div class="nav-item" data-tab="esteira_ia" onclick="window.rotearAba(\'esteira_ia\')">',
            '    <div class="nav-item-left">&#129302; <span>Assistente Pessoal IA &amp; RACI</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="auditoria" onclick="window.rotearAba(\'auditoria\')">',
            '    <div class="nav-item-left">&#128737;&#65039; <span>Hub de Auditoria TCE-SP &amp; IMR</span></div>',
            '</div>',

            '<div class="menu-category">5. GOVERNANÇA, CADERNOS &amp; INFRA</div>',
            '<div class="nav-item" data-tab="cadernos" onclick="window.rotearAba(\'cadernos\')">',
            '    <div class="nav-item-left">&#128218; <span>Cadernos Temáticos &amp; Minutas A4</span></div>',
            '</div>',
            '<div class="nav-item" data-tab="configuracoes" onclick="window.rotearAba(\'configuracoes\')">',
            '    <div class="nav-item-left">&#128295; <span>Central de Configurações &amp; RBAC</span></div>',
            '</div>'
        ].join('\n');

        sidebarMenu.innerHTML = htmlMenu;
    }

    // 3. SINCRONISMO COM A URL HASH
    function sincAbaHash() {
        var hash = window.location.hash.replace('#', '').trim();
        if (hash) {
            window.rotearAba(hash);
        }
    }

    // 4. TELEMETRIA DA INFRAESTRUTURA (:5000)
    async function atualizarTelemetria() {
        var sMariaDB = false, sOllama = false, sGlpi = false, sOpenProject = false, sNewApi = false;
        try {
            var ctrl = new AbortController();
            var tid = setTimeout(function () { ctrl.abort(); }, 1800);
            var rStatus = await fetch('/api/v1/telemetria', { signal: ctrl.signal, cache: 'no-store' });
            clearTimeout(tid);
            if (rStatus.ok) {
                var json = await rStatus.json();
                sMariaDB = Boolean(json.mariadb);
                sOllama = Boolean(json.ollama);
                sGlpi = Boolean(json.glpi);
                sOpenProject = Boolean(json.openproject);
                sNewApi = Boolean(json.newapi);
            }
        } catch (eUni) {}

        var elMariaDB = document.getElementById('led-mariadb');
        var elOllama = document.getElementById('led-ollama');
        var elGlpi = document.getElementById('led-glpi');
        var elOp = document.getElementById('led-openproject');
        var elNewApi = document.getElementById('led-newapi');

        if (elMariaDB) elMariaDB.textContent = sMariaDB ? '\u{1F7E2}' : '\u{1F534}';
        if (elOllama) elOllama.textContent = sOllama ? '\u{1F7E2}' : '\u{1F534}';
        if (elGlpi) elGlpi.textContent = sGlpi ? '\u{1F7E2}' : '\u{1F534}';
        if (elOp) elOp.textContent = sOpenProject ? '\u{1F7E2}' : '\u{1F534}';
        if (elNewApi) elNewApi.textContent = sNewApi ? '\u{1F7E2}' : '\u{1F534}';

        var elSinc = document.getElementById('tempo-sinc');
        if (elSinc) {
            var agora = new Date();
            elSinc.textContent = agora.toLocaleTimeString('pt-BR');
        }
    }

    function montarWidgetInfra() {
        var topbar = document.querySelector('.topbar') || document.querySelector('#topbar') || document.querySelector('header');
        if (!topbar) return;

        var containerInfra = document.getElementById('widget-infra-cockpit');
        if (!containerInfra) {
            containerInfra = document.createElement('div');
            containerInfra.id = 'widget-infra-cockpit';
            containerInfra.style.display = 'inline-flex';
            containerInfra.style.alignItems = 'center';
            containerInfra.style.gap = '8px';
            containerInfra.style.margin = '0 10px';
            containerInfra.style.flexShrink = '0';

            containerInfra.innerHTML = [
                '<div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 16px; font-size: 11px; color: #334155;">',
                '    <span style="font-weight: 700; letter-spacing: 0.5px; color: #0f172a;">INFRA :5000</span>',
                '    <span id="led-mariadb" title="MariaDB (:3306)">\u{1F7E2}</span>',
                '    <span id="led-ollama" title="Ollama (:11434)">\u{1F7E2}</span>',
                '    <span id="led-glpi" title="GLPI Produção (Read-Only)">\u{1F7E2}</span>',
                '    <span id="led-openproject" title="OpenProject Produção (Trava SA-GTI)">\u{1F7E2}</span>',
                '    <span id="led-newapi" title="New API (:3001)">\u{1F7E2}</span>',
                '    <span style="color: #64748b; margin-left: 4px;">Sinc:</span>',
                '    <span id="tempo-sinc" style="font-weight: 600; color: #0f172a;">--:--:--</span>',
                '    <span id="btn-recarregar-infra" style="cursor: pointer; opacity: 0.8;" title="Recarregar Telemetria">&#128260;</span>',
                '</div>'
            ].join('\n');

            var elRef = topbar.querySelector('.user-pill') || topbar.querySelector('.user-profile') || topbar.querySelector('select') || null;
            if (elRef && elRef.parentNode) {
                elRef.parentNode.insertBefore(containerInfra, elRef);
            } else {
                topbar.appendChild(containerInfra);
            }

            var btnRec = document.getElementById('btn-recarregar-infra');
            if (btnRec) btnRec.addEventListener('click', atualizarTelemetria);
        }
    }

    // 5. INICIALIZAÇÃO
    
    // --- CONEXÃO AO VIVO COM A BASE DE PROCESSOS DO MARIADB ---
    window.atualizarCardsDashboardsAoVivo = async function() {
        try {
            var resp = await fetch('/api/v1/processos/estatisticas', { cache: 'no-store' });
            if (resp.ok) {
                var json = await resp.json();
                if (json.status === 'sucesso' && json.metricas) {
                    var m = json.metricas;
                    
                    // 1. Total de Processos
                    var elTotal = document.getElementById('kpi-val-acervo-total');
                    if (elTotal) {
                        elTotal.textContent = m.total_processos || 0;
                        var card = elTotal.closest('.kpi-card');
                        var spanSub = card ? card.querySelector('span') : null;
                        if (spanSub) {
                            spanSub.innerHTML = '🟢 Base Viva (MariaDB &amp; SEI-SP)';
                            spanSub.style.color = '#10b981';
                            spanSub.style.fontWeight = '700';
                        }
                    }

                    // 2. Farois de Criticidade (Apurados via SQL)
                    var elInt = document.getElementById('kpi-val-intervencao');
                    if (elInt) elInt.textContent = m.farol_vermelho || 0;

                    var elSan = document.getElementById('kpi-val-saneamento');
                    if (elSan) elSan.textContent = m.farol_laranja || 0;

                    var elMon = document.getElementById('kpi-val-monitoramento');
                    if (elMon) elMon.textContent = m.farol_amarelo || 0;

                    var elFlux = document.getElementById('kpi-val-fluxo-normal');
                    if (elFlux) elFlux.textContent = m.farol_verde || 0;

                    // 3. Sub-totais por Eixo de Gestao
                    var elRot = document.getElementById('kpi-val-rotina');
                    if (elRot) elRot.textContent = (m.total_rotina || 0) + ' processos';
                }
            }
        } catch (e) {
            console.warn('Conexao viva com MariaDB processos_sei pendente:', e);
        }
    };

    
    // --- ATUALIZAÇÃO AO VIVO DA ABA 2 (VISÃO ESTRATÉGICA & PORÉNS) ---
    window.atualizarVisaoEstrategicaAoVivo = async function() {
        try {
            var resp = await fetch('/api/v1/processos/estatisticas', { cache: 'no-store' });
            if (resp.ok) {
                var json = await resp.json();
                if (json.status === 'sucesso' && json.metricas) {
                    var m = json.metricas;
                    var taticos = m.total_taticos_ativos || 87;
                    var porens = m.total_porens || 25;
                    var internos = Math.max(0, taticos - porens);

                    // 1. Scorecards de Custodia
                    var elInt = document.getElementById('visao-kpi-interno');
                    if (elInt) elInt.textContent = internos;

                    var elExt = document.getElementById('visao-kpi-externo');
                    if (elExt) {
                        elExt.textContent = porens;
                        var card = elExt.closest('.kpi-card');
                        var spanSub = card ? card.querySelector('span') : null;
                        if (spanSub) {
                            spanSub.innerHTML = '🟢 Base Viva (MariaDB: ' + porens + ' suspensões)';
                            spanSub.style.color = '#10b981';
                            spanSub.style.fontWeight = '700';
                        }
                    }

                    // 2. Pills de Farois com contagem real
                    var bTodos = document.getElementById('btn-filtro-todos');
                    if (bTodos) bTodos.textContent = '🌐 Todos os Processos (' + taticos + ')';

                    var bVerm = document.getElementById('btn-filtro-vermelho');
                    if (bVerm) bVerm.textContent = '🔴 1 - Intervenção Imediata (' + (m.farol_vermelho || 0) + ')';

                    var bLaranja = document.getElementById('btn-filtro-laranja');
                    if (bLaranja) bLaranja.textContent = '🟠 2 - Saneamento Prioritário (' + (m.farol_laranja || 0) + ')';

                    var bAmarelo = document.getElementById('btn-filtro-amarelo');
                    if (bAmarelo) bAmarelo.textContent = '🟡 3 - Monitoramento Ativo (' + (m.farol_amarelo || 0) + ')';

                    var bVerde = document.getElementById('btn-filtro-verde');
                    if (bVerde) bVerde.textContent = '🟢 4 - Fluxo Normal (' + (m.farol_verde || 0) + ')';
                }
            }
        } catch (e) {
            console.warn('Conexão com MariaDB para Aba 2:', e);
        }
    };

    // Filtro rapido de texto na tabela estrategica
    window.filtrarBuscaRapidaEstrategica = function(termo) {
        var termoLow = (termo || '').toLowerCase().trim();
        var linhas = document.querySelectorAll('#tbody-visao-estrategica tr');
        linhas.forEach(function(tr) {
            var txt = tr.textContent.toLowerCase();
            tr.style.display = (termoLow === '' || txt.indexOf(termoLow) !== -1) ? '' : 'none';
        });
    };

    
    // --- MOTOR GLOBAL DO MODAL DE PROCESSO, TIMELINE E DOSSIÊ ---
    window.abrirDetalhesProcesso = function (idProcesso) {
        if (!idProcesso) return;
        var lista = window.PROCESSOS || (typeof PROCESSOS !== 'undefined' ? PROCESSOS : []);
        var p = lista.find(function (item) {
            return (item.ID_Processo === idProcesso || item.id_processo === idProcesso || item.id === idProcesso);
        });
        if (!p) {
            console.warn('Processo não localizado na memória:', idProcesso);
            return;
        }

        // Gera a timeline e governança institucional
        var timelineHtml = (typeof window.gerarTimelineProcessualHtml === 'function')
            ? window.gerarTimelineProcessualHtml(p)
            : '';

        var modTit = document.getElementById('modal-titulo');
        if (modTit) modTit.innerText = 'Processo SEI: ' + (p.ID_Processo || p.id_processo);

        var modCont = document.getElementById('modal-conteudo');
        if (modCont) {
            var idP = p.ID_Processo || p.id_processo;
            modCont.innerHTML = timelineHtml + [
                '<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; padding: 12px 14px; border-radius: 6px; margin: 14px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">',
                '    <div>',
                '        <strong style="color: #14532d; font-size: 12px;">🌐 Consulta em Tempo Real no Site Oficial (PNCP / Compras SP / SEI)</strong>',
                '        <div style="font-size: 11px; color: #15803d; margin-top: 2px;">Verifique publicações da Lei 14.133, andamento no SEI-SP ou atas homologadas no PNCP.</div>',
                '    </div>',
                '    <div style="display: flex; gap: 8px;">',
                '        <button class="btn btn-primary" onclick="window.consultarProcessoAoVivoPNCP(\'' + idP + '\')" style="background: #01a75f; border-color: #01a75f; font-size: 11px; padding: 5px 12px; font-weight: 700; cursor: pointer;">🔍 Checar no Site Oficial</button>',
                '        <a href="https://pncp.gov.br/app/editais?q=' + encodeURIComponent(idP) + '" target="_blank" class="btn btn-secondary" style="font-size: 11px; padding: 5px 10px; text-decoration: none; color: #002d5a; font-weight: 600;">Abrir PNCP ↗</a>',
                '        <a href="https://sei.sp.gov.br/sei/controlador_externo.php?acao=usuario_externo_consultar&id_orgao_acesso_externo=0" target="_blank" class="btn btn-secondary" style="font-size: 11px; padding: 5px 10px; text-decoration: none; color: #002d5a; font-weight: 600;">Abrir SEI-SP ↗</a>',
                '    </div>',
                '</div>',
                '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; font-size: 12px;">',
                '    <div><strong>Eixo de Gestão:</strong> ' + (p.Eixo_Gestao || p.eixo_gestao || '-') + '</div>',
                '    <div><strong>Bucket OpenProject:</strong> ' + (p.Bucket_OpenProject || p.bucket_openproject || '-') + '</div>',
                '    <div><strong>Status OpenProject:</strong> ' + (p.Status_OpenProject || p.status_openproject || '-') + '</div>',
                '    <div><strong>Farol Criticidade:</strong> ' + (p.Farol_Criticidade || p.farol_criticidade || '-') + '</div>',
                '    <div><strong>Faixa Aging:</strong> ' + (p.Faixa_Aging || p.faixa_aging || '-') + ' (' + (p.Dias_Ultima_Mov || p.dias_ultima_mov || 0) + ' dias sem mov.)</div>',
                '    <div><strong>Classificação de Risco:</strong> ' + (p.Classificacao_Risco || p.classificacao_risco || '-') + '</div>',
                '    <div><strong>Responsável Técnico:</strong> ' + (p.Responsavel_Tecnico || p.responsavel_tecnico || 'Não atribuído') + '</div>',
                '    <div><strong>Tipo de Processo:</strong> ' + (p.Tipo_Processo || p.tipo_processo || '-') + '</div>',
                '</div>',
                '<div style="margin-bottom: 12px;">',
                '    <strong>Especificação da Demanda:</strong>',
                '    <p style="background: #f1f5f9; padding: 10px; border-radius: 6px; margin-top: 4px; font-size: 12px; line-height: 1.45;">' + (p.Especificacao || p.especificacao || '-') + '</p>',
                '</div>',
                '<div style="margin-bottom: 12px;">',
                '    <strong>Observações / Contexto:</strong>',
                '    <p style="background: #f8fafc; padding: 10px; border-radius: 6px; margin-top: 4px; border: 1px solid #e2e8f0; font-size: 12px; line-height: 1.45;">' + (p.Observacao_Texto || p.observacao_texto || 'Sem observações adicionais registradas.') + '</p>',
                '</div>'
            ].join('\n');
        }

        var modEl = document.getElementById('modal-processo');
        if (modEl) {
            modEl.style.display = 'flex';
            modEl.style.position = 'fixed';
            modEl.style.inset = '0';
            modEl.style.zIndex = '99999';
            modEl.style.background = 'rgba(15, 23, 42, 0.65)';
            modEl.style.alignItems = 'center';
            modEl.style.justifyContent = 'center';
            modEl.style.padding = '20px';
        }
    };

    window.fecharModalProcesso = function () {
        var modEl = document.getElementById('modal-processo');
        if (modEl) modEl.style.display = 'none';
    };

    
    // --- ENRIQUECIMENTO AUTOMÁTICO DA TABELA DE VISÃO ESTRATÉGICA ---
    window.enriquecerTabelaVisaoEstrategica = function () {
        var tbody = document.getElementById('tbody-visao-estrategica');
        if (!tbody) return;

        var linhas = tbody.querySelectorAll('tr');
        linhas.forEach(function (tr) {
            var tdId = tr.querySelector('td:first-child');
            var tdAcoes = tr.querySelector('td:last-child');

            // Torna o numero SEI azul e clicavel
            if (tdId && !tdId.querySelector('a')) {
                var numSei = tdId.textContent.trim();
                if (/^\d{3}\.\d{5,8}\/\d{4}-\d{2}$/.test(numSei)) {
                    tdId.innerHTML = '<a href="javascript:void(0)" onclick="window.abrirDetalhesProcesso(\'' + numSei + '\')" style="color: #0544cf; font-weight: 700; text-decoration: underline; cursor: pointer;" title="Abrir Dossiê & Timeline">' + numSei + '</a>';
                }
            }

            // Injeta o botao azul Dossie antes do botao de Checkpoint
            if (tdAcoes && !tdAcoes.querySelector('.btn-dossie-injetado')) {
                var btnCk = tdAcoes.querySelector('button');
                var numProc = '';
                if (btnCk) {
                    var m = (btnCk.getAttribute('onclick') || '').match(/'([^']+)'/);
                    if (m && m[1]) numProc = m[1];
                }
                if (!numProc && tdId) {
                    var m2 = tdId.textContent.trim().match(/\d{3}\.\d{5,8}\/\d{4}-\d{2}/);
                    if (m2) numProc = m2[0];
                }

                if (numProc) {
                    var btnDos = document.createElement('button');
                    btnDos.className = 'btn btn-primary btn-dossie-injetado';
                    btnDos.style.cssText = 'padding: 3px 8px; font-size: 11px; margin-right: 4px; background: #0070ba; border-color: #0070ba; color: white; font-weight: 700; cursor: pointer;';
                    btnDos.innerHTML = '🔍 Dossiê';
                    btnDos.onclick = function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        window.abrirDetalhesProcesso(numProc);
                    };
                    if (btnCk) {
                        tdAcoes.insertBefore(btnDos, btnCk);
                    } else {
                        tdAcoes.appendChild(btnDos);
                    }
                }
            }
        });
    };

    // --- DELEGAÇÃO GLOBAL DE CLIQUES EM QUALQUER PROCESSO SEI DO COCKPIT ---
    document.addEventListener('click', function (e) {
        // Se clicou no botao Checkpoint, permite que ele abra a minuta de notificacao
        if (e.target.closest('button') && e.target.closest('button').textContent.indexOf('Checkpoint') !== -1) {
            return;
        }

        var cell = e.target.closest('td, strong, span, a');
        if (cell && !cell.closest('button')) {
            var txt = cell.textContent.trim();
            var m = txt.match(/\b(\d{3}\.\d{5,8}\/\d{4}-\d{2})\b/);
            if (m && m[1]) {
                if (!e.target.closest('#modal-processo') && !e.target.closest('#modal-checkpoint')) {
                    e.preventDefault();
                    window.abrirDetalhesProcesso(m[1]);
                }
            }
        }
    }, true);

    
    // --- FILTRO RÁPIDO EM PILLS DO OPENPROJECT ---
    window.filtrarModoRapidoOP = function (modo) {
        document.querySelectorAll('.pill-filtro-op').forEach(function (b) {
            b.className = 'btn btn-secondary pill-filtro-op';
        });
        var btnAtivo = document.getElementById('btn-op-' + modo);
        if (btnAtivo) btnAtivo.className = 'btn btn-primary pill-filtro-op';

        var selProj = document.getElementById('op-filtro-projeto');
        var selStatus = document.getElementById('op-filtro-status');
        var inpBusca = document.getElementById('op-filtro-busca');

        if (selProj) selProj.value = '';
        if (selStatus) selStatus.value = '';
        if (inpBusca) inpBusca.value = '';

        if (modo === 'sagti') {
            if (selProj) selProj.value = 'SA-GTI - Gerência de TI';
        } else if (modo === 'pdtic') {
            if (inpBusca) inpBusca.value = 'PDTIC';
        } else if (modo === 'progresso') {
            if (selStatus) selStatus.value = 'progresso';
        } else if (modo === 'espera') {
            if (selStatus) selStatus.value = 'espera';
        }

        if (typeof window.filtrarPortfolioOpenProject === 'function') {
            window.filtrarPortfolioOpenProject();
        }
    };

    function init() {
        aplicarMenu5Pilares();
        montarWidgetInfra();
        atualizarTelemetria();
        window.atualizarCardsDashboardsAoVivo();
        window.atualizarVisaoEstrategicaAoVivo();
        window.enriquecerTabelaVisaoEstrategica();
        setInterval(window.enriquecerTabelaVisaoEstrategica, 1500);
        sincAbaHash();
        window.addEventListener('hashchange', sincAbaHash);
        setInterval(atualizarTelemetria, 15000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
