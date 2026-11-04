import os

caminhos = [
    r"C:\Cockpit_GTI\frontend\painel.html",
    r"frontend\painel.html",
    "painel.html"
]

target = None
for c in caminhos:
    if os.path.exists(c):
        target = c
        break

if not target:
    print("❌ Arquivo painel.html não encontrado!")
    exit(1)

with open(target, 'r', encoding='utf-8') as f:
    text = f.read()

new_clean_sidebar = """<div id="sidebar">
        <!-- 1. IDENTIDADE INSTITUCIONAL MODERNIZADA -->
        <div class="sidebar-brand" style="display: flex; align-items: center; justify-content: space-between; padding: 20px 16px 16px 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.07);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(56, 189, 248, 0.35); box-shadow: 0 0 16px rgba(5, 68, 207, 0.3), inset 0 1px 0 rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px); flex-shrink: 0;">
                    <img src="" data-spaguas-logo="1" alt="SP-Águas" style="height: 22px; width: auto; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));">
                </div>
                <div class="brand-text">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-size: 16px; font-weight: 900; color: #ffffff; letter-spacing: -0.3px;">SP-Águas</span>
                        <span style="font-size: 9px; font-weight: 800; background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 1px 6px; border-radius: 6px; text-transform: uppercase;">v11</span>
                    </div>
                    <p style="font-size: 10.5px; color: #94a3b8; font-weight: 600; margin: 2px 0 0 0;">SA-GTI • Governança Digital</p>
                </div>
            </div>
            <button class="btn-toggle-sidebar" id="btn-collapse-sidebar" onclick="toggleSidebar()" title="Recolher/Expandir menu lateral" style="width: 26px; height: 26px; border-radius: 6px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #94a3b8; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 11px; transition: all 0.2s ease;">◀</button>
        </div>

        <!-- 2. NAVEGAÇÃO DOS 4 EIXOS ESTRATÉGICOS (MINIMALISTA & DIRETA) -->
        <div class="sidebar-menu" style="flex: 1; overflow-y: auto; padding: 14px 10px; display: flex; flex-direction: column; gap: 6px;">
            <div class="nav-item active" data-tab="dashboards" onclick="switchTab('dashboards')" style="padding: 12px 14px; border-radius: 12px; font-size: 13px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">📺</span>
                    <span style="font-weight: 700;">1. Gestão à Vista 360°</span>
                </div>
                <span class="nav-badge" style="background: rgba(255,255,255,0.2); color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">360°</span>
            </div>

            <div class="nav-item" data-tab="mesa_trabalho" onclick="switchTab('mesa_trabalho')" style="padding: 12px 14px; border-radius: 12px; font-size: 13px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">💼</span>
                    <span style="font-weight: 700;">2. Mesa de Trabalho &amp; IA</span>
                </div>
                <span class="nav-badge" style="background: #00a859; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">Hub</span>
            </div>

            <div class="nav-item" data-tab="daily_warroom" onclick="switchTab('daily_warroom')" style="padding: 12px 14px; border-radius: 12px; font-size: 13px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">🤝</span>
                    <span style="font-weight: 700;">3. Sala de Reuniões &amp; Atas</span>
                </div>
                <span class="nav-badge" style="background: #0284c7; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">15m</span>
            </div>

            <div class="nav-item" data-tab="configuracoes" onclick="switchTab('configuracoes')" style="padding: 12px 14px; border-radius: 12px; font-size: 13px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">⚙️</span>
                    <span style="font-weight: 700;">4. Central de Configurações</span>
                </div>
                <span class="nav-badge" style="background: #475569; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">Admin</span>
            </div>
        </div>

        <!-- 3. SESSÃO DO USUÁRIO LIMPA (SEM DIRETORIA & SEM INFRA) -->
        <div id="sidebar-user-footer" style="padding: 16px 14px; border-top: 1px solid rgba(255, 255, 255, 0.08); background: rgba(11, 15, 25, 0.95);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #0544cf 0%, #00a859 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 12px; color: #fff; flex-shrink: 0; box-shadow: 0 2px 8px rgba(5,68,207,0.35);">
                    LS
                </div>
                <div style="flex: 1; overflow: hidden; line-height: 1.25;">
                    <div style="font-size: 13px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Luiz Seixeiro</div>
                    <div style="font-size: 11px; color: #94a3b8; display: flex; align-items: center; gap: 4px; margin-top: 2px;">
                        <span style="color: #facc15;">👑</span> Super-Admin
                    </div>
                </div>
            </div>

            <!-- Elementos Ocultos em Segundo Plano para Preservar Rotinas JS -->
            <div style="display: none;">
                <input type="text" id="sidebar-search-input" value="">
                <select id="select-diretoria-spaguas">
                    <option value="todas" selected>Toda a SP-Águas (Consolidado)</option>
                </select>
                <select id="select-perfil-ativo">
                    <option value="Super-Admin" selected>Super-Admin</option>
                </select>
                <div id="widget-infra-sidebar">
                    <span id="led-mariadb">🟢</span>
                    <span id="led-ollama">🟢</span>
                    <span id="led-glpi">🟢</span>
                    <span id="led-openproject">🟢</span>
                    <span id="led-newapi">🟢</span>
                </div>
            </div>
        </div>
    </div>"""

pos_side = text.find('id="sidebar"')
start_side = text.rfind('<div', 0, pos_side)

pos_main = text.find('id="main"')
start_main = text.rfind('<div', 0, pos_main)

new_text = text[:start_side] + new_clean_sidebar + '\n\n    <!-- MAIN -->\n    ' + text[start_main:]

o = new_text.count('<div')
c = new_text.count('</div')

if o != c:
    print(f"❌ Diferença de tags detectada: open={o}, close={c}")
    exit(1)

with open(target, 'w', encoding='utf-8') as f:
    f.write(new_text)

print("✅ Barra lateral limpa e minimalista atualizada com sucesso!")
print(f"📁 Arquivo atualizado: {target} (Tags balanceadas: {o})")
