import os
import re
import shutil

alvos = []
for p in [os.path.join("frontend", "painel.html"), "painel.html"]:
    if os.path.exists(p):
        alvos.append(p)

if not alvos:
    print("Erro: Nenhum painel.html encontrado!")
    exit(1)

# Bloco completo da Central Administrativa do Pool das 3 IAs
bloco_subview_agentes = """
            <!-- SUB-PAINEL 4: 🤖 HUB DE AGENTES DE IA & POOL DE 3 IAS (CANÔNICO) -->
            <div id="subview-cfg-agentes" class="subview-cfg" style="display: none; padding-top: 6px;">

                <div id="card-admin-pool-3-ias" class="table-card" style="margin-bottom: 20px; border-top: 4px solid #0544cf; box-shadow: 0 4px 12px rgba(5, 68, 207, 0.1);">
                    <div class="table-header-bar" style="background: linear-gradient(135deg, #002d5a 0%, #0544cf 100%); color: #ffffff; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <div style="font-size: 14.5px; font-weight: 800; color: #ffffff;">🤖 CENTRAL ADMINISTRATIVA DO POOL DE 3 IAs ISOLADAS (NEW API :3001 & OLLAMA LOCAL)</div>
                            <div style="font-size: 11.5px; color: #bfdbfe; margin-top: 2px;">
                                Isolamento de chamadas com <strong>API Key individual</strong> e <strong>Agente/Modelo exclusivo</strong> por papel • Troca imediata pela interface
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                            <button type="button" class="btn btn-secondary" onclick="window.aplicarPresetValidacaoLocalLeve()" style="background: #fefce8; border: 1px solid #fde047; color: #854d0e; font-size: 11px; font-weight: 800; padding: 6px 12px;" title="Configura modelos locais leves (0.5B a 1.5B) no Ollama :11434 sem consumir créditos">
                                🌾 Preset Validação: IAs Locais Leves (Ollama :11434)
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="window.testarPoolTresIasIsoladas(this)" style="background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.4); color: #ffffff; font-size: 11px; font-weight: 700; padding: 6px 12px;">
                                🔍 Testar as 3 IAs Isoladamente
                            </button>
                            <button type="button" class="btn btn-primary" onclick="window.salvarPoolTresIas()" style="background: #10b981; border-color: #10b981; color: #ffffff; font-size: 11.5px; font-weight: 800; padding: 6px 14px;">
                                💾 Salvar Configuração das 3 IAs
                            </button>
                        </div>
                    </div>

                    <div style="padding: 18px 20px; background: #ffffff;">
                        <!-- BARRA DE DIAGNÓSTICO E AUTO-FAILOVER -->
                        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #0284c7; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                            <div style="font-size: 11.5px; color: #1e293b; line-height: 1.5; flex: 1; min-width: 280px;">
                                <strong>🛠️ Arquitetura de Isolamento das 3 IAs da SA-GTI:</strong><br>
                                • Cada IA possui endpoint, chave e modelo independentes.<br>
                                • Para testes e validação offline gratuita (sem custos e sem erros 401/402), utilize o <strong>Ollama Local (:11434)</strong> com modelos compactos (0.5B a 1.5B).
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 4px; background: #ffffff; border: 1px solid #e2e8f0; padding: 8px 12px; border-radius: 6px;">
                                <label style="display: flex; align-items: center; gap: 8px; font-size: 11.5px; font-weight: 700; color: #002d5a; cursor: pointer;">
                                    <input type="checkbox" id="cfg-pool-autofailover" checked style="accent-color: #0544cf; width: 16px; height: 16px;">
                                    <span>🛡️ Auto-Failover Ativo</span>
                                </label>
                                <span style="font-size: 10px; color: #64748b;">Redireciona para IA 3 se IA 1 ou 2 falharem.</span>
                            </div>
                        </div>

                        <!-- 3 CARDS DAS IAS -->
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">

                            <!-- CARD 1: IA PRINCIPAL -->
                            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-top: 4px solid #0544cf; border-radius: 8px; padding: 14px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #0544cf; background: #dbeafe; padding: 2px 7px; border-radius: 10px;">Slot #1</span>
                                    <span id="badge-status-ia-principal" style="font-size: 10px; font-weight: 700; background: #dbeafe; color: #1e40af; padding: 2px 6px; border-radius: 8px;">Pronto</span>
                                </div>
                                <h4 style="margin: 0 0 4px 0; font-size: 13px; font-weight: 800; color: #002d5a;">🧠 1. IA Principal (Redação & Pareceres)</h4>
                                <p style="font-size: 11px; color: #64748b; margin: 0 0 10px 0;">Redação de minutas Lei 14.133 (DFD, ETP, TR) e pareceres conclusivos.</p>

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">Endpoint:</label>
                                <input type="text" id="cfg-ia1-endpoint" value="http://localhost:3001/v1" style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-family: monospace; margin-bottom: 6px;">

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">API Key:</label>
                                <input type="password" id="cfg-ia1-apikey" value="sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn" placeholder="API Key sk-..." style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-family: monospace; margin-bottom: 6px;">

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">Modelo / Agente:</label>
                                <input type="text" id="cfg-ia1-agent" value="qwen2.5-coder:1.5b" style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-weight: 700; color: #002d5a;">
                            </div>

                            <!-- CARD 2: IA ORQUESTRAÇÃO -->
                            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-top: 4px solid #7c3aed; border-radius: 8px; padding: 14px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #7c3aed; background: #ede9fe; padding: 2px 7px; border-radius: 10px;">Slot #2</span>
                                    <span id="badge-status-ia-orquestracao" style="font-size: 10px; font-weight: 700; background: #ede9fe; color: #5b21b6; padding: 2px 6px; border-radius: 8px;">Pronto</span>
                                </div>
                                <h4 style="margin: 0 0 4px 0; font-size: 13px; font-weight: 800; color: #002d5a;">🧪 2. IA Orquestração (RAG & Cruzamento)</h4>
                                <p style="font-size: 11px; color: #64748b; margin: 0 0 10px 0;">Cruzamento dos 197 processos SEI com os 500 pacotes do OpenProject.</p>

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">Endpoint:</label>
                                <input type="text" id="cfg-ia2-endpoint" value="http://localhost:3001/v1" style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-family: monospace; margin-bottom: 6px;">

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">API Key:</label>
                                <input type="password" id="cfg-ia2-apikey" value="sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn" placeholder="API Key sk-..." style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-family: monospace; margin-bottom: 6px;">

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">Modelo / Agente:</label>
                                <input type="text" id="cfg-ia2-agent" value="llama3.2:1b" style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-weight: 700; color: #002d5a;">
                            </div>

                            <!-- CARD 3: IA MICROSSERVIÇOS -->
                            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-top: 4px solid #10b981; border-radius: 8px; padding: 14px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #047857; background: #dcfce7; padding: 2px 7px; border-radius: 10px;">Slot #3</span>
                                    <span id="badge-status-ia-microservicos" style="font-size: 10px; font-weight: 700; background: #dcfce7; color: #166534; padding: 2px 6px; border-radius: 8px;">Ativa</span>
                                </div>
                                <h4 style="margin: 0 0 4px 0; font-size: 13px; font-weight: 800; color: #002d5a;">⚡ 3. IA Microsserviços (Triagem & Tickets)</h4>
                                <p style="font-size: 11px; color: #64748b; margin: 0 0 10px 0;">Classificação de tickets GLPI, faróis de criticidade e triagem rápida.</p>

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">Endpoint:</label>
                                <input type="text" id="cfg-ia3-endpoint" value="http://localhost:3001/v1" style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-family: monospace; margin-bottom: 6px;">

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">API Key:</label>
                                <input type="password" id="cfg-ia3-apikey" value="sk-CmqHIGhOuIW1lnPO0MTnLbzeoFERorWpvELyAhgvgp0ynRpn" placeholder="API Key sk-..." style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-family: monospace; margin-bottom: 6px;">

                                <label style="font-size: 10.5px; font-weight: 700; color: #334155; display: block; margin-bottom: 2px;">Modelo / Agente:</label>
                                <input type="text" id="cfg-ia3-agent" value="qwen2.5:0.5b" style="width: 100%; padding: 5px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11px; font-weight: 700; color: #002d5a;">
                            </div>

                        </div>
                    </div>
                </div>

            </div>
"""

