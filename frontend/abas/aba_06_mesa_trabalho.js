window.initAba_mesa = async function() {
    console.log("🚀 Inicializando módulo Mesa de Trabalho Operacional (Cockpit)...");

    let MESA_DADOS = null;
    let modo = "demonstracao";
    let estadoApi = "API não conectada";

    try {
        const response = await fetch('/api/mesa/minhas-tarefas');
        if (response.ok) {
            const json = await response.json();
            if (!json.dados
                || !Array.isArray(json.dados.aprovacoes)
                || !Array.isArray(json.dados.tarefas)
                || !Array.isArray(json.dados.alertas)) {
                throw new Error("Formato de resposta inválido");
            }
            MESA_DADOS = json.dados;
            modo = "persistido";
            estadoApi = "API disponível";
        } else {
            estadoApi = `API indisponível (HTTP ${response.status})`;
        }
    } catch (error) {
        estadoApi = "API indisponível (erro de comunicação)";
    }

    if (!MESA_DADOS) {
        MESA_DADOS = gerarDadosFallbackMesa();
    }

    renderizarMesaTrabalho(MESA_DADOS, modo, estadoApi);
};

function escapeHtml(valor) {
    return String(valor ?? '').replace(/[&<>"']/g, caractere => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[caractere]);
}

function renderizarMesaTrabalho(dados, modo, estadoApi) {
    const container = document.getElementById('conteudo-mesa');
    if (!container) {
        console.error("❌ Container 'conteudo-mesa' não encontrado no painel.html");
        return;
    }

    const estadoPersistencia = modo === "persistido"
        ? "Tarefas persistidas no GLPI local."
        : "Modo demonstração: estes dados de exemplo não são salvos.";
    let html = `
        <div role="status" style="padding: 12px; margin-bottom: 16px; border-radius: 6px; background: ${modo === "persistido" ? "#dcfce7" : "#fef3c7"}; color: #334155;">
            <strong>${estadoPersistencia}</strong> ${escapeHtml(estadoApi)}
        </div>
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
    `;

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
                        <div style="font-weight: bold; color: #991b1b; font-size: 0.95rem;">${escapeHtml(aprov.titulo)}</div>
                        <div style="font-size: 0.8rem; color: #b91c1c; margin-top: 4px;">Origem: ${escapeHtml(aprov.origem)} | Prazo: ${escapeHtml(aprov.prazo)}</div>
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
        const coresPrioridade = { Alta: '#ea580c', 'Média': '#ca8a04', Baixa: '#16a34a' };
        const corPrioridade = Object.prototype.hasOwnProperty.call(coresPrioridade, tarefa.prioridade)
            ? coresPrioridade[tarefa.prioridade]
            : '#64748b';
        html += `
            <div style="border: 1px solid #e2e8f0; border-left: 4px solid ${corPrioridade}; background: #f8fafc; border-radius: 6px; padding: 12px; display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="font-weight: bold; color: #1e293b; font-size: 0.95rem;">${escapeHtml(tarefa.titulo)}</div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                        Status: <span style="font-weight: bold; color: #334155;">${escapeHtml(tarefa.status)}</span> | Sistema: ${escapeHtml(tarefa.sistema)}
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
                <strong>${escapeHtml(alerta.data)}:</strong> ${escapeHtml(alerta.mensagem)}
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