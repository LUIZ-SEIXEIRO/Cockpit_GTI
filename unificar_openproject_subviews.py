# -*- coding: utf-8 -*-
import os, sys, re

print("=" * 70)
print(" REORGANIZAÇÃO: UNIFICAÇÃO DE TRACKS E PDTIC NO PORTFÓLIO OPENPROJECT")
print(" Eliminação de abas duplicadas no topo e fusão em sub-abas temáticas")
print("=" * 70)

caminhos = [
    os.path.join(os.getcwd(), "frontend", "painel.html"),
    os.path.join(os.getcwd(), "painel.html")
]

subviews_op_js = """
<script>
(function() {
    window.opModoRapidoAtivo = 'todos';

    window.filtrarModoRapidoOP = function(modo) {
        window.opModoRapidoAtivo = modo || 'todos';

        // 1. Atualizar botões de sub-aba do Portfólio
        var ids = ['btn-op-todos', 'btn-op-sagti', 'btn-op-pdtic'];
        var mapa = {
            'todos': 'btn-op-todos',
            'sagti': 'btn-op-sagti',
            'pdtic': 'btn-op-pdtic'
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

        // 2. Alternar visibilidade das 3 subviews
        var svTodos = document.getElementById('subview-op-todos');
        var svSagti = document.getElementById('subview-op-sagti');
        var svPdtic = document.getElementById('subview-op-pdtic');

        if (svTodos) svTodos.style.display = (modo === 'todos') ? 'block' : 'none';
        if (svSagti) svSagti.style.display = (modo === 'sagti') ? 'block' : 'none';
        if (svPdtic) svPdtic.style.display = (modo === 'pdtic') ? 'block' : 'none';

        // 3. Executar o renderizador da subview selecionada
        if (modo === 'todos') {
            if (typeof window.filtrarPortfolioOpenProject === 'function') {
                window.filtrarPortfolioOpenProject('todos');
            }
        } else if (modo === 'sagti') {
            if (typeof window.filtrarPilarSagti === 'function') {
                window.filtrarPilarSagti(window.pilarSagtiAtivo || 'todos');
            }
        } else if (modo === 'pdtic') {
            if (typeof window.filtrarEixoPdtic === 'function') {
                window.filtrarEixoPdtic(window.eixoPdticAtivo || '');
            }
        }
    };

    window.filtrarPilarSagti = function(pilar) {
        window.pilarSagtiAtivo = pilar || 'todos';
        var tbody = document.getElementById('tbody-tracks-sagti');
        if (!tbody) return;
        var dados = window.OP_PACOTES_OFICIAIS || [];
        var itensGti = dados.filter(function(p) {
            if (p.macro !== 'spaguas-sa-gti' && p.projeto !== 'SA-GTI - Gerência de TI' && p.projeto !== 'Divisão de Infraestrutura') return false;
            if (pilar && pilar !== 'todos') {
                if (pilar === 'A-017' && p.projeto === 'Divisão de Infraestrutura') return true;
                return (p.backlog || '').indexOf(pilar) !== -1;
            }
            return true;
        });

        var bTodos = document.getElementById('btn-pilar-todos');
        var bA018 = document.getElementById('btn-pilar-a018');
        var bA017 = document.getElementById('btn-pilar-a017');
        if (bTodos) bTodos.className = (pilar === 'todos') ? 'btn btn-primary' : 'btn btn-secondary';
        if (bA018) bA018.className = (pilar === 'A-018') ? 'btn btn-primary' : 'btn btn-secondary';
        if (bA017) bA017.className = (pilar === 'A-017') ? 'btn btn-primary' : 'btn btn-secondary';

        var cnt = document.getElementById('sagti-tracks-count');
        if (cnt) cnt.innerText = itensGti.length + ' pacotes SA-GTI';

        var esc = window.escapeHtml || function(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); };
        var html = '';
        itensGti.forEach(function(p) {
            var bgTag = p.backlog ? p.backlog.split('.')[0] : (p.projeto === 'Divisão de Infraestrutura' ? 'DIF-INFRA' : 'SA-GTI');
            var corBg = bgTag.indexOf('A-018') !== -1 ? 'background:rgba(56,189,248,0.18); color:#38bdf8; border:1px solid rgba(56,189,248,0.4);' : (bgTag.indexOf('A-017') !== -1 || bgTag === 'DIF-INFRA' ? 'background:rgba(168,85,247,0.18); color:#c084fc; border:1px solid rgba(168,85,247,0.4);' : 'background:rgba(16,185,129,0.18); color:#34d399; border:1px solid rgba(16,185,129,0.4);');
            var crono = (p.ini || p.fim) ? ((p.ini || '?') + ' → ' + (p.fim || '?')) : '<span style="color:#64748b;">Contínuo</span>';
            var linkOP = 'https://projetos.spaguas.sp.gov.br/work_packages/' + p.id;

            html += '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">' +
                '<td style="padding:10px 12px; font-family:monospace; font-weight:800;"><a href="' + linkOP + '" target="_blank" rel="noopener noreferrer" style="color:#38bdf8; text-decoration:none;">#' + p.id + '</a></td>' +
                '<td style="padding:10px 12px;"><span style="padding:2px 8px; border-radius:8px; font-size:11px; font-weight:700; ' + corBg + '">' + esc(p.backlog || p.projeto) + '</span></td>' +
                '<td style="padding:10px 12px;"><span style="background:rgba(255,255,255,0.06); color:#e2e8f0; border:1px solid rgba(255,255,255,0.12); padding:2px 8px; border-radius:8px; font-size:11px; font-weight:600;">' + esc(p.tipo) + '</span></td>' +
                '<td style="padding:10px 12px; font-weight:700; color:#ffffff;">' + esc(p.assunto) + '</td>' +
                '<td style="padding:10px 12px; color:#94a3b8; font-size:11px;">' + (p.pai ? '↳ ' + esc(p.pai) : 'Raiz') + '</td>' +
                '<td style="padding:10px 12px;"><span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; background:rgba(56,189,248,0.15); color:#38bdf8;">' + esc(p.status) + '</span></td>' +
                '<td style="padding:10px 12px; color:#cbd5e1; font-size:11.5px;">👤 ' + esc(p.atrib || p.autor || 'SA-GTI') + '</td>' +
                '<td style="padding:10px 12px; text-align:center; font-family:monospace; font-size:11px; color:#cbd5e1;">' + crono + '</td>' +
                '</tr>';
        });
        tbody.innerHTML = html;
    };

    window.filtrarEixoPdtic = function(eixo) {
        window.eixoPdticAtivo = eixo || '';
        var dados = window.OP_PACOTES_OFICIAIS || [];

        var gridKpis = document.getElementById('grid-kpis-pdtic-oficial');
        if (gridKpis) {
            var kpis = [
                { id: '1221', assunto: 'KPI-001: Disponibilidade dos Links WAN e SD-WAN', desc: 'Meta IMR >= 99.5% em todas as 22 Diretorias de Bacia' },
                { id: '1222', assunto: 'KPI-002: Resiliência de Backup 3-2-1-1-0 e RTO <= 4h', desc: 'Cópias imutáveis WORM e testes trimestrais em sandbox' },
                { id: '1223', assunto: 'KPI-003: Eficiência Operacional e Aging Médio SEI', desc: 'Redução da inércia interna da SA-GTI para menos de 30 dias' },
                { id: '1224', assunto: 'KPI-004: Conformidade Súmula 269 TCU (UST/PF)', desc: '100% dos pagamentos de fábrica de software vinculados a entregáveis' },
                { id: '1225', assunto: 'KPI-005: Governança de Custos Nuvem (FinOps)', desc: 'Otimização contínua de recursos elásticos e reversibilidade' },
                { id: '1226', assunto: 'KPI-006: Matriz de Riscos de TIC (R01 a R12)', desc: 'Mitigação proativa de riscos de segurança ISO/IEC 27001' },
                { id: '1227', assunto: 'KPI-007: Resolução de Incidentes GLPI no SLA', desc: 'Meta de 95% dos chamados atendidos dentro da faixa pactuada' },
                { id: '1228', assunto: 'KPI-008: Execução das 35 Iniciativas do PDTIC', desc: 'Acompanhamento do cronograma físico-financeiro no OpenProject' }
            ];
            var esc = window.escapeHtml || function(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); };
            gridKpis.innerHTML = kpis.map(function(k) {
                return '<div style="background:rgba(15,23,42,0.7); border:1px solid rgba(255,255,255,0.08); border-left:4px solid #38bdf8; border-radius:10px; padding:12px;">' +
                    '<div style="font-size:10.5px; font-weight:800; color:#38bdf8;">#' + k.id + ' • INDICADOR OFICIAL</div>' +
                    '<div style="font-size:12.5px; font-weight:700; color:#ffffff; margin:4px 0;">' + esc(k.assunto) + '</div>' +
                    '<div style="font-size:11px; color:#94a3b8; line-height:1.4;">' + esc(k.desc) + '</div>' +
                    '</div>';
            }).join('');
        }

        var tbody = document.getElementById('tbody-pdtic-iniciativas');
        if (!tbody) return;

        var inics = dados.filter(function(p) {
            if (p.tipo !== 'Iniciativas' && (p.assunto||'').indexOf('E1-') === -1 && (p.assunto||'').indexOf('E2-') === -1 && (p.assunto||'').indexOf('E3-') === -1 && (p.assunto||'').indexOf('E4-') === -1 && (p.assunto||'').indexOf('E5-') === -1) {
                if ((p.assunto||'').indexOf('PDTIC') === -1) return false;
            }
            if (eixo && p.projeto.indexOf(eixo) === -1 && (p.assunto||'').indexOf(eixo) === -1) return false;
            return true;
        });

        var cnt = document.getElementById('pdtic-inic-count');
        if (cnt) cnt.innerText = inics.length + ' iniciativas oficiais';

        var esc = window.escapeHtml || function(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); };
        var html = '';
        inics.forEach(function(i) {
            var prioBg = (i.prio === 'Imediata' || (i.prio||'').indexOf('Alt') !== -1) ? 'background:rgba(239,68,68,0.2); color:#f87171; border:1px solid rgba(239,68,68,0.4);' : 'background:rgba(56,189,248,0.2); color:#38bdf8; border:1px solid rgba(56,189,248,0.4);';
            var vig = (i.ini || i.fim) ? ((i.ini || '?') + ' → ' + (i.fim || '?')) : '2027 → 2030';
            var linkOP = 'https://projetos.spaguas.sp.gov.br/work_packages/' + i.id;

            html += '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">' +
                '<td style="padding:10px 12px; font-family:monospace; font-weight:800;"><a href="' + linkOP + '" target="_blank" rel="noopener noreferrer" style="color:#38bdf8; text-decoration:none;">#' + i.id + '</a></td>' +
                '<td style="padding:10px 12px; color:#e2e8f0; font-weight:600;">' + esc(i.projeto) + '</td>' +
                '<td style="padding:10px 12px; color:#ffffff; font-weight:700;">' + esc(i.assunto) + '</td>' +
                '<td style="padding:10px 12px;"><span style="padding:2px 8px; border-radius:12px; font-size:10.5px; font-weight:700; ' + prioBg + '">' + esc(i.prio || 'Normal') + '</span></td>' +
                '<td style="padding:10px 12px; color:#cbd5e1; font-size:11.5px;">👤 ' + esc(i.atrib || 'Comitê de TIC') + '</td>' +
                '<td style="padding:10px 12px; text-align:center; font-family:monospace; font-size:11px; color:#cbd5e1;">' + vig + '</td>' +
                '</tr>';
        });
        tbody.innerHTML = html;
    };
})();
</script>
"""

