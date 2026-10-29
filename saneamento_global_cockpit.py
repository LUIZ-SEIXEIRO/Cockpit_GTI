# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
caminho_painel = os.path.join(frontend_dir, "painel.html")
caminho_js = os.path.join(frontend_dir, "conector_api.js")

# 1. SANEAMENTO GLOBAL DE TEXTOS DESATUALIZADOS NO painel.html
if os.path.exists(caminho_painel):
    with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    substituicoes = [
        ("PCA 2026", "PCA 2027"),
        ("pca_2026", "pca_2027"),
        ("6 FONTES CANÔNICAS", "8 MOTORES CANÔNICOS DE VARREDURA"),
        ("6 Fontes Canônicas", "8 Motores Canônicos de Varredura"),
        ("Central de Varredura (6 Fontes)", "Central de Varredura Multissistêmica (8 Motores)"),
        ("679 Registros no RAG", "882 Registros de Governança (500 OP + 203 GLPI + 179 SEI)"),
        ("679 registros", "882 registros oficiais"),
        ("Base Atualizada: 22/09/2026", "Base Integrada: SOE / Outorgas & SEI-SP"),
        ("22/09/2026", "Atualização Contínua"),
        ("🌐 179 Processos no Backlog", "🌐 Processos Integrados (SOE & SEI)"),
        ("Mapeamento de 179 processos ativos", "Mapeamento de processos e outorgas ativas")
    ]

    total_subst = 0
    for antigo, novo in substituicoes:
        qtd = html.count(antigo)
        if qtd > 0:
            html = html.replace(antigo, novo)
            total_subst += qtd

    with open(caminho_painel, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"1. painel.html saneado com sucesso! {total_subst} referências legadas atualizadas em todas as abas.")

# 2. ENRIQUECIMENTO AUTOMÁTICO E DELEGAÇÃO GLOBAL NO conector_api.js
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8", errors="ignore") as f:
        js = f.read()

    bloco_dossie_global = r'''
    // --- ENRIQUECIMENTO AUTOMÁTICO DA TABELA DE VISÃO ESTRATÉGICA ---
    window.enriquecerTabelaVisaoEstrategica = function () {
        var tbody = document.getElementById('tbody-visao-estrategica');
        if (!tbody) return;

        var linhas = tbody.querySelectorAll('tr');
        linhas.forEach(function (tr) {
            var tdId = tr.querySelector('td:first-child');
            var tdAcoes = tr.querySelector('td:last-child');

            // Torna o numero SEI azul e clicavel
            if (tdId && !tdId.querySelector('a')) {
                var numSei = tdId.textContent.trim();
                if (/^\d{3}\.\d{5,8}\/\d{4}-\d{2}$/.test(numSei)) {
                    tdId.innerHTML = '<a href="javascript:void(0)" onclick="window.abrirDetalhesProcesso(\'' + numSei + '\')" style="color: #0544cf; font-weight: 700; text-decoration: underline; cursor: pointer;" title="Abrir Dossiê & Timeline">' + numSei + '</a>';
                }
            }

            // Injeta o botao azul Dossie antes do botao de Checkpoint
            if (tdAcoes && !tdAcoes.querySelector('.btn-dossie-injetado')) {
                var btnCk = tdAcoes.querySelector('button');
                var numProc = '';
                if (btnCk) {
                    var m = (btnCk.getAttribute('onclick') || '').match(/'([^']+)'/);
                    if (m && m[1]) numProc = m[1];
                }
                if (!numProc && tdId) {
                    var m2 = tdId.textContent.trim().match(/\d{3}\.\d{5,8}\/\d{4}-\d{2}/);
                    if (m2) numProc = m2[0];
                }

                if (numProc) {
                    var btnDos = document.createElement('button');
                    btnDos.className = 'btn btn-primary btn-dossie-injetado';
                    btnDos.style.cssText = 'padding: 3px 8px; font-size: 11px; margin-right: 4px; background: #0070ba; border-color: #0070ba; color: white; font-weight: 700; cursor: pointer;';
                    btnDos.innerHTML = '🔍 Dossiê';
                    btnDos.onclick = function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        window.abrirDetalhesProcesso(numProc);
                    };
                    if (btnCk) {
                        tdAcoes.insertBefore(btnDos, btnCk);
                    } else {
                        tdAcoes.appendChild(btnDos);
                    }
                }
            }
        });
    };

    // --- DELEGAÇÃO GLOBAL DE CLIQUES EM QUALQUER PROCESSO SEI DO COCKPIT ---
    document.addEventListener('click', function (e) {
        // Se clicou no botao Checkpoint, permite que ele abra a minuta de notificacao
        if (e.target.closest('button') && e.target.closest('button').textContent.indexOf('Checkpoint') !== -1) {
            return;
        }

        var cell = e.target.closest('td, strong, span, a');
        if (cell && !cell.closest('button')) {
            var txt = cell.textContent.trim();
            var m = txt.match(/\b(\d{3}\.\d{5,8}\/\d{4}-\d{2})\b/);
            if (m && m[1]) {
                if (!e.target.closest('#modal-processo') && !e.target.closest('#modal-checkpoint')) {
                    e.preventDefault();
                    window.abrirDetalhesProcesso(m[1]);
                }
            }
        }
    }, true);
'''

    if "enriquecerTabelaVisaoEstrategica" not in js:
        idx_init = js.find("function init()")
        if idx_init != -1:
            js = js[:idx_init] + bloco_dossie_global + "\n    " + js[idx_init:]
            js = js.replace("window.atualizarVisaoEstrategicaAoVivo();", "window.atualizarVisaoEstrategicaAoVivo();\n        window.enriquecerTabelaVisaoEstrategica();\n        setInterval(window.enriquecerTabelaVisaoEstrategica, 1500);")

        with open(caminho_js, "w", encoding="utf-8") as f:
            f.write(js)
        print("2. conector_api.js atualizado com injeção do botão '🔍 Dossiê' e delegação global de cliques!")
    else:
        print("2. conector_api.js já possuía os handlers globais.")

print("Saneamento global concluído com sucesso!")
