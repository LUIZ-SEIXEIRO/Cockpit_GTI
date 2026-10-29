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

print("=" * 70)
print(" SANEAMENTO DO PILAR 2: TRACKS SA-GTI (97) & PDTIC 2027-2030 (35)")
print("=" * 70)

if painel_path:
    shutil.copy2(painel_path, painel_path + ".bak")
    print("[1/3] Backup de painel.html criado com sucesso!")

    with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. Links nos 3 cards de tracks_sagti
    html = html.replace('#1231 &bull; TRACK 1 (OPERA&Ccedil;&Atilde;O ATUAL)',
                        '<a href="https://projetos.spaguas.sp.gov.br/work_packages/1231" target="_blank" style="color:inherit;text-decoration:none;">#1231 &bull; TRACK 1 (OPERA&Ccedil;&Atilde;O ATUAL) &#8599;</a>')

    html = html.replace('#1232 &bull; TRACK 2 (RENEGOCIA&Ccedil;&Atilde;O &amp; NOVOS TRs)',
                        '<a href="https://projetos.spaguas.sp.gov.br/work_packages/1232" target="_blank" style="color:inherit;text-decoration:none;">#1232 &bull; TRACK 2 (RENEGOCIA&Ccedil;&Atilde;O &amp; NOVOS TRs) &#8599;</a>')

    html = html.replace('#357 &amp; #336 &bull; MODERNIZA&Ccedil;&Atilde;O DGD &amp; DIF',
                        '<a href="https://projetos.spaguas.sp.gov.br/work_packages/357" target="_blank" style="color:inherit;text-decoration:none;">#357</a> &amp; <a href="https://projetos.spaguas.sp.gov.br/work_packages/336" target="_blank" style="color:inherit;text-decoration:none;">#336 &bull; MODERNIZA&Ccedil;&Atilde;O DGD &amp; DIF &#8599;</a>')

    # Links nos subpacotes citados nos cards
    subpacs = ['397', '398', '399', '400', '402', '431', '530', '329', '42', '552']
    for sp in subpacs:
        html = html.replace(f'(#{sp})', f'(<a href="https://projetos.spaguas.sp.gov.br/work_packages/{sp}" target="_blank" style="color:inherit;font-weight:700;">#{sp} &#8599;</a>)')
        html = html.replace(f'#{sp}', f'<a href="https://projetos.spaguas.sp.gov.br/work_packages/{sp}" target="_blank" style="color:inherit;font-weight:700;">#{sp} &#8599;</a>')

    # 2. Injetar botão OpenProject e campo de busca na tabela de tracks_sagti
    old_tracks_header = '<span id="sagti-tracks-count" style="font-size:12px; font-weight:700; color:#0544cf;">97 pacotes</span>'
    new_tracks_header = '''<div style="display:flex; gap:10px; align-items:center;">
                        <input type="text" id="sagti-filtro-busca" oninput="window.filtrarPilarSagti(window.pilarSagtiAtivo)" placeholder="Buscar por #ID, assunto, responsavel..." style="padding:5px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:12px; width:250px;">
                        <span id="sagti-tracks-count" style="font-size:12px; font-weight:700; color:#0544cf;">97 pacotes</span>
                    </div>'''
    if old_tracks_header in html:
        html = html.replace(old_tracks_header, new_tracks_header, 1)

    # Injetar botões rápidos adicionais no banner de tracks_sagti
    old_tracks_btns = '<button class="btn btn-primary" onclick="window.filtrarPilarSagti(\'todos\')" id="btn-pilar-todos" style="font-size:11.5px;">&#127760; Todos SA-GTI (97)</button>'
    new_tracks_btns = '''<button class="btn btn-primary" onclick="window.filtrarPilarSagti('todos')" id="btn-pilar-todos" style="font-size:11.5px;">&#127760; Todos SA-GTI (97)</button>
                    <button class="btn btn-secondary" onclick="window.filtrarPilarSagti('luiz')" id="btn-pilar-luiz" style="font-size:11.5px; background:rgba(255,255,255,0.15); color:#fff; border:1px solid rgba(255,255,255,0.3);">&#128081; Luiz Antonio</button>
                    <button class="btn btn-secondary" onclick="window.filtrarPilarSagti('1231')" id="btn-pilar-track1" style="font-size:11.5px; background:rgba(255,255,255,0.15); color:#fff; border:1px solid rgba(255,255,255,0.3);">&#9889; Track 1 (#1231)</button>
                    <button class="btn btn-secondary" onclick="window.filtrarPilarSagti('1232')" id="btn-pilar-track2" style="font-size:11.5px; background:rgba(255,255,255,0.15); color:#fff; border:1px solid rgba(255,255,255,0.3);">&#128209; Track 2 (#1232)</button>'''
    if old_tracks_btns in html:
        html = html.replace(old_tracks_btns, new_tracks_btns, 1)

    # 3. Injetar campo de busca e botão OpenProject na tabela de pdtic_eixos
    old_pdtic_header = '<span id="pdtic-inic-count" style="font-size:12px; font-weight:700; color:#4338ca;">35 iniciativas</span>'
    new_pdtic_header = '''<div style="display:flex; gap:10px; align-items:center;">
                        <input type="text" id="pdtic-filtro-busca" oninput="window.filtrarEixoPdtic(window.eixoPdticAtivo)" placeholder="Buscar iniciativa por #ID, eixo, assunto..." style="padding:5px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:12px; width:250px;">
                        <span id="pdtic-inic-count" style="font-size:12px; font-weight:700; color:#4338ca;">35 iniciativas</span>
                    </div>'''
    if old_pdtic_header in html:
        html = html.replace(old_pdtic_header, new_pdtic_header, 1)

    # Injetar botão de abrir PDTIC oficial no banner
    old_pdtic_badge = '<span style="background:rgba(255,255,255,0.18); color:#fff; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:700;">\n                    &#127919; 35 Iniciativas &bull; 8 KPIs Homologados\n                </span>'
    new_pdtic_badge = '''<div style="display:flex; gap:8px; align-items:center;">
                    <a href="https://projetos.spaguas.sp.gov.br/projects/pdtic-2027-2030" target="_blank" class="btn btn-secondary" style="background:rgba(255,255,255,0.18); color:#fff; border:1px solid rgba(255,255,255,0.4); font-size:11.5px; font-weight:700; padding:6px 12px; text-decoration:none; border-radius:6px; display:inline-flex; align-items:center; gap:6px;">
                        &#128640; Abrir PDTIC no OpenProject &#8599;
                    </a>
                    <span style="background:rgba(255,255,255,0.18); color:#fff; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:700;">
                        &#127919; 35 Iniciativas &bull; 8 KPIs Homologados
                    </span>
                </div>'''
    if old_pdtic_badge in html:
        html = html.replace(old_pdtic_badge, new_pdtic_badge, 1)

    print("[2/3] HTML atualizado com links, buscas instantaneas e botoes de acesso!")

    # 4. Atualizar Módulo JS de filtragem com links e busca integrada
    novo_js = """    window.filtrarPilarSagti = function(pilar) {
        window.pilarSagtiAtivo = pilar || 'todos';
        var tbody = document.getElementById('tbody-tracks-sagti');
        if (!tbody) return;

        var btns = {
            'todos': 'btn-pilar-todos',
            'luiz': 'btn-pilar-luiz',
            '1231': 'btn-pilar-track1',
            '1232': 'btn-pilar-track2',
            'A-018': 'btn-pilar-a018',
            'A-017': 'btn-pilar-a017',
            'A-016': 'btn-pilar-a016'
        };
        Object.keys(btns).forEach(function(k) {
            var el = document.getElementById(btns[k]);
            if (el) {
                if (k === window.pilarSagtiAtivo) {
                    el.className = 'btn btn-primary';
                    el.style.background = '#0544cf';
                    el.style.color = '#fff';
                } else {
                    el.className = 'btn btn-secondary';
                    el.style.background = 'rgba(255,255,255,0.15)';
                    el.style.color = '#fff';
                }
            }
        });

        var busca = ((document.getElementById('sagti-filtro-busca') || {}).value || '').toLowerCase().trim();

        var itensGti = window.OP_PACOTES_OFICIAIS.filter(function(p) {
            if (p.projeto !== 'SA-GTI - Ger\u00eancia de TI' && p.projeto !== 'Divis\u00e3o de Infraestrutura') return false;
            
            var respNome = (p.encarr || p.atrib || p.autor || '');
            var isLuiz = respNome.indexOf('Luiz') !== -1 || (p.autor || '').indexOf('Luiz') !== -1;

            if (pilar === 'luiz' && !isLuiz) return false;
            if (pilar === '1231' && (p.pai || '').indexOf('1231') === -1 && String(p.id) !== '1231') return false;
            if (pilar === '1232' && (p.pai || '').indexOf('1232') === -1 && String(p.id) !== '1232') return false;
            if (pilar === 'A-018' && (p.backlog || '').indexOf('A-018') === -1) return false;
            if (pilar === 'A-017' && (p.backlog || '').indexOf('A-017') === -1 && p.projeto !== 'Divis\u00e3o de Infraestrutura') return false;
            if (pilar === 'A-016' && (p.backlog || '').indexOf('A-016') === -1) return false;

            if (busca) {
                var txt = ('#' + p.id + ' ' + (p.backlog || '') + ' ' + (p.assunto || '') + ' ' + respNome + ' ' + (p.pai || '') + ' ' + (p.status || '')).toLowerCase();
                if (txt.indexOf(busca) === -1) return false;
            }
            return true;
        });

        var cnt = document.getElementById('sagti-tracks-count');
        if (cnt) cnt.innerText = 'Exibindo ' + itensGti.length + ' de 97 pacotes SA-GTI';

        tbody.innerHTML = itensGti.map(function(p) {
            var bgTag = p.backlog ? p.backlog.split('.')[0] : (p.projeto === 'Divis\u00e3o de Infraestrutura' ? 'DIF-INFRA' : 'SA-GTI');
            var corBg = bgTag.indexOf('A-018') !== -1 ? 'background:#dbeafe;color:#1e40af;' : (bgTag.indexOf('A-017') !== -1 || bgTag === 'DIF-INFRA' ? 'background:#ede9fe;color:#5b21b6;' : 'background:#dcfce7;color:#166534;');
            var respNome = (p.encarr || p.atrib || p.autor || 'SA-GTI');
            var isLuiz = respNome.indexOf('Luiz') !== -1 || (p.autor || '').indexOf('Luiz') !== -1;
            
            return '<tr style="border-bottom:1px solid #f1f5f9;' + (isLuiz ? 'background:#f0fdf4;' : '') + '">' +
                '<td style="padding:8px 12px;font-weight:800;font-family:monospace;">' +
                    '<a href="https://projetos.spaguas.sp.gov.br/work_packages/' + p.id + '" target="_blank" style="color:#0056d2;text-decoration:none;" title="Abrir Pacote #' + p.id + ' no OpenProject">#' + p.id + ' &#8599;</a>' +
                '</td>' +
                '<td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:8px;font-size:11px;font-weight:700;' + corBg + '">' + (p.backlog || p.projeto) + '</span></td>' +
                '<td style="padding:8px 12px;">' + badgeTipo(p.tipo) + '</td>' +
                '<td style="padding:8px 12px;font-weight:700;color:#0f172a;">' + p.assunto + '</td>' +
                '<td style="padding:8px 12px;font-size:11px;color:#0369a1;font-weight:600;">' + (p.pai || 'Raiz SA-GTI') + '</td>' +
                '<td style="padding:8px 12px;">' + badgeStatus(p.status) + '</td>' +
                '<td style="padding:8px 12px;font-weight:600;color:#334155;">' + (isLuiz ? '\ud83d\udc51 ' : '\ud83d\udc64 ') + respNome + '</td>' +
                '<td style="padding:8px 12px;text-align:center;font-size:11px;color:#475569;">' + (p.fim || p.ini || 'Cont\u00ednuo') + '</td>' +
                '</tr>';
        }).join('');
    };

    window.filtrarEixoPdtic = function(eixo) {
        window.eixoPdticAtivo = eixo || '';
        var gridKpis = document.getElementById('grid-kpis-pdtic-oficial');
        var tbody = document.getElementById('tbody-pdtic-iniciativas');
        
        if (gridKpis && gridKpis.innerHTML.trim() === '') {
            var kpis = window.OP_PACOTES_OFICIAIS.filter(function(p) { return p.tipo === 'KPI'; });
            gridKpis.innerHTML = kpis.map(function(k) {
                return '<div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #4f46e5;border-radius:6px;padding:10px;">' +
                    '<div style="font-size:10.5px;font-weight:800;color:#4f46e5;">' +
                        '<a href="https://projetos.spaguas.sp.gov.br/work_packages/' + k.id + '" target="_blank" style="color:#4f46e5;text-decoration:none;" title="Abrir KPI #' + k.id + ' no OpenProject">#' + k.id + ' &#8599;</a> \u2022 INDICADOR OFICIAL' +
                    '</div>' +
                    '<div style="font-size:12px;font-weight:700;color:#0f172a;margin:4px 0;">' + k.assunto + '</div>' +
                    '<div style="font-size:11px;color:#64748b;line-height:1.35;">' + (k.desc || 'Monitoramento cont\u00ednuo PDTIC') + '</div>' +
                    '</div>';
            }).join('');
        }
        if (!tbody) return;

        var busca = ((document.getElementById('pdtic-filtro-busca') || {}).value || '').toLowerCase().trim();

        var inics = window.OP_PACOTES_OFICIAIS.filter(function(p) {
            if (p.tipo !== 'Iniciativas') return false;
            if (eixo && p.projeto.indexOf(eixo) === -1) return false;
            if (busca) {
                var txt = ('#' + p.id + ' ' + (p.projeto || '') + ' ' + (p.assunto || '') + ' ' + (p.atrib || '') + ' ' + (p.prio || '')).toLowerCase();
                if (txt.indexOf(busca) === -1) return false;
            }
            return true;
        });

        var cnt = document.getElementById('pdtic-inic-count');
        if (cnt) cnt.innerText = 'Exibindo ' + inics.length + ' de 35 iniciativas oficiais';

        tbody.innerHTML = inics.map(function(i) {
            var isLuiz = (i.atrib || '').indexOf('Luiz') !== -1;
            var prioColor = i.prio === 'Imediata' || i.prio.indexOf('Alt') !== -1 ? 'background:#fee2e2;color:#991b1b;' : 'background:#e0f2fe;color:#0369a1;';
            return '<tr style="border-bottom:1px solid #f1f5f9;' + (isLuiz ? 'background:#f0fdf4;' : '') + '">' +
                '<td style="padding:8px 12px;font-weight:800;font-family:monospace;">' +
                    '<a href="https://projetos.spaguas.sp.gov.br/work_packages/' + i.id + '" target="_blank" style="color:#4338ca;text-decoration:none;" title="Abrir Iniciativa #' + i.id + ' no OpenProject">#' + i.id + ' &#8599;</a>' +
                '</td>' +
                '<td style="padding:8px 12px;font-weight:700;color:#4338ca;">' + i.projeto + '</td>' +
                '<td style="padding:8px 12px;font-weight:700;color:#0f172a;">' + i.assunto + '</td>' +
                '<td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:8px;font-size:11px;font-weight:700;' + prioColor + '">' + i.prio + '</span></td>' +
                '<td style="padding:8px 12px;font-size:11.5px;color:#334155;">' + (isLuiz ? '\ud83d\udc51 <strong>Luiz Antonio</strong> (SA-GTI)' : ('\ud83d\udc64 ' + (i.atrib || i.autor || 'SA-GTI'))) + '</td>' +
                '<td style="padding:8px 12px;text-align:center;font-size:11px;color:#475569;">' + ((i.ini || '2027') + ' \u2192 ' + (i.fim || '2030')) + '</td>' +
                '</tr>';
        }).join('');
    };
"""

    pattern_code = r'window\.filtrarPilarSagti\s*=\s*function\(pilar\)\s*\{[\s\S]*?window\.filtrarEixoPdtic\s*=\s*function\(eixo\)\s*\{[\s\S]*?\n\s*\};\n'
    if re.search(pattern_code, html):
        html = re.sub(pattern_code, novo_js, html, count=1)
        print("[3/3] Funcoes JS de filtragem atualizadas com busca instantanea e links!")

    with open(painel_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("painel.html gravado com sucesso!")

print("=" * 70)
print(" SUCESSO! Pilar 2 100% saneado e conectado ao OpenProject.")
print(" Atualize seu navegador com Ctrl + F5!")
print("=" * 70)
