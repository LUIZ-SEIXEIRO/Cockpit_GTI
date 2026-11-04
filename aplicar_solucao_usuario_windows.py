# -*- coding: utf-8 -*-
import os, sys, re

print("=== ATUALIZADOR OFICIAL DA MESA DE TRABALHO (SP-AGUAS SA-GTI) ===")

caminhos = [
    'frontend/painel.html',
    'painel.html',
    'C:/Cockpit_GTI/frontend/painel.html',
    'C:/Cockpit_GTI/painel.html'
]

alvos = [p for p in caminhos if os.path.exists(p)]
if not alvos:
    print("ERRO: Nenhum arquivo painel.html encontrado nos diretorios padrao.")
    sys.exit(1)

print(f"Arquivos identificados: {alvos}")

novo_script_mesa = """<script>
(function() {
    window.modoMesaAtivo = window.modoMesaAtivo || 'custodia';
    window.paginaMesa = 1;
    window.tamanhoPaginaMesa = 15;
    window.filtrosMesaPopulados = false;

    window.toggleFixado = function(procId) {
        if (!procId) return;
        var fixados = [];
        try { fixados = JSON.parse(localStorage.getItem('sagti_fixados') || '[]'); } catch(e) {}
        var idx = fixados.indexOf(procId);
        if (idx === -1) {
            fixados.push(procId);
        } else {
            fixados.splice(idx, 1);
        }
        localStorage.setItem('sagti_fixados', JSON.stringify(fixados));
        if (typeof window.atualizarContadoresPillsMesa === 'function') window.atualizarContadoresPillsMesa();
        if (typeof window.renderizarTabelaMesa === 'function') window.renderizarTabelaMesa();
        if (typeof window.renderizarTabelaConsulta === 'function') window.renderizarTabelaConsulta();
    };

    window.toggleFixadoModal = function() {
        if (window.processoModalAtivo) {
            window.toggleFixado(window.processoModalAtivo);
            var fixados = [];
            try { fixados = JSON.parse(localStorage.getItem('sagti_fixados') || '[]'); } catch(e) {}
            var btn = document.getElementById('btn-modal-fixar');
            if (btn) {
                var isFix = fixados.includes(window.processoModalAtivo);
                btn.innerHTML = isFix ? '⭐ Remover da Watchlist' : '⭐ Fixar na Watchlist';
            }
        }
    };

    window.atualizarContadoresPillsMesa = function() {
        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var opDados = (typeof OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(OP_PACOTES_OFICIAIS)) ? OP_PACOTES_OFICIAIS : (window.OP_PACOTES_OFICIAIS || []);
        var fixados = [];
        try { fixados = JSON.parse(localStorage.getItem('sagti_fixados') || '[]'); } catch(e) {}

        var luizProcs = baseProcs.filter(function(p) {
            var resp = (p.Responsavel_Tecnico || '').toLowerCase().trim();
            return resp.includes('luiz') || resp.includes('seixeiro');
        });
        var elCustodia = document.getElementById('count-mesa-custodia');
        if (elCustodia) elCustodia.innerText = luizProcs.length;
        var elKpiCustodia = document.getElementById('mesa-kpi-custodia');
        if (elKpiCustodia) elKpiCustodia.innerText = luizProcs.length;

        var elFixados = document.getElementById('count-mesa-fixados');
        if (elFixados) elFixados.innerText = fixados.length;

        var luizOP = opDados.filter(function(p) {
            var atrib = (p.atrib || '').toLowerCase();
            var autor = (p.autor || '').toLowerCase();
            var encarr = (p.encarr || '').toLowerCase();
            return (atrib.includes('luiz antonio') || atrib.includes('seixeiro') ||
                    autor.includes('luiz antonio') || autor.includes('seixeiro') ||
                    encarr.includes('luiz antonio') || encarr.includes('seixeiro'));
        });
        var elOP = document.getElementById('count-mesa-op');
        if (elOP) elOP.innerText = luizOP.length;

        var elAcervo = document.getElementById('count-mesa-acervo');
        if (elAcervo) elAcervo.innerText = baseProcs.length;
    };

    window.inicializarFiltrosMesa = function() {
        if (window.filtrosMesaPopulados) return;
        var procs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        if (!procs.length) return;

        function popularSelect(selId, campo) {
            var sel = document.getElementById(selId);
            if (!sel || sel.options.length > 1) return;
            var valores = [];
            procs.forEach(function(p) {
                var v = p[campo];
                if (v && valores.indexOf(v) === -1) valores.push(v);
            });
            valores.sort();
            valores.forEach(function(val) {
                var opt = document.createElement('option');
                opt.value = val;
                opt.innerText = val;
                sel.appendChild(opt);
            });
        }

        popularSelect('filtro-mesa-bucket', 'Bucket_OpenProject');
        popularSelect('filtro-mesa-resp', 'Responsavel_Tecnico');
        popularSelect('filtro-mesa-farol', 'Farol_Criticidade');
        popularSelect('filtro-mesa-aging', 'Faixa_Aging');
        popularSelect('filtro-mesa-risco', 'Classificacao_Risco');
        popularSelect('filtro-mesa-tipo', 'Tipo_Processo');
        popularSelect('filtro-mesa-marcadores', 'Marcadores_Institucionais');
        window.filtrosMesaPopulados = true;
    };

    window.alternarModoMesa = function(modo) {
        window.modoMesaAtivo = modo || 'custodia';
        window.paginaMesa = 1;

        var ids = ['custodia', 'fixados', 'acervo', 'openproject'];
        ids.forEach(function(m) {
            var btn = document.getElementById('btn-mesa-' + m);
            if (btn) {
                if (m === window.modoMesaAtivo) {
                    btn.className = 'btn btn-primary pill-filtro-mesa active';
                    btn.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                    btn.style.color = '#ffffff';
                    btn.style.fontWeight = '700';
                } else {
                    btn.className = 'btn btn-secondary pill-filtro-mesa';
                    btn.style.background = 'rgba(255,255,255,0.06)';
                    btn.style.color = '#cbd5e1';
                    btn.style.fontWeight = '600';
                }
            }
        });

        var painelFiltros = document.getElementById('painel-filtros-acervo-sei');
        if (painelFiltros) {
            if (window.modoMesaAtivo === 'acervo') {
                painelFiltros.style.display = 'block';
                window.inicializarFiltrosMesa();
            } else {
                painelFiltros.style.display = 'none';
            }
        }

        window.renderizarTabelaMesa();
    };

    window.aplicarFiltrosConsultaMesa = function() {
        window.paginaMesa = 1;
        window.renderizarTabelaMesa();
    };

    window.limparFiltrosConsultaMesa = function() {
        var ids = ['filtro-mesa-id', 'filtro-mesa-bucket', 'filtro-mesa-resp', 'filtro-mesa-farol',
                   'filtro-mesa-aging', 'filtro-mesa-risco', 'filtro-mesa-tipo', 'filtro-mesa-espec', 'filtro-mesa-marcadores'];
        ids.forEach(function(id) {
            var el = document.getElementById(id);
            if (el) el.value = '';
        });
        window.paginaMesa = 1;
        window.renderizarTabelaMesa();
    };

    window.paginaAnteriorMesa = function() {
        if (window.paginaMesa > 1) {
            window.paginaMesa--;
            window.renderizarTabelaMesa();
        }
    };

    window.proximaPaginaMesa = function() {
        var totalItens = window.totalItensMesaAtivo || 0;
        var tamPag = window.tamanhoPaginaMesa || 15;
        var totalPaginas = Math.ceil(totalItens / tamPag) || 1;
        if (window.paginaMesa < totalPaginas) {
            window.paginaMesa++;
            window.renderizarTabelaMesa();
        }
    };

    window.renderizarTabelaMesa = function() {
        window.atualizarContadoresPillsMesa();

        var tbody = document.getElementById('tbody-meus-processos');
        if (!tbody) return;

        var baseProcs = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];
        var opDados = (typeof OP_PACOTES_OFICIAIS !== 'undefined' && Array.isArray(OP_PACOTES_OFICIAIS)) ? OP_PACOTES_OFICIAIS : (window.OP_PACOTES_OFICIAIS || []);
        var fixados = [];
        try { fixados = JSON.parse(localStorage.getItem('sagti_fixados') || '[]'); } catch(e) {}

        var buscaLivre = (document.getElementById('busca-mesa-input') ? document.getElementById('busca-mesa-input').value : '').toLowerCase().trim();
        var thead = tbody.parentElement ? tbody.parentElement.querySelector('thead') : null;

        var modo = window.modoMesaAtivo || 'custodia';

        if (thead) {
            if (modo === 'openproject') {
                thead.innerHTML = '<tr style="border-bottom: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.03); color: #94a3b8; font-size: 10.5px; text-transform: uppercase;">' +
                    '<th style="width: 36px; text-align: center; padding: 10px 8px;">📦</th>' +
                    '<th style="padding: 10px 12px;">Pacote OP</th>' +
                    '<th style="padding: 10px 12px;">Assunto / Iniciativa</th>' +
                    '<th style="padding: 10px 12px;">Responsável</th>' +
                    '<th style="padding: 10px 12px;">Status & Tipo</th>' +
                    '<th style="padding: 10px 12px; text-align: center;">Cronograma</th>' +
                    '<th style="text-align: center; padding: 10px 12px;">Ações</th>' +
                    '</tr>';
            } else {
                thead.innerHTML = '<tr style="border-bottom: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.03); color: #94a3b8; font-size: 10.5px; text-transform: uppercase;">' +
                    '<th style="width: 36px; text-align: center; padding: 10px 8px;">⭐</th>' +
                    '<th style="padding: 10px 12px;">Processo SEI</th>' +
                    '<th style="padding: 10px 12px;">Especificação / Objeto</th>' +
                    '<th style="padding: 10px 12px;">Responsável</th>' +
                    '<th style="padding: 10px 12px;">Status</th>' +
                    '<th style="padding: 10px 12px;">Aging Líquido</th>' +
                    '<th style="text-align: center; padding: 10px 12px;">Ações</th>' +
                    '</tr>';
            }
        }

        var lista = [];

        if (modo === 'custodia') {
            lista = baseProcs.filter(function(p) {
                var resp = (p.Responsavel_Tecnico || '').toLowerCase().trim();
                var isLuiz = resp.includes('luiz') || resp.includes('seixeiro');
                if (!isLuiz) return false;
                if (buscaLivre) {
                    var str = (p.ID_Processo + ' ' + (p.Especificacao || '') + ' ' + (p.Status_OpenProject || '') + ' ' + (p.Bucket_OpenProject || '')).toLowerCase();
                    if (!str.includes(buscaLivre)) return false;
                }
                return true;
            });

            window.totalItensMesaAtivo = lista.length;

            if (lista.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 36px 16px; color: #94a3b8;">' +
                    '<span style="font-size: 32px; display: block; margin-bottom: 8px;">📌</span>' +
                    '<strong style="color: #f1f5f9; font-size: 13px;">Nenhuma demanda SEI atribuída nominalmente a Luiz Seixeiro no momento.</strong>' +
                    '<div style="font-size: 11.5px; color: #64748b; margin-top: 6px;">Todas as 179 demandas do acervo estão atribuídas a outros responsáveis técnicos ou pendentes de alocação nominal.</div>' +
                    '</td></tr>';
                var pagInfo = document.getElementById('mesa-pag-info');
                if (pagInfo) pagInfo.innerText = 'Exibindo 0 de 0 demandas (Minha Custódia)';
                return;
            }
        } else if (modo === 'fixados') {
            lista = baseProcs.filter(function(p) {
                if (!fixados.includes(p.ID_Processo)) return false;
                if (buscaLivre) {
                    var str = (p.ID_Processo + ' ' + (p.Especificacao || '') + ' ' + (p.Responsavel_Tecnico || '') + ' ' + (p.Status_OpenProject || '')).toLowerCase();
                    if (!str.includes(buscaLivre)) return false;
                }
                return true;
            });

            window.totalItensMesaAtivo = lista.length;

            if (lista.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 36px 16px; color: #94a3b8;">' +
                    '<span style="font-size: 32px; display: block; margin-bottom: 8px;">⭐</span>' +
                    '<strong style="color: #f1f5f9; font-size: 13px;">Nenhum processo fixado para acompanhamento na sua Watchlist pessoal.</strong>' +
                    '<div style="font-size: 11.5px; color: #64748b; margin-top: 6px;">Clique no ícone de estrela (☆) em qualquer processo do Acervo SEI para fixá-lo aqui.</div>' +
                    '</td></tr>';
                var pagInfo = document.getElementById('mesa-pag-info');
                if (pagInfo) pagInfo.innerText = 'Exibindo 0 de 0 processos (Fixados)';
                return;
            }
        } else if (modo === 'openproject') {
            lista = opDados.filter(function(p) {
                var atrib = (p.atrib || '').toLowerCase();
                var autor = (p.autor || '').toLowerCase();
                var encarr = (p.encarr || '').toLowerCase();
                var isLuiz = (atrib.includes('luiz antonio') || atrib.includes('seixeiro') ||
                              autor.includes('luiz antonio') || autor.includes('seixeiro') ||
                              encarr.includes('luiz antonio') || encarr.includes('seixeiro'));
                if (!isLuiz) return false;
                if (buscaLivre) {
                    var str = (p.id + ' ' + (p.assunto || '') + ' ' + (p.projeto || '') + ' ' + (p.tipo || '') + ' ' + (p.status || '')).toLowerCase();
                    if (!str.includes(buscaLivre)) return false;
                }
                return true;
            });

            window.totalItensMesaAtivo = lista.length;

            if (lista.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 36px 16px; color: #94a3b8;">' +
                    '<span style="font-size: 32px; display: block; margin-bottom: 8px;">📦</span>' +
                    '<strong style="color: #f1f5f9; font-size: 13px;">Nenhum pacote do OpenProject sob sua responsabilidade localizado.</strong>' +
                    '</td></tr>';
                var pagInfo = document.getElementById('mesa-pag-info');
                if (pagInfo) pagInfo.innerText = 'Exibindo 0 de 0 pacotes (OpenProject)';
                return;
            }

            var totalItens = lista.length;
            var tamPag = window.tamanhoPaginaMesa || 15;
            var totalPaginas = Math.ceil(totalItens / tamPag) || 1;
            if (window.paginaMesa > totalPaginas) window.paginaMesa = totalPaginas;
            var inicio = (window.paginaMesa - 1) * tamPag;
            var paginaItens = lista.slice(inicio, inicio + tamPag);

            var pagInfo = document.getElementById('mesa-pag-info');
            if (pagInfo) pagInfo.innerText = 'Exibindo ' + (inicio + 1) + '-' + Math.min(inicio + tamPag, totalItens) + ' de ' + totalItens + ' pacotes (OpenProject - Luiz Antonio Seixeiro)';

            var html = '';
            paginaItens.forEach(function(p) {
                var linkOP = 'https://projetos.spaguas.sp.gov.br/work_packages/' + p.id;
                var crono = (p.ini || p.fim) ? ((p.ini || '?') + ' → ' + (p.fim || '?')) : '<span style="color:#64748b">Contínuo</span>';

                html += '<tr style="border-bottom: 1px solid rgba(255,255,255,0.06); transition: background 0.15s ease;">' +
                    '<td style="text-align: center; padding: 9px 8px; font-size: 14px;">📦</td>' +
                    '<td style="padding: 9px 12px; font-family: monospace; font-weight: 800;">' +
                        '<a href="' + linkOP + '" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; text-decoration: none;">#' + p.id + '</a>' +
                    '</td>' +
                    '<td style="max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 11.5px; color: #ffffff; font-weight: 600; padding: 9px 12px;" title="' + (p.assunto || '') + '">' +
                        (p.assunto || '') +
                        '<div style="font-size: 10.5px; color: #94a3b8; font-weight: 400; margin-top: 2px;">' + (p.projeto || '') + '</div>' +
                    '</td>' +
                    '<td style="padding: 9px 12px; font-size: 11px; color: #cbd5e1;">👤 ' + (p.atrib || p.autor || 'Luiz Antonio') + '</td>' +
                    '<td style="padding: 9px 12px;">' +
                        '<span style="background: rgba(56,189,248,0.15); color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); padding: 2px 7px; border-radius: 8px; font-size: 10.5px; font-weight: 700;">' + (p.status || 'Em progresso') + '</span> ' +
                        '<span style="background: rgba(255,255,255,0.06); color: #e2e8f0; padding: 2px 6px; border-radius: 8px; font-size: 10px;">' + (p.tipo || 'Pacote') + '</span>' +
                    '</td>' +
                    '<td style="padding: 9px 12px; text-align: center; font-family: monospace; font-size: 11px; color: #cbd5e1;">' + crono + '</td>' +
                    '<td style="padding: 9px 12px; text-align: center;">' +
                        '<a href="' + linkOP + '" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="padding: 3px 8px; font-size: 10.5px; border-radius: 6px; text-decoration: none; display: inline-block;">Abrir no OP ↗</a>' +
                    '</td>' +
                    '</tr>';
            });
            tbody.innerHTML = html;
            return;
        } else if (modo === 'acervo') {
            var fId = (document.getElementById('filtro-mesa-id') ? document.getElementById('filtro-mesa-id').value : '').toLowerCase().trim();
            var fBucket = document.getElementById('filtro-mesa-bucket') ? document.getElementById('filtro-mesa-bucket').value : '';
            var fResp = document.getElementById('filtro-mesa-resp') ? document.getElementById('filtro-mesa-resp').value : '';
            var fFarol = document.getElementById('filtro-mesa-farol') ? document.getElementById('filtro-mesa-farol').value : '';
            var fAging = document.getElementById('filtro-mesa-aging') ? document.getElementById('filtro-mesa-aging').value : '';
            var fRisco = document.getElementById('filtro-mesa-risco') ? document.getElementById('filtro-mesa-risco').value : '';
            var fTipo = document.getElementById('filtro-mesa-tipo') ? document.getElementById('filtro-mesa-tipo').value : '';
            var fEspec = (document.getElementById('filtro-mesa-espec') ? document.getElementById('filtro-mesa-espec').value : '').toLowerCase().trim();
            var fMarc = document.getElementById('filtro-mesa-marcadores') ? document.getElementById('filtro-mesa-marcadores').value : '';

            lista = baseProcs.filter(function(p) {
                if (fId && !(p.ID_Processo || '').toLowerCase().includes(fId)) return false;
                if (fBucket && p.Bucket_OpenProject !== fBucket) return false;
                if (fResp && p.Responsavel_Tecnico !== fResp) return false;
                if (fFarol && p.Farol_Criticidade !== fFarol) return false;
                if (fAging && p.Faixa_Aging !== fAging) return false;
                if (fRisco && p.Classificacao_Risco !== fRisco) return false;
                if (fTipo && p.Tipo_Processo !== fTipo) return false;
                if (fEspec && !(p.Especificacao || '').toLowerCase().includes(fEspec)) return false;
                if (fMarc && p.Marcadores_Institucionais !== fMarc) return false;
                if (buscaLivre) {
                    var str = (p.ID_Processo + ' ' + (p.Especificacao || '') + ' ' + (p.Responsavel_Tecnico || '') + ' ' + (p.Status_OpenProject || '') + ' ' + (p.Bucket_OpenProject || '')).toLowerCase();
                    if (!str.includes(buscaLivre)) return false;
                }
                return true;
            });

            window.totalItensMesaAtivo = lista.length;

            if (lista.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 36px 16px; color: #94a3b8;">' +
                    '<span style="font-size: 32px; display: block; margin-bottom: 8px;">📂</span>' +
                    '<strong style="color: #f1f5f9; font-size: 13px;">Nenhum processo localizado com os filtros selecionados no Acervo SEI.</strong>' +
                    '</td></tr>';
                var pagInfo = document.getElementById('mesa-pag-info');
                if (pagInfo) pagInfo.innerText = 'Exibindo 0 de 0 processos (Acervo SEI)';
                return;
            }
        }

        var totalItens = lista.length;
        var tamPag = window.tamanhoPaginaMesa || 15;
        var totalPaginas = Math.ceil(totalItens / tamPag) || 1;
        if (window.paginaMesa > totalPaginas) window.paginaMesa = totalPaginas;
        var inicio = (window.paginaMesa - 1) * tamPag;
        var paginaItens = lista.slice(inicio, inicio + tamPag);

        var pagInfo = document.getElementById('mesa-pag-info');
        var rotuloModo = modo === 'custodia' ? 'Minha Custódia' : (modo === 'fixados' ? 'Fixados' : 'Acervo SEI');
        if (pagInfo) pagInfo.innerText = 'Exibindo ' + (inicio + 1) + '-' + Math.min(inicio + tamPag, totalItens) + ' de ' + totalItens + ' processos (' + rotuloModo + ')';

        var html = '';
        paginaItens.forEach(function(p) {
            var isFixado = fixados.includes(p.ID_Processo);
            var pillAging = 'pill-green';
            if ((p.Faixa_Aging || '').includes('Crítico')) pillAging = 'pill-red';
            else if ((p.Faixa_Aging || '').includes('Atenção')) pillAging = 'pill-yellow';
            else if ((p.Faixa_Aging || '').includes('Alerta')) pillAging = 'pill-orange';

            html += '<tr style="border-bottom: 1px solid rgba(255,255,255,0.06); transition: background 0.15s ease;">' +
                '<td style="text-align: center; padding: 9px 8px;">' +
                    '<button data-proc="' + p.ID_Processo + '" onclick="window.toggleFixado(this.dataset.proc)" style="background: none; border: none; cursor: pointer; font-size: 15px;" title="' + (isFixado ? 'Remover dos Fixados' : 'Fixar Processo') + '">' +
                        (isFixado ? '⭐' : '☆') +
                    '</button>' +
                '</td>' +
                '<td style="padding: 9px 12px;"><strong style="color: #38bdf8; font-size: 12px;">' + p.ID_Processo + '</strong></td>' +
                '<td style="max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 11.5px; color: #e2e8f0; padding: 9px 12px;" title="' + (p.Especificacao || '') + '">' + (p.Especificacao || '') + '</td>' +
                '<td style="padding: 9px 12px; font-size: 11px; color: #cbd5e1;">' + (p.Responsavel_Tecnico || '<span style="color:#64748b">Não atribuído</span>') + '</td>' +
                '<td style="padding: 9px 12px;"><span style="background: rgba(255,255,255,0.06); color: #e2e8f0; border: 1px solid rgba(255,255,255,0.12); padding: 2px 7px; border-radius: 8px; font-size: 10.5px;">' + (p.Status_OpenProject || p.Status_Kanban || 'Backlog') + '</span></td>' +
                '<td style="padding: 9px 12px;"><span class="pill-tag ' + pillAging + '">' + (p.Faixa_Aging || 'Normal') + ' (' + (p.Dias_Ultima_Mov || 0) + 'd)</span></td>' +
                '<td style="padding: 9px 12px; text-align: center;">' +
                    '<button data-proc="' + p.ID_Processo + '" class="btn btn-secondary" style="padding: 3px 8px; font-size: 10.5px; border-radius: 6px;" onclick="window.abrirDetalhesProcesso(this.dataset.proc)">Ver Detalhes</button>' +
                '</td>' +
                '</tr>';
        });
        tbody.innerHTML = html;
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.atualizarContadoresPillsMesa();
            window.renderizarTabelaMesa();
        });
    } else {
        window.atualizarContadoresPillsMesa();
        window.renderizarTabelaMesa();
    }
})();
</script>"""

