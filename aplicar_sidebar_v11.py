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

pos1 = text.find('id="sidebar"')
if pos1 == -1:
    print("❌ Tag #sidebar não encontrada no arquivo!")
    exit(1)

start_div = text.rfind('<div', 0, pos1)
pos2 = text.find('<!-- MAIN -->')
if pos2 == -1:
    pos2 = text.find('id="main"')
    end_div = text.rfind('<div', 0, pos2)
else:
    end_div = pos2

new_sidebar = """<div id="sidebar">
        <!-- 1. IDENTIDADE INSTITUCIONAL MODERNIZADA -->
        <div class="sidebar-brand" style="display: flex; align-items: center; justify-content: space-between; padding: 18px 14px 14px 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.07);">
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

        <!-- 2. BUSCA GLOBAL 360° NA SIDEBAR -->
        <div style="padding: 12px 12px 8px 12px;">
            <div style="position: relative; display: flex; align-items: center;">
                <input type="text" id="sidebar-search-input" placeholder="🔍 Busca 360° (Ctrl+K)..." onkeydown="if(event.key==='Enter'){if(window.dispararBuscaGlobal)window.dispararBuscaGlobal(this.value);}" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12); background: rgba(255, 255, 255, 0.05); color: #fff; font-size: 11.5px; outline: none; box-sizing: border-box; transition: all 0.2s ease;">
            </div>
        </div>

        <!-- 3. NAVEGAÇÃO DOS 4 EIXOS ESTRATÉGICOS (DIRETA & LIMPA) -->
        <div class="sidebar-menu" style="flex: 1; overflow-y: auto; padding: 6px 10px; display: flex; flex-direction: column; gap: 5px;">
            <div class="nav-item active" data-tab="dashboards" onclick="switchTab('dashboards')" style="padding: 10px 12px; border-radius: 8px; font-size: 12.5px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">📺</span>
                    <span style="font-weight: 700;">1. Gestão à Vista 360°</span>
                </div>
                <span class="nav-badge" style="background: rgba(255,255,255,0.2); color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">360°</span>
            </div>

            <div class="nav-item" data-tab="mesa_trabalho" onclick="switchTab('mesa_trabalho')" style="padding: 10px 12px; border-radius: 8px; font-size: 12.5px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">💼</span>
                    <span style="font-weight: 700;">2. Mesa de Trabalho &amp; IA</span>
                </div>
                <span class="nav-badge" style="background: #00a859; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">Hub</span>
            </div>

            <div class="nav-item" data-tab="daily_warroom" onclick="switchTab('daily_warroom')" style="padding: 10px 12px; border-radius: 8px; font-size: 12.5px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">🤝</span>
                    <span style="font-weight: 700;">3. Sala de Reuniões &amp; Atas</span>
                </div>
                <span class="nav-badge" style="background: #0284c7; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">15m</span>
            </div>

            <div class="nav-item" data-tab="configuracoes" onclick="switchTab('configuracoes')" style="padding: 10px 12px; border-radius: 8px; font-size: 12.5px;">
                <div class="nav-item-left" style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 16px;">⚙️</span>
                    <span style="font-weight: 700;">4. Central de Configurações</span>
                </div>
                <span class="nav-badge" style="background: #475569; color: #fff; font-size: 10px; padding: 2px 7px; border-radius: 10px;">Admin</span>
            </div>
        </div>

        <!-- 4. SESSÃO DO USUÁRIO & TELEMETRIA (100% DARK MODE EXCLUSIVO) -->
        <div id="sidebar-user-footer" style="padding: 14px 12px; border-top: 1px solid rgba(255, 255, 255, 0.08); background: rgba(11, 15, 25, 0.95); display: flex; flex-direction: column; gap: 10px;">
            <!-- Usuário Autenticado -->
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #0544cf 0%, #00a859 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 12px; color: #fff; flex-shrink: 0; box-shadow: 0 2px 8px rgba(5,68,207,0.35);">
                    LS
                </div>
                <div style="flex: 1; overflow: hidden; line-height: 1.25;">
                    <div style="font-size: 12.5px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Luiz Seixeiro</div>
                    <div style="font-size: 10.5px; color: #94a3b8; display: flex; align-items: center; gap: 4px;">
                        <span style="color: #facc15;">👑</span> Super-Admin
                    </div>
                </div>
            </div>

            <!-- Seletor de Diretoria (Compacto) -->
            <div style="display: flex; align-items: center; gap: 6px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 5px 8px;">
                <span style="font-size: 11px;">🏛️</span>
                <select id="select-diretoria-spaguas" onchange="window.filtrarPorDiretoriaSpAguas(this.value)" style="border: none; background: transparent; font-size: 11px; font-weight: 600; color: #e2e8f0; width: 100%; outline: none; cursor: pointer;">
                    <option value="todas" style="background: #0f172a; color: #fff;">Toda a SP-Águas (Consolidado)</option>
                    <option value="spaguas-sh" style="background: #0f172a; color: #fff;">[SH] Segurança Hídrica</option>
                    <option value="spaguas-sd" style="background: #0f172a; color: #fff;">[SD] Descentralizadas</option>
                    <option value="spaguas-sr" style="background: #0f172a; color: #fff;">[SR] Regulação</option>
                    <option value="spaguas-sf" style="background: #0f172a; color: #fff;">[SF] Fiscalização</option>
                    <option value="spaguas-sa" style="background: #0f172a; color: #fff;">[SA] Administrativa</option>
                    <option value="spaguas-sa-gti" style="background: #0f172a; color: #fff;">[SA-GTI] TIC Governança</option>
                </select>
            </div>

            <!-- Seletor Oculto para compatibilidade com RBAC -->
            <select id="select-perfil-ativo" onchange="window.trocarPerfilAtivo(this.value)" style="display: none;">
                <option value="Super-Admin">Super-Admin</option>
                <option value="Gestor">Gestor</option>
                <option value="Analista">Analista</option>
                <option value="Demandante">Demandante</option>
            </select>

            <!-- Telemetria INFRA em Linha Única -->
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 2px 0 2px;">
                <div id="widget-infra-sidebar" style="display: inline-flex; align-items: center; gap: 5px; font-size: 10px; color: #94a3b8; font-family: monospace;">
                    <span style="font-weight: 800; color: #4ade80; letter-spacing: 0.5px;">INFRA</span>
                    <span id="led-mariadb" title="MariaDB (:3306)">🟢</span>
                    <span id="led-ollama" title="Ollama (:11434)">🟢</span>
                    <span id="led-glpi" title="GLPI">🟢</span>
                    <span id="led-openproject" title="OpenProject">🟢</span>
                    <span id="led-newapi" title="New API (:3001)">🟢</span>
                </div>
                <span style="font-size: 9.5px; color: #64748b; font-weight: 600;">Sistemas OK</span>
            </div>
        </div>
    </div>"""

patched = text[:start_div] + new_sidebar + '\n\n    ' + text[end_div:]

o = patched.count('<div')
c = patched.count('</div')
if o != c:
    print(f"❌ Erro de integridade de tags: open={o}, close={c}")
    exit(1)

with open(target, 'w', encoding='utf-8') as f:
    f.write(patched)

print("✅ Sidebar modernizada e integrada com sucesso!")
print(f"📁 Arquivo atualizado: {target} (Tags balanceadas: {o})")
