# -*- coding: utf-8 -*-
import os, sys, re

print("=" * 70)
print(" ATIVAÇÃO DOS FILTROS RÁPIDOS DO OPENPROJECT: 'EM PROGRESSO' E 'EM ESPERA'")
print(" Tela: Portfólio OpenProject (500 Pacotes)")
print("=" * 70)

caminhos = [
    os.path.join(os.getcwd(), "frontend", "painel.html"),
    os.path.join(os.getcwd(), "painel.html")
]

pills_bar_html = '''            <!-- SELETOR RÁPIDO DE MODOS E VISÕES DO OPENPROJECT -->
            <div id="container-pills-op" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.08);">
                <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                    <button class="btn btn-primary pill-filtro-op active" id="btn-op-todos" onclick="window.filtrarModoRapidoOP('todos')">🌐 Todos os Pacotes (500)</button>
                    <button class="btn btn-secondary pill-filtro-op" id="btn-op-sagti" onclick="window.filtrarModoRapidoOP('sagti')">⚡ Tracks SA-GTI (97)</button>
                    <button class="btn btn-secondary pill-filtro-op" id="btn-op-pdtic" onclick="window.filtrarModoRapidoOP('pdtic')">🧭 PDTIC 2027-2030 (35)</button>
                    <button class="btn btn-secondary pill-filtro-op" id="btn-op-progresso" onclick="window.filtrarModoRapidoOP('progresso')">🚀 Em Progresso</button>
                    <button class="btn btn-secondary pill-filtro-op" id="btn-op-espera" onclick="window.filtrarModoRapidoOP('espera')">⏸️ Em Espera</button>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: #4ade80; background: rgba(16, 185, 129, 0.15); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
                    <span>🛡️ Trava de Segurança SA-GTI Ativa</span>
                    <span style="font-weight: normal; color: #bbf7d0;">(Escopo: spaguas-sa-gti)</span>
                </div>
            </div>'''

