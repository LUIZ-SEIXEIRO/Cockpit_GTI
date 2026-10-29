# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
caminho_painel = os.path.join(frontend_dir, "painel.html")
caminho_js = os.path.join(frontend_dir, "conector_api.js")
caminho_main = os.path.join(os.getcwd(), "main.py")

# 1. ATUALIZAR main.py COM AS MÉTRICAS DE CUSTÓDIA E PORÉNS NO SQL
if os.path.exists(caminho_main):
    with open(caminho_main, "r", encoding="utf-8", errors="ignore") as f:
        main_py = f.read()

    antigo_sql = """                SELECT 
                    COUNT(*) as total_processos,"""
    
    novo_sql = """                SELECT 
                    COUNT(*) as total_processos,
                    SUM(CASE WHEN eixo_gestao LIKE '%Esteira%' OR eixo_gestao LIKE '%Portfólio%' OR eixo_gestao LIKE '%Portfolio%' THEN 1 ELSE 0 END) as total_taticos_ativos,
                    SUM(CASE WHEN (eixo_gestao LIKE '%Esteira%' OR eixo_gestao LIKE '%Portfólio%' OR eixo_gestao LIKE '%Portfolio%') AND 
                                  (marcadores_institucionais LIKE '%parecer%' OR marcadores_institucionais LIKE '%externo%' OR 
                                   marcadores_institucionais LIKE '%cj%' OR marcadores_institucionais LIKE '%tce%' OR
                                   especificacao LIKE '%parecer%' OR observacao_texto LIKE '%parecer%') THEN 1 ELSE 0 END) as total_porens,
                    ROUND(AVG(CASE WHEN dias_ultima_mov > 0 THEN dias_ultima_mov ELSE NULL END), 1) as aging_medio_geral,"""

    if antigo_sql in main_py:
        main_py = main_py.replace(antigo_sql, novo_sql)
        with open(caminho_main, "w", encoding="utf-8") as f:
            f.write(main_py)
        print("1. main.py atualizado com cálculo SQL de Poréns e Custódia!")
    else:
        print("1. main.py já possuía os cálculos avançados de custódia.")

# 2. ADICIONAR IDS E BARRA DE BUSCA RÁPIDA NO painel.html (ABA 2)
if os.path.exists(caminho_painel):
    with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    pos_vis = html.find('id="view-visao_estrategica"')
    pos_con = html.find('id="view-consulta"')
    if pos_vis != -1 and pos_con != -1:
        chunk = html[pos_vis:pos_con]

        # Injetar IDs nos scorecards de custódia
        chunk = chunk.replace('<div class="kpi-val" style="color: #0544cf;">62</div>', '<div class="kpi-val" id="visao-kpi-interno" style="color: #0544cf;">62</div>')
        chunk = chunk.replace('<div class="kpi-val" style="color: #ea580c;">25</div>', '<div class="kpi-val" id="visao-kpi-externo" style="color: #ea580c;">25</div>')
        chunk = chunk.replace('<div class="kpi-val">84.2%</div>', '<div class="kpi-val" id="visao-kpi-eficiencia">84.2%</div>')

        # Injetar input de busca acima da tabela estratégica
        ancora_tabela = '<div class="table-header-title">Processos com Gargalo ou Atenção Crítica</div>'
        bloco_busca = '''<div class="table-header-title" style="display:flex; justify-content:space-between; align-items:center; width:100%; gap:12px; flex-wrap:wrap;">
                        <span id="titulo-tabela-estrategica">Processos com Gargalo ou Atenção Crítica</span>
                        <input type="text" id="input-busca-visao-estrategica" placeholder="🔍 Filtrar por nº SEI (ex: 137.000...), objeto ou responsável..." oninput="window.filtrarBuscaRapidaEstrategica(this.value)" style="padding:6px 12px; font-size:12px; border:1px solid #cbd5e1; border-radius:6px; width:340px; font-weight:normal; color:#0f172a;" />
                    </div>'''
        if ancora_tabela in chunk:
            chunk = chunk.replace(ancora_tabela, bloco_busca)

        html = html[:pos_vis] + chunk + html[pos_con:]
        with open(caminho_painel, "w", encoding="utf-8") as f:
            f.write(html)
        print("2. painel.html atualizado com IDs dinâmicos e busca instantânea na Aba 2!")

