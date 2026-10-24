// H:\glpi-spaguas\frontend\abas\aba_06_mesa_trabalho.js

window.initAba_mesa = async function() {
    console.log("🚀 Inicializando módulo Mesa de Trabalho Operacional (Cockpit)...");

    let MESA_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/mesa/minhas-tarefas');
        if (response.ok) {
            const json = await response.json();
            MESA_DADOS = json.dados;
        } else {
            console.warn("⚠️ API da Mesa de Trabalho indisponível. Carregando dados de fallback para UI.");
            MESA_DADOS = gerarDadosFallbackMesa(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        MESA_DADOS = gerarDadosFallbackMesa();
    }

    renderizarMesaTrabalho(MESA_DADOS);
};

// 2. Motor de Renderização do Cockpit do Usuário
function renderizarMesaTrabalho(dados) {
    const container = document.getElementById('conteudo-mesa');
    if (!container) {
        console.error("❌ Container 'conteudo-mesa' não encontrado no painel.html");
        return;
    }

    // Grid principal: 2 colunas (Tarefas/Aprovações à esquerda, Alertas à direita)
    let html = `<div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">`;

    // COLUNA ESQUERDA: Tarefas e Aprovações
    html += `<div style="display: flex; flex-direction: column; gap: 20px;">`;

    // Bloco: Aprovações Pendentes (Prioridade Máxima)
    html += `
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <h3 style="margin: 0 0 15px 0; color: #ef4444; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span>⚠️</span> Aprovações Pendentes (Ação Requerida)
            </h3>
            <div style="display: flex; flex-direction: column; gap: 10px;">
    `;
    if (dados.aprovacoes.length === 0) {
        html += `<div style="color: #64748b; font-size: 0.9rem;">Nenhuma aprovação pendente.</div>`;
    } else {
        dados.aprovacoes.forEach(aprov => {
            html += `
                <div style="border: 1px solid #f87171; background: #fef2f2; border-radius: 6px; padding: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: bold; color: #991b1b; font-size: 0.95rem;">${aprov.titulo}</div>
                        <div style="font-size: 0.8rem; color: #b91c1c; margin-top: 4px;">Origem: ${aprov.origem} | Prazo: ${aprov.prazo}</div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; font-weight: bold;">Analisar</button>
                    </div>
                </div>
            `;
        });
    }
    html += `</div></div>`;

    // Bloco: Tarefas de Hoje (Fila de Trabalho)
    html += `
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <h3 style="margin: 0 0 15px 0; color: #002d5a; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span>📋</span> Minhas Tarefas de Hoje
            </h3>
            <div style="display: flex; flex-direction: column; gap: 10px;">
    `;
    dados.tarefas.forEach(tarefa => {
        let corPrioridade = tarefa.prioridade === 'Alta' ? '#ea580c' : (tarefa.prioridade === 'Média' ? '#ca8a04' : '#16a34a');
        html += `
            <div style="border: 1px solid #e2e8f0; border-left: 4px solid ${corPrioridade}; background: #f8fafc; border-radius: 6px; padding: 12px; display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="font-weight: bold; color: #1e293b; font-size: 0.95rem;">${tarefa.titulo}</div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                        Status: <span style="font-weight: bold; color: #334155;">${tarefa.status}</span> | Sistema: ${tarefa.sistema}
                    </div>
                </div>
                <button style="background: white; border: 1px solid #cbd5e1; color: #334155; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">
                    Acessar
                </button>
            </div>
        `;
    });
    html += `</div></div></div>`;

    // COLUNA DIREITA: Avisos e Atalhos Rápidos
    html += `<div style="display: flex; flex-direction: column; gap: 20px;">`;

    // Bloco: Alertas do Sistema
    html += `
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <h3 style="margin: 0 0 15px 0; color: #002d5a; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span>🔔</span> Alertas Globais
            </h3>
            <div style="display: flex; flex-direction: column; gap: 10px;">
    `;
    dados.alertas.forEach(alerta => {
        html += `
            <div style="padding: 10px; border-radius: 6px; background: #fffbeb; border: 1px solid #fef3c7; color: #92400e; font-size: 0.85rem;">
                <strong>${alerta.data}:</strong> ${alerta.mensagem}
            </div>
        `;
    });
    html += `</div></div>`;

    // Bloco: Ações Rápidas (Atalhos)
    html += `
        <div style="background: #002d5a; border-radius: 8px; padding: 20px; color: white; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0; font-size: 1.1rem; color: white;">⚡ Ações Rápidas</h3>
            <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                <button style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; padding: 10px; border-radius: 6px; cursor: pointer; text-align: left; transition: background 0.2s;">+ Abrir Chamado Interno</button>
                <button style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; padding: 10px; border-radius: 6px; cursor: pointer; text-align: left; transition: background 0.2s;">+ Nova Tarefa OpenProject</button>
                <button style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; padding: 10px; border-radius: 6px; cursor: pointer; text-align: left; transition: background 0.2s;">+ Pesquisa SEI (Agente IA)</button>
            </div>
        </div>
    `;

    html += `</div></div>`;
    container.innerHTML = html;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackMesa() {
    return {
        aprovacoes: [
            { titulo: "Aprovação de ETP - Servidores", origem: "Processo SEI", prazo: "Hoje, 17:00" },
            { titulo: "Validação de Sprint Backlog", origem: "OpenProject", prazo: "Amanhã, 10:00" }
        ],
        tarefas: [
            { titulo: "Revisar mapeamento BPMN da DGD", prioridade: "Alta", status: "Aguardando Revisão", sistema: "Bizagi/SharePoint" },
            { titulo: "Atualizar Documento de Formalizacao de Demanda (DFD)", prioridade: "Média", status: "Em Andamento", sistema: "SEI" },
            { titulo: "Responder ticket de integração API SIGRH", prioridade: "Baixa", status: "Novo", sistema: "GLPI" },
            { titulo: "Validar Quality Gate SonarQube", prioridade: "Alta", status: "Bloqueado", sistema: "GitLab" }
        ],
        alertas: [
            { data: "22/10", mensagem: "Manutenção programada no ambiente de homologação a partir das 20h." },
            { data: "21/10", mensagem: "Relatório Mensal de SLAs do Helpdesk disponível para assinatura." }
        ]
    };
}