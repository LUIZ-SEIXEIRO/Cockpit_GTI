# -*- coding: utf-8 -*-
import os

frontend_dir = os.path.join(os.getcwd(), "frontend")
caminho_painel = os.path.join(frontend_dir, "painel.html")
caminho_js = os.path.join(frontend_dir, "conector_api.js")

# 1. ATIVAR CLIQUES E BOTÃO DE DOSSIÊ NA TABELA DA ABA 2 (painel.html)
if os.path.exists(caminho_painel):
    with open(caminho_painel, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Torna o ID_Processo clicavel com link estilizado
    td_antigo = '<td style="font-family: monospace; font-weight: 700; color: #0544cf;">${p.ID_Processo}</td>'
    td_novo = '<td style="font-family: monospace; font-weight: 700;"><a href="javascript:void(0)" onclick="window.abrirDetalhesProcesso(\'${p.ID_Processo}\')" style="color: #0544cf; text-decoration: underline; cursor: pointer;" title="Clique para abrir Dossiê e Timeline">${p.ID_Processo}</a></td>'

    # Adiciona o botao de Dossie na coluna de acoes
    btn_antigo = '<button class="btn btn-secondary" onclick="window.abrirModalCheckpointComProc(\'${p.ID_Processo}\')" style="padding: 3px 8px; font-size: 11px;">Notificar</button>'
    btn_novo = '<button class="btn btn-primary" onclick="window.abrirDetalhesProcesso(\'${p.ID_Processo}\')" style="padding: 3px 8px; font-size: 11px; margin-right: 4px; background: #0544cf; border-color: #0544cf; cursor: pointer;">🔍 Dossiê</button><button class="btn btn-secondary" onclick="window.abrirModalCheckpointComProc(\'${p.ID_Processo}\')" style="padding: 3px 8px; font-size: 11px;">Notificar</button>'

    alterado = False
    if td_antigo in html:
        html = html.replace(td_antigo, td_novo)
        alterado = True

    if btn_antigo in html:
        html = html.replace(btn_antigo, btn_novo)
        alterado = True

    if alterado:
        with open(caminho_painel, "w", encoding="utf-8") as f:
            f.write(html)
        print("1. Links e botão '🔍 Dossiê' ativados na tabela do painel.html!")
    else:
        print("1. Tabela já possuía os links de dossiê.")

# 2. DECLARAR ABRIR DETALHES PROCESSO E TIMELINE NO ESCOPO GLOBAL (conector_api.js)
if os.path.exists(caminho_js):
    with open(caminho_js, "r", encoding="utf-8", errors="ignore") as f:
        js = f.read()

    bloco_modal_timeline = r'''
    // --- MOTOR GLOBAL DO MODAL DE PROCESSO, TIMELINE E DOSSIÊ ---
    window.abrirDetalhesProcesso = function (idProcesso) {
        if (!idProcesso) return;
        var lista = window.PROCESSOS || (typeof PROCESSOS !== 'undefined' ? PROCESSOS : []);
        var p = lista.find(function (item) {
            return (item.ID_Processo === idProcesso || item.id_processo === idProcesso || item.id === idProcesso);
        });
        if (!p) {
            console.warn('Processo não localizado na memória:', idProcesso);
            return;
        }

        // Gera a timeline e governança institucional
        var timelineHtml = (typeof window.gerarTimelineProcessualHtml === 'function')
            ? window.gerarTimelineProcessualHtml(p)
            : '';

        var modTit = document.getElementById('modal-titulo');
        if (modTit) modTit.innerText = 'Processo SEI: ' + (p.ID_Processo || p.id_processo);

        var modCont = document.getElementById('modal-conteudo');
        if (modCont) {
            var idP = p.ID_Processo || p.id_processo;
            modCont.innerHTML = timelineHtml + [
                '<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; padding: 12px 14px; border-radius: 6px; margin: 14px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">',
                '    <div>',
                '        <strong style="color: #14532d; font-size: 12px;">🌐 Consulta em Tempo Real no Site Oficial (PNCP / Compras SP / SEI)</strong>',
                '        <div style="font-size: 11px; color: #15803d; margin-top: 2px;">Verifique publicações da Lei 14.133, andamento no SEI-SP ou atas homologadas no PNCP.</div>',
                '    </div>',
                '    <div style="display: flex; gap: 8px;">',
                '        <button class="btn btn-primary" onclick="window.consultarProcessoAoVivoPNCP(\'' + idP + '\')" style="background: #01a75f; border-color: #01a75f; font-size: 11px; padding: 5px 12px; font-weight: 700; cursor: pointer;">🔍 Checar no Site Oficial</button>',
                '        <a href="https://pncp.gov.br/app/editais?q=' + encodeURIComponent(idP) + '" target="_blank" class="btn btn-secondary" style="font-size: 11px; padding: 5px 10px; text-decoration: none; color: #002d5a; font-weight: 600;">Abrir PNCP ↗</a>',
                '        <a href="https://sei.sp.gov.br/sei/controlador_externo.php?acao=usuario_externo_consultar&id_orgao_acesso_externo=0" target="_blank" class="btn btn-secondary" style="font-size: 11px; padding: 5px 10px; text-decoration: none; color: #002d5a; font-weight: 600;">Abrir SEI-SP ↗</a>',
                '    </div>',
                '</div>',
                '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; font-size: 12px;">',
                '    <div><strong>Eixo de Gestão:</strong> ' + (p.Eixo_Gestao || p.eixo_gestao || '-') + '</div>',
                '    <div><strong>Bucket OpenProject:</strong> ' + (p.Bucket_OpenProject || p.bucket_openproject || '-') + '</div>',
                '    <div><strong>Status OpenProject:</strong> ' + (p.Status_OpenProject || p.status_openproject || '-') + '</div>',
                '    <div><strong>Farol Criticidade:</strong> ' + (p.Farol_Criticidade || p.farol_criticidade || '-') + '</div>',
                '    <div><strong>Faixa Aging:</strong> ' + (p.Faixa_Aging || p.faixa_aging || '-') + ' (' + (p.Dias_Ultima_Mov || p.dias_ultima_mov || 0) + ' dias sem mov.)</div>',
                '    <div><strong>Classificação de Risco:</strong> ' + (p.Classificacao_Risco || p.classificacao_risco || '-') + '</div>',
                '    <div><strong>Responsável Técnico:</strong> ' + (p.Responsavel_Tecnico || p.responsavel_tecnico || 'Não atribuído') + '</div>',
                '    <div><strong>Tipo de Processo:</strong> ' + (p.Tipo_Processo || p.tipo_processo || '-') + '</div>',
                '</div>',
                '<div style="margin-bottom: 12px;">',
                '    <strong>Especificação da Demanda:</strong>',
                '    <p style="background: #f1f5f9; padding: 10px; border-radius: 6px; margin-top: 4px; font-size: 12px; line-height: 1.45;">' + (p.Especificacao || p.especificacao || '-') + '</p>',
                '</div>',
                '<div style="margin-bottom: 12px;">',
                '    <strong>Observações / Contexto:</strong>',
                '    <p style="background: #f8fafc; padding: 10px; border-radius: 6px; margin-top: 4px; border: 1px solid #e2e8f0; font-size: 12px; line-height: 1.45;">' + (p.Observacao_Texto || p.observacao_texto || 'Sem observações adicionais registradas.') + '</p>',
                '</div>'
            ].join('\n');
        }

        var modEl = document.getElementById('modal-processo');
        if (modEl) {
            modEl.style.display = 'flex';
            modEl.style.position = 'fixed';
            modEl.style.inset = '0';
            modEl.style.zIndex = '99999';
            modEl.style.background = 'rgba(15, 23, 42, 0.65)';
            modEl.style.alignItems = 'center';
            modEl.style.justifyContent = 'center';
            modEl.style.padding = '20px';
        }
    };

    window.fecharModalProcesso = function () {
        var modEl = document.getElementById('modal-processo');
        if (modEl) modEl.style.display = 'none';
    };
'''

    if "window.abrirDetalhesProcesso" not in js:
        idx_init = js.find("function init()")
        if idx_init != -1:
            js = js[:idx_init] + bloco_modal_timeline + "\n    " + js[idx_init:]
        with open(caminho_js, "w", encoding="utf-8") as f:
            f.write(js)
        print("2. conector_api.js atualizado com o modal global de Timeline!")
    else:
        print("2. conector_api.js já possuía o motor global do modal.")

print("Timeline e Dossiê restaurados com sucesso!")
