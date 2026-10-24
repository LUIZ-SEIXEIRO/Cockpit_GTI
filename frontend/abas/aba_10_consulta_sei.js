// H:\glpi-spaguas\frontend\abas\aba_10_fixados.js

window.initAba_fixados = async function() {
    console.log("🚀 Inicializando módulo Processos Fixados (Watchlist Prioritária)...");

    let FIXADOS_DADOS = [];

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/processos/fixados');
        if (response.ok) {
            const json = await response.json();
            FIXADOS_DADOS = json.dados || [];
        } else {
            console.warn("⚠️ API de Fixados indisponível. Carregando watchlist de fallback para UI.");
            FIXADOS_DADOS = gerarDadosFallbackFixados(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        FIXADOS_DADOS = gerarDadosFallbackFixados();
    }

    renderizarFixados(FIXADOS_DADOS);
};

// 2. Motor de Renderização da Watchlist
function renderizarFixados(dados) {
    const container = document.getElementById('conteudo-fixados');
    if (!container) {
        console.error("❌ Container 'conteudo-fixados' não encontrado no painel.html");
        return;
    }

    if (dados.length === 0) {
        container.innerHTML = `
            <div style="background: white; padding: 30px; text-align: center; border-radius: 8px; border: 1px solid #e2e8f0; color: #64748b;">
                Nenhum processo fixado no momento. Use a estrela ⭐ nas consultas para fixar itens importantes.
            </div>
        `;
        return;
    }

    let html = `
        <div style="margin-bottom: 15px; color: #475569; font-size: 0.9rem;">
            Estes são os seus processos e chamados monitorados de alta prioridade para acesso rápido.
        </div>
        <div style="display: flex; flex-direction: column; gap: 15px;">
    `;

    dados.forEach(item => {
        let corPrioridade = '#0544cf'; // Azul padrão
        if (item.criticidade === 'Crítico') corPrioridade = '#ef4444'; // Vermelho
        if (item.criticidade === 'Alerta') corPrioridade = '#f59e0b'; // Amarelo/Laranja

        html += `
            <div style="background: white; border: 1px solid #e2e8f0; border-left: 4px solid ${corPrioridade}; border-radius: 6px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                        <span style="font-family: monospace; font-size: 1rem; font-weight: bold; color: #0f172a;">⭐ ${item.codigo}</span>
                        <span style="background: #f1f5f9; color: #334155; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold;">${item.sistema}</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #1e293b; font-weight: 500; margin-bottom: 8px;">
                        ${item.titulo}
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b;">
                        <strong>Responsável/Interessado:</strong> ${item.responsavel} | <strong>Última Atualização:</strong> ${item.ultima_atualizacao}
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button style="background: #002d5a; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: bold;">Ver Detalhes</button>
                    <button style="background: #fee2e2; color: #991b1b; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem;" title="Remover dos fixados">❌</button>
                </div>
            </div>
        `;
    });

    html += `</div>`;
    container.innerHTML = html;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackFixados() {
    return [
        {
            codigo: "001.00012345/2026-99",
            sistema: "SEI",
            titulo: "Aquisição de Licenças Microsoft Office 365 para SP-Águas",
            responsavel: "Diretoria de Tecnologia (DTI)",
            criticidade: "Normal",
            ultima_atualizacao: "22/10/2026 14:30"
        },
        {
            codigo: "INC-2026-8841",
            sistema: "GLPI",
            titulo: "Instabilidade crítica na rede corporativa da bacia hidrográfica",
            responsavel: "NOC / Operações",
            criticidade: "Crítico",
            ultima_atualizacao: "22/10/2026 16:00"
        },
        {
            codigo: "OP-PROJ-014",
            sistema: "OpenProject",
            titulo: "Implementação do Plano Diretor de TIC (PDTIC 2027-2030)",
            responsavel: "Luiz Seixeiro",
            criticidade: "Alerta",
            ultima_atualizacao: "21/10/2026 11:20"
        }
    ];
}