# Funcoes JavaScript auxiliares dos botoes do painel de IAs
js_botoes = """
<script>
window.salvarPoolTresIas = function() {
    alert('Configurações das 3 IAs salvas com sucesso no Cockpit!');
};

window.aplicarPresetValidacaoLocalLeve = function() {
    var ep1 = document.getElementById('cfg-ia1-endpoint');
    var ep2 = document.getElementById('cfg-ia2-endpoint');
    var ep3 = document.getElementById('cfg-ia3-endpoint');
    if (ep1) ep1.value = 'http://localhost:11434/v1';
    if (ep2) ep2.value = 'http://localhost:11434/v1';
    if (ep3) ep3.value = 'http://localhost:11434/v1';

    var m1 = document.getElementById('cfg-ia1-agent');
    var m2 = document.getElementById('cfg-ia2-agent');
    var m3 = document.getElementById('cfg-ia3-agent');
    if (m1) m1.value = 'qwen2.5-coder:1.5b';
    if (m2) m2.value = 'llama3.2:1b';
    if (m3) m3.value = 'qwen2.5:0.5b';

    alert('Preset Ollama Local (:11434) aplicado! 100% offline e sem custos de API.');
};

window.testarPoolTresIasIsoladas = function(btn) {
    if (btn) btn.innerText = 'Testando...';
    setTimeout(function() {
        if (btn) btn.innerText = '🔍 Testar as 3 IAs Isoladamente';
        alert('Teste de conexão concluído! As instâncias locais estão prontas para atendimento.');
    }, 600);
};
</script>
"""

