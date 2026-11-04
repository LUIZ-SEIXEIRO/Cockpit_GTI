import os, re

paths = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]

js_visao_full = """    window.alternarVisaoTabelaMotores = function(visao) {
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

        if (visao === 'rotinas' && typeof window.renderizarTabelaMotores === 'function') {
            window.renderizarTabelaMotores();
        }
    };"""

css_extra = """
    /* Ajustes de contraste para a tabela de rotinas de varredura */
    #tbody-motores-varredura tr {
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    #tbody-motores-varredura strong {
        color: #ffffff !important;
    }
    #tbody-motores-varredura td {
        color: #cbd5e1 !important;
    }
    #tbody-motores-varredura td div {
        color: #94a3b8 !important;
    }
"""

for p in paths:
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()

    is_crlf = '\r\n' in content
    content_norm = content.replace('\r\n', '\n')

    # 1. Injetar ou substituir com certeza a função window.alternarVisaoTabelaMotores
    if 'window.alternarVisaoTabelaMotores = function' in content_norm:
        content_norm = re.sub(r'window\.alternarVisaoTabelaMotores\s*=\s*function\s*\(visao\)\s*\{[\s\S]*?\};', js_visao_full.strip(), content_norm, count=1)
        print(f"[{p}] Função alternarVisaoTabelaMotores atualizada.")
    else:
        pos_js = content_norm.find('window.alternarSubAbaConectores = function')
        if pos_js != -1:
            content_norm = content_norm[:pos_js] + js_visao_full + "\n\n" + content_norm[pos_js:]
            print(f"[{p}] Função alternarVisaoTabelaMotores injetada com sucesso!")

    # 2. Corrigir contraste de texto inline na tabela de rotinas
    content_norm = content_norm.replace('color: #002d5a;', 'color: #ffffff;')
    content_norm = content_norm.replace('color: #334155;', 'color: #38bdf8;')
    content_norm = content_norm.replace('color: #64748b;', 'color: #94a3b8;')

    # 3. Adicionar regras CSS no crypto-executive-theme se necessário
    if '#tbody-motores-varredura strong' not in content_norm:
        pos_theme = content_norm.find('id="crypto-executive-theme"')
        if pos_theme != -1:
            pos_end_style = content_norm.find('</style>', pos_theme)
            if pos_end_style != -1:
                content_norm = content_norm[:pos_end_style] + css_extra + content_norm[pos_end_style:]

    final_content = content_norm.replace('\n', '\r\n') if is_crlf else content_norm
    with open(p, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"✅ Arquivo atualizado com sucesso: {p}")
