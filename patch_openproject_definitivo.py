# -*- coding: utf-8 -*-
import os, sys, zlib, base64, re

RELATORIO_OP_B64 = """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"""

def aplicar_patch_op():
    caminhos = ["frontend/painel.html", "painel.html"]
    alvos = [c for c in caminhos if os.path.exists(c)]
    if not alvos:
        print("❌ Erro: painel.html não encontrado no diretório atual!")
        sys.exit(1)

    relatorio_op_html = zlib.decompress(base64.b64decode(RELATORIO_OP_B64.encode('ascii'))).decode('utf-8')

    barra_op_html = """            <!-- SELETOR DE SUB-ABAS OFICIAL OPENPROJECT (DESIGN SYSTEM SP-ÁGUAS V11) -->
            <div id="barra-subabas-op" style="display: flex; gap: 8px; margin-bottom: 16px; background: rgba(15,23,42,0.85); padding: 8px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); align-items: center; flex-wrap: wrap;">
                <span style="font-size: 11px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em; margin-right: 6px; display: flex; align-items: center; gap: 6px;">
                    <span>🏗️</span> MÓDULO OPENPROJECT:
                </span>
                <button type="button" id="btn-op-subaba-operacional" class="btn btn-primary active" onclick="window.alternarSubAbaOpenProject('operacional')" style="background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%); color: #ffffff; font-weight: 700; font-size: 12px; padding: 7px 16px; border-radius: 8px; border: 1px solid rgba(56,189,248,0.5); cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 8px rgba(2,132,199,0.3);">
                    <span>🌐</span> Todos os Pacotes &amp; Estrutura (500)
                </button>
                <button type="button" id="btn-op-subaba-relatorio" class="btn btn-secondary" onclick="window.alternarSubAbaOpenProject('relatorio')" style="background: rgba(255,255,255,0.06); color: #cbd5e1; font-weight: 600; font-size: 12px; padding: 7px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12); cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s ease;">
                    <span>📑</span> Relatório Mensal Executivo do Portfólio OpenProject (Novembro/2026)
                </button>
                <div style="margin-left: auto; display: flex; align-items: center; gap: 8px;">
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: #4ade80; background: rgba(16,185,129,0.15); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(16,185,129,0.3);">
                        <span>🛡️ Trava de Segurança SA-GTI Ativa</span>
                        <span style="font-weight: normal; color: #86efac;">(Escopo: spaguas-sa-gti)</span>
                    </div>
                </div>
            </div>"""

    for alvo in alvos:
        with open(alvo, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        print(f"📖 Processando {alvo} ({len(text)} caracteres)...")

        p_op = text.find('id="view-portfolio_openproject"')
        if p_op == -1:
            print(f"⚠️ view-portfolio_openproject não encontrada em {alvo}, pulando...")
            continue

        p_next_view = text.find('id="view-', p_op + 30)
        if p_next_view == -1: p_next_view = text.find('<script', p_op)

        # 1. Localiza a barra antiga (que contém Tracks SA-GTI, btn-op-sagti ou Trava de Segurança)
        match_termo = None
        for termo in ['btn-op-sagti', 'Tracks SA-GTI', 'btn-op-todos', 'Trava de Segurança SA-GTI']:
            pos_t = text.find(termo, p_op, p_next_view)
            if pos_t != -1:
                match_termo = pos_t
                break

        if match_termo:
            p_div_barra_start = text.rfind('<div', p_op, match_termo)
            pos = p_div_barra_start + 4
            depth = 1
            while depth > 0 and pos < p_next_view:
                no = text.find('<div', pos, p_next_view)
                nc = text.find('</div>', pos, p_next_view)
                if nc == -1: break
                if no != -1 and no < nc:
                    depth += 1
                    pos = no + 4
                else:
                    depth -= 1
                    pos = nc + 6
            p_div_barra_end = pos
            print(f"   Barra antiga localizada e removida (posições {p_div_barra_start} a {p_div_barra_end})")
            text = text[:p_div_barra_start] + barra_op_html + text[p_div_barra_end:]
        elif 'id="barra-subabas-op"' not in text[p_op:p_next_view]:
            p_kpi = text.find('class="kpi-row"', p_op, p_next_view)
            if p_kpi != -1:
                p_kpi_start = text.rfind('<div', p_op, p_kpi)
                text = text[:p_kpi_start] + barra_op_html + "\n" + text[p_kpi_start:]
                print("   Nova barra oficial inserida antes dos KPIs!")

        # Recalcula limites
        p_op = text.find('id="view-portfolio_openproject"')
        p_next_view = text.find('id="view-', p_op + 30)
        if p_next_view == -1: p_next_view = text.find('<script', p_op)
        p_close_view = text.rfind('</div>', p_op, p_next_view)

        # 2. Encapsula conteúdo operacional em subview-op-operacional se necessário
        if 'id="subview-op-operacional"' not in text[p_op:p_next_view]:
            p_bar = text.find('id="barra-subabas-op"', p_op, p_next_view)
            if p_bar != -1:
                pos = p_bar + 4
                depth = 1
                while depth > 0 and pos < p_next_view:
                    no = text.find('<div', pos, p_next_view)
                    nc = text.find('</div>', pos, p_next_view)
                    if nc == -1: break
                    if no != -1 and no < nc:
                        depth += 1
                        pos = no + 4
                    else:
                        depth -= 1
                        pos = nc + 6
                p_bar_end = pos
                conteudo_operacional = text[p_bar_end:p_close_view]
                novo_operacional = '\n            <!-- SUB-ABA 1: FILA OPERACIONAL & WORK PACKAGES -->\n            <div id="subview-op-operacional" class="subview-op">' + conteudo_operacional + '\n            </div> <!-- FIM SUBVIEW OP OPERACIONAL -->\n'
                text = text[:p_bar_end] + novo_operacional + text[p_close_view:]
                print("   Visão operacional encapsulada com sucesso!")

        # Recalcula limites para inserir o relatório executivo
        p_op = text.find('id="view-portfolio_openproject"')
        p_next_view = text.find('id="view-', p_op + 30)
        if p_next_view == -1: p_next_view = text.find('<script', p_op)
        p_close_view = text.rfind('</div>', p_op, p_next_view)

        # 3. Inserir ou atualizar subview-op-relatorio
        if 'id="subview-op-relatorio"' not in text[p_op:p_next_view]:
            text = text[:p_close_view] + "\n" + relatorio_op_html + "\n        " + text[p_close_view:]
            print("   Relatório Executivo OpenProject injetado com sucesso!")

        # 4. Injetar função JS de alternância do OpenProject
        if 'window.alternarSubAbaOpenProject = function' not in text:
            op_js = """
    window.subAbaOpAtiva = 'operacional';
    window.alternarSubAbaOpenProject = function(subAba) {
        window.subAbaOpAtiva = subAba || 'operacional';
        var vOperacional = document.getElementById('subview-op-operacional');
        var vRelatorio = document.getElementById('subview-op-relatorio');
        var btnOperacional = document.getElementById('btn-op-subaba-operacional');
        var btnRelatorio = document.getElementById('btn-op-subaba-relatorio');

        if (subAba === 'relatorio') {
            if (vOperacional) vOperacional.style.display = 'none';
            if (vRelatorio) {
                vRelatorio.style.display = 'block';
                vRelatorio.style.opacity = '1';
            }
            if (btnOperacional) {
                btnOperacional.className = 'btn btn-secondary';
                btnOperacional.style.background = 'rgba(255,255,255,0.06)';
                btnOperacional.style.color = '#cbd5e1';
                btnOperacional.style.fontWeight = '600';
                btnOperacional.style.border = '1px solid rgba(255,255,255,0.12)';
                btnOperacional.style.boxShadow = 'none';
            }
            if (btnRelatorio) {
                btnRelatorio.className = 'btn btn-primary active';
                btnRelatorio.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                btnRelatorio.style.color = '#ffffff';
                btnRelatorio.style.fontWeight = '700';
                btnRelatorio.style.border = '1px solid rgba(56,189,248,0.5)';
                btnRelatorio.style.boxShadow = '0 2px 8px rgba(2,132,199,0.3)';
            }
        } else {
            if (vRelatorio) vRelatorio.style.display = 'none';
            if (vOperacional) {
                vOperacional.style.display = 'block';
                vOperacional.style.opacity = '1';
            }
            if (btnOperacional) {
                btnOperacional.className = 'btn btn-primary active';
                btnOperacional.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                btnOperacional.style.color = '#ffffff';
                btnOperacional.style.fontWeight = '700';
                btnOperacional.style.border = '1px solid rgba(56,189,248,0.5)';
                btnOperacional.style.boxShadow = '0 2px 8px rgba(2,132,199,0.3)';
            }
            if (btnRelatorio) {
                btnRelatorio.className = 'btn btn-secondary';
                btnRelatorio.style.background = 'rgba(255,255,255,0.06)';
                btnRelatorio.style.color = '#cbd5e1';
                btnRelatorio.style.fontWeight = '600';
                btnRelatorio.style.border = '1px solid rgba(255,255,255,0.12)';
                btnRelatorio.style.boxShadow = 'none';
            }
        }
    };
"""
            p_last = text.rfind('</script>')
            if p_last != -1:
                text = text[:p_last] + op_js + "\n" + text[p_last:]
                print("   Função JS alternarSubAbaOpenProject injetada com sucesso!")

        with open(alvo, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"💾 {alvo} salvo com sucesso!")

    print("\n🎉 Concluído com sucesso! Atalhos removidos e Relatório Executivo OpenProject 100% ativo.")

if __name__ == '__main__':
    aplicar_patch_op()
