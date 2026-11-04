import os, re

paths = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]

for p in paths:
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()

    is_crlf = '\r\n' in content
    content_norm = content.replace('\r\n', '\n')

    # 1. Substituir os dois cards pelo card único unificado
    old_block_pattern = r'<!-- PAINEL 1: MATRIZ DE CONECTORES UNIFICADA -->[\s\S]*?<div id="subcon-painel-matriz"[\s\S]*?id="tbody-motores-unificados-v9"[\s\S]*?id="tbody-motores-varredura"[\s\S]*?</div>\s*</div>\s*</div>\s*(?=\s*<!-- PAINEL 2|\s*<div id="subcon-painel-endpoints")'

    new_matriz_block = """<!-- PAINEL 1: MATRIZ DE CONECTORES UNIFICADA -->
                <div id="subcon-painel-matriz" class="subcon-painel" style="display:block;">
                    <div class="table-card" id="card-motores-unificados-v9" style="margin-bottom:20px;">
                        <!-- CABEÇALHO UNIFICADO CONSOLIDADO -->
                        <div class="table-header-bar" style="display:flex; justify-content:space-between; align-items:center; padding:15px 18px; flex-wrap:wrap; gap:12px; border-bottom:1px solid rgba(255,255,255,0.08);">
                            <div>
                                <div class="table-header-title" style="font-size:13.5px; font-weight:800; color:#ffffff; display:flex; align-items:center; gap:8px;">
                                    <span>📡 MATRIZ UNIFICADA DE CONECTORES &amp; GERENCIAMENTO DE VARREDURA</span>
                                    <span style="font-size:10px; font-weight:700; background:rgba(14,165,233,0.2); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); padding:2px 8px; border-radius:10px;">11 Fontes Mapeadas</span>
                                </div>
                                <div style="font-size:11px; color:#94a3b8; margin-top:3px;">
                                    Sondagem HTTP real com 4 status auditados, fallbacks de contingência e gestão de rotinas autônomas de coleta
                                </div>
                            </div>
                            <div style="display:flex; align-items:center; gap:8px;">
                                <button class="btn btn-secondary" onclick="window.redefinirMotoresPadrao()" style="font-size:11.5px; padding:6px 12px; border-radius:8px; font-weight:600; display:inline-flex; align-items:center; gap:6px;">
                                    🔄 Restaurar Padrões
                                </button>
                                <button class="btn btn-primary" onclick="window.abrirModalNovoMotor()" style="font-size:11.5px; padding:6px 14px; border-radius:8px; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
                                    ➕ Novo Motor
                                </button>
                            </div>
                        </div>

                        <!-- SELETOR DE VISÃO INTERNA DO CARD -->
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 18px; background:rgba(255,255,255,0.02); border-bottom:1px solid rgba(255,255,255,0.06); flex-wrap:wrap; gap:8px;">
                            <div style="display:flex; gap:8px;">
                                <button type="button" class="btn btn-primary pill-filtro-dash subtab-conector-btn active" id="btn-visao-status-http" onclick="window.alternarVisaoTabelaMotores('status')" style="font-size:11px; padding:5px 12px;">
                                    📊 1. Matriz de Status &amp; Sonda HTTP (11 Conectores)
                                </button>
                                <button type="button" class="btn btn-secondary pill-filtro-dash subtab-conector-btn" id="btn-visao-rotinas-acoes" onclick="window.alternarVisaoTabelaMotores('rotinas')" style="font-size:11px; padding:5px 12px;">
                                    ⚙️ 2. Rotinas de Coleta &amp; Ações Operacionais
                                </button>
                            </div>
                            <div style="font-size:11px; color:#94a3b8;">
                                Alterne entre a auditoria técnica de conectores e a gestão operacional de rotinas
                            </div>
                        </div>

                        <!-- VISÃO 1: STATUS & SONDA HTTP -->
                        <div id="visao-motores-status" style="display:block; overflow-x:auto;">
                            <table style="width:100%; border-collapse:collapse; font-size:12px;">
                                <thead>
                                    <tr>
                                        <th style="padding:11px 14px; text-align:left;">Motor / Barramento</th>
                                        <th style="padding:11px 14px; text-align:left;">Endpoint Oficial</th>
                                        <th style="padding:11px 14px; text-align:left;">Status Auditado</th>
                                        <th style="padding:11px 14px; text-align:left;">Proveniência / Fallback Local</th>
                                    </tr>
                                </thead>
                                <tbody id="tbody-motores-unificados-v9"></tbody>
                            </table>
                        </div>

                        <!-- VISÃO 2: GERENCIAMENTO DE ROTINAS & AÇÕES -->
                        <div id="visao-motores-rotinas" style="display:none; overflow-x:auto;">
                            <table style="width:100%; border-collapse:collapse; font-size:12px;">
                                <thead>
                                    <tr>
                                        <th style="padding:11px 14px; text-align:left;">Motor / Robô</th>
                                        <th style="padding:11px 14px; text-align:left;">Tipo / Protocolo</th>
                                        <th style="padding:11px 14px; text-align:left;">Endpoint / Alvo</th>
                                        <th style="padding:11px 14px; text-align:center;">Frequência</th>
                                        <th style="padding:11px 14px; text-align:center;">Status</th>
                                        <th style="padding:11px 14px; text-align:center;">Ações</th>
                                    </tr>
                                </thead>
                                <tbody id="tbody-motores-varredura"></tbody>
                            </table>
                        </div>
                    </div>
                </div>"""

    if re.search(old_block_pattern, content_norm):
        content_norm = re.sub(old_block_pattern, new_matriz_block, content_norm, count=1)
        print(f"[{p}] Tabelas unificadas com sucesso!")

    # 2. Injetar a função JS alternarVisaoTabelaMotores
    js_visao = """    window.alternarVisaoTabelaMotores = function(visao) {
        const vStatus = document.getElementById('visao-motores-status');
        const vRotinas = document.getElementById('visao-motores-rotinas');
        const bStatus = document.getElementById('btn-visao-status-http');
        const bRotinas = document.getElementById('btn-visao-rotinas-acoes');

        if (vStatus) vStatus.style.display = (visao === 'status') ? 'block' : 'none';
        if (vRotinas) vRotinas.style.display = (visao === 'rotinas') ? 'block' : 'none';

        if (bStatus && bRotinas) {
            if (visao === 'status') {
                bStatus.classList.add('active', 'btn-primary');
                bStatus.classList.remove('btn-secondary');
                bRotinas.classList.remove('active', 'btn-primary');
                bRotinas.classList.add('btn-secondary');
            } else {
                bRotinas.classList.add('active', 'btn-primary');
                bRotinas.classList.remove('btn-secondary');
                bStatus.classList.remove('active', 'btn-primary');
                bStatus.classList.add('btn-secondary');
            }
        }
    };"""

    if 'window.alternarVisaoTabelaMotores' not in content_norm:
        pos_js = content_norm.find('window.alternarSubAbaConectores = function')
        if pos_js != -1:
            content_norm = content_norm[:pos_js] + js_visao + "\n\n" + content_norm[pos_js:]

    final_content = content_norm.replace('\n', '\r\n') if is_crlf else content_norm
    with open(p, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"✅ Arquivo unificado e gravado com sucesso: {p}")
