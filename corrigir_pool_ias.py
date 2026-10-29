import os
import re
import shutil

print("[1/3] Criando backup de seguranca do painel.html...")
painel_path = os.path.join("frontend", "painel.html")
if not os.path.exists(painel_path):
    painel_path = "painel.html"

shutil.copyfile(painel_path, painel_path + ".bak")

with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

print("[2/3] Corrigindo exibicao da sub-aba 4 e conectores das 3 IAs...")

# 1. Garante que subview-cfg-agentes tenha style display correto e visibilidade garantida
# Corrige a funcao alternarSubConfig no JavaScript
old_alternar = "window.alternarSubConfig = function(modo) {"
new_alternar = """window.alternarSubConfig = function(modo) {
        window.subConfigAtivo = modo;
        document.querySelectorAll('.subview-cfg').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.pill-cfg').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
        });

        const target = document.getElementById('subview-cfg-' + modo);
        if (target) {
            target.style.display = 'block';
            target.style.visibility = 'visible';
            target.style.opacity = '1';
        }

        const btn = document.getElementById('btn-cfg-' + modo);
        if (btn) {
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-primary');
        }

        const titulosCfg = {
            'rbac': '🛡️ 1. MATRIZ DE CONTROLE DE ACESSO POR PERFIL (RBAC)',
            'parametros': '⚖️ 2. PARÂMETROS DE GOVERNANÇA, AGING & SPRINTS',
            'conectores': '🔌 3. CONECTORES & CENTRAL DE VARREDURA MULTISSISTÊMICA',
            'agentes': '🤖 4. HUB DE AGENTES DE INTELIGÊNCIA ARTIFICIAL',
            'backup': '💾 5. BACKUP & RESTAURAÇÃO (DRP / PCN)'
        };

        const tit = document.getElementById('cfg-banner-titulo');
        if (tit) tit.innerText = titulosCfg[modo] || 'CONFIGURAÇÕES SA-GTI';
    };"""

if old_alternar in html:
    pos_alt = html.find(old_alternar)
    pos_end_alt = html.find("};", pos_alt) + 2
    html = html[:pos_alt] + new_alternar + html[pos_end_alt:]
    print("  -> Funcao alternarSubConfig corrigida com forca de exibicao!")

# 2. Se subview-cfg-agentes estiver com style inline display:none rígido, ajusta
html = html.replace('id="subview-cfg-agentes" class="subview-cfg" style="display: none;"', 'id="subview-cfg-agentes" class="subview-cfg"')

# 3. Atualiza os textos do painel lateral da Esteira IA para os dados oficiais
html = html.replace("203 Chamados (179 Demandas SEI + 24 Tickets ITSM)", "13 Chamados Não Solucionados (< 1500)")
html = html.replace("179 Processos SEI", "197 Processos SEI")

# 4. Grava de forma atomica e segura
tmp_path = painel_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)
shutil.move(tmp_path, painel_path)

print("[3/3] Correcao finalizada com sucesso!")