for caminho in caminhos:
    if not os.path.exists(caminho):
        continue

    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # 1. Remover os 2 botões redundantes da barra superior barra-subabas-eixo1
    pattern_sagti_btn = r'\s*<button[^>]*data-subtab=[\"\']tracks_sagti[\"\'][^>]*>[\s\S]*?</button>'
    pattern_pdtic_btn = r'\s*<button[^>]*data-subtab=[\"\']pdtic_eixos[\"\'][^>]*>[\s\S]*?</button>'
    html = re.sub(pattern_sagti_btn, '', html, count=1)
    html = re.sub(pattern_pdtic_btn, '', html, count=1)

    # 2. Localizar e fundir as views se ainda existirem como tab-views separadas
    idx_op_start = html.find('<div id="view-portfolio_openproject" class="tab-view">')
    idx_tr_start = html.find('<div id="view-tracks_sagti" class="tab-view">')
    idx_pd_start = html.find('<div id="view-pdtic_eixos" class="tab-view">')
    idx_gl_start = html.find('<div id="view-gestao_glpi"', idx_op_start if idx_op_start != -1 else 0)

    if idx_op_start != -1 and idx_tr_start != -1 and idx_pd_start != -1 and idx_gl_start != -1:
        tr_block = html[idx_tr_start:idx_pd_start]
        idx_tr_first = tr_block.find('>') + 1
        idx_tr_last = tr_block.rfind('</div>')
        tr_inner = tr_block[idx_tr_first:idx_tr_last].strip()

        pd_block = html[idx_pd_start:idx_gl_start]
        idx_pd_first = pd_block.find('>') + 1
        idx_pd_last = pd_block.rfind('</div>')
        pd_inner = pd_block[idx_pd_first:idx_pd_last].strip()

        op_block = html[idx_op_start:idx_tr_start]
        idx_op_first = op_block.find('>') + 1
        idx_op_last = op_block.rfind('</div>')
        op_inner = op_block[idx_op_first:idx_op_last].strip()

        idx_pills_end = op_inner.find('</div>\n\n            <div class="kpi-row"')
        if idx_pills_end == -1:
            idx_pills_end = op_inner.find('</div>', op_inner.find('id="container-pills-op"')) + 6

        pills_op_header = op_inner[:idx_pills_end].strip()
        op_todos_body = op_inner[idx_pills_end:].strip()

        pills_op_header = pills_op_header.replace('🧭 PDTIC 2027-2030 (35)', '🧭 Governança PDTIC 2027-2030 &amp; KPIs (35)')

        nova_view_portfolio = f'''<div id="view-portfolio_openproject" class="tab-view">
            {pills_op_header}

            <!-- SUB-VIEW 1: TODOS OS PACOTES (500) -->
            <div id="subview-op-todos" class="subview-op">
                {op_todos_body}
            </div>

            <!-- SUB-VIEW 2: TRACKS SA-GTI (97) -->
            <div id="subview-op-sagti" class="subview-op" style="display: none;">
                {tr_inner}
            </div>

            <!-- SUB-VIEW 3: GOVERNANÇA PDTIC 2027-2030 & KPIS (35) -->
            <div id="subview-op-pdtic" class="subview-op" style="display: none;">
                {pd_inner}
            </div>
        </div>

            '''
        html = html[:idx_op_start] + nova_view_portfolio + html[idx_gl_start:]

    # 3. Injetar a lógica JS de controle das sub-abas se ausente
    if 'window.filtrarPilarSagti' not in html:
        idx_body = html.rfind('</body>')
        if idx_body != -1:
            html = html[:idx_body] + subviews_op_js + '\n' + html[idx_body:]

    open_divs = len(re.findall(r'<div\b', html, re.IGNORECASE))
    close_divs = len(re.findall(r'</div\b', html, re.IGNORECASE))
    diff = open_divs - close_divs

    if diff == 0:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[*] {caminho}: Reorganização e fusão concluídas com sucesso! (Div balance = 0)")
    else:
        print(f"[!] Erro de balanceamento de divs em {caminho}: diff={diff}")

print("\n" + "=" * 70)
print(" UNIFICAÇÃO DO OPENPROJECT CONCLUÍDA")
print("=" * 70)
