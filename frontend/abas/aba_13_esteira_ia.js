// H:\glpi-spaguas\frontend\abas\aba_13_cadernos.js

window.initAba_cadernos = async function() {
    console.log("🚀 Inicializando módulo Cadernos Temáticos & Modelos A4 Oficiais...");

    let CADERNOS_DADOS = null;

    // 1. Busca ativa dos dados via FastAPI (Backend)
    try {
        const response = await fetch('/api/cadernos/documentos');
        if (response.ok) {
            const json = await response.json();
            CADERNOS_DADOS = json.dados;
        } else {
            console.warn("⚠️ API de Cadernos indisponível. Carregando repositório de fallback para UI.");
            CADERNOS_DADOS = gerarDadosFallbackCadernos(); 
        }
    } catch (error) {
        console.error("❌ Erro na comunicação com o backend FastAPI:", error);
        CADERNOS_DADOS = gerarDadosFallbackCadernos();
    }

    renderizarCadernos(CADERNOS_DADOS);
};

// 2. Motor de Renderização do Repositório de Documentos
function renderizarCadernos(dados) {
    const container = document.getElementById('conteudo-cadernos');
    if (!container) {
        console.error("❌ Container 'conteudo-cadernos' não encontrado no painel.html");
        return;
    }

    let html = `
        <div style="margin-bottom: 20px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <h3 style="margin: 0 0 8px 0; color: #002d5a; font-size: 1.1rem;">Repositório Oficial de Artefatos Técnicos & Toolkits</h3>
            <p style="margin: 0; color: #64748b; font-size: 0.9rem;">
                Modelos padronizados em conformidade com a identidade visual da SP-Águas e diretrizes normativas da SA-GTI.
            </p>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px;">
    `;

    dados.forEach(cat => {
        let itensHtml = '';
        cat.itens.forEach(item => {
            itensHtml += `
                <div style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #1e293b; font-size: 0.9rem;">${item.titulo}</div>
                        <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">Formato: <strong>${item.formato}</strong> | Versão: ${item.versao}</div>
                    </div>
                    <button onclick="alert('Baixando artefato: ${item.titulo}')" style="background: #0544cf; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; font-weight: bold; transition: background 0.2s;">
                        Baixar 📥
                    </button>
                </div>
            `;
        });

        html += `
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <h4 style="margin: 0 0 15px 0; color: #002d5a; font-size: 1.05rem; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
                    ${cat.categoria}
                </h4>
                <div style="display: flex; flex-direction: column;">
                    ${itensHtml}
                </div>
            </div>
        `;
    });

    html += `</div>`;
    container.innerHTML = html;
}

// 3. Mock de Dados Temporário (Enquanto API não responde)
function gerarDadosFallbackCadernos() {
    return [
        {
            categoria: "📄 Pareceres & Relatórios Técnicos (SEI)",
            itens: [
                { titulo: "Modelo Canônico de Parecer em 3 Páginas (Tripla Validação)", formato: "PDF / HTML", versao: "v2.4" },
                { titulo: "Relatório Técnico de Aceite de Fábrica de Software", formato: "PDF (ReportLab)", versao: "v1.9" },
                { titulo: "Termo de Recebimento Provisório / Definitivo (TRP/TRD)", formato: "DOCX / SEI", versao: "v3.0" }
            ]
        },
        {
            categoria: "🏗️ Processos & Arquitetura (BPMN 2.0)",
            itens: [
                { titulo: "Manual de Modelagem de Processos SA-GTI", formato: "PDF / Bizagi", versao: "v2.0" },
                { titulo: "Diagrama Canônico: Fluxo de Incidentes ITSM (GLPI)", formato: "XML / BPMN", versao: "v1.2" },
                { titulo: "Arquitetura de Integração de APIs & Barramento", formato: "PDF", versao: "v1.0" }
            ]
        },
        {
            categoria: "⚖️ Contratações Públicas (Lei 14.133/2021)",
            itens: [
                { titulo: "Toolkit Completo: DFD, ETP e Termo de Referência (TR)", formato: "ZIP / DOCX", versao: "v4.1" },
                { titulo: "Planilha de Cálculo de IMR e Glosas Contratuais", formato: "XLSX", versao: "v2.2" },
                { titulo: "Matriz de Riscos de TIC (Modelos R01 a R12)", formato: "PDF / XLSX", versao: "v3.1" }
            ]
        }
    ];
}