// H:\glpi-spaguas\frontend\abas\aba_04_gestao_glpi.js

window.initAba_glpi = async function() {
    console.log("🚀 Inicializando módulo Gestão GLPI 10 (Helpdesk ITSM)...");

    let CHAMADOS = [];

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/glpi/chamados');
        if (response.ok) {
            const json = await response.json();
            CHAMADOS = json.dados || [];
        } else {
            console.warn("⚠️ API do GLPI indisponível. Carregando fila de fallback para UI.");
            CHAMADOS = gerarDadosFallbackGLPI(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        CHAMADOS = gerarDadosFallbackGLPI();
    }

    renderizarFilaGLPI(CHAMADOS);
};

// 2. Motor de Renderização da Fila de Chamados (Tabela Dinâmica)
function renderizarFilaGLPI(chamados) {
    const container = document.getElementById('conteudo-glpi');
    if (!container) {
        console.error("❌ Container 'conteudo-glpi' não encontrado no painel.html");
        return;
    }

    if (chamados.length === 0) {
        container.innerHTML = '<p>Nenhum chamado aberto na fila.</p>';
        return;
    }

    // Estrutura de tabela moderna e responsiva
    let html = `
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                    <tr>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.85rem; text-transform: uppercase;">ID</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.85rem; text-transform: uppercase;">Título</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.85rem; text-transform: uppercase;">Requerente</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.85rem; text-transform: uppercase;">Prioridade</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.85rem; text-transform: uppercase;">Status</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.85rem; text-transform: uppercase;">SLA (TTO/TTR)</th>
                    </tr>
                </thead>
                <tbody>
    `;

    chamados.forEach(chamado => {
        // Lógica de cores para Prioridade
        let corPrioridade = '#16a34a'; // Baixa (Verde)
        if (chamado.prioridade === 'Média') corPrioridade = '#f59e0b'; // Amarelo
        if (chamado.prioridade === 'Alta') corPrioridade = '#ea580c'; // Laranja
        if (chamado.prioridade === 'Crítica') corPrioridade = '#ef4444'; // Vermelho

        // Lógica de cores para Status
        let corStatusBg = '#e2e8f0'; let corStatusTxt = '#475569'; // Novo/Padrão
        if (chamado.status === 'Em Andamento') { corStatusBg = '#dbeafe'; corStatusTxt = '#1d4ed8'; }
        if (chamado.status === 'Solucionado') { corStatusBg = '#dcfce7'; corStatusTxt = '#15803d'; }
        if (chamado.status === 'Pendente') { corStatusBg = '#fef3c7'; corStatusTxt = '#b45309'; }

        html += `
            <tr style="border-bottom: 1px solid #f1f5f9; transition: background-color 0.2s;">
                <td style="padding: 12px 15px; font-weight: bold; color: #0f172a;">#${chamado.id}</td>
                <td style="padding: 12px 15px; color: #334155; font-weight: 500;">${chamado.titulo}</td>
                <td style="padding: 12px 15px; color: #64748b; font-size: 0.9rem;">${chamado.requerente}</td>
                <td style="padding: 12px 15px;">
                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: ${corPrioridade}; margin-right: 6px;"></span>
                    <span style="font-size: 0.85rem; color: #475569;">${chamado.prioridade}</span>
                </td>
                <td style="padding: 12px 15px;">
                    <span style="background: ${corStatusBg}; color: ${corStatusTxt}; padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold;">
                        ${chamado.status}
                    </span>
                </td>
                <td style="padding: 12px 15px; color: #64748b; font-size: 0.85rem; font-family: monospace;">${chamado.sla}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackGLPI() {
    return [
        { id: "20261001", titulo: "Lentidão no acesso ao ERP Corporativo", requerente: "Maria Souza (Financeiro)", prioridade: "Alta", status: "Em Andamento", sla: "01h 15m restantes" },
        { id: "20261002", titulo: "Liberação de licença Office 365", requerente: "João Pedro (RH)", prioridade: "Média", status: "Novo", sla: "23h 45m restantes" },
        { id: "20261003", titulo: "Instabilidade no Wi-Fi da Diretoria", requerente: "Carlos Silva (Presidência)", prioridade: "Crítica", status: "Em Andamento", sla: "00h 30m restantes" },
        { id: "20261004", titulo: "Troca de toner impressora central", requerente: "Recepção", prioridade: "Baixa", status: "Pendente", sla: "Pausado" },
        { id: "20261005", titulo: "Criação de usuário no SEI", requerente: "Ana Lima (Engenharia)", prioridade: "Média", status: "Solucionado", sla: "Entregue no prazo" },
        { id: "20261006", titulo: "Configuração de VPN para Home Office", requerente: "Fernando Costa (Projetos)", prioridade: "Alta", status: "Em Andamento", sla: "03h 10m restantes" }
    ];
}