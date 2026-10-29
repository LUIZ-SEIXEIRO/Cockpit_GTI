import os
import re
import shutil

# Localiza e atualiza todos os arquivos painel.html encontrados
alvos = []
for p in [os.path.join("frontend", "painel.html"), "painel.html"]:
    if os.path.exists(p):
        alvos.append(p)

if not alvos:
    print("Erro: Nenhum painel.html localizado!")
    exit(1)

for painel_path in alvos:
    print(f"\n[Processando {painel_path}]")
    shutil.copyfile(painel_path, painel_path + ".bak")

    with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. Ajuste da altura do grid do chat para fixar a barra de digitacao na tela visivel
    html, n_chat = re.subn(
        r'id="grid-layout-chat-ia"[^>]*style="[^"]*"',
        'id="grid-layout-chat-ia" style="display: grid; grid-template-columns: 1fr; gap: 16px; height: calc(100vh - 280px); max-height: calc(100vh - 280px); min-height: 400px;"',
        html
    )
    print(f"  -> Altura do Chat IA ajustada (substituicoes: {n_chat})")

    # 2. Desbloqueio e exibição forçada do container do Pool das 3 IAs
    html, n_age = re.subn(
        r'<div\s+id="subview-cfg-agentes"[^>]*>',
        '<div id="subview-cfg-agentes" class="subview-cfg" style="display: block !important; visibility: visible !important;">',
        html
    )
    print(f"  -> Container subview-cfg-agentes desbloqueado (substituicoes: {n_age})")

    # 3. Injecao da sobrescrita limpa de alternarSubConfig antes de </body>
    js_override = """
<script>
// SOBRESCRITA OFICIAL DE ALTERNARSUBOCNFIG COM DISPLAY IMPORTANT E AUTO-SCROLL
window.alternarSubConfig = function(modo) {
    window.subConfigAtivo = modo;
    document.querySelectorAll(".subview-cfg").forEach(function(el) {
        el.style.setProperty("display", "none", "important");
    });
    document.querySelectorAll(".pill-cfg").forEach(function(btn) {
        btn.classList.remove("btn-primary");
        btn.classList.add("btn-secondary");
    });

    var target = document.getElementById("subview-cfg-" + modo);
    if (target) {
        target.style.setProperty("display", "block", "important");
        target.style.setProperty("visibility", "visible", "important");
        target.style.setProperty("opacity", "1", "important");
        target.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    var btn = document.getElementById("btn-cfg-" + modo);
    if (btn) {
        btn.classList.remove("btn-secondary");
        btn.classList.add("btn-primary");
    }

    var titulosCfg = {
        "rbac": "🛡️ 1. MATRIZ DE CONTROLE DE ACESSO POR PERFIL (RBAC)",
        "parametros": "⚖️ 2. PARÂMETROS DE GOVERNANÇA, AGING & SPRINTS",
        "conectores": "🔌 3. CONECTORES & CENTRAL DE VARREDURA MULTISSISTÊMICA",
        "agentes": "🤖 4. HUB DE AGENTES DE INTELIGÊNCIA ARTIFICIAL",
        "backup": "💾 5. BACKUP & RESTAURAÇÃO (DRP / PCN)"
    };

    var tit = document.getElementById("cfg-banner-titulo");
    if (tit) tit.innerText = titulosCfg[modo] || "CONFIGURAÇÕES SA-GTI";
};
</script>
"""
    if "SOBRESCRITA OFICIAL DE ALTERNARSUBOCNFIG" not in html:
        pos_body = html.rfind("</body>")
        if pos_body != -1:
            html = html[:pos_body] + js_override + "\n" + html[pos_body:]
        else:
            html += js_override
        print("  -> Script de controle reativo injetado com sucesso!")

    # 4. Gravacao atomica segura
    tmp_path = painel_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)
    shutil.move(tmp_path, painel_path)
    print(f"  -> {painel_path} gravado com sucesso!")

print("\nConcluido! Recarregue a pagina no navegador.")
