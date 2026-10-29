# -*- coding: utf-8 -*-
import os
import re
import shutil

BASE_DIR = r"C:\Cockpit_GTI"
candidate_html = [
    os.path.join(BASE_DIR, "frontend", "painel.html"),
    os.path.join(BASE_DIR, "painel.html")
]
painel_path = next((p for p in candidate_html if os.path.exists(p)), None)

if not painel_path:
    painel_path = os.path.join(BASE_DIR, "frontend", "painel.html")

print("=" * 70)
print(" FILTRO ESTRITO DA MESA DE TRABALHO: VINCULO DIRETO COM O USUARIO")
print("=" * 70)

# 1. Backup de seguranca
shutil.copy2(painel_path, painel_path + ".bak")
print("[1/2] Backup criado com sucesso (.bak)!")

with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# 2. Injetar a funcao com filtro estrito de vinculo direto
novo_render_mesa = """window.renderizarMeusProcessosMesa = function() {
        const tbody = document.getElementById('tbody-meus-processos');
        if (!tbody) return;

        const selPerfil = document.getElementById('select-perfil-ativo');
        const perfilAtivo = selPerfil ? selPerfil.value : 'Super-Admin';

        // Carrega watchlist de fixados do usuario logado (salva no localStorage)
        let fixados = [];
        try {
            const rawFix = localStorage.getItem('sagti_fixados');
            if (rawFix === null) {
                fixados = ['137.00010608/2025-63', '137.00000119/2026-84'];
                localStorage.setItem('sagti_fixados', JSON.stringify(fixados));
            } else {
                fixados = JSON.parse(rawFix || '[]');
            }
        } catch(e) { fixados = []; }

        const procsBase = (typeof PROCESSOS !== 'undefined' && Array.isArray(PROCESSOS)) ? PROCESSOS : [];

        // Filtro ESTRITO: Somente processos com vinculo DIRETO com o usuario logado
        let meusProcessos = [];

        if (perfilAtivo === 'Super-Admin' || perfilAtivo === 'Gestor') {
            // Luiz Seixeiro: Apenas processos com responsavel nominal a ele OU expressamente favoritados com estrela
            meusProcessos = procsBase.filter(p => {
                const idProc = p.ID_Processo || p.id || '';
                const resp = (p.Responsavel_Tecnico || p.responsavel || '').toLowerCase();
                const isFixado = fixados.includes(idProc);
                const isLuiz = resp.includes('luiz') || resp.includes('seixeiro');

                return isFixado || isLuiz;
            });
        } else if (perfilAtivo === 'Analista') {
            // Analistas: Apenas processos atribuidos nominalmente a Marcos/Diego + fixados
            meusProcessos = procsBase.filter(p => {
                const idProc = p.ID_Processo || p.id || '';
                const resp = (p.Responsavel_Tecnico || p.responsavel || '').toLowerCase();
                return resp.includes('marcos') || resp.includes('diego') || fixados.includes(idProc);
            });
        } else {
            // Demandante: Somente os que ele fixou na sua propria watchlist
            meusProcessos = procsBase.filter(p => fixados.includes(p.ID_Processo || p.id));
        }

        // Atualiza Scorecards dinâmicos EXCLUSIVAMENTE sobre os processos vinculados ao usuário
        const elCustodia = document.getElementById('mesa-kpi-custodia');
        if (elCustodia) elCustodia.innerText = String(meusProcessos.length);

        const criticos = meusProcessos.filter(p => (p.Faixa_Aging || '').includes('Crítico') || parseInt(p.Dias_Ultima_Mov || 0, 10) > 90).length;
        const elCriticos = document.getElementById('mesa-kpi-criticos');
        if (elCriticos) elCriticos.innerText = String(criticos);

        const porens = meusProcessos.filter(p => (p.Status_Kanban || p.Status_OpenProject || '').includes('CJ') || (p.Marcadores_Institucionais || '').includes('Suspensão') || (p.Farol_Criticidade || '').includes('Porem') || (p.Farol_Criticidade || '').includes('Porém')).length;
        const elPorens = document.getElementById('mesa-kpi-porens');
        if (elPorens) elPorens.innerText = String(porens);

        if (meusProcessos.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 28px; color: #64748b;">
                        <span style="font-size: 26px; display: block; margin-bottom: 6px;">📂</span>
                        <strong style="color:#0f2d59; font-size:13px;">Nenhum processo diretamente vinculado à sua mesa no momento.</strong><br>
                        <span style="font-size: 11.5px;">Para acompanhar processos aqui, clique na estrela ⭐ ao lado de qualquer processo no <strong>Acervo SEI</strong> ou na <strong>Visão Estratégica</strong>.</span>
                    </td>
                </tr>
            `;
            return;
        }

        let htmlTrs = '';
        meusProcessos.forEach(p => {
            const idProc = p.ID_Processo || p.id || '';
            const isFixado = fixados.includes(idProc);
            let pillAgingClass = 'pill-green';
            if ((p.Faixa_Aging || '').includes('Crítico')) pillAgingClass = 'pill-red';
            else if ((p.Faixa_Aging || '').includes('Atenção')) pillAgingClass = 'pill-yellow';
            else if ((p.Faixa_Aging || '').includes('Alerta')) pillAgingClass = 'pill-orange';

            const espTxt = p.Especificacao || p.especificacao || p.tipo || 'Demanda TIC';

            htmlTrs += `
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="text-align: center;">
                        <button onclick="toggleFixado('${idProc}'); window.renderizarMeusProcessosMesa();" style="background: none; border: none; cursor: pointer; font-size: 15px;" title="Fixar/Desafixar da Watchlist">
                            ${isFixado ? '⭐' : '☆'}
                        </button>
                    </td>
                    <td style="font-family: monospace; font-weight: 700;">
                        <a href="javascript:void(0)" onclick="abrirDetalhesProcesso('${idProc}')" style="color: #0056d2; text-decoration: none;" title="Abrir Dossiê 360°">${idProc}</a>
                    </td>
                    <td style="max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 12px; color: #1e293b;" title="${espTxt}">${espTxt}</td>
                    <td><span class="pill-tag pill-blue" style="font-size: 11px;">${p.Status_OpenProject || p.Status_Kanban || 'Em Andamento'}</span></td>
                    <td><span class="pill-tag ${pillAgingClass}" style="font-size: 11px;">${p.Faixa_Aging || 'Normal'} (${p.Dias_Ultima_Mov || 0}d)</span></td>
                    <td style="text-align: center; white-space: nowrap;">
                        <button class="btn btn-primary" onclick="abrirDetalhesProcesso('${idProc}')" style="background: #0056d2; border-color: #0056d2; padding: 4px 10px; font-size: 11px; font-weight: 700; border-radius: 4px; cursor: pointer;" title="Abrir Dossiê com Timeline">
                            🔍 Dossiê
                        </button>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = htmlTrs;
    };"""

pattern_func_mesa = r'window\.renderizarMeusProcessosMesa\s*=\s*function\(\)\s*\{[\s\S]*?tbody\.innerHTML\s*=\s*htmlTrs;\s*\};'
if re.search(pattern_func_mesa, html):
    html = re.sub(pattern_func_mesa, novo_render_mesa, html, count=1)
    print("[2/2] Funcao renderizarMeusProcessosMesa atualizada com vinculo estrito!")

# Gravacao atomica protegida
tmp_path = painel_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)

shutil.move(tmp_path, painel_path)
print("=" * 70)
print(" SUCESSO! Mesa de Trabalho agora exibe apenas a sua carteira vinculada.")
print(" De Ctrl + F5 no navegador!")
print("=" * 70)
