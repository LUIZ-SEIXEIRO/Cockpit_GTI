// H:\glpi-spaguas\frontend\abas\aba_08_daily_warroom.js

window.initAba_warroom = async function() {
    console.log("🚀 Inicializando módulo War Room (Daily Scrum)...");

    let WARROOM_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/agil/warroom');
        if (response.ok) {
            const json = await response.json();
            WARROOM_DADOS = json.dados;
        } else {
            console.warn("⚠️ API da War Room indisponível. Carregando dados de fallback para UI.");
            WARROOM_DADOS = gerarDadosFallbackWarRoom(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        WARROOM_DADOS = gerarDadosFallbackWarRoom();
    }

    renderizarWarRoom(WARROOM_DADOS);
    iniciarCronometroDaily();
};

// Variável global para controle do timer e evitar múltiplos intervalos
let dailyTimer = null;

// 2. Motor de Renderização da War Room
function renderizarWarRoom(dados) {
    const container = document.getElementById('conteudo-warroom');
    if (!container) {
        console.error("❌ Container 'conteudo-warroom' não encontrado no painel.html");
        return;
    }

    // Bloco Superior: Timer e Status da Sprint
    let html = `
        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
            <!-- Cronômetro Timebox -->
            <div style="flex: 1; background: #0f172a; color: white; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 10px 0; color: #94a3b8; font-size: 1rem; text-transform: uppercase;">⏱️ Timebox da Daily</h3>
                <div id="daily-timer-display" style="font-size: 3.5rem; font-weight: bold; font-family: monospace; color: #10b981; line-height: 1;">
                    15:00
                </div>
                <div style="margin-top: 15px; display: flex; justify-content: center; gap: 10px;">
                    <button onclick="iniciarCronometroDaily()" style="background: #3b82f6; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">▶️ Iniciar</button>
                    <button onclick="pausarCronometroDaily()" style="background: #f59e0b; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">⏸️ Pausar</button>
                    <button onclick="resetarCronometroDaily()" style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">🔄 Resetar</button>
                </div>
            </div>

            <!-- Dados da Sprint Atual -->
            <div style="flex: 2; background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <h3 style="margin: 0 0 15px 0; color: #002d5a; font-size: 1.1rem;">Resumo Executivo da Sprint</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <div style="font-size: 0.85rem; color: #64748b;">Dia da Sprint</div>
                        <div style="font-weight: bold; font-size: 1.1rem; color: #1e293b;">${dados.sprint.dia_atual} de ${dados.sprint.total_dias}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: #64748b;">Velocidade (Burn-down)</div>
                        <div style="font-weight: bold; font-size: 1.1rem; color: #10b981;">${dados.sprint.velocidade}</div>
                    </div>
                    <div style="grid-column: span 2;">
                        <div style="font-size: 0.85rem; color: #64748b;">Foco do Dia (Meta Diária)</div>
                        <div style="font-weight: bold; font-size: 1rem; color: #0544cf;">${dados.sprint.foco_dia}</div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Bloco Inferior: Impedimentos e Pauta da Equipe
    html += `<div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px;">`;

    // Coluna: Impedimentos (Blockers)
    html += `
        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px;">
            <h3 style="margin: 0 0 15px 0; color: #b91c1c; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span>🚨</span> Impedimentos Ativos
            </h3>
            <div style="display: flex; flex-direction: column; gap: 10px;">
    `;
    if (dados.impedimentos.length === 0) {
        html += `<div style="color: #991b1b; font-size: 0.9rem;">Nenhum bloqueio reportado. Caminho livre! 🚀</div>`;
    } else {
        dados.impedimentos.forEach(imp => {
            html += `
                <div style="background: white; border-left: 4px solid #ef4444; border-radius: 4px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                    <div style="font-weight: bold; color: #7f1d1d; font-size: 0.9rem;">${imp.titulo}</div>
                    <div style="font-size: 0.8rem; color: #991b1b; margin-top: 5px;"><strong>Afeta:</strong> ${imp.afeta}</div>
                    <div style="font-size: 0.8rem; color: #991b1b;"><strong>Resp. Desbloqueio:</strong> ${imp.responsavel_desbloqueio}</div>
                </div>
            `;
        });
    }
    html += `</div></div>`;

    // Coluna: Status da Equipe (O que fez / O que fará)
    html += `
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px;">
            <h3 style="margin: 0 0 15px 0; color: #002d5a; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span>👥</span> Atualizações da Equipe (Pauta)
            </h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
    `;
    dados.equipe.forEach(membro => {
        let statusColor = membro.presente ? '#10b981' : '#94a3b8';
        html += `
            <div style="border: 1px solid #f1f5f9; border-radius: 6px; padding: 12px; display: flex; gap: 15px; align-items: start;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: #e2e8f0; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #475569; position: relative;">
                    ${membro.iniciais}
                    <span style="position: absolute; bottom: 0; right: 0; width: 10px; height: 10px; background: ${statusColor}; border-radius: 50%; border: 2px solid white;"></span>
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: bold; color: #1e293b; font-size: 0.95rem;">${membro.nome}</div>
                    <div style="font-size: 0.85rem; color: #475569; margin-top: 4px;">
                        <strong>Ontem:</strong> ${membro.ontem}<br>
                        <strong>Hoje:</strong> ${membro.hoje}
                    </div>
                </div>
            </div>
        `;
    });
    html += `</div></div></div>`;

    container.innerHTML = html;
}

// 3. Lógica do Cronômetro de 15 Minutos (Daily Scrum)
let tempoRestante = 15 * 60; // 15 minutos em segundos

window.iniciarCronometroDaily = function() {
    if (dailyTimer) clearInterval(dailyTimer);
    dailyTimer = setInterval(() => {
        if (tempoRestante <= 0) {
            clearInterval(dailyTimer);
            document.getElementById('daily-timer-display').style.color = '#ef4444';
            return;
        }
        tempoRestante--;
        atualizarDisplayCronometro();
    }, 1000);
};

window.pausarCronometroDaily = function() {
    if (dailyTimer) clearInterval(dailyTimer);
};

window.resetarCronometroDaily = function() {
    if (dailyTimer) clearInterval(dailyTimer);
    tempoRestante = 15 * 60;
    document.getElementById('daily-timer-display').style.color = '#10b981';
    atualizarDisplayCronometro();
};

function atualizarDisplayCronometro() {
    const display = document.getElementById('daily-timer-display');
    if (!display) return;
    const minutos = Math.floor(tempoRestante / 60);
    const segundos = tempoRestante % 60;
    display.textContent = \`\${minutos.toString().padStart(2, '0')}:\${segundos.toString().padStart(2, '0')}\`;
    
    // Alerta visual nos últimos 3 minutos
    if (tempoRestante <= 180 && tempoRestante > 0) {
        display.style.color = '#f59e0b';
    }
}

// 4. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackWarRoom() {
    return {
        sprint: {
            dia_atual: 5,
            total_dias: 10,
            velocidade: "No Alvo (On Track)",
            foco_dia: "Homologação do Frontend SPA e Início da Conexão com GLPI."
        },
        impedimentos: [
            { titulo: "Acesso Negado na Porta 3306", afeta: "Backend FastAPI", responsavel_desbloqueio: "Infraestrutura (Redes)" }
        ],
        equipe: [
            { nome: "Luiz Seixeiro", iniciais: "LS", presente: true, ontem: "Estruturação das Abas 01 a 06 no frontend.", hoje: "Finalizar abas 07 e 08 e montar o orquestrador de IA no backend." },
            { nome: "Ana Desenvolvedora", iniciais: "AD", presente: true, ontem: "Mapeamento dos endpoints REST do GLPI.", hoje: "Desenvolver conectores no `sis_01_glpi_8088_prod.py`." },
            { nome: "Carlos Infra", iniciais: "CI", presente: false, ontem: "Subida dos containers Docker (MariaDB e FastAPI).", hoje: "Liberar regras de firewall para comunicação entre containers." }
        ]
    };
}