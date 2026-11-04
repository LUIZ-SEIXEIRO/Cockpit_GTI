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

clean_tail = '''    window.alternarSubAbaOpenProject = function(subAba) {
        window.subAbaOpAtiva = subAba || 'operacional';
        window.configurarBotoesRelatorioOpenProject();

        var btnOperacional = document.getElementById('btn-op-subaba-operacional');
        var btnRelatorio = document.getElementById('btn-op-subaba-relatorio');
        var viewOp = document.getElementById('view-portfolio_openproject');
        if (!viewOp && btnOperacional) {
            viewOp = btnOperacional.closest('.tab-view');
        }
        var vRelatorio = document.getElementById('subview-op-relatorio');
        var vOperacional = document.getElementById('subview-op-operacional');
        var barraTopo = window.obterBarraTopoOpenProject ? window.obterBarraTopoOpenProject() : null;

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
                    if (child === barraTopo || child.id === 'barra-subabas-op') return;
                    var temBotao = child.querySelector && (
                        child.querySelector('#btn-op-subaba-relatorio') ||
                        child.querySelector('#btn-op-subaba-operacional')
                    );
                    if (temBotao) return;
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
            var scroller = document.querySelector('.content-scroll') ||
                           document.querySelector('.main-content') || window;
            if (scroller && scroller.scrollTo) {
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
    };

    window.configurarBotoesRelatorioOpenProject();
    document.addEventListener('DOMContentLoaded', function() {
        window.configurarBotoesRelatorioOpenProject();
        setTimeout(window.configurarBotoesRelatorioOpenProject, 250);
        setTimeout(window.configurarBotoesRelatorioOpenProject, 800);
    });
    setInterval(window.configurarBotoesRelatorioOpenProject, 800);
})();
</script>'''

for filepath in targets:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    orig_len = len(text)
    idx_script = text.find('<script id="script-relatorio-openproject-v11">')
    if idx_script != -1:
        idx_alt = text.find('window.alternarSubAbaOpenProject = function(subAba)', idx_script)
        idx_close = text.find('</script>', idx_script)
        if idx_alt != -1 and idx_close != -1:
            text = text[:idx_alt] + clean_tail.lstrip() + text[idx_close + len('</script>'):]
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"[OK] Sintaxe JS corrigida em: {filepath} ({orig_len} -> {len(text)} bytes)")