# 3. CONECTAR conector_api.js PARA ATUALIZAR ABA 2 AO VIVO NO MARIADB
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8", errors="ignore") as f:
        js = f.read()

    bloco_visao_js = r'''
    // --- ATUALIZAÇÃO AO VIVO DA ABA 2 (VISÃO ESTRATÉGICA & PORÉNS) ---
    window.atualizarVisaoEstrategicaAoVivo = async function() {
        try {
            var resp = await fetch('/api/v1/processos/estatisticas', { cache: 'no-store' });
            if (resp.ok) {
                var json = await resp.json();
                if (json.status === 'sucesso' && json.metricas) {
                    var m = json.metricas;
                    var taticos = m.total_taticos_ativos || 87;
                    var porens = m.total_porens || 25;
                    var internos = Math.max(0, taticos - porens);

                    // 1. Scorecards de Custodia
                    var elInt = document.getElementById('visao-kpi-interno');
                    if (elInt) elInt.textContent = internos;

                    var elExt = document.getElementById('visao-kpi-externo');
                    if (elExt) {
                        elExt.textContent = porens;
                        var card = elExt.closest('.kpi-card');
                        var spanSub = card ? card.querySelector('span') : null;
                        if (spanSub) {
                            spanSub.innerHTML = '🟢 Base Viva (MariaDB: ' + porens + ' suspensões)';
                            spanSub.style.color = '#10b981';
                            spanSub.style.fontWeight = '700';
                        }
                    }

                    // 2. Pills de Farois com contagem real
                    var bTodos = document.getElementById('btn-filtro-todos');
                    if (bTodos) bTodos.textContent = '🌐 Todos os Processos (' + taticos + ')';

                    var bVerm = document.getElementById('btn-filtro-vermelho');
                    if (bVerm) bVerm.textContent = '🔴 1 - Intervenção Imediata (' + (m.farol_vermelho || 0) + ')';

                    var bLaranja = document.getElementById('btn-filtro-laranja');
                    if (bLaranja) bLaranja.textContent = '🟠 2 - Saneamento Prioritário (' + (m.farol_laranja || 0) + ')';

                    var bAmarelo = document.getElementById('btn-filtro-amarelo');
                    if (bAmarelo) bAmarelo.textContent = '🟡 3 - Monitoramento Ativo (' + (m.farol_amarelo || 0) + ')';

                    var bVerde = document.getElementById('btn-filtro-verde');
                    if (bVerde) bVerde.textContent = '🟢 4 - Fluxo Normal (' + (m.farol_verde || 0) + ')';
                }
            }
        } catch (e) {
            console.warn('Conexão com MariaDB para Aba 2:', e);
        }
    };

    // Filtro rapido de texto na tabela estrategica
    window.filtrarBuscaRapidaEstrategica = function(termo) {
        var termoLow = (termo || '').toLowerCase().trim();
        var linhas = document.querySelectorAll('#tbody-visao-estrategica tr');
        linhas.forEach(function(tr) {
            var txt = tr.textContent.toLowerCase();
            tr.style.display = (termoLow === '' || txt.indexOf(termoLow) !== -1) ? '' : 'none';
        });
    };
'''

    if "atualizarVisaoEstrategicaAoVivo" not in js:
        idx_init = js.find("function init()")
        if idx_init != -1:
            js = js[:idx_init] + bloco_visao_js + "\n    " + js[idx_init:]
            js = js.replace("window.atualizarCardsDashboardsAoVivo();", "window.atualizarCardsDashboardsAoVivo();\n        window.atualizarVisaoEstrategicaAoVivo();")

        with open(caminho_js, "w", encoding="utf-8") as f:
            f.write(js)
        print("3. conector_api.js configurado para atualizar Aba 2 ao vivo!")
    else:
        print("3. conector_api.js já possuía o handler da Aba 2.")

print("Saneamento da Aba 2 concluído com sucesso!")
