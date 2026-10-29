# -*- coding: utf-8 -*-
import os

caminho_js = os.path.join(os.getcwd(), "frontend", "conector_api.js")
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8", errors="ignore") as f:
        codigo = f.read()

    bloco_conexao_banco = r'''
    // --- CONEXÃO AO VIVO COM A BASE DE PROCESSOS DO MARIADB ---
    window.atualizarCardsDashboardsAoVivo = async function() {
        try {
            var resp = await fetch('/api/v1/processos/estatisticas', { cache: 'no-store' });
            if (resp.ok) {
                var json = await resp.json();
                if (json.status === 'sucesso' && json.metricas) {
                    var m = json.metricas;
                    
                    // 1. Total de Processos
                    var elTotal = document.getElementById('kpi-val-acervo-total');
                    if (elTotal) {
                        elTotal.textContent = m.total_processos || 0;
                        var card = elTotal.closest('.kpi-card');
                        var spanSub = card ? card.querySelector('span') : null;
                        if (spanSub) {
                            spanSub.innerHTML = '🟢 Base Viva (MariaDB &amp; SEI-SP)';
                            spanSub.style.color = '#10b981';
                            spanSub.style.fontWeight = '700';
                        }
                    }

                    // 2. Farois de Criticidade (Apurados via SQL)
                    var elInt = document.getElementById('kpi-val-intervencao');
                    if (elInt) elInt.textContent = m.farol_vermelho || 0;

                    var elSan = document.getElementById('kpi-val-saneamento');
                    if (elSan) elSan.textContent = m.farol_laranja || 0;

                    var elMon = document.getElementById('kpi-val-monitoramento');
                    if (elMon) elMon.textContent = m.farol_amarelo || 0;

                    var elFlux = document.getElementById('kpi-val-fluxo-normal');
                    if (elFlux) elFlux.textContent = m.farol_verde || 0;

                    // 3. Sub-totais por Eixo de Gestao
                    var elRot = document.getElementById('kpi-val-rotina');
                    if (elRot) elRot.textContent = (m.total_rotina || 0) + ' processos';
                }
            }
        } catch (e) {
            console.warn('Conexao viva com MariaDB processos_sei pendente:', e);
        }
    };
'''

    # Injeta a funcao e acopla no init()
    if "atualizarCardsDashboardsAoVivo" not in codigo:
        idx_init = codigo.find("function init()")
        if idx_init != -1:
            codigo = codigo[:idx_init] + bloco_conexao_banco + "\n    " + codigo[idx_init:]
            # Adiciona a chamada no corpo de init()
            codigo = codigo.replace("atualizarTelemetria();", "atualizarTelemetria();\n        window.atualizarCardsDashboardsAoVivo();")

        with open(caminho_js, "w", encoding="utf-8") as f:
            f.write(codigo)
        print("conector_api.js conectado ao vivo com MariaDB processos_sei!")
    else:
        print("conector_api.js ja possui a conexao ao vivo.")
