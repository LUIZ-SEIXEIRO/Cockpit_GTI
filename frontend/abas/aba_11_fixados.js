// H:\glpi-spaguas\frontend\abas\aba_11_auditoria_tce.js

window.initAba_auditoria = async function() {
    console.log("🚀 Inicializando módulo Hub de Auditoria Contínua (TCE-SP & TCU)...");

    let AUDITORIA_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/auditoria/tce-tcu');
        if (response.ok) {
            const json = await response.json();
            AUDITORIA_DADOS = json.dados;
        } else {
            console.warn("⚠️ API de Auditoria indisponível. Carregando dados de fallback para UI.");
            AUDITORIA_DADOS = gerarDadosFallbackAuditoria(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        AUDITORIA_DADOS = gerarDadosFallbackAuditoria();
    }

    renderizarHubAuditoria(AUDITORIA_DADOS);
};

// 2. Motor de Renderização do Hub de Auditoria
function renderizarHubAuditoria(dados) {
    const container = document.getElementById('conteudo-auditoria');
    if (!container) {
        console.error("❌ Container 'conteudo-auditoria' não encontrado no painel.html");
        return;
    }

    // Bloco Superior: Cards de Indicadores de Conformidade
    let html = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px;">
            <div style="background: white; border-top: 4px solid #0544cf; border-radius: 6px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: bold;">Índice Conformidade TCU</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #0f172a; margin-top: 5px;">${dados.indicadores.conformidade_tcu}%</div>
                <div style="font-size: 0.75rem; color: #16a34a; margin-top: 5px;">Súmula 269 Atendida</div>
            </div>
            <div style="background: white; border-top: 4px solid #16a34a; border-radius: 6px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: bold;">Maturidade Governança</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #0f172a; margin-top: 5px;">${dados.indicadores.nivel_maturidade}</div>
                <div style="font-size: 0.75rem; color: #16a34a; margin-top: 5px;">Meta 2026: Nível 3</div>
            </div>
            <div style="background: white; border-top: 4px solid #f59e0b; border-radius: 6px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: bold;">Apontamentos TCE-SP</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #0f172a; margin-top: 5px;">${dados.indicadores.apontamentos_abertos}</div>
                <div style="font-size: 0.75rem; color: #d97706; margin-top: 5px;">Em fase de saneamento</div>
            </div>
            <div style="background: white; border-top: 4px solid #01a75f; border-radius: 6px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: bold;">Planos de Ação</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #0f172a; margin-top: 5px;">${dados.indicadores.planos_concluidos}/${dados.indicadores.total_planos}</div>
                <div style="font-size: 0.75rem; color: #16a34a; margin-top: 5px;">Concluídos com sucesso</div>
            </div>
        </div>
    `;

    // Bloco Inferior: Tabela de Apontamentos e Recomendações
    html += `
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="padding: 15px 20px; background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; color: #002d5a; font-size: 1.1rem;">Matriz de Conformidade & Recomendações Regulatórias</h3>
                <button style="background: #002d5a; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">+ Novo Apontamento</button>
            </div>
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead style="background-color: #f1f5f9; border-bottom: 2px solid #e2e8f0;">
                    <tr>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.8rem; text-transform: uppercase;">Órgão</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.8rem; text-transform: uppercase;">Processo / Ref</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.8rem; text-transform: uppercase;">Descrição da Conformidade / Apontamento</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.8rem; text-transform: uppercase;">Status</th>
                        <th style="padding: 12px 15px; color: #475569; font-size: 0.8rem; text-transform: uppercase;">Ação / Prazo</th>
                    </tr>
                </thead>
                <tbody>
    `;

    dados.auditorias.forEach(item => {
        let corStatusBg = '#dcfce7'; let corStatusTxt = '#15803d'; // Conforme
        if (item.status === 'Em Saneamento') { corStatusBg = '#fef3c7'; corStatusTxt = '#b45309'; }
        if (item.status === 'Pendente') { corStatusBg = '#fee2e2'; corStatusTxt = '#991b1b'; }

        html += `
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 12px 15px; font-weight: bold; color: #0f172a; font-size: 0.9rem;">${item.orgao}</td>
                <td style="padding: 12px 15px; font-family: monospace; font-size: 0.85rem; color: #334155;">${item.referencia}</td>
                <td style="padding: 12px 15px; color: #475569; font-size: 0.9rem; line-height: 1.4;">${item.descricao}</td>
                <td style="padding: 12px 15px;">
                    <span style="background: ${corStatusBg}; color: ${corStatusTxt}; padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold;">
                        ${item.status}
                    </span>
                </td>
                <td style="padding: 12px 15px; color: #64748b; font-size: 0.85rem;">
                    ${item.acao_prazo}
                </td>
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
function gerarDadosFallbackAuditoria() {
    return {
        indicadores: {
            conformidade_tcu: 92,
            nivel_maturidade: "Nível 2.5",
            apontamentos_abertos: 2,
            planos_concluidos: 14,
            total_planos: 16
        },
        auditorias: [
            {
                orgao: "TCU",
                referencia: "Súmula 269 / 2026",
                descricao: "Vedação de contratação de serviços por postos de trabalho sem métricas claras de entrega (UST/Pontos de Função).",
                status: "Conforme",
                acao_prazo: "Ajustado no ETP atual (Prazo: Concluído)"
            },
            {
                orgao: "TCE-SP",
                referencia: "Proc. 001234/2025",
                descricao: "Recomendação de aprimoramento nos controles de acesso lógico aos servidores de banco de dados.",
                status: "Em Saneamento",
                acao_prazo: "Implantação de MFA (Prazo: 30/11/2026)"
            },
            {
                orgao: "Auditoria Interna",
                referencia: "Relatório GTI-04/2026",
                descricao: "Validação de inventário de ativos de TIC integrados ao GLPI 10.",
                status: "Conforme",
                acao_prazo: "Validado em homologação"
            },
            {
                orgao: "TCE-SP",
                referencia: "Inspeção Ordinária",
                descricao: "Comprovação de cronograma de desembolso financeiro do PDTIC.",
                status: "Pendente",
                acao_prazo: "Aguardando parecer da DGF (Prazo: 10/11/2026)"
            }
        ]
    };
}