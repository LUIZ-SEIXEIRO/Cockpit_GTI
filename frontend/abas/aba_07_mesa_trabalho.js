// H:\glpi-spaguas\frontend\abas\aba_07_gestao_agil.js

window.initAba_agil = async function() {
    console.log("🚀 Inicializando módulo Gestão Ágil (Sprint Planning & Kanban)...");

    let AGIL_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend / OpenProject)
    try {
        const response = await fetch('/api/agil/sprint-atual');
        if (response.ok) {
            const json = await response.json();
            AGIL_DADOS = json.dados;
        } else {
            console.warn("⚠️ API de Gestão Ágil indisponível. Carregando dados de fallback para UI.");
            AGIL_DADOS = gerarDadosFallbackAgil(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        AGIL_DADOS = gerarDadosFallbackAgil();
    }

    renderizarGestaoAgil(AGIL_DADOS);
};

// 2. Motor de Renderização do Quadro Ágil
function renderizarGestaoAgil(dados) {
    const container = document.getElementById('conteudo-agil');
    if (!container) {
        console.error("❌ Container 'conteudo-agil' não encontrado no painel.html");
        return;
    }

    // Bloco Superior: Informações da Sprint Atual
    let html = `
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
                <div>
                    <h3 style="margin: 0 0 5px 0; color: #002d5a; font-size: 1.2rem;">🚀 ${dados.sprint.nome}</h3>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;"><strong>Meta:</strong> ${dados.sprint.meta}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.85rem; color: #475569; margin-bottom: 5px;">
                        Período: <strong>${dados.sprint.data_inicio}</strong> a <strong>${dados.sprint.data_fim}</strong>
                    </div>
                    <span style="background: #e0e7ff; color: #3730a3; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold;">
                        ${dados.sprint.dias_restantes} dias restantes
                    </span>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #475569; margin-bottom: 5px;">
                <span>Progresso da Sprint (Story Points)</span>
                <span style="font-weight: bold;">${dados.sprint.progresso}%</span>
            </div>
            <div style="background-color: #e2e8f0; border-radius: 4px; height: 10px; width: 100%; overflow: hidden;">
                <div style="background-color: #0544cf; width: ${dados.sprint.progresso}%; height: 100%; transition: width 0.5s ease-in-out;"></div>
            </div>
        </div>
    `;

    // Função local para renderizar os cards do Kanban
    const renderCards = (tarefas, corBorda) => {
        if (tarefas.length === 0) {
            return `<div style="padding: 15px; text-align: center; color: #94a3b8; font-size: 0.85rem; border: 2px dashed #cbd5e1; border-radius: 6px;">Nenhuma tarefa</div>`;
        }
        return tarefas.map(t => `
            <div style="background: white; border-left: 4px solid ${corBorda}; border-radius: 6px; padding: 12px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.1s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between;">
                    <span>#${t.id}</span>
                    <span style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px;">🎯 ${t.pontos} pts</span>
                </div>
                <div style="font-weight: 600; color: #1e293b; font-size: 0.9rem; margin-bottom: 8px; line-height: 1.3;">
                    ${t.titulo}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.75rem; background: #e2e8f0; color: #475569; padding: 2px 6px; border-radius: 12px;">
                        ${t.tipo}
                    </span>
                    <span style="font-size: 0.8rem; color: #002d5a; font-weight: 500;">
                        👤 ${t.responsavel}
                    </span>
                </div>
            </div>
        `).join('');
    };

    // Bloco Inferior: Quadro Kanban (CSS Grid)
    html += `
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; align-items: start;">
            <!-- Coluna To Do -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;">
                <h4 style="margin: 0 0 15px 0; color: #475569; display: flex; justify-content: space-between;">
                    A Fazer (To Do) <span style="background: #cbd5e1; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">${dados.kanban.todo.length}</span>
                </h4>
                ${renderCards(dados.kanban.todo, '#94a3b8')}
            </div>

            <!-- Coluna In Progress -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;">
                <h4 style="margin: 0 0 15px 0; color: #0544cf; display: flex; justify-content: space-between;">
                    Em Andamento <span style="background: #dbeafe; color: #1d4ed8; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">${dados.kanban.in_progress.length}</span>
                </h4>
                ${renderCards(dados.kanban.in_progress, '#3b82f6')}
            </div>

            <!-- Coluna Done -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;">
                <h4 style="margin: 0 0 15px 0; color: #01a75f; display: flex; justify-content: space-between;">
                    Concluído <span style="background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">${dados.kanban.done.length}</span>
                </h4>
                ${renderCards(dados.kanban.done, '#10b981')}
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackAgil() {
    return {
        sprint: {
            nome: "Sprint 24 - Outubro/2026",
            meta: "Finalizar Módulos de Frontend do Cockpit e Estruturar APIs do GLPI.",
            data_inicio: "12/10/2026",
            data_fim: "26/10/2026",
            dias_restantes: 4,
            progresso: 68
        },
        kanban: {
            todo: [
                { id: "1045", titulo: "Criar endpoint /api/pdtic/governanca", pontos: 3, tipo: "Backend", responsavel: "Backend Team" },
                { id: "1048", titulo: "Validar layout CSS em telas 1366x768", pontos: 2, tipo: "Frontend", responsavel: "UI/UX" }
            ],
            in_progress: [
                { id: "1041", titulo: "Conectar roteador JS com a aba de Gestão Ágil", pontos: 5, tipo: "Frontend", responsavel: "Luiz Seixeiro" },
                { id: "1042", titulo: "Desenvolver orquestrador de IA no main.py", pontos: 8, tipo: "Backend", responsavel: "Luiz Seixeiro" },
                { id: "1047", titulo: "Migrar scripts SQL do GLPI 10", pontos: 5, tipo: "DevOps", responsavel: "Infra" }
            ],
            done: [
                { id: "1038", titulo: "Criar docker-compose.yml base", pontos: 3, tipo: "DevOps", responsavel: "Luiz Seixeiro" },
                { id: "1039", titulo: "Estruturar roteador_abas.js", pontos: 5, tipo: "Frontend", responsavel: "Luiz Seixeiro" },
                { id: "1040", titulo: "Mock de dados da aba Visão Estratégica", pontos: 2, tipo: "Frontend", responsavel: "Luiz Seixeiro" }
            ]
        }
    };
}