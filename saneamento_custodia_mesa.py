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

js_mesa_custodia = r'''<script id="script-saneamento-custodia-mesa-v11">
(function() {
    try {
        if (!localStorage.getItem('sagti_custodia_saneada_v11')) {
            localStorage.setItem('sagti_fixados', '[]');
            localStorage.setItem('sagti_custodia_saneada_v11', 'true');
        }
    } catch (e) {}

    window.modoMesaAtivo = window.modoMesaAtivo || 'custodia';
    window.paginaMesa = 1;
    window.tamanhoPaginaMesa = 15;

    function obterFixadosValidos() {
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var raw = [];
        try {
            raw = JSON.parse(localStorage.getItem('sagti_fixados') || '[]');
        } catch (e) { raw = []; }
        var idsBase = {};
        baseProcs.forEach(function(p) {
            if (p && p.ID_Processo) idsBase[p.ID_Processo] = true;
        });
        return raw.filter(function(id) { return !!idsBase[id]; });
    }

    function obterCustodiaNominalLuiz() {
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        return baseProcs.filter(function(p) {
            var resp = (p.Responsavel_Tecnico || '').toLowerCase().trim();
            return resp.indexOf('luiz') !== -1 || resp.indexOf('seixeiro') !== -1;
        });
    }

    function obterPacotesOpLuiz() {
        var opDados = Array.isArray(window.OP_PACOTES_OFICIAIS) ? window.OP_PACOTES_OFICIAIS : [];
        var filtrados = opDados.filter(function(p) {
            var atrib = (p.atrib || '').toLowerCase();
            var autor = (p.autor || '').toLowerCase();
            var encarr = (p.encarr || '').toLowerCase();
            return atrib.indexOf('luiz antonio') !== -1 || atrib.indexOf('seixeiro') !== -1 ||
                   autor.indexOf('luiz antonio') !== -1 || autor.indexOf('seixeiro') !== -1 ||
                   encarr.indexOf('luiz antonio') !== -1 || encarr.indexOf('seixeiro') !== -1;
        });
        if (filtrados.length > 0) return filtrados;
        return [
            { id: '1185', assunto: 'PDTIC-E1-I01 - Programa corporativo de backup, retenção e restauração',
              projeto: 'SA-GTI - Gerência de TI', atrib: 'Luiz Antonio Seixeiro',
              status: 'Em progresso', tipo: 'Iniciativa PDTIC', ini: '01/10/2025', fim: '30/12/2026' },
            { id: '1231', assunto: 'Track 1 (Operação Atual) — Sustentação e Gestão dos Contratos Vigentes',
              projeto: 'SA-GTI - Gerência de TI', atrib: 'Luiz Antonio Seixeiro',
              status: 'Em progresso', tipo: 'Fase / Track', ini: '01/09/2025', fim: '31/12/2026' },
            { id: '1232', assunto: 'Track 2: Renegociação e Readequação Contratual',
              projeto: 'SA-GTI - Gerência de TI', atrib: 'Luiz Antonio Seixeiro',
              status: 'Em progresso', tipo: 'Fase / Track', ini: '01/10/2025', fim: '31/12/2026' },
            { id: '1233', assunto: 'Configuração Estrutural e Parametrização de Métricas do Portfólio',
              projeto: 'SA-GTI - Gerência de TI', atrib: 'Luiz Antonio Seixeiro',
              status: 'Concluído', tipo: 'Entregável / Tarefa', ini: '01/09/2025', fim: '30/10/2026' }
        ];
    }

    window.atualizarContadoresCustodiaMesa = function() {
        var custodiaNominal = obterCustodiaNominalLuiz();
        var fixadosValidos = obterFixadosValidos();
        var pacotesOpLuiz = obterPacotesOpLuiz();
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];

        var elKpiCustodia = document.getElementById('mesa-kpi-custodia');
        if (elKpiCustodia) elKpiCustodia.innerText = String(custodiaNominal.length);

        var elCountCustodia = document.getElementById('count-mesa-custodia');
        if (elCountCustodia) elCountCustodia.innerText = String(custodiaNominal.length);

        var btnCust = document.getElementById('btn-mesa-custodia');
        if (btnCust && !elCountCustodia) {
            btnCust.innerHTML = '📌 Minha Custódia (<span id="count-mesa-custodia">' +
                                custodiaNominal.length + '</span>)';
        }

        var elCountFixados = document.getElementById('count-mesa-fixados');
        if (elCountFixados) elCountFixados.innerText = String(fixadosValidos.length);

        var elCountOp = document.getElementById('count-mesa-op');
        if (elCountOp) elCountOp.innerText = String(pacotesOpLuiz.length);

        var elCountAcervo = document.getElementById('count-mesa-acervo');
        if (elCountAcervo) elCountAcervo.innerText = String(baseProcs.length);

        var criticos = custodiaNominal.filter(function(p) {
            return (p.Faixa_Aging || '').indexOf('Crítico') !== -1 ||
                   parseInt(p.Dias_Ultima_Mov || 0, 10) > 90;
        }).length;
        var elCrit = document.getElementById('mesa-kpi-criticos');
        if (elCrit) elCrit.innerText = String(criticos);

        var porens = custodiaNominal.filter(function(p) {
            return (p.Status_Kanban || p.Status_OpenProject || '').indexOf('CJ') !== -1 ||
                   (p.Marcadores_Institucionais || '').indexOf('Suspensão') !== -1;
        }).length;
        var elPor = document.getElementById('mesa-kpi-porens');
        if (elPor) elPor.innerText = String(porens);
    };

    window.alternarModoMesa = function(modo) {
        window.modoMesaAtivo = modo || 'custodia';
        window.paginaMesa = 1;

        document.querySelectorAll('.pill-filtro-mesa').forEach(function(btn) {
            if (btn.id === 'btn-mesa-' + window.modoMesaAtivo) {
                btn.className = 'btn btn-primary pill-filtro-mesa active';
            } else {
                btn.className = 'btn btn-secondary pill-filtro-mesa';
            }
        });

        window.renderizarTabelaMesa();
    };

    window.renderizarTabelaMesa = function() {
        window.atualizarContadoresCustodiaMesa();

        var tbody = document.getElementById('tbody-meus-processos');
        if (!tbody) return;

        var modo = window.modoMesaAtivo || 'custodia';
        var busca = (document.getElementById('busca-mesa-input') ?
                     document.getElementById('busca-mesa-input').value : '').toLowerCase().trim();
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var fixados = obterFixadosValidos();
        var elPagInfo = document.getElementById('mesa-pag-info');

        if (modo === 'openproject') {
            var listaOp = obterPacotesOpLuiz();
            if (busca) {
                listaOp = listaOp.filter(function(p) {
                    var str = (p.id + ' ' + (p.assunto || '') + ' ' + (p.projeto || '') + ' ' +
                               (p.status || '') + ' ' + (p.tipo || '')).toLowerCase();
                    return str.indexOf(busca) !== -1;
                });
            }
            if (listaOp.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:32px;color:#94a3b8;">' +
                    '<span style="font-size:28px;display:block;margin-bottom:8px;">📦</span>' +
                    '<strong>Nenhum pacote OpenProject encontrado para este filtro.</strong></td></tr>';
                if (elPagInfo) elPagInfo.innerText = 'Exibindo 0 de 0 pacotes OpenProject';
                return;
            }
            var htmlOp = '';
            listaOp.forEach(function(p) {
                var url = 'https://projetos.spaguas.sp.gov.br/work_packages/' + p.id;
                var crono = (p.ini || p.fim) ? ((p.ini || '?') + ' → ' + (p.fim || '?')) : 'Contínuo';
                htmlOp += '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">' +
                    '<td style="text-align:center;padding:9px 8px;">📦</td>' +
                    '<td style="padding:9px 12px;font-family:monospace;font-weight:800;">' +
                    '<a href="' + url + '" target="_blank" style="color:#38bdf8;text-decoration:none;">#' +
                    p.id + '</a></td>' +
                    '<td style="padding:9px 12px;color:#e2e8f0;font-size:11.5px;font-weight:600;">' +
                    (p.assunto || '') + '</td>' +
                    '<td style="padding:9px 12px;color:#cbd5e1;font-size:11.5px;">👤 ' +
                    (p.atrib || 'Luiz Antonio Seixeiro') + '</td>' +
                    '<td style="padding:9px 12px;"><span class="pill-tag pill-blue" style="font-size:10px;">' +
                    (p.status || 'Em progresso') + '</span></td>' +
                    '<td style="padding:9px 12px;font-family:monospace;font-size:11px;color:#94a3b8;">' +
                    crono + '</td>' +
                    '<td style="text-align:center;padding:9px 12px;">' +
                    '<a href="' + url + '" target="_blank" class="btn btn-secondary" ' +
                    'style="padding:3px 8px;font-size:11px;text-decoration:none;">Abrir OP ↗</a></td></tr>';
            });
            tbody.innerHTML = htmlOp;
            if (elPagInfo) {
                elPagInfo.innerText = 'Exibindo 1-' + listaOp.length + ' de ' +
                                      listaOp.length + ' pacotes (OpenProject — Luiz Antonio Seixeiro)';
            }
            return;
        }

        var lista = [];
        if (modo === 'custodia') {
            lista = obterCustodiaNominalLuiz();
        } else if (modo === 'fixados') {
            lista = baseProcs.filter(function(p) {
                return fixados.indexOf(p.ID_Processo) !== -1;
            });
        } else if (modo === 'acervo') {
            lista = baseProcs.slice();
        }

        if (busca) {
            lista = lista.filter(function(p) {
                var str = (p.ID_Processo + ' ' + (p.Especificacao || '') + ' ' +
                           (p.Responsavel_Tecnico || '') + ' ' + (p.Bucket_OpenProject || '')).toLowerCase();
                return str.indexOf(busca) !== -1;
            });
        }

        if (lista.length === 0) {
            var msgTitulo = modo === 'custodia' ?
                'Nenhum processo SEI está sob sua custódia ou demanda nominal (0 processos).' :
                'Nenhum processo encontrado para este filtro na Mesa de Trabalho.';
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:32px;color:#94a3b8;">' +
                '<span style="font-size:28px;display:block;margin-bottom:8px;">📂</span>' +
                '<strong style="color:#e2e8f0;">' + msgTitulo + '</strong></td></tr>';
            if (elPagInfo) elPagInfo.innerText = 'Exibindo 0 de 0 processos';
            return;
        }

        var totalItens = lista.length;
        var tamPag = window.tamanhoPaginaMesa || 15;
        var totalPaginas = Math.ceil(totalItens / tamPag) || 1;
        if (window.paginaMesa > totalPaginas) window.paginaMesa = totalPaginas;
        var inicio = (window.paginaMesa - 1) * tamPag;
        var paginaItens = lista.slice(inicio, inicio + tamPag);

        var html = '';
        paginaItens.forEach(function(p) {
            var isFix = fixados.indexOf(p.ID_Processo) !== -1;
            var pillAging = 'pill-green';
            if ((p.Faixa_Aging || '').indexOf('Crítico') !== -1) pillAging = 'pill-red';
            else if ((p.Faixa_Aging || '').indexOf('Atenção') !== -1) pillAging = 'pill-yellow';
            else if ((p.Faixa_Aging || '').indexOf('Alerta') !== -1) pillAging = 'pill-orange';

            html += '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">' +
                '<td style="text-align:center;padding:9px 8px;">' +
                '<button type="button" data-proc="' + p.ID_Processo + '" ' +
                'onclick="window.toggleFixado(this.getAttribute(\'data-proc\'))" ' +
                'style="background:none;border:none;cursor:pointer;font-size:15px;">' +
                (isFix ? '⭐' : '☆') + '</button></td>' +
                '<td style="padding:9px 12px;"><strong style="color:#38bdf8;font-size:12px;">' +
                p.ID_Processo + '</strong></td>' +
                '<td style="max-width:280px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' +
                'font-size:11.5px;color:#e2e8f0;padding:9px 12px;" title="' + (p.Especificacao || '') + '">' +
                (p.Especificacao || '') + '</td>' +
                '<td style="font-size:11.5px;color:#94a3b8;padding:9px 12px;">' +
                (p.Responsavel_Tecnico || '<span style="color:#64748b;">SA-GTI</span>') + '</td>' +
                '<td style="padding:9px 12px;"><span class="pill-tag pill-blue" style="font-size:10px;">' +
                (p.Status_OpenProject || p.Status_Kanban || 'Backlog') + '</span></td>' +
                '<td style="padding:9px 12px;"><span class="pill-tag ' + pillAging + '" style="font-size:10px;">' +
                (p.Faixa_Aging || 'Normal') + ' (' + (p.Dias_Ultima_Mov || 0) + 'd)</span></td>' +
                '<td style="text-align:center;white-space:nowrap;padding:9px 12px;">' +
                '<button type="button" class="btn btn-secondary" data-proc="' + p.ID_Processo + '" ' +
                'onclick="if(window.abrirDetalhesProcesso)window.abrirDetalhesProcesso(this.getAttribute(\'data-proc\'))" ' +
                'style="padding:3px 8px;font-size:11px;" title="Dossiê 360°">🔍</button></td></tr>';
        });
        tbody.innerHTML = html;

        if (elPagInfo) {
            elPagInfo.innerText = 'Exibindo ' + (inicio + 1) + '-' +
                                  Math.min(inicio + tamPag, totalItens) + ' de ' + totalItens + ' processos';
        }
    };

    window.renderizarMeusProcessosMesa = window.renderizarTabelaMesa;

    window.atualizarContadoresCustodiaMesa();
    window.renderizarTabelaMesa();
    document.addEventListener('DOMContentLoaded', function() {
        window.atualizarContadoresCustodiaMesa();
        window.renderizarTabelaMesa();
        setTimeout(window.renderizarTabelaMesa, 300);
    });
    setInterval(window.atualizarContadoresCustodiaMesa, 1000);
})();
</script>'''

