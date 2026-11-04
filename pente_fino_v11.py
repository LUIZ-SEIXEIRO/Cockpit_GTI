import os
import shutil
import re

print("🚀 Executando Pente Fino Definitivo: Ocultando Watchlist do topo e aplicando 4 Eixos na Sidebar...")

raiz = r"C:\Cockpit_GTI"
alvos = []
for root, dirs, files in os.walk(raiz):
    if "Snapshot" in root or "backup" in root or ".git" in root:
        continue
    for f in files:
        if f == "painel.html":
            alvos.append(os.path.join(root, f))

print(f"📁 Arquivos localizados para sincronização: {alvos}")

js_pente_fino = """
<style id="css-pente-fino-v11">
    /* Ocultar faixa roxa da watchlist no topo do Dashboard */
    #card-watchlist-dashboard, #card-watchlist-topo, .card-watchlist-topo,
    div[id*="watchlist"]:has(table) {
        display: none !important;
    }
</style>

<script id="script-ui-pente-fino-v11">
(function() {
    function aplicarPenteFinoDOM() {
        // 1. Ocultar a faixa roxa de Watchlist no topo do Dashboard
        document.querySelectorAll(".table-card, div").forEach(function(el) {
            if (el.innerText && el.innerText.includes("Watchlist Prioritária") && el.querySelector("table")) {
                el.style.setProperty("display", "none", "important");
            }
        });

        // 2. Substituir a Sidebar para as 4 Visões Mestras se ainda estiver com os itens antigos
        var menu = document.querySelector(".sidebar-menu");
        if (menu && !document.getElementById("sidebar-menu-v11-enforced")) {
            menu.id = "sidebar-menu-v11-enforced";
            menu.style.cssText = "flex: 1; overflow-y: auto;";
            menu.innerHTML = `
                <div class="menu-category" style="font-size: 10px; font-weight: 800; color: #64748b; letter-spacing: 0.8px; padding: 6px 14px 10px 14px;">VISÕES ESTRATÉGICAS (4 EIXOS)</div>
                
                <!-- EIXO 1: GESTÃO À VISTA (DASHBOARD 360°) -->
                <div class="nav-item active" data-tab="dashboards" onclick="switchTab('dashboards')" style="margin: 4px 10px; border-radius: 8px; padding: 11px 12px;">
                    <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 12.5px;">
                        <span style="font-size: 16px;">📺</span> <span>1. Gestão à Vista</span>
                    </div>
                    <span class="nav-badge" style="background: rgba(37, 99, 235, 0.35); border: 1px solid rgba(96, 165, 250, 0.4); color: #93c5fd; font-size: 10px; font-weight: 700;">360°</span>
                </div>

                <!-- EIXO 2: MESA DE TRABALHO ÚNICA (HUB OPERACIONAL) -->
                <div class="nav-item" data-tab="mesa_trabalho" onclick="switchTab('mesa_trabalho')" style="margin: 4px 10px; border-radius: 8px; padding: 11px 12px;">
                    <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 12.5px;">
                        <span style="font-size: 16px;">💼</span> <span>2. Mesa de Trabalho</span>
                    </div>
                    <span class="nav-badge" style="background: rgba(16, 185, 129, 0.25); border: 1px solid rgba(52, 211, 153, 0.4); color: #a7f3d0; font-size: 10px; font-weight: 700;">Operação</span>
                </div>

                <!-- EIXO 3: SALA DE REUNIÕES & DIRETORIA -->
                <div class="nav-item" data-tab="daily_warroom" onclick="switchTab('daily_warroom')" style="margin: 4px 10px; border-radius: 8px; padding: 11px 12px;">
                    <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 12.5px;">
                        <span style="font-size: 16px;">🤝</span> <span>3. Sala de Reuniões</span>
                    </div>
                    <span class="nav-badge" style="background: rgba(124, 58, 237, 0.25); border: 1px solid rgba(167, 139, 250, 0.4); color: #ddd6fe; font-size: 10px; font-weight: 700;">15m • Ata</span>
                </div>

                <!-- EIXO 4: CONFIGURAÇÕES & CONECTORES -->
                <div class="nav-item" data-tab="configuracoes" onclick="switchTab('configuracoes')" style="margin: 4px 10px; border-radius: 8px; padding: 11px 12px;">
                    <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 12.5px;">
                        <span style="font-size: 16px;">⚙️</span> <span>4. Configurações</span>
                    </div>
                    <span class="nav-badge" style="background: rgba(245, 158, 11, 0.25); border: 1px solid rgba(251, 191, 36, 0.4); color: #fde68a; font-size: 10px; font-weight: 700;">Sistema</span>
                </div>
            `;
        }
    }

    aplicarPenteFinoDOM();
    document.addEventListener("DOMContentLoaded", aplicarPenteFinoDOM);
    window.addEventListener("load", aplicarPenteFinoDOM);
    setInterval(aplicarPenteFinoDOM, 600);
})();
</script>
"""

for target in alvos:
    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    html = re.sub(r'<style id="css-pente-fino-v11">[\s\S]*?</style>', '', html)
    html = re.sub(r'<script id="script-ui-pente-fino-v11">[\s\S]*?</script>', '', html)

    if "</body>" in html:
        idx = html.rfind("</body>")
        html = html[:idx] + "\n" + js_pente_fino + "\n" + html[idx:]
    else:
        html = html + "\n" + js_pente_fino

    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)
    shutil.move(tmp, target)
    print(f"✅ Pente fino aplicado em: {target}")

print("\n🚀 Concluído! Pressione Ctrl + F5 no navegador para validar a limpeza da Watchlist e os 4 Eixos na Sidebar.")
