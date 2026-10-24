// H:\glpi-spaguas\frontend\abas\aba_14_configuracoes.js

window.initAba_configuracoes = async function() {
    console.log("🚀 Inicializando módulo Configurações [Sistemas Internos & Busca Externa]...");

    let CONFIG_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/configuracoes/status');
        if (response.ok) {
            const json = await response.json();
            CONFIG_DADOS = json.dados;
        } else {
            console.warn("⚠️ API de Configurações indisponível. Carregando dados de fallback para UI.");
            CONFIG_DADOS = gerarDadosFallbackConfig(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        CONFIG_DADOS = gerarDadosFallbackConfig();
    }

    renderizarConfiguracoes(CONFIG_DADOS);
};

// 2. Motor de Renderização do Painel de Configurações
function renderizarConfiguracoes(dados) {
    const container = document.getElementById('conteudo-configuracoes');
    if (!container) {
        console.error("❌ Container 'conteudo-configuracoes' não encontrado no painel.html");
        return;
    }

    let html = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            
            <!-- SEÇÃO 1: SISTEMAS INTERNOS (GRUPO A) -->
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <h3 style="margin: 0 0 15px 0; color: #002d5a; font-size: 1.1rem; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
                    🔗 Sistemas Internos (Grupo A)
                </h3>
                <div style="display: flex; flex-direction: column; gap: 15px;">
    `;

    dados.sistemas_internos.forEach(sis => {
        let badgeColor = sis.ativo ? '#10b981' : '#ef4444';
        let badgeText = sis.ativo ? 'Conectado' : 'Desconectado';
        
        html += `
            <div style="border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; background: #f8fafc; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: bold; color: #1e293b; font-size: 0.95rem;">${sis.nome}</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">Endpoint: <code>${sis.url}</code></div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="background: ${badgeColor}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: bold;">${badgeText}</span>
                    <button onclick="alert('Testando conexão com ${sis.nome}...') " style="background: white; border: 1px solid #cbd5e1; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.75rem;">Testar</button>
                </div>
            </div>
        `;
    });

    html += `
                </div>
            </div>

            <!-- SEÇÃO 2: BUSCA ATIVA EXTERNA (GRUPO B) -->
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <h3 style="margin: 0 0 15px 0; color: #002d5a; font-size: 1.1rem; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
                    🌐 Robôs & Busca Ativa Externa (Grupo B)
                </h3>
                <div style="display: flex; flex-direction: column; gap: 15px;">
    `;

    dados.buscas_externas.forEach(ext => {
        let badgeColor = ext.ativo ? '#10b981' : '#f59e0b';
        let badgeText = ext.ativo ? 'Ativo (Sincronizado)' : 'Pendente Sincronização';

        html += `
            <div style="border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; background: #f8fafc; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: bold; color: #1e293b; font-size: 0.95rem;">${ext.nome}</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">Última varredura: ${ext.ultima_sincronizacao}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="background: ${badgeColor}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: bold;">${badgeText}</span>
                    <button onclick="alert('Disparando scraper para ${ext.nome}...') " style="background: #002d5a; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.75rem;">Sincronizar</button>
                </div>
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
function gerarDadosFallbackConfig() {
    return {
        sistemas_internos: [
            { nome: "GLPI 10 (ITSM)", url: "http://glpi:8088", ativo: true },
            { nome: "OpenProject (Portfólio)", url: "http://openproject:8090", ativo: true },
            { nome: "New API / Gateway IA", url: "http://newapi:3001", ativo: true }
        ],
        buscas_externas: [
            { nome: "DOESP (Diário Oficial)", ultima_sincronizacao: "Hoje, 08:00", ativo: true },
            { nome: "PNCP (Portal de Contratações)", ultima_sincronizacao: "Ontem, 23:30", ativo: true },
            { nome: "SIGRH / SOI (Portal Hídrico)", ultima_sincronizacao: "Hoje, 06:15", ativo: true },
            { nome: "Zabbix NOC (Bacias)", ultima_sincronizacao: "Há 10 minutos", ativo: true }
        ]
    };
}