js_op_filters = '''
    // =========================================================================
    // FILTROS RÁPIDOS E RENDERIZAÇÃO DO PORTFÓLIO OPENPROJECT (500 PACOTES)
    // =========================================================================
    window.opModoRapidoAtivo = 'todos';

    window.filtrarModoRapidoOP = function(modo) {
        window.opModoRapidoAtivo = modo || 'todos';

        // 1. Atualizar estilo visual dos 5 botões
        var ids = ['btn-op-todos', 'btn-op-sagti', 'btn-op-pdtic', 'btn-op-progresso', 'btn-op-espera'];
        var mapa = {
            'todos': 'btn-op-todos',
            'sagti': 'btn-op-sagti',
            'pdtic': 'btn-op-pdtic',
            'progresso': 'btn-op-progresso',
            'espera': 'btn-op-espera'
        };

        ids.forEach(function(bid) {
            var b = document.getElementById(bid);
            if (b) {
                if (bid === mapa[modo]) {
                    b.className = 'btn btn-primary pill-filtro-op active';
                    b.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                    b.style.color = '#ffffff';
                    b.style.fontWeight = '700';
                } else {
                    b.className = 'btn btn-secondary pill-filtro-op';
                    b.style.background = 'rgba(255,255,255,0.06)';
                    b.style.color = '#cbd5e1';
                    b.style.fontWeight = '600';
                }
            }
        });

        // 2. Sincronizar o dropdown de status e busca
        var selStatus = document.getElementById('op-filtro-status');
        var selMacro = document.getElementById('op-filtro-macro');
        var inpBusca = document.getElementById('op-filtro-busca');

        if (modo === 'progresso') {
            if (selStatus) selStatus.value = 'Em progresso';
            if (selMacro) selMacro.value = '';
            if (inpBusca) inpBusca.value = '';
        } else if (modo === 'espera') {
            if (selStatus) selStatus.value = 'Em espera';
            if (selMacro) selMacro.value = '';
            if (inpBusca) inpBusca.value = '';
        } else if (modo === 'sagti') {
            if (selStatus) selStatus.value = '';
            if (selMacro) selMacro.value = 'spaguas-sa-gti';
            if (inpBusca) inpBusca.value = '';
        } else if (modo === 'pdtic') {
            if (selStatus) selStatus.value = '';
            if (selMacro) selMacro.value = '';
            if (inpBusca) inpBusca.value = 'PDTIC';
        } else {
            if (selStatus) selStatus.value = '';
            if (selMacro) selMacro.value = '';
            if (inpBusca) inpBusca.value = '';
        }

        // 3. Executar o filtro da tabela com o modo selecionado
        window.filtrarPortfolioOpenProject(modo);
    };

    window.filtrarPortfolioOpenProject = function(modoOpcional) {
        var tbody = document.getElementById('tbody-portfolio-openproject');
        if (!tbody) return;

        var modo = modoOpcional || window.opModoRapidoAtivo || 'todos';
        var dados = window.OP_PACOTES_OFICIAIS || [];

        var fMacro = (document.getElementById('op-filtro-macro') || {}).value || '';
        var fProj = (document.getElementById('op-filtro-projeto') || {}).value || '';
        var fTipo = (document.getElementById('op-filtro-tipo') || {}).value || '';
        var fStatus = (document.getElementById('op-filtro-status') || {}).value || '';
        var fResp = (document.getElementById('op-filtro-resp') || {}).value || '';
        var fBusca = ((document.getElementById('op-filtro-busca') || {}).value || '').toLowerCase().trim();

        var filtrados = dados.filter(function(p) {
            var stLower = (p.status || '').toLowerCase();

            // Filtro por modo rápido (Pills do topo)
            if (modo === 'progresso') {
                if (stLower.indexOf('progresso') === -1) return false;
            } else if (modo === 'espera') {
                if (stLower.indexOf('espera') === -1 && stLower.indexOf('agendado') === -1) return false;
            } else if (modo === 'sagti') {
                if (p.macro !== 'spaguas-sa-gti') return false;
            } else if (modo === 'pdtic') {
                var bPdtic = ((p.assunto||'') + ' ' + (p.projeto||'') + ' ' + (p.backlog||'')).toLowerCase();
                if (bPdtic.indexOf('pdtic') === -1) return false;
            }

            // Filtro por dropdown de Status (se não estiver em modo rápido conflitante)
            if (fStatus && modo === 'todos') {
                var fsLower = fStatus.toLowerCase();
                if (fsLower === 'em espera') {
                    if (stLower.indexOf('espera') === -1 && stLower.indexOf('agendado') === -1) return false;
                } else if (stLower.indexOf(fsLower) === -1) {
                    return false;
                }
            }

            // Filtros adicionais dos dropdowns
            if (fMacro && modo !== 'sagti' && p.macro !== fMacro) return false;
            if (fProj && p.projeto !== fProj) return false;
            if (fTipo && (p.tipo || '').indexOf(fTipo) === -1) return false;
            if (fResp && p.atrib !== fResp && p.autor !== fResp && p.encarr !== fResp) return false;
            if (fBusca && modo !== 'pdtic') {
                var blob = ('#' + p.id + ' ' + (p.assunto||'') + ' ' + (p.projeto||'') + ' ' + (p.pai||'') + ' ' + (p.atrib||'')).toLowerCase();
                if (blob.indexOf(fBusca) === -1) return false;
            }

            return true;
        });

        // Atualizar contador da tabela
        var headerCont = document.getElementById('op-contagem-filtrada') || document.querySelector('#view-portfolio_openproject .table-header-title span') || document.querySelector('.table-header-title');
        if (headerCont && headerCont.innerText.indexOf('Exibindo') !== -1) {
            headerCont.innerText = 'Exibindo ' + filtrados.length + ' de ' + dados.length + ' pacotes';
        }

        // Renderização HTML da tabela
        var esc = window.escapeHtml || function(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); };
        var html = '';

        filtrados.slice(0, 300).forEach(function(p) {
            var crono = (p.ini || p.fim) ? ((p.ini || '?') + ' → ' + (p.fim || '?')) : '<span style="color:#64748b;">Contínuo</span>';
            var paiTxt = p.pai ? '<span style="color:#38bdf8; font-weight:600; font-size:11px;">↳ ' + esc(p.pai) + '</span>' : '<span style="color:#64748b; font-size:11px;">Raiz do Projeto</span>';

            var sL = (p.status || '').toLowerCase();
            var stBadge = '';
            if (sL.indexOf('progresso') !== -1) {
                stBadge = '<span style="background:rgba(16,185,129,0.18); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:2px 8px; border-radius:12px; font-weight:700; font-size:10.5px;">🚀 Em progresso</span>';
            } else if (sL.indexOf('espera') !== -1 || sL.indexOf('agendado') !== -1) {
                stBadge = '<span style="background:rgba(245,158,11,0.18); color:#fbbf24; border:1px solid rgba(245,158,11,0.4); padding:2px 8px; border-radius:12px; font-weight:700; font-size:10.5px;">⏳ Em espera</span>';
            } else if (sL.indexOf('novo') !== -1) {
                stBadge = '<span style="background:rgba(56,189,248,0.18); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); padding:2px 8px; border-radius:12px; font-weight:700; font-size:10.5px;">💡 Novo</span>';
            } else {
                stBadge = '<span style="background:rgba(148,163,184,0.15); color:#cbd5e1; border:1px solid rgba(148,163,184,0.3); padding:2px 8px; border-radius:12px; font-weight:700; font-size:10.5px;">' + esc(p.status) + '</span>';
            }

            var tipoBadge = '<span style="background:rgba(255,255,255,0.06); color:#e2e8f0; border:1px solid rgba(255,255,255,0.12); padding:2px 8px; border-radius:8px; font-size:11px; font-weight:600;">' + esc(p.tipo) + '</span>';
            var linkOP = 'https://projetos.spaguas.sp.gov.br/work_packages/' + p.id;

            html += '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">' +
                '<td style="padding:10px 12px; font-family:monospace; font-weight:800;"><a href="' + linkOP + '" target="_blank" rel="noopener noreferrer" style="color:#38bdf8; text-decoration:none;">#' + p.id + '</a></td>' +
                '<td style="padding:10px 12px; color:#e2e8f0; font-weight:600;">' + esc(p.projeto) + '</td>' +
                '<td style="padding:10px 12px;">' + tipoBadge + '</td>' +
                '<td style="padding:10px 12px; color:#ffffff; font-weight:700;">' + esc(p.assunto) + '</td>' +
                '<td style="padding:10px 12px;">' + paiTxt + '</td>' +
                '<td style="padding:10px 12px;">' + stBadge + '</td>' +
                '<td style="padding:10px 12px; color:#94a3b8; font-size:11.5px;">👤 ' + esc(p.atrib || p.autor || 'Equipe') + '</td>' +
                '<td style="padding:10px 12px; text-align:center; font-family:monospace; font-size:11px; color:#cbd5e1;">' + crono + '</td>' +
                '</tr>';
        });

        tbody.innerHTML = html;
    };

    window.inicializarFiltrosPortfolioOP = function() {
        var selProj = document.getElementById('op-filtro-projeto');
        var selResp = document.getElementById('op-filtro-resp');
        var dados = window.OP_PACOTES_OFICIAIS || [];

        if (selProj && selProj.options.length <= 1) {
            var projs = [];
            dados.forEach(function(p) {
                if (p.projeto && projs.indexOf(p.projeto) === -1) projs.push(p.projeto);
            });
            projs.sort().forEach(function(pr) {
                var opt = document.createElement('option');
                opt.value = pr; opt.textContent = pr;
                selProj.appendChild(opt);
            });
        }

        if (selResp && selResp.options.length <= 1) {
            var resps = [];
            dados.forEach(function(p) {
                [p.atrib, p.autor, p.encarr].forEach(function(nome) {
                    if (nome && nome !== 'OpenProject' && resps.indexOf(nome) === -1) resps.push(nome);
                });
            });
            resps.sort().forEach(function(r) {
                var opt = document.createElement('option');
                opt.value = r; opt.textContent = r;
                selResp.appendChild(opt);
            });
        }
    };
'''

