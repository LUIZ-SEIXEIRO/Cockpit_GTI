import os

painel_path = os.path.join("frontend", "painel.html")
if not os.path.exists(painel_path):
    painel_path = "painel.html"

with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# 1. Sincroniza badges da Esteira IA para refletir os números reais oficiais
html = html.replace("500 OP + 203 GLPI + 179 SEI", "500 OP + 13 GLPI + 197 SEI")
html = html.replace("Total Integrado: 882 Registros", "Total Integrado: 710 Registros")

# 2. Ativa links clicáveis e botões 📋 nos 4 processos da tabela de indenização
indenizacoes = [
    "359.00002923/2025-01",
    "359.00010545/2025-21",
    "137.00004201/2025-05",
    "137.00012207/2025-48"
]

for pid in indenizacoes:
    old_td = f"<td><strong>{pid}</strong></td>"
    new_td = f"""<td>
        <div style="display: flex; align-items: center; gap: 6px;">
            <a href="javascript:void(0)" onclick="abrirDetalhesProcesso('{pid}')" style="font-weight: 700; color: #991b1b; text-decoration: none;" title="Abrir Dossiê 360° no Cockpit">{pid}</a>
            <button type="button" class="btn btn-secondary" onclick="navigator.clipboard.writeText('{pid}'); alert('Número copiado: {pid}');" style="padding: 1px 5px; font-size: 10px; cursor: pointer;" title="Copiar número do processo">📋</button>
            <a href="https://sei.sp.gov.br" target="_blank" style="font-size: 11px; text-decoration: none;" title="Abrir portal do SEI-SP">↗️</a>
        </div>
    </td>"""
    if old_td in html:
        html = html.replace(old_td, new_td)

tmp_path = painel_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)
os.replace(tmp_path, painel_path)
print("Ajuste fino do Pilar 4 aplicado com sucesso!")
