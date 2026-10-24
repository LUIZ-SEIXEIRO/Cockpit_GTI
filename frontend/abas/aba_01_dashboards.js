// H:\glpi-spaguas\frontend\abas\aba_01_dashboards.js

window.initAba_dashboards = async function() {
    console.log("🚀 Inicializando módulo Dashboards (Consolidado 360°)...");

    let PROCESSOS = [];

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/glpi/chamados');
        if (response.ok) {
            const json = await response.json();
            PROCESSOS = json.dados || [];
        } else {
            console.warn("⚠️ API do GLPI indisponível ou vazia, carregando dados de fallback para UI.");
            PROCESSOS = gerarDadosFallback(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        PROCESSOS = gerarDadosFallback();
    }

    if (PROCESSOS.length === 0) {
        document.getElementById('conteudo-dashboards').innerHTML = '<p>Nenhum dado encontrado para exibição.</p>';
        return;
    }

    // 2. Atualização dos KPIs Consolidado 360°
    if (document.getElementById('kpi-val-acervo-total')) {
        document.getElementById('kpi-val-acervo-total').textContent = PROCESSOS.length;
        
        const countIntervencao = PROCESSOS.filter(p => p.Farol_Criticidade && p.Farol_Criticidade.includes("1")).length;
        const countSaneamento = PROCESSOS.filter(p => p.Farol_Criticidade && p.Farol_Criticidade.includes("2")).length;
        const countMonitoramento = PROCESSOS.filter(p => p.Farol_Criticidade && p.Farol_Criticidade.includes("3")).length;
        const countNormal = PROCESSOS.filter(p => p.Farol_Criticidade && p.Farol_Criticidade.includes("4")).length;

        document.getElementById('kpi-val-intervencao').textContent = countIntervencao;
        document.getElementById('kpi-val-saneamento').textContent = countSaneamento;
        document.getElementById('kpi-val-monitoramento').textContent = countMonitoramento;
        document.getElementById('kpi-val-fluxo-normal').textContent = countNormal;
    }

    // 3. Função Auxiliar para Agrupar Dados para os Gráficos
    function agruparDados(atributo) {
        const contagem = {};
        PROCESSOS.forEach(p => {
            const chave = p[atributo] || "Não Informado";
            contagem[chave] = (contagem[chave] || 0) + 1;
        });
        return {
            labels: Object.keys(contagem),
            series: Object.values(contagem)
        };
    }

    // 4. Renderização dos Gráficos (ApexCharts)
    const renderChart = (elementId, data, type = 'pie', colors = null) => {
        const container = document.querySelector(`#${elementId}`);
        if (!container) return;
        
        container.innerHTML = ''; // Limpa o gráfico anterior em caso de recarregamento
        
        const options = {
            series: data.series,
            labels: data.labels,
            chart: { 
                type: type, 
                height: 280, 
                background: 'transparent',
                toolbar: { show: false }
            },
            colors: colors || ['#002d5a', '#0544cf', '#01a75f', '#f59e0b', '#ef4444', '#7c3aed'],
            dataLabels: { enabled: true },
            legend: { position: 'bottom' },
            theme: { mode: 'light' },
            stroke: { width: 1, colors: ['#ffffff'] }
        };
        new ApexCharts(container, options).render();
    };

    // 5. Estruturação dos Dados Agrupados e Injeção Visual
    const dadosEixo = agruparDados("Eixo_Gestao");
    const dadosFarol = agruparDados("Farol_Criticidade");
    const dadosRisco = agruparDados("Classificacao_Risco");

    // Cores condicionais imutáveis para os Faróis da SP Águas
    const coresFarol = dadosFarol.labels.map(label => {
        if (label.includes("1")) return '#ef4444'; // Vermelho Crítico
        if (label.includes("2")) return '#ea580c'; // Laranja Alerta
        if (label.includes("3")) return '#ca8a04'; // Amarelo Monitoramento
        if (label.includes("4")) return '#16a34a'; // Verde Normal
        return '#64748b'; // Cinza Neutro
    });

    // Dispara a renderização dos 3 painéis
    renderChart('chart-cons-eixo', dadosEixo, 'donut');
    renderChart('chart-cons-criticidade', dadosFarol, 'pie', coresFarol);
    renderChart('chart-cons-risco', dadosRisco, 'donut');
};

// Alternância de abas internas do Dashboard (Consolidado, Esteira, etc.)
window.alternarModoDashboard = function(modo) {
    document.querySelectorAll('.subview-dash').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.pill-filtro-dash').forEach(el => {
        el.classList.remove('btn-primary');
        el.classList.add('btn-secondary');
    });

    const subview = document.getElementById('subview-dash-' + modo);
    const btn = document.getElementById('btn-dash-' + modo);
    
    if (subview) subview.style.display = 'block';
    if (btn) {
        btn.classList.remove('btn-secondary');
        btn.classList.add('btn-primary');
    }
};

// Função de Fallback Estrutural para testes contínuos de UI/UX
function gerarDadosFallback() {
    return [
        { Eixo_Gestao: "Infraestrutura", Farol_Criticidade: "4 - Fluxo Normal", Classificacao_Risco: "Baixo" },
        { Eixo_Gestao: "Sistemas", Farol_Criticidade: "2 - Saneamento", Classificacao_Risco: "Alto" },
        { Eixo_Gestao: "Governança", Farol_Criticidade: "1 - Intervenção", Classificacao_Risco: "Crítico" },
        { Eixo_Gestao: "Infraestrutura", Farol_Criticidade: "3 - Monitoramento", Classificacao_Risco: "Médio" },
        { Eixo_Gestao: "Sistemas", Farol_Criticidade: "4 - Fluxo Normal", Classificacao_Risco: "Baixo" },
        { Eixo_Gestao: "Segurança", Farol_Criticidade: "3 - Monitoramento", Classificacao_Risco: "Alto" },
        { Eixo_Gestao: "Operações", Farol_Criticidade: "4 - Fluxo Normal", Classificacao_Risco: "Baixo" }
    ];
}