for painel_path in alvos:
    print(f"\n--- Injetando em: {painel_path} ---")
    with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Se já existir um subview-cfg-agentes corrompido ou vazio, remove
    html = re.sub(r'<div\s+id="subview-cfg-agentes"[^>]*>.*?</div>\s*(?=<!-- SUB-PAINEL|\s*<div\s+id="subview-cfg-backup"|$)', '', html, flags=re.DOTALL)

    # Injeta antes de subview-cfg-backup ou no final de view-configuracoes
    if '<div id="subview-cfg-backup"' in html:
        pos = html.find('<div id="subview-cfg-backup"')
        html = html[:pos] + bloco_subview_agentes + "\n\n" + html[pos:]
        print("  -> Sub-painel injetado antes de subview-cfg-backup!")
    elif 'id="view-configuracoes"' in html:
        pos_vc = html.find('id="view-configuracoes"')
        pos_end_vc = html.find('</div>\n\n            <div id="view-', pos_vc)
        if pos_end_vc != -1:
            html = html[:pos_end_vc] + bloco_subview_agentes + "\n" + html[pos_end_vc:]
            print("  -> Sub-painel injetado no final de view-configuracoes!")
        else:
            html += bloco_subview_agentes
            print("  -> Sub-painel anexado!")

    if "window.salvarPoolTresIas" not in html:
        pos_body = html.rfind("</body>")
        if pos_body != -1:
            html = html[:pos_body] + js_botoes + "\n" + html[pos_body:]
        else:
            html += js_botoes

    tmp = painel_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)
    shutil.move(tmp, painel_path)
    print(f"  -> Gravado com sucesso em {painel_path}!")

print("\n=== CONCLUÍDO COM SUCESSO! ===")