auto_init = '''
<script>
(function() {
    function initOP() {
        if (typeof window.inicializarFiltrosPortfolioOP === 'function') window.inicializarFiltrosPortfolioOP();
        if (typeof window.filtrarPortfolioOpenProject === 'function') window.filtrarPortfolioOpenProject('todos');
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOP);
    } else {
        initOP();
    }
    window.addEventListener('load', initOP);
    window.addEventListener('hashchange', function() {
        if (window.location.hash.indexOf('portfolio') !== -1 || window.location.hash.indexOf('openproject') !== -1) {
            initOP();
        }
    });
})();
</script>
'''

for caminho in caminhos:
    if not os.path.exists(caminho):
        continue

    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # 1. Garantir que a barra de botões com os IDs corretos existe
    if 'id="btn-op-progresso"' not in html:
        target_kpi = '<div class="kpi-row" style="grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 16px;">'
        pos_kpi = html.find(target_kpi)
        if pos_kpi != -1:
            html = html[:pos_kpi] + pills_bar_html + '\n\n            ' + html[pos_kpi:]

    # 2. Injetar funções de filtro se ausentes
    if 'window.filtrarModoRapidoOP' not in html:
        idx_body = html.rfind('</body>')
        if idx_body != -1:
            html = html[:idx_body] + '<script>\n' + js_op_filters + '\n</script>\n' + html[idx_body:]

    # 3. Injetar auto-init se ausente
    if 'initOP' not in html:
        idx_body = html.rfind('</body>')
        if idx_body != -1:
            html = html[:idx_body] + auto_init + '\n' + html[idx_body:]

    open_divs = len(re.findall(r'<div\b', html, re.IGNORECASE))
    close_divs = len(re.findall(r'</div\b', html, re.IGNORECASE))
    diff = open_divs - close_divs

    if diff == 0:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[*] {caminho}: Filtros rápidos ativados com sucesso! (Div balance = 0)")
    else:
        print(f"[!] Erro de div balance em {caminho}: diff={diff}")

print("\n" + "=" * 70)
print(" ATIVAÇÃO CONCLUÍDA")
print("=" * 70)
