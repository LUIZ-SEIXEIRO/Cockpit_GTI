import os
import shutil

print("[1/3] Localizando arquivo mestre do frontend...")
painel_path = os.path.join("frontend", "painel.html")
if not os.path.exists(painel_path):
    painel_path = "painel.html"

with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

print("[2/3] Aplicando correcao visual no Chat e na sub-aba do Pool de IAs...")

# 1. Ajuste da altura do grid do chat para fixar a barra de digitacao na tela visivel
old_grid = 'style="display: grid; grid-template-columns: 1fr; gap: 16px; height: calc(100vh - 195px); min-height: 580px;"'
new_grid = 'style="display: grid; grid-template-columns: 1fr; gap: 16px; height: calc(100vh - 290px); max-height: calc(100vh - 290px); min-height: 420px;"'

if old_grid in html:
    html = html.replace(old_grid, new_grid)
    print("  -> Altura do Chat IA ajustada: campo de digitacao agora fica visivel no rodape!")

# 2. Substituicao exata e segura da funcao alternarSubConfig
old_fn = """window.alternarSubConfig = function(modo) {
        window.subConfigAtivo = modo;
        document.querySelectorAll('.subview-cfg').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.pill-cfg').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
        });

        const target = document.getElementById('subview-cfg-' + modo);
        if (target) target.style.display = 'block';

        const btn = document.getElementById('btn-cfg-' + modo);
        if (btn) {
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-primary');
        }

        const titulosCfg = {
            'rbac': '🛡️ 1. MATRIZ DE CONTROLE DE ACESSO POR PERFIL (RBAC)',
            'parametros': '⚖️ 2. PARÂMETROS DE GOVERNANÇA, AGING & SPRINTS',
            'conectores': '🔌 3. CONECTORES & CENTRAL DE VARREDURA MULTISSISTÊMICA',
            'agentes': '🤖 4. HUB DE AGENTES DE INTELIGÊNCIA ARTIFICIAL'
        };

        const tit = document.getElementById('cfg-banner-titulo');
        if (tit) tit.innerText = titulosCfg[modo] || 'CONFIGURAÇÕES SA-GTI';
    };"""

new_fn = """window.alternarSubConfig = function(modo) {
        window.subConfigAtivo = modo;
        document.querySelectorAll('.subview-cfg').forEach(function(el) {
            el.style.setProperty('display', 'none', 'important');
        });
        document.querySelectorAll('.pill-cfg').forEach(function(btn) {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
        });

        var target = document.getElementById('subview-cfg-' + modo);
        if (target) {
            target.style.setProperty('display', 'block', 'important');
            target.style.visibility = 'visible';
            target.style.opacity = '1';
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
    };"""

if old_fn in html:
    html = html.replace(old_fn, new_fn)
    print("  -> Funcao alternarSubConfig atualizada com diretiva prioritaria display: block !important!")

# 3. Remove o display: none rigido inicial do container
html = html.replace('<div id="subview-cfg-agentes" class="subview-cfg" style="display: none;">', '<div id="subview-cfg-agentes" class="subview-cfg">')

# 4. Gravacao atomica segura
tmp_path = painel_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)
shutil.move(tmp_path, painel_path)

print("[3/3] Correcao aplicada com sucesso!")
