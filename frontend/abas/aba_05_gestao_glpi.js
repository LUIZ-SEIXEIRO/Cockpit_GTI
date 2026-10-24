// H:\glpi-spaguas\frontend\abas\aba_05_visao_estrategica.js

window.initAba_visao = async function() {
    console.log("🚀 Inicializando módulo Visão Estratégica & Faróis de Criticidade...");

    let ESTRATEGIA_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/estrategia/farois');
        if (response.ok) {
            const json = await response.json();
            ESTRATEGIA_DADOS = json.dados;
        } else {
            console.warn("⚠️ API de Visão Estratégica indisponível. Carregando dados de fallback para UI.");
            ESTRATEGIA_DADOS = gerarDadosFallbackVisaoEstrategica(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        ESTRATEGIA_DADOS = gerarDadosFallbackVisaoEstrategica();
    }

    renderizarVisaoEstrategica(ESTRATEGIA_DADOS);
};

// 2. Motor de Renderização do Painel Estratégico
function renderizarVisaoEstrategica(dados) {
    const container = document.getElementById('conteudo-visao');
    if (!container) {
        console.error("❌ Container 'conteudo-visao' não encontrado no painel.html");
        return;
    }

    // Renderização dos Faróis de Criticidade (Sistemas e Serviços Core)
    let faroisHtml = `
        <h3 style="color: #002d5a; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">
            Faróis de Criticidade (Sistemas Core)
        </h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 30px;">
    `;
    
    dados.farois.forEach(farol => {
        let corStatus = '#16a34a'; // Verde (Operacional)
        let icone = '✅';
        
        if (farol.status === 'Alerta') { corStatus = '#f59e0b'; icone = '⚠️'; }
        if (farol.status === 'Crítico') { corStatus = '#ef4444'; icone = '🚨'; }
        if (farol.status === 'Manutenção') { corStatus = '#64748b'; icone = '🔧'; }

        faroisHtml += `
            <div style="background: white; border: 1px solid #e2e8f0; border-top: 4px solid ${corStatus}; border-radius: 6px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: bold; color: #0f172a; font-size: 1.05rem;">${farol.sistema}</span>
                    <span style="font-size: 1.2rem;">${icone}</span>
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-bottom: 10px; min-height: 35px;">
                    ${farol.descricao}
                </div>
                <div style="font-size: 0.75rem; color: ${corStatus}; font-weight: bold; text-transform: uppercase;">
                    Status: ${farol.status}
                </div>
            </div>
        `;
    });
    faroisHtml += `</div>`;

    // Renderização dos Objetivos Estratégicos (OKRs)
    let okrsHtml = `
        <h3 style="color: #002d5a; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">
            Objetivos e Resultados Chave (OKRs T3-2026)
        </h3>
        <div style="display: flex; flex-direction: column; gap: 15px;">
    `;

    dados.okrs.forEach(okr => {
        okrsHtml += `
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; display: flex; align-items: center; gap: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="flex: 1;">
                    <div style="font-weight: bold; color: #1e293b; font-size: 1rem; margin-bottom: 5px;">${okr.objetivo}</div>
                    <div style="font-size: 0.85rem; color: #64748b;">Responsável: ${okr.owner}</div>
                </div>
                <div style="flex: 2;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #475569; margin-bottom: 5px;">
                        <span>Progresso</span>
                        <span style="font-weight: bold;">${okr.progresso}%</span>
                    </div>
                    <div style="background-color: #e2e8f0; border-radius: 4px; height: 8px; width: 100%; overflow: hidden;">
                        <div style="background-color: #0544cf; width: ${okr.progresso}%; height: 100%;"></div>
                    </div>
                </div>
            </div>
        `;
    });
    okrsHtml += `</div>`;

    container.innerHTML = faroisHtml + okrsHtml;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackVisaoEstrategica() {
    return {
        farois: [
            { sistema: "Data Center Primário", status: "Operacional", descricao: "Servidores físicos e conectividade principal." },
            { sistema: "Integração SIGRH", status: "Crítico", descricao: "Falha de sincronização na malha de telemetria nas últimas 4h." },
            { sistema: "Portal SEI", status: "Alerta", descricao: "Latência acima de 2000ms detectada no último teste de carga." },
            { sistema: "Firewall e VPN", status: "Operacional", descricao: "Tráfego normal e links redundantes ativos." },
            { sistema: "Nuvem Pública (AWS)", status: "Manutenção", descricao: "Janela de atualização do banco de dados RDS." }
        ],
        okrs: [
            { objetivo: "Reduzir tempo de resolução de chamados (TTR) em 20%", owner: "Helpdesk N2", progresso: 65 },
            { objetivo: "Alcançar 100% de conformidade com a LGPD nos sistemas core", owner: "Comitê de Segurança", progresso: 40 },
            { objetivo: "Implementar automação de IA para triagem de 50% das demandas", owner: "Luiz Seixeiro", progresso: 80 },
            { objetivo: "Garantir 99.9% de uptime para o Portal de Outorgas", owner: "Infraestrutura", progresso: 95 }
        ]
    };
}