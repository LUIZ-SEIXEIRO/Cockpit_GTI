# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
caminho_painel = os.path.join(frontend_dir, "painel.html")
caminho_js = os.path.join(frontend_dir, "conector_api.js")

# 1. ATUALIZAR painel.html COM PILLS RÁPIDAS E LINKS DO OPENPROJECT
if os.path.exists(caminho_painel):
    with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    ancora_banner = '''<div style="display:flex; gap:8px; align-items:center;">
                    
                </div>
            </div>

            <div class="kpi-row" style="grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 16px;">'''

    pills_op = '''<div style="display:flex; gap:8px; align-items:center;">
                    <a href="https://projetos.spaguas.sp.gov.br" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="font-size:11px; padding:5px 10px; background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); color:#fff; text-decoration:none; font-weight:700;">🌐 Abrir projetos.spaguas.sp.gov.br ↗</a>
                </div>
            </div>

            <!-- SELETOR RÁPIDO DE MODOS E VISÕES DO OPENPROJECT -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; background: white; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--sp-border); box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                    <button class="btn btn-primary pill-filtro-op" id="btn-op-todos" onclick="window.filtrarModoRapidoOP('todos')">🌐 Todos os Pacotes (500)</button>
                    <button class="btn btn-secondary pill-filtro-op" id="btn-op-sagti" onclick="window.filtrarModoRapidoOP('sagti')">⚡ Tracks SA-GTI (97)</button>
                    <button class="btn btn-secondary pill-filtro-op" id="btn-op-pdtic" onclick="window.filtrarModoRapidoOP('pdtic')">🧭 PDTIC 2027-2030 (35)</button>
                    <button class="btn btn-secondary pill-filtro-op" id="btn-op-progresso" onclick="window.filtrarModoRapidoOP('progresso')">🚀 Em Progresso</button>
                    <button class="btn btn-secondary pill-filtro-op" id="btn-op-espera" onclick="window.filtrarModoRapidoOP('espera')">⏸️ Em Espera</button>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: #166534; background: #dcfce7; padding: 4px 10px; border-radius: 12px; border: 1px solid #bbf7d0;">
                    <span>🛡️ Trava de Segurança SA-GTI Ativa</span>
                    <span style="font-weight: normal; color: #15803d;">(Escopo: spaguas-sa-gti)</span>
                </div>
            </div>

            <div class="kpi-row" style="grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 16px;">'''

    antigo_td_id = '\'<td style="padding:8px 12px;font-weight:800;color:#002d5a;font-family:monospace;">#\' + p.id + \'</td>\''
    novo_td_id = '\'<td style="padding:8px 12px;font-weight:800;font-family:monospace;">\' + (p.id ? (\'<a href="https://projetos.spaguas.sp.gov.br/work_packages/\' + p.id + \'" target="_blank" rel="noopener noreferrer" style="color:#0070ba;text-decoration:underline;" title="Abrir Pacote no OpenProject Oficial">#\' + p.id + \'</a>\') : \'<span style="color:#94a3b8;">#REF</span>\') + \'</td>\''

    alterado = False
    if ancora_banner in html:
        html = html.replace(ancora_banner, pills_op)
        alterado = True

    if antigo_td_id in html:
        html = html.replace(antigo_td_id, novo_td_id)
        alterado = True

    if alterado:
        with open(caminho_painel, "w", encoding="utf-8") as f:
            f.write(html)
        print("1. painel.html atualizado com pills e links do OpenProject!")
    else:
        print("1. painel.html já possuía os ajustes do OpenProject.")

# 2. INJETAR LÓGICA DE FILTROS RÁPIDOS NO conector_api.js
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8", errors="ignore") as f:
        js = f.read()

    bloco_op_js = r'''
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
'''

    if "filtrarModoRapidoOP" not in js:
        idx_init = js.find("function init()")
        if idx_init != -1:
            js = js[:idx_init] + bloco_op_js + "\n    " + js[idx_init:]
        with open(caminho_js, "w", encoding="utf-8") as f:
            f.write(js)
        print("2. conector_api.js atualizado com o controlador de pills do OpenProject!")
    else:
        print("2. conector_api.js já possuía o controlador de pills.")

print("Aba 3 (Portfólio OpenProject) saneada com sucesso!")
