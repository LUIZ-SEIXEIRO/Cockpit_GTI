// H:\glpi-spaguas\frontend\abas\aba_03_pdtic_eixos.js

window.initAba_pdtic = async function() {
    console.log("🚀 Inicializando módulo PDTIC 2027-2030 (Eixos e Governança)...");

    let PDTIC_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        // Rota futura para consumir dados consolidados do banco ou via integração
        const response = await fetch('/api/pdtic/governanca');
        if (response.ok) {
            const json = await response.json();
            PDTIC_DADOS = json.dados;
        } else {
            console.warn("⚠️ API do PDTIC indisponível. Carregando dados de fallback para UI.");
            PDTIC_DADOS = gerarDadosFallbackPDTIC();
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        PDTIC_DADOS = gerarDadosFallbackPDTIC();
    }

    renderizarPDTIC(PDTIC_DADOS);
};

// 2. Motor de Renderização do Painel PDTIC
function renderizarPDTIC(dados) {
    const container = document.getElementById('conteudo-pdtic');
    if (!container) {
        console.error("❌ Container 'conteudo-pdtic' não encontrado no painel.html");
        return;
    }

    // Renderização dos KPIs Superiores (8 KPIs Estratégicos simplificados no mock)
    let kpisHtml = `<div style="display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap;">`;
    dados.kpis.forEach(kpi => {
        let corKpi = kpi.status === 'No Alvo' ? '#01a75f' : (kpi.status === 'Atenção' ? '#f59e0b' : '#ef4444');
        kpisHtml += `
            <div style="flex: 1; min-width: 150px; background: white; border-left: 4px solid ${corKpi}; border-radius: 6px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: bold;">${kpi.nome}</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #0f172a; margin-top: 5px;">${kpi.valor}</div>
                <div style="font-size: 0.75rem; color: ${corKpi}; margin-top: 5px;">Status: ${kpi.status}</div>
            </div>
        `;
    });
    kpisHtml += `</div>`;

    // Renderização dos 5 Eixos e suas Iniciativas
    let eixosHtml = `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px;">`;
    dados.eixos.forEach(eixo => {
        let iniciativasHtml = '';
        eixo.iniciativas.forEach(ini => {
            let statusIcon = ini.status === 'Concluído' ? '✅' : (ini.status === 'Em Andamento' ? '🔄' : '⏳');
            iniciativasHtml += `
                <div style="padding: 10px 0; border-bottom: 1px solid #f1f5f9; display: flex; align-items: flex-start; gap: 10px;">
                    <span style="font-size: 1.1rem;">${statusIcon}</span>
                    <div>
                        <div style="font-size: 0.9rem; font-weight: bold; color: #334155;">${ini.nome}</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Prazo: ${ini.prazo}</div>
                    </div>
                </div>
            `;
        });

        eixosHtml += `
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <h3 style="margin: 0 0 15px 0; color: #002d5a; font-size: 1.1rem; display: flex; justify-content: space-between; align-items: center;">
                    ${eixo.nome}
                    <span style="background: #e2e8f0; color: #475569; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">${eixo.iniciativas.length} Iniciativas</span>
                </h3>
                <div style="margin-top: 10px;">
                    ${iniciativasHtml}
                </div>
            </div>
        `;
    });
    eixosHtml += `</div>`;

    container.innerHTML = kpisHtml + eixosHtml;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackPDTIC() {
    return {
        kpis: [
            { nome: "Iniciativas Entregues", valor: "12/35", status: "Atenção" },
            { nome: "Orçamento Executado", valor: "45%", status: "No Alvo" },
            { nome: "Índice de Maturidade", valor: "Nível 3", status: "No Alvo" },
            { nome: "SLA Contratos", valor: "98.5%", status: "No Alvo" }
        ],
        eixos: [
            {
                nome: "1. Governança de TI",
                iniciativas: [
                    { nome: "Revisão da Política de Segurança (POSI)", status: "Concluído", prazo: "T1 2026" },
                    { nome: "Adequação Súmula 269 TCU", status: "Em Andamento", prazo: "T3 2026" }
                ]
            },
            {
                nome: "2. Sistemas de Informação",
                iniciativas: [
                    { nome: "Implantação GLPI 10 e ITSM", status: "Em Andamento", prazo: "T4 2026" },
                    { nome: "Integração SEI e OpenProject", status: "Pendente", prazo: "T1 2027" }
                ]
            },
            {
                nome: "3. Infraestrutura e Nuvem",
                iniciativas: [
                    { nome: "Migração de Datacenter Locaweb", status: "Concluído", prazo: "T2 2026" },
                    { nome: "Implementação Firewall NGFW", status: "Em Andamento", prazo: "T4 2026" }
                ]
            },
            {
                nome: "4. Segurança e Privacidade",
                iniciativas: [
                    { nome: "Auditoria Contínua LGPD", status: "Em Andamento", prazo: "Contínuo" },
                    { nome: "Campanha de Conscientização Phishing", status: "Concluído", prazo: "T2 2026" }
                ]
            },
            {
                nome: "5. Inovação e Dados",
                iniciativas: [
                    { nome: "Deploy Cockpit IA Local (Docker)", status: "Em Andamento", prazo: "T4 2026" },
                    { nome: "Painéis de Telemetria Hídrica", status: "Pendente", prazo: "T2 2027" }
                ]
            }
        ]
    };
}