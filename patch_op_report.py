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

clean_bar = '''<!-- SELETOR DE SUB-ABAS OFICIAL OPENPROJECT (DESIGN SYSTEM SP-ÁGUAS V11) -->
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
            </div>

            '''

new_alternar_fn = '''window.alternarSubAbaOpenProject = function(subAba) {
        window.subAbaOpAtiva = subAba || 'operacional';
        var viewOp = document.getElementById('view-portfolio_openproject');
        if (!viewOp) {
            var btn = document.getElementById('btn-op-subaba-operacional') || document.getElementById('btn-op-subaba-relatorio');
            if (btn) viewOp = btn.closest('.tab-view');
        }
        var btnOperacional = document.getElementById('btn-op-subaba-operacional');
        var btnRelatorio = document.getElementById('btn-op-subaba-relatorio');
        var vRelatorio = document.getElementById('subview-op-relatorio');
        var vOperacional = document.getElementById('subview-op-operacional');

        if (subAba === 'relatorio') {
            if (vOperacional) {
                vOperacional.style.setProperty('display', 'none', 'important');
            }

            if (viewOp) {
                viewOp.querySelectorAll('.kpi-row').forEach(function(el) {
                    if (!el.closest('#subview-op-relatorio')) {
                        el.style.setProperty('display', 'none', 'important');
                    }
                });

                viewOp.querySelectorAll('.table-card').forEach(function(el) {
                    if (!el.closest('#subview-op-relatorio')) {
                        el.style.setProperty('display', 'none', 'important');
                    }
                });

                Array.prototype.slice.call(viewOp.children).forEach(function(child) {
                    if (child.id === 'subview-op-relatorio') return;
                    if (child.classList && child.classList.contains('page-banner')) return;
                    if (child.id === 'barra-subabas-op' || (child.querySelector && (child.querySelector('#btn-op-subaba-relatorio') || child.querySelector('#btn-op-subaba-operacional')))) return;
                    child.style.setProperty('display', 'none', 'important');
                });
            }

            if (vRelatorio) {
                vRelatorio.style.setProperty('display', 'block', 'important');
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

            var scroller = document.querySelector('.content-scroll') || document.querySelector('.main-content') || window;
            if (scroller.scrollTo) {
                try { scroller.scrollTo({ top: 0, behavior: 'smooth' }); } catch(e) {}
            }
        } else {
            if (vRelatorio) {
                vRelatorio.style.setProperty('display', 'none', 'important');
            }

            if (vOperacional) {
                vOperacional.style.removeProperty('display');
                vOperacional.style.display = 'block';
            }

            if (viewOp) {
                viewOp.querySelectorAll('.kpi-row').forEach(function(el) {
                    if (!el.closest('#subview-op-relatorio')) {
                        el.style.removeProperty('display');
                        el.style.display = '';
                    }
                });

                viewOp.querySelectorAll('.table-card').forEach(function(el) {
                    if (!el.closest('#subview-op-relatorio')) {
                        el.style.removeProperty('display');
                        el.style.display = '';
                    }
                });

                Array.prototype.slice.call(viewOp.children).forEach(function(child) {
                    if (child.id === 'subview-op-relatorio') return;
                    child.style.removeProperty('display');
                });
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

            if (typeof window.filtrarModoRapidoOP === 'function') {
                try { window.filtrarModoRapidoOP('todos'); } catch(e) {}
            } else if (typeof window.filtrarPortfolioOpenProject === 'function') {
                try { window.filtrarPortfolioOpenProject(); } catch(e) {}
            }
        }
    };'''

for filepath in targets:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    orig_len = len(text)

    # 1. Limpa barra duplicada se existir
    old_dup_start = text.find('<!-- SELETOR DE SUB-ABAS OFICIAL OPENPROJECT (DESIGN SYSTEM SP-ÁGUAS V11) -->')
    idx_op = text.find('<!-- SUB-ABA 1: FILA OPERACIONAL & WORK PACKAGES')
    if old_dup_start != -1 and idx_op != -1 and old_dup_start < idx_op:
        text = text[:old_dup_start] + clean_bar + text[idx_op:]

    # 2. Limpa declaracao legada redundante
    idx_script = text.find('id="script-relatorio-openproject-v11"')
    if idx_script != -1:
        idx1 = text.rfind("window.subAbaOpAtiva = 'operacional';", 0, idx_script)
        if idx1 != -1:
            idx_end = text.find('</script>', idx1)
            if idx_end != -1 and idx_end < idx_script:
                text = text[:idx1] + text[idx_end:]

    # 3. Atualiza alternarSubAbaOpenProject
    idx_script = text.find('id="script-relatorio-openproject-v11"')
    if idx_script != -1:
        idx_func = text.find('window.alternarSubAbaOpenProject = function(subAba)', idx_script)
        if idx_func != -1:
            idx_func_end = text.find('window.configurarBotoesRelatorioOpenProject();', idx_func)
            if idx_func_end != -1:
                text = text[:idx_func] + new_alternar_fn + '\n\n    ' + text[idx_func_end:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"[OK] Atualizado com sucesso: {filepath} ({orig_len} -> {len(text)} bytes)")

print("\nCorrecao concluida com sucesso!")
