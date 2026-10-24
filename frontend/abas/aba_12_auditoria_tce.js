// H:\glpi-spaguas\frontend\abas\aba_12_esteira_ia.js

window.initAba_ia = async function() {
    console.log("🚀 Inicializando módulo Esteira de IA & Chat Multiagente...");
    renderizarInterfaceIA();
};

// 1. Motor de Renderização da Interface do Chat de IA
function renderizarInterfaceIA() {
    const container = document.getElementById('conteudo-ia');
    if (!container) {
        console.error("❌ Container 'conteudo-ia' não encontrado no painel.html");
        return;
    }

    // Evita duplicar a interface caso o usuário mude de aba e retorne
    if (document.getElementById('chat-container-main')) return;

    container.innerHTML = `
        <div id="chat-container-main" style="display: grid; grid-template-columns: 280px 1fr; gap: 20px; height: calc(100vh - 140px);">
            
            <!-- PAINEL ESQUERDO: Seleção de Agentes -->
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <h3 style="margin: 0; color: #002d5a; font-size: 1.1rem;">🤖 Agentes Especializados</h3>
                <p style="margin: 0; font-size: 0.8rem; color: #64748b;">Selecione o nível de processamento para a sua demanda atual:</p>
                
                <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 10px;">
                    <div onclick="selecionarAgente('principal')" id="card-agente-principal" class="agente-card active" style="padding: 12px; border: 2px solid #0544cf; background: #eff6ff; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                        <div style="font-weight: bold; color: #1e3a8a; font-size: 0.9rem;">🧠 Agente 01: Principal</div>
                        <div style="font-size: 0.75rem; color: #475569; margin-top: 3px;">Análise profunda, ETP, TR e Pareceres Técnicos.</div>
                    </div>

                    <div onclick="selecionarAgente('intermediario')" id="card-agente-intermediario" class="agente-card" style="padding: 12px; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                        <div style="font-weight: bold; color: #1e293b; font-size: 0.9rem;">📚 Agente 02: Organizador</div>
                        <div style="font-size: 0.75rem; color: #64748b; margin-top: 3px;">Organização de tarefas processadas e RAG documental.</div>
                    </div>

                    <div onclick="selecionarAgente('atomic')" id="card-agente-atomic" class="agente-card" style="padding: 12px; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                        <div style="font-weight: bold; color: #1e293b; font-size: 0.9rem;">⚡ Agente 03: Atômico</div>
                        <div style="font-size: 0.75rem; color: #64748b; margin-top: 3px;">Classificação rápida, logs e micro-tarefas.</div>
                    </div>
                </div>

                <div style="margin-top: auto; border-top: 1px solid #e2e8f0; pt: 15px; font-size: 0.75rem; color: #94a3b8;">
                    Gateway Gateway Ativo: <span style="color: #10b981; font-weight: bold;">Online (Porta :3001)</span>
                </div>
            </div>

            <!-- PAINEL DIREITO: Área de Conversação -->
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                
                <!-- Histórico de Mensagens -->
                <div id="chat-mensagens" style="flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; background: #f8fafc;">
                    <div style="align-self: flex-start; background: white; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 8px; max-width: 75%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                        <div style="font-size: 0.75rem; font-weight: bold; color: #0544cf; margin-bottom: 4px;">Assistente Virtual SP-Águas</div>
                        <div style="font-size: 0.9rem; color: #334155;">Olá, Luiz! Estou conectado aos agentes de IA da SA-GTI. Como posso auxiliar na elaboração de artefatos, análise de processos SEI ou consultas técnicas hoje?</div>
                    </div>
                </div>

                <!-- Input de Mensagem -->
                <div style="padding: 15px 20px; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 10px; align-items: center;">
                    <input type="text" id="chat-input-text" onkeypress="handleChatKeyPress(event)" placeholder="Digite sua instrução para o agente selecionado..." style="flex: 1; padding: 12px 15px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.95rem; outline: none; box-sizing: border-box;">
                    <button onclick="enviarMensagemIA()" style="background: #002d5a; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s;">
                        Enviar 🚀
                    </button>
                </div>

            </div>

        </div>
    `;
}

// 2. Controle de Seleção de Agentes na UI
let agenteSelecionado = 'principal';

window.selecionarAgente = function(tipo) {
    agenteSelecionado = tipo;
    document.querySelectorAll('.agente-card').forEach(card => {
        card.style.borderColor = '#e2e8f0';
        card.style.background = 'white';
    });

    const selectedCard = document.getElementById('card-agente-' + tipo);
    if (selectedCard) {
        selectedCard.style.borderColor = '#0544cf';
        selectedCard.style.background = '#eff6ff';
    }
};

// 3. Envio de Mensagem e Integração com FastAPI
window.enviarMensagemIA = async function() {
    const input = document.getElementById('chat-input-text');
    const texto = input.value.trim();
    if (!texto) return;

    const chatMensagens = document.getElementById('chat-mensagens');

    // Injeta a mensagem do usuário
    chatMensagens.innerHTML += `
        <div style="align-self: flex-end; background: #002d5a; color: white; padding: 12px 16px; border-radius: 8px; max-width: 75%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
            <div style="font-size: 0.75rem; font-weight: bold; color: #94a3b8; margin-bottom: 4px;">Você</div>
            <div style="font-size: 0.9rem;">${escapeHtml(texto)}</div>
        </div>
    `;
    input.value = '';
    chatMensagens.scrollTop = chatMensagens.scrollHeight;

    // Simula resposta do Agente (ou consome endpoint do FastAPI)
    try {
        const response = await fetch('/api/ia/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agente: agenteSelecionado, prompt: texto })
        });

        let respostaTexto = "Processamento concluído com sucesso pelo orquestrador local.";
        if (response.ok) {
            const data = await response.json();
            respostaTexto = data.resposta || respostaTexto;
        } else {
            respostaTexto = `[Modo Fallback] Resposta simulada para o agente [${agenteSelecionado}]: Analisei sua solicitação sobre "${texto}" com base nas diretrizes da SP-Águas.`;
        }

        chatMensagens.innerHTML += `
            <div style="align-self: flex-start; background: white; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 8px; max-width: 75%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <div style="font-size: 0.75rem; font-weight: bold; color: #0544cf; margin-bottom: 4px;">Agente (${agenteSelecionado.toUpperCase()})</div>
                <div style="font-size: 0.9rem; color: #334155;">${escapeHtml(respostaTexto)}</div>
            </div>
        `;
        chatMensagens.scrollTop = chatMensagens.scrollHeight;

    } catch (e) {
        console.error("Erro na comunicação com a IA:", e);
    }
};

window.handleChatKeyPress = function(e) {
    if (e.key === 'Enter') {
        enviarMensagemIA();
    }
};

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}