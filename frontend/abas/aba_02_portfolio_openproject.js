// H:\glpi-spaguas\frontend\abas\aba_02_portfolio_openproject.js

window.initAba_openproject = async function() {
    console.log("🚀 Inicializando módulo OpenProject (Portfólio Corporativo)...");

    let PROJETOS = [];

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        // Esta rota será criada na Sprint 5 (sis_02_openproject_8090_prod.py)
        const response = await fetch('/api/openproject/projetos'); 
        if (response.ok) {
            const json = await response.json();
            PROJETOS = json.dados || [];
        } else {
            console.warn("⚠️ API do OpenProject indisponível. Carregando dados de fallback para UI.");
            PROJETOS = gerarDadosFallbackOpenProject(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        PROJETOS = gerarDadosFallbackOpenProject();
    }

    renderizarPortfolio(PROJETOS);
};

// 2. Motor de Renderização de Cards do Portfólio
function renderizarPortfolio(projetos) {
    const container = document.getElementById('conteudo-openproject');
    if (!container) {
        console.error("❌ Container 'conteudo-openproject' não encontrado no painel.html");
        return;
    }

    if (projetos.length === 0) {
        container.innerHTML = '<p>Nenhum projeto encontrado no portfólio.</p>';
        return;
    }

    // Grid CSS moderno e responsivo
    let html = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; padding-top: 15px;">`;

    projetos.forEach(proj => {
        // Lógica de cores baseada no status e identidade visual da SP-Águas
        let corStatus = '#64748b'; // Cinza (Padrão/Neutro)
        if (proj.status === 'Em Andamento') corStatus = '#0544cf'; // Azul Royal
        if (proj.status === 'Concluído') corStatus = '#01a75f'; // Verde SP-Águas
        if (proj.status === 'Atrasado') corStatus = '#ef4444'; // Vermelho Crítico
        if (proj.status === 'Pausado') corStatus = '#f59e0b'; // Laranja Alerta

        // Barra de progresso visual
        const barraProgresso = `
            <div style="background-color: #e2e8f0; border-radius: 4px; height: 8px; width: 100%; margin-top: 10px; overflow: hidden;">
                <div style="background-color: ${corStatus}; width: ${proj.progresso}%; height: 100%;"></div>
            </div>
        `;

        // Card HTML
        html += `
            <div class="card-projeto" style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <span style="background: ${corStatus}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">
                        ${proj.status}
                    </span>
                    <span style="font-size: 0.85rem; font-weight: bold; color: #475569;">${proj.progresso}%</span>
                </div>
                
                <h3 style="margin: 0 0 10px 0; font-size: 1.1rem; color: #0f172a; line-height: 1.3;">
                    ${proj.nome}
                </h3>
                <p style="margin: 0 0 20px 0; font-size: 0.9rem; color: #475569; min-height: 40px;">
                    ${proj.descricao}
                </p>
                
                <div style="font-size: 0.85rem; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 15px; display: flex; justify-content: space-between;">
                    <span><strong>PO:</strong> ${proj.responsavel}</span>
                    <span><strong>Prazo:</strong> ${proj.prazo}</span>
                </div>
                ${barraProgresso}
            </div>
        `;
    });

    html += `</div>`;
    container.innerHTML = html;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackOpenProject() {
    return [
        { nome: "Migração e Configuração GLPI 10", descricao: "Reestruturação do ITSM da SP-Águas, catálogos e SLAs.", status: "Em Andamento", progresso: 65, responsavel: "Luiz Seixeiro", prazo: "30/11/2026" },
        { nome: "Governança PDTIC 2027-2030", descricao: "Mapeamento das 35 iniciativas do plano diretor e integração de faróis.", status: "Em Andamento", progresso: 40, responsavel: "Comitê TIC", prazo: "15/12/2026" },
        { nome: "Integração API Hídrica SIGRH", descricao: "Conexão de dados de telemetria externa com os painéis.", status: "Atrasado", progresso: 15, responsavel: "Dev Team", prazo: "15/10/2026" },
        { nome: "Auditoria Súmula 269 TCU", descricao: "Revisão e mapeamento de conformidade dos processos de software.", status: "Concluído", progresso: 100, responsavel: "Luiz Seixeiro", prazo: "01/09/2026" },
        { nome: "Orquestração Cockpit IA", descricao: "Deploy dos agentes locais e failover com LLMs no Docker.", status: "Pausado", progresso: 50, responsavel: "Luiz Seixeiro", prazo: "20/11/2026" }
    ];
}