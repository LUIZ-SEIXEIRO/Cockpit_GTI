// H:\glpi-spaguas\frontend\abas\aba_15_logs_sistema.js

window.initAba_logs = async function() {
    console.log("🚀 Inicializando módulo Logs de Sistema & Telemetria...");

    let LOGS_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/sistema/logs');
        if (response.ok) {
            const json = await response.json();
            LOGS_DADOS = json.dados;
        } else {
            console.warn("⚠️ API de Logs indisponível. Carregando logs de fallback para UI.");
            LOGS_DADOS = gerarDadosFallbackLogs(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        LOGS_DADOS = gerarDadosFallbackLogs();
    }

    renderizarLogsSistema(LOGS_DADOS);
};

// 2. Motor de Renderização do Painel de Logs
function renderizarLogsSistema(dados) {
    const container = document.getElementById('conteudo-logs');
    if (!container) {
        console.error("❌ Container 'conteudo-logs' não encontrado no painel.html");
        return;
    }

    let html = `
        <div style="display: flex; flex-direction: column; gap: 20px;">
            
            <!-- Bloco Superior: Métricas de Recursos dos Contêineres -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
    `;

    dados.recursos.forEach(rec => {
        html += `
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: bold;">${rec.container}</div>
                <div style="font-size: 1.4rem; font-weight: bold; color: #0f172a; margin-top: 5px;">${rec.uso_cpu} <span style="font-size: 0.8rem; color: #10b981;">CPU</span></div>
                <div style="font-size: 0.85rem; color: #475569; margin-top: 3px;">RAM: <strong>${rec.uso_ram}</strong></div>
            </div>
        `;
    });

    html += `
            </div>

            <!-- Bloco Inferior: Console de Logs em Tempo Real -->
            <div style="background: #0f172a; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); color: #e2e8f0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #1e293b; padding-bottom: 10px;">
                    <h3 style="margin: 0; color: #f8fafc; font-size: 1rem; font-family: monospace;">🖥️ Console de Auditoria & System Logs</h3>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="alert('Atualizando fluxo de logs...')" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 0.75rem;">🔄 Atualizar</button>
                        <button onclick="alert('Logs limpos da visualização.')" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 0.75rem;">🧹 Limpar</button>
                    </div>
                </div>
                <div style="font-family: monospace; font-size: 0.85rem; line-height: 1.5; max-height: 350px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px;">
    `;

    dados.logs_recentes.forEach(log => {
        let corLog = '#94a3b8'; // Padrão
        if (log.tipo === 'SUCCESS') corLog = '#10b981';
        if (log.tipo === 'WARNING') corLog = '#f59e0b';
        if (log.tipo === 'ERROR') corLog = '#ef4444';

        html += `
            <div>
                <span style="color: #64748b;">[${log.timestamp}]</span> 
                <span style="color: ${corLog}; font-weight: bold;">[${log.tipo}]</span> 
                <span style="color: #f1f5f9;">${log.mensagem}</span>
            </div>
        `;
    });

    html += `
                </div>
            </div>

        </div>
    `;

    container.innerHTML = html;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackLogs() {
    return {
        recursos: [
            { container: "spaguas_fastapi", uso_cpu: "1.2%", uso_ram: "84 MB" },
            { container: "spaguas_mariadb", uso_cpu: "0.8%", uso_ram: "245 MB" },
            { container: "spaguas_glpi", uso_cpu: "0.4%", uso_ram: "180 MB" },
            { container: "spaguas_openproject", uso_cpu: "2.1%", uso_ram: "512 MB" }
        ],
        logs_recentes: [
            { timestamp: "2026-10-22 15:40:12", tipo: "SUCCESS", mensagem: "Conexão com pool MariaDB estabelecida com sucesso." },
            { timestamp: "2026-10-22 15:39:50", tipo: "SUCCESS", mensagem: "FastAPI endpoint /api/glpi/chamados consultado com sucesso." },
            { timestamp: "2026-10-22 15:35:00", tipo: "WARNING", mensagem: "Latência superior a 500ms detectada na API externa do SIGRH." },
            { timestamp: "2026-10-22 15:30:05", tipo: "SUCCESS", mensagem: "Container spaguas_fastapi reiniciado via docker-compose." },
            { timestamp: "2026-10-22 15:20:10", tipo: "SUCCESS", mensagem: "Início da varredura de processos no acervo probatório SEI." }
        ]
    };
}