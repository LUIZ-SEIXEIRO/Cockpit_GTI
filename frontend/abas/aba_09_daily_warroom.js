// H:\glpi-spaguas\frontend\abas\aba_09_consulta_sei.js

window.initAba_sei = async function() {
    console.log("🚀 Inicializando módulo Acervo Probatório SEI...");

    let SEI_DADOS = [];

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/sei/processos');
        if (response.ok) {
            const json = await response.json();
            SEI_DADOS = json.dados || [];
        } else {
            console.warn("⚠️ API do SEI indisponível. Carregando acervo de fallback para UI.");
            SEI_DADOS = gerarDadosFallbackSEI(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        SEI_DADOS = gerarDadosFallbackSEI();
    }

    // Armazena globalmente para permitir o filtro na barra de pesquisa
    window.processosSEIAtuais = SEI_DADOS;
    
    renderizarInterfaceSEI();
    renderizarListaSEI(window.processosSEIAtuais);
};

// 2. Monta a Interface Base (Barra de Busca e Estrutura)
function renderizarInterfaceSEI() {
    const container = document.getElementById('conteudo-sei');
    if (!container) {
        console.error("❌ Container 'conteudo-sei' não encontrado no painel.html");
        return;
    }

    // Só injeta a barra de pesquisa se ela ainda não existir
    if (!document.getElementById('sei-search-bar')) {
        container.innerHTML = `
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 20px;">
                <div style="display: flex; gap: 15px; align-items: center;">
                    <div style="flex: 1; position: relative;">
                        <span style="position: absolute; left: 15px; top: 12px; color: #94a3b8;">🔍</span>
                        <input type="text" id="sei-search-bar" onkeyup="filtrarProcessosSEI()" placeholder="Buscar por Nº do Processo, Assunto ou Interessado..." style="width: 100%; padding: 12px 15px 12px 40px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.95rem; box-sizing: border-box; outline: none; transition: border-color 0.2s;">
                    </div>
                    <button style="background: #002d5a; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s;">
                        Pesquisa Avançada
                    </button>
                </div>
            </div>
            <div id="sei-lista-container"></div>
        `;

        // Estilização dinâmica para o input focado
        const searchInput = document.getElementById('sei-search-bar');
        searchInput.addEventListener('focus', () => searchInput.style.borderColor = '#0544cf');
        searchInput.addEventListener('blur', () => searchInput.style.borderColor = '#cbd5e1');
    }
}

// 3. Renderiza a Lista de Processos
function renderizarListaSEI(processos) {
    const listaContainer = document.getElementById('sei-lista-container');
    if (!listaContainer) return;

    if (processos.length === 0) {
        listaContainer.innerHTML = `
            <div style="background: white; padding: 30px; text-align: center; border-radius: 8px; border: 1px solid #e2e8f0; color: #64748b;">
                Nenhum processo encontrado para os critérios de busca.
            </div>
        `;
        return;
    }

    let html = `<div style="display: flex; flex-direction: column; gap: 15px;">`;

    processos.forEach(proc => {
        let corStatus = '#64748b'; // Neutro
        if (proc.status === 'Aberto') corStatus = '#16a34a'; // Verde
        if (proc.status === 'Sobrestado') corStatus = '#f59e0b'; // Laranja
        if (proc.status === 'Concluído') corStatus = '#3b82f6'; // Azul

        html += `
            <div style="background: white; border: 1px solid #e2e8f0; border-left: 4px solid ${corStatus}; border-radius: 6px; padding: 15px; display: flex; flex-direction: column; gap: 10px; transition: box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.1)'" onmouseout="this.style.boxShadow='none'">
                
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-family: monospace; font-size: 1.1rem; font-weight: bold; color: #0f172a;">
                        📄 ${proc.numero}
                    </div>
                    <span style="font-size: 0.8rem; background: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 12px; font-weight: bold;">
                        ${proc.status}
                    </span>
                </div>

                <div style="font-size: 0.95rem; color: #334155; font-weight: 500;">
                    ${proc.assunto}
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 10px; font-size: 0.85rem; color: #64748b;">
                    <div><strong>Interessado:</strong> ${proc.interessado}</div>
                    <div><strong>Unidade Atual:</strong> <span style="color: #002d5a; font-weight: bold;">${proc.unidade}</span></div>
                    <div><strong>Última Movimentação:</strong> ${proc.ultima_movimentacao}</div>
                </div>

            </div>
        `;
    });

    html += `</div>`;
    listaContainer.innerHTML = html;
}

// 4. Lógica de Filtro Local (Search)
window.filtrarProcessosSEI = function() {
    const termo = document.getElementById('sei-search-bar').value.toLowerCase();
    
    if (!termo) {
        renderizarListaSEI(window.processosSEIAtuais);
        return;
    }

    const processosFiltrados = window.processosSEIAtuais.filter(proc => 
        proc.numero.toLowerCase().includes(termo) ||
        proc.assunto.toLowerCase().includes(termo) ||
        proc.interessado.toLowerCase().includes(termo) ||
        proc.unidade.toLowerCase().includes(termo)
    );

    renderizarListaSEI(processosFiltrados);
};

// 5. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackSEI() {
    return [
        {
            numero: "001.00012345/2026-99",
            assunto: "Aquisição de Licenças Microsoft Office 365",
            interessado: "Diretoria de Tecnologia e Inovação (DTI)",
            unidade: "SA-GTI",
            status: "Aberto",
            ultima_movimentacao: "22/10/2026 14:30"
        },
        {
            numero: "001.00054321/2026-88",
            assunto: "Estudo Técnico Preliminar (ETP) - Migração de Data Center",
            interessado: "Núcleo de Infraestrutura",
            unidade: "DIF",
            status: "Aberto",
            ultima_movimentacao: "21/10/2026 09:15"
        },
        {
            numero: "001.00098765/2026-77",
            assunto: "Contratação de Fábrica de Software",
            interessado: "Gabinete Presidência",
            unidade: "Comissão de Licitação",
            status: "Sobrestado",
            ultima_movimentacao: "15/10/2026 11:00"
        },
        {
            numero: "001.00024680/2026-11",
            assunto: "Política de Segurança da Informação (POSI)",
            interessado: "Comitê de Governança",
            unidade: "Arquivo Geral",
            status: "Concluído",
            ultima_movimentacao: "01/09/2026 16:45"
        }
    ];
}