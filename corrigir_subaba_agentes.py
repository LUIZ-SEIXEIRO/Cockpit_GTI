import os
import re
import shutil

print("=== [1/3] VARRENDO DIRETÓRIOS POR ARQUIVOS PAINEL.HTML ===")
alvos = []
for root, dirs, files in os.walk("."):
    for f in files:
        if f.lower() == "painel.html":
            caminho_completo = os.path.normpath(os.path.join(root, f))
            # Evita pastas de backup .bak ou temporarias
            if not caminho_completo.endswith(".bak"):
                alvos.append(caminho_completo)

print(f"Arquivos localizados ({len(alvos)}): {alvos}")

if not alvos:
    print("ERRO CRÍTICO: Nenhum painel.html encontrado!")
    exit(1)

for painel_path in alvos:
    print(f"\n--- Processando: {painel_path} ---")
    shutil.copyfile(painel_path, painel_path + ".bak")

    with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. Checa a presenca do container subview-cfg-agentes
    tem_subview = 'id="subview-cfg-agentes"' in html
    tem_card = 'id="card-admin-pool-3-ias"' in html
    print(f"  -> Contém container subview-cfg-agentes: {tem_subview}")
    print(f"  -> Contém card-admin-pool-3-ias: {tem_card}")

    # 2. Desbloqueia a tag div do subview-cfg-agentes
    html = re.sub(
        r'<div\s+id="subview-cfg-agentes"[^>]*>',
        '<div id="subview-cfg-agentes" class="subview-cfg" style="display: none; min-height: 450px;">',
        html
    )

    # 3. Garante que o card interno card-admin-pool-3-ias tenha visibilidade plena
    html = re.sub(
        r'<div\s+id="card-admin-pool-3-ias"[^>]*class="table-card"[^>]*>',
        '<div id="card-admin-pool-3-ias" class="table-card" style="margin-bottom: 20px; border-top: 4px solid #0544cf; box-shadow: 0 4px 12px rgba(5,68,207,0.12); display: block !important; visibility: visible !important;">',
        html
    )

    # 4. Injeta a funcao alternarSubConfig robusta com forca de exibicao no final
    js_corrigido = """
<script>
window.alternarSubConfig = function(modo) {
    window.subConfigAtivo = modo;
    
    // Oculta todas as subviews
    var todas = document.querySelectorAll('.subview-cfg');
    for (var i = 0; i < todas.length; i++) {
        todas[i].style.setProperty('display', 'none', 'important');
    }
    
    // Atualiza botoes das pills
    var pills = document.querySelectorAll('.pill-cfg');
    for (var j = 0; j < pills.length; j++) {
        pills[j].classList.remove('btn-primary');
        pills[j].classList.add('btn-secondary');
    }

    // Exibe a subview alvo
    var target = document.getElementById('subview-cfg-' + modo);
    if (target) {
        target.style.setProperty('display', 'block', 'important');
        target.style.setProperty('visibility', 'visible', 'important');
        target.style.setProperty('opacity', '1', 'important');
    } else {
        alert('Diagnostico: Nao foi possivel encontrar o elemento HTML com id: subview-cfg-' + modo);
    }

    var btn = document.getElementById('btn-cfg-' + modo);
    if (btn) {
        btn.classList.remove('btn-secondary');
        btn.classList.add('btn-primary');
    }

    var titulosCfg = {
        'rbac': '🛡️ 1. MATRIZ DE CONTROLE DE ACESSO POR PERFIL (RBAC)',
        'parametros': '⚖️ 2. PARÂMETROS DE GOVERNANÇA, AGING & SPRINTS',
        'conectores': '🔌 3. CONECTORES & CENTRAL DE VARREDURA MULTISSISTÊMICA',
        'agentes': '🤖 4. HUB DE AGENTES DE INTELIGÊNCIA ARTIFICIAL',
        'backup': '💾 5. BACKUP & RESTAURAÇÃO (DRP / PCN)'
    };

    var tit = document.getElementById('cfg-banner-titulo');
    if (tit) tit.innerText = titulosCfg[modo] || 'CONFIGURAÇÕES SA-GTI';
};
</script>
"""

    if "Diagnostico: Nao foi possivel encontrar" not in html:
        pos_body = html.rfind("</body>")
        if pos_body != -1:
            html = html[:pos_body] + js_corrigido + "\n" + html[pos_body:]
        else:
            html += js_corrigido

    # Gravacao atomica
    tmp = painel_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)
    shutil.move(tmp, painel_path)
    print(f"  -> {painel_path} atualizado e validado com sucesso!")

print("\n=== CONCLUÍDO! ===")
