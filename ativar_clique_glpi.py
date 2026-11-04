# -*- coding: utf-8 -*-
import os

glpi_js = """
    window.subAbaGlpiAtiva = 'operacional';
    window.alternarSubAbaGlpi = function(subAba) {
        window.subAbaGlpiAtiva = subAba || 'operacional';
        var vOperacional = document.getElementById('subview-glpi-operacional');
        var vRelatorio = document.getElementById('subview-glpi-relatorio');
        var btnOperacional = document.getElementById('btn-glpi-subaba-operacional');
        var btnRelatorio = document.getElementById('btn-glpi-subaba-relatorio');

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

for caminho in ['frontend/painel.html', 'painel.html']:
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()

        if 'window.alternarSubAbaGlpi = function' not in conteudo:
            p = conteudo.rfind('</script>')
            if p != -1:
                conteudo = conteudo[:p] + glpi_js + '\n' + conteudo[p:]
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                print(f"✅ Função JS ativada em: {caminho}")
        else:
            print(f"ℹ️ Função já estava presente em: {caminho}")

print("\n🎉 Pronto! Ação de clique ativada com sucesso.")
