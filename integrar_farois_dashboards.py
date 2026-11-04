# -*- coding: utf-8 -*-
import os, sys, re

print("=" * 70)
print(" REORGANIZAÇÃO: INTEGRAR FARÓIS & GARGALOS COMO SUB-ABA DE DASHBOARDS")
print(" Origem: Aba Independente ──> Sub-aba ao lado de Portfólio Estratégico")
print("=" * 70)

caminhos = [
    os.path.join(os.getcwd(), "frontend", "painel.html"),
    os.path.join(os.getcwd(), "painel.html")
]

for caminho in caminhos:
    if not os.path.exists(caminho):
        continue

    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # 1. Remover botão do topo em barra-subabas-eixo1 se existir
    pattern_top_btn = r'\s*<button[^>]*data-subtab=[\"\']visao_estrategica[\"\'][^>]*>[\s\S]*?</button>'
    html = re.sub(pattern_top_btn, '', html, count=1)

    # 2. Adicionar o 5º botão na barra de sub-abas da Central de Dashboards
    if 'id="btn-dash-farois"' not in html:
        target_subtab = '<button class="btn btn-secondary pill-filtro-dash" id="btn-dash-portfolio" onclick="alternarModoDashboard(\'portfolio\')">🚀 Portfólio Estratégico (31)</button>'
        new_subtab_btn = target_subtab + '\n                <button class="btn btn-secondary pill-filtro-dash" id="btn-dash-farois" onclick="alternarModoDashboard(\'farois\')">🎯 Faróis &amp; Gargalos (87)</button>'
        html = html.replace(target_subtab, new_subtab_btn)

    # 3. Mover view-visao_estrategica para dentro de view-dashboards se ainda for tab-view externa
    if '<div id="view-visao_estrategica" class="tab-view">' in html:
        idx_ve_start = html.find('<div id="view-visao_estrategica" class="tab-view">')
        idx_ve_end = html.find('<div id="view-', idx_ve_start + 30)

        ve_block = html[idx_ve_start:idx_ve_end]

        idx_first_close = ve_block.find('>') + 1
        idx_last_close = ve_block.rfind('</div>')
        ve_inner = ve_block[idx_first_close:idx_last_close].strip()

        pattern_ve_banner = r'\s*<div class="page-banner"[\s\S]*?</div>\s*</div>'
        ve_inner_clean = re.sub(pattern_ve_banner, '', ve_inner, count=1).strip()

        subview_farois_html = f'''
            <!-- SUB-VIEW 5: FARÓIS & GARGALOS OPERACIONAIS (87) -->
            <div id="subview-dash-farois" class="subview-dash" style="display: none;">
                {ve_inner_clean}
            </div>'''

        html = html[:idx_ve_start] + html[idx_ve_end:]
        idx_dash_close = html.rfind('</div>', 0, idx_ve_start)
        html = html[:idx_dash_close] + subview_farois_html + '\n        ' + html[idx_dash_close:]

    # 4. Injetar a lógica JS de alternarModoDashboard se ausente
    if 'window.alternarModoDashboard' not in html or 'btn-dash-farois' not in html:
        js_switcher = '''
<script>
(function() {
    window.modoDashboardAtivo = 'consolidado';

    window.alternarModoDashboard = function(modo) {
        window.modoDashboardAtivo = modo || 'consolidado';

        var modos = ['consolidado', 'esteira', 'rotina', 'portfolio', 'farois'];
        modos.forEach(function(m) {
            var btn = document.getElementById('btn-dash-' + m);
            if (btn) {
                if (m === modo) {
                    btn.className = 'btn btn-primary pill-filtro-dash active';
                    btn.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                    btn.style.color = '#ffffff';
                    btn.style.fontWeight = '700';
                } else {
                    btn.className = 'btn btn-secondary pill-filtro-dash';
                    btn.style.background = 'rgba(255,255,255,0.06)';
                    btn.style.color = '#cbd5e1';
                    btn.style.fontWeight = '600';
                }
            }
        });

        document.querySelectorAll('#view-dashboards .subview-dash').forEach(function(el) {
            el.style.display = 'none';
        });

        var target = document.getElementById('subview-dash-' + modo);
        if (target) target.style.display = 'block';

        var titulos = {
            'consolidado': {
                titulo: '📊 CENTRAL DE DASHBOARDS: VISÃO CONSOLIDADA 360°',
                desc: 'Visão executiva integrada de todos os 179 processos de TIC da SA-GTI',
                badge: '🌐 179 Processos no Backlog'
            },
            'esteira': {
                titulo: '📑 ESTEIRA DE CONTRATAÇÃO & LICITAÇÕES (LEI 14.133/2021)',
                desc: 'Acompanhamento de DFD, ETP, Termos de Referência e Pareceres Jurídicos',
                badge: '📑 55 Processos em Contratação'
            },
            'rotina': {
                titulo: '⚙️ ROTINA OPERACIONAL & SUSTENTAÇÃO DE TIC',
                desc: 'Fiscalização técnica, IMR, faturas de concessionárias e medições PRODESP',
                badge: '⚙️ 93 Processos Operacionais'
            },
            'portfolio': {
                titulo: '🚀 PORTFÓLIO ESTRATÉGICO & INICIATIVAS ESTRUTURANTES',
                desc: 'Modernização de infraestrutura, nuvem FinOps e desenvolvimento de sistemas',
                badge: '🚀 31 Projetos Estratégicos'
            },
            'farois': {
                titulo: '🎯 VISÃO ESTRATÉGICA: FARÓIS & GARGALOS OPERACIONAIS',
                desc: 'Monitoramento executivo por farol, segregação de custódia (Interno SA-GTI vs. Suspensões Externas "Poréns") e apuração de Aging Líquido',
                badge: '🎯 87 Processos Auditados'
            }
        };

        var info = titulos[modo] || titulos['consolidado'];
        var elTitulo = document.getElementById('dash-banner-titulo') || document.querySelector('#view-dashboards .page-banner h3');
        var elDesc = document.getElementById('dash-banner-desc') || document.querySelector('#view-dashboards .page-banner p');
        var elBadge = document.getElementById('dash-banner-badge');
        if (elTitulo) elTitulo.innerText = info.titulo;
        if (elDesc) elDesc.innerText = info.desc;
        if (elBadge) elBadge.innerText = info.badge;

        if (modo === 'farois') {
            if (typeof window.filtrarModoFarol === 'function') {
                window.filtrarModoFarol(window.modoFarolAtivo || 'todos');
            }
        }
    };
})();
</script>
'''
        idx_body = html.rfind('</body>')
        if idx_body != -1:
            html = html[:idx_body] + js_switcher + '\n' + html[idx_body:]

    open_divs = len(re.findall(r'<div\b', html, re.IGNORECASE))
    close_divs = len(re.findall(r'</div\b', html, re.IGNORECASE))
    diff = open_divs - close_divs

    if diff == 0:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[*] {caminho}: Reorganização concluída com sucesso! (Div balance = 0)")
    else:
        print(f"[!] Erro de div balance em {caminho}: diff={diff}")

print("\n" + "=" * 70)
print(" INTEGRAÇÃO DE FARÓIS & GARGALOS CONCLUÍDA")
print("=" * 70)