for alvo in alvos:
    try:
        with open(alvo, 'r', encoding='utf-8') as f:
            html = f.read()

        html = html.replace('id="count-mesa-custodia">18</span>', 'id="count-mesa-custodia">0</span>')
        html = html.replace('id="count-mesa-op">97</span>', 'id="count-mesa-op">4</span>')
        html = html.replace('id="count-mesa-op">31</span>', 'id="count-mesa-op">4</span>')
        html = html.replace('id="mesa-kpi-custodia" style="color: #38bdf8;">18</div>', 'id="mesa-kpi-custodia" style="color: #38bdf8;">0</div>')

        tag_inicio = html.find('window.modoMesaAtivo = window.modoMesaAtivo ||')
        if tag_inicio == -1:
            tag_inicio = html.find('// Garantir que alternarModoMesa')
        if tag_inicio == -1:
            tag_inicio = html.find('window.alternarModoMesa = function(modo)')
        
        tag_fim = html.find('// Sincronização oficial de alternância de abas para o Eixo 2')
        if tag_inicio != -1 and tag_fim != -1:
            pos_script_start = html.rfind('<script>', 0, tag_inicio)
            pos_script_end = html.rfind('</script>', 0, tag_fim) + len('</script>')
            if pos_script_start != -1 and pos_script_end != -1:
                html = html[:pos_script_start] + novo_script_mesa + html[pos_script_end:]
                print(f"[{alvo}] Bloco da Mesa substituido com sucesso!")

        open_divs = len(re.findall(r'<div[\s>]', html, re.I))
        close_divs = len(re.findall(r'</div[\s>]', html, re.I))
        diff = open_divs - close_divs
        print(f"[{alvo}] Div balance: open={open_divs}, close={close_divs}, diff={diff}")

        if diff == 0:
            with open(alvo, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[{alvo}] Sucesso na gravacao!")
        else:
            print(f"[{alvo}] AVISO: Divergencia de tags div ({diff}).")
    except Exception as e:
        print(f"[{alvo}] Erro: {e}")

print("=== CONCLUIDO ===")
