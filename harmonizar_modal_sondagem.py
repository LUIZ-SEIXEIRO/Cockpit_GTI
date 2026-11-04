import os

base_dir = r"C:\Cockpit_GTI"
alvos = []

if os.path.exists(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower() == "painel.html":
                alvos.append(os.path.join(root, f))
else:
    alvos = [r"frontend\painel.html", "painel.html"]

if not alvos:
    print("❌ Nenhuma cópia de painel.html encontrada!")
    exit(1)

css_modal = """
    /* ==========================================================
       MODAL DE SONDAGEM REAL DOS MOTORES (#modal-sonda-real-v9)
       ========================================================== */
    #modal-sonda-real-v9 {
        background: rgba(0, 0, 0, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
    }
    #modal-sonda-real-v9 > div {
        background: #0b0f19 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-top: 4px solid #0ea5e9 !important;
        border-radius: 18px !important;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.85) !important;
        color: #ffffff !important;
    }
    #modal-sonda-real-v9 h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    #modal-sonda-real-v9 div[style*="color:#64748b"],
    #modal-sonda-real-v9 div[style*="color: #64748b"] {
        color: #94a3b8 !important;
    }
    #modal-sonda-real-v9 table {
        background: transparent !important;
        border-collapse: collapse !important;
    }
    #modal-sonda-real-v9 table thead tr {
        background: rgba(15, 23, 42, 0.95) !important;
    }
    #modal-sonda-real-v9 table thead th {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 10px 12px !important;
    }
    #modal-sonda-real-v9 table tbody tr td {
        background: rgba(15, 23, 42, 0.6) !important;
        color: #f1f5f9 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding: 12px 12px !important;
        font-size: 12px !important;
    }
    #modal-sonda-real-v9 table tbody tr:hover td {
        background: rgba(30, 41, 59, 0.8) !important;
    }
    #modal-sonda-real-v9 table tbody td a,
    #modal-sonda-real-v9 table tbody td[style*="monospace"] {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    #modal-sonda-real-v9 .btn-secondary {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        font-weight: 700 !important;
    }
    #modal-sonda-real-v9 .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }
"""

new_modal_js = """modal.innerHTML = '<div style="background:#0b0f19;border-radius:18px;max-width:880px;width:100%;max-height:88vh;overflow-y:auto;box-shadow:0 24px 60px rgba(0,0,0,0.85);border:1px solid rgba(255,255,255,0.12);border-top:4px solid #0ea5e9;padding:22px;color:#ffffff;">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:14px;margin-bottom:16px;">' +
                '<div>' +
                    '<h3 style="margin:0;color:#ffffff;font-size:16px;font-weight:800;">&#128269; Diagn&oacute;stico Real dos 8 Motores &amp; Portais Oficiais (Zero Falso Positivo)</h3>' +
                    '<div style="font-size:11.5px;color:#94a3b8;margin-top:3px;">Sondagem HTTP com AbortController + Medidor de Lat&ecirc;ncia &bull; ' + onlineCnt + ' Online Vivo | ' + localCnt + ' Fonte Local Auditada | ' + semSondaCnt + ' Sem Sonda Ativa</div>' +
                '</div>' +
                '<button onclick="document.getElementById(\\'modal-sonda-real-v9\\').style.display=\\'none\\'" class="btn btn-secondary" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#fff;font-weight:700;">&#10006; Fechar</button>' +
            '</div>' +
            '<table style="width:100%;border-collapse:collapse;font-size:12px;">' +
                '<thead><tr style="background:rgba(15,23,42,0.95);color:#94a3b8;"><th style="padding:10px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.1);">Motor / Conector</th><th style="padding:10px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.1);">Endpoint Sondado</th><th style="padding:10px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.1);">Status Real</th><th style="padding:10px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.1);">Proveni&ecirc;ncia / Evid&ecirc;ncia</th></tr></thead>' +
                '<tbody>' +
                resultados.map(function(r) {
                    return '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">' +
                        '<td style="padding:12px 12px;font-weight:700;color:#ffffff;">' + window.escapeHtml(r.nome) + '</td>' +
                        '<td style="padding:12px 12px;font-family:monospace;font-size:11.5px;color:#38bdf8;font-weight:700;word-break:break-all;">' + window.escapeHtml(r.endpoint) + '</td>' +
                        '<td style="padding:12px 12px;white-space:nowrap;">' + r.badgeHtml + '</td>' +
                        '<td style="padding:12px 12px;font-size:11.5px;color:#cbd5e1;">' + window.escapeHtml(r.detalhe) + '</td>' +
                    '</tr>';
                }).join('') +
                '</tbody>' +
            '</table>' +
        '</div>';"""

for target in alvos:
    try:
        with open(target, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        # 1. Atualizar o template JS da modal de sondagem
        p_start = text.find('modal.innerHTML = \'<div style="background:#fff;border-radius:12px;')
        if p_start != -1:
            p_end = text.find("</div>';", p_start)
            if p_end != -1:
                p_end += len("</div>';")
                text = text[:p_start] + new_modal_js + text[p_end:]

        # 2. Injetar CSS de alto contraste para a modal
        if '#modal-sonda-real-v9' not in text:
            pos_style = text.find('<style id="crypto-executive-theme">')
            if pos_style != -1:
                end_style = text.find('</style>', pos_style)
                text = text[:end_style] + css_modal + text[end_style:]

        with open(target, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ [CONTRASTE ATUALIZADO] -> {target}")
    except Exception as e:
        print(f"❌ Erro ao atualizar {target}: {e}")

print("🏁 Todas as instâncias da modal de sondagem foram harmonizadas!")