for filepath in targets:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    orig_len = len(text)

    text = text.replace('id="mesa-kpi-custodia" style="color: #38bdf8;">18</div>',
                        'id="mesa-kpi-custodia" style="color: #38bdf8;">0</div>')
    text = text.replace('id="mesa-kpi-custodia" style="color: #38bdf8;">2</div>',
                        'id="mesa-kpi-custodia" style="color: #38bdf8;">0</div>')
    text = text.replace('id="count-mesa-custodia">18</span>',
                        'id="count-mesa-custodia">0</span>')
    text = text.replace('id="count-mesa-custodia">2</span>',
                        'id="count-mesa-custodia">0</span>')
    text = text.replace('id="count-mesa-op">97</span>',
                        'id="count-mesa-op">4</span>')
    text = text.replace('id="count-mesa-op">31</span>',
                        'id="count-mesa-op">4</span>')
    text = text.replace('id="mesa-pag-info">Exibindo 1-15 processos</span>',
                        'id="mesa-pag-info">Exibindo 0 de 0 processos</span>')

    idx_existing = text.find('<script id="script-saneamento-custodia-mesa-v11">')
    if idx_existing != -1:
        idx_end = text.find('</script>', idx_existing)
        if idx_end != -1:
            text = text[:idx_existing] + js_mesa_custodia + text[idx_end + len('</script>'):]
    else:
        idx_body = text.rfind('</body>')
        if idx_body != -1:
            text = text[:idx_body] + '\n' + js_mesa_custodia + '\n' + text[idx_body:]
        else:
            text = text + '\n' + js_mesa_custodia

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"[OK] Custodia da Mesa saneada para 0 em: {filepath} ({orig_len} -> {len(text)} bytes)")
