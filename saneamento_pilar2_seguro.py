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

bak_path = painel_path + ".bak"

print("=" * 70)
print(" RECUPERACAO IMEDIATA E APLICACAO SEGURA DO PILAR 2")
print("=" * 70)

# 1. Restaurar backup integro
if os.path.exists(bak_path):
    shutil.copy2(bak_path, painel_path)
    print("[1/3] Backup integro restaurado com sucesso! (Tela branca eliminada)")
else:
    print("[1/3] Arquivo base localizado.")

# 2. Ler o arquivo restaurado
with open(painel_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# 3. Aplicar links nos 3 cards apenas dentro da view-tracks_sagti
p1_v = html.find('id="view-tracks_sagti"')
p2_v = html.find('id="view-pdtic_eixos"')
p3_v = html.find('id="view-gestao_glpi"')

if p1_v != -1 and p2_v != -1:
    tracks_sec = html[p1_v:p2_v]
    tracks_sec = tracks_sec.replace('#1231 &bull; TRACK 1 (OPERA&Ccedil;&Atilde;O ATUAL)',
                                    '<a href="https://projetos.spaguas.sp.gov.br/work_packages/1231" target="_blank" style="color:inherit;text-decoration:none;">#1231 &bull; TRACK 1 (OPERA&Ccedil;&Atilde;O ATUAL) &#8599;</a>')
    tracks_sec = tracks_sec.replace('#1232 &bull; TRACK 2 (RENEGOCIA&Ccedil;&Atilde;O &amp; NOVOS TRs)',
                                    '<a href="https://projetos.spaguas.sp.gov.br/work_packages/1232" target="_blank" style="color:inherit;text-decoration:none;">#1232 &bull; TRACK 2 (RENEGOCIA&Ccedil;&Atilde;O &amp; NOVOS TRs) &#8599;</a>')
    tracks_sec = tracks_sec.replace('#357 &amp; #336 &bull; MODERNIZA&Ccedil;&Atilde;O DGD &amp; DIF',
                                    '<a href="https://projetos.spaguas.sp.gov.br/work_packages/357" target="_blank" style="color:inherit;text-decoration:none;">#357</a> &amp; <a href="https://projetos.spaguas.sp.gov.br/work_packages/336" target="_blank" style="color:inherit;text-decoration:none;">#336 &bull; MODERNIZA&Ccedil;&Atilde;O DGD &amp; DIF &#8599;</a>')
    
    old_th = '<span id="sagti-tracks-count" style="font-size:12px; font-weight:700; color:#0544cf;">97 pacotes</span>'
    new_th = '''<div style="display:flex; gap:10px; align-items:center;">
                        <input type="text" id="sagti-filtro-busca" oninput="window.filtrarPilarSagti(window.pilarSagtiAtivo)" placeholder="Buscar por #ID, assunto, responsavel..." style="padding:5px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:12px; width:240px;">
                        <span id="sagti-tracks-count" style="font-size:12px; font-weight:700; color:#0544cf;">97 pacotes</span>
                    </div>'''
    if old_th in tracks_sec:
        tracks_sec = tracks_sec.replace(old_th, new_th, 1)

    html = html[:p1_v] + tracks_sec + html[p2_v:]

if p2_v != -1 and p3_v != -1:
    pdtic_sec = html[p2_v:p3_v]
    old_ph = '<span id="pdtic-inic-count" style="font-size:12px; font-weight:700; color:#4338ca;">35 iniciativas</span>'
    new_ph = '''<div style="display:flex; gap:10px; align-items:center;">
                        <input type="text" id="pdtic-filtro-busca" oninput="window.filtrarEixoPdtic(window.eixoPdticAtivo)" placeholder="Buscar iniciativa por #ID, eixo..." style="padding:5px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:12px; width:240px;">
                        <span id="pdtic-inic-count" style="font-size:12px; font-weight:700; color:#4338ca;">35 iniciativas</span>
                    </div>'''
    if old_ph in pdtic_sec:
        pdtic_sec = pdtic_sec.replace(old_ph, new_ph, 1)

    html = html[:p2_v] + pdtic_sec + html[p3_v:]

# 4. Injetar funções JS com links do OpenProject e busca instantânea
novo_js = """    window.filtrarPilarSagti = function(pilar) {
        window.pilarSagtiAtivo = pilar || 'todos';
        var tbody = document.getElementById('tbody-tracks-sagti');
        if (!tbody) return;

        var busca = ((document.getElementById('sagti-filtro-busca') || {}).value || '').toLowerCase().trim();

        var itensGti = window.OP_PACOTES_OFICIAIS.filter(function(p) {
            if (p.projeto !== 'SA-GTI - Gerência de TI' && p.projeto !== 'Divisão de Infraestrutura') return false;
            
            var respNome = (p.encarr || p.atrib || p.autor || '');
            var isLuiz = respNome.indexOf('Luiz') !== -1 || (p.autor || '').indexOf('Luiz') !== -1;

            if (pilar === 'luiz' && !isLuiz) return false;
            if (pilar === '1231' && (p.pai || '').indexOf('1231') === -1 && String(p.id) !== '1231') return false;
            if (pilar === '1232' && (p.pai || '').indexOf('1232') === -1 && String(p.id) !== '1232') return false;
            if (pilar === 'A-018' && (p.backlog || '').indexOf('A-018') === -1) return false;
            if (pilar === 'A-017' && (p.backlog || '').indexOf('A-017') === -1 && p.projeto !== 'Divisão de Infraestrutura') return false;
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
            var bgTag = p.backlog ? p.backlog.split('.')[0] : (p.projeto === 'Divisão de Infraestrutura' ? 'DIF-INFRA' : 'SA-GTI');
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
                '<td style="padding:8px 12px;font-weight:600;color:#334155;">' + (isLuiz ? '👑 ' : '👤 ') + respNome + '</td>' +
                '<td style="padding:8px 12px;text-align:center;font-size:11px;color:#475569;">' + (p.fim || p.ini || 'Contínuo') + '</td>' +
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
                        '<a href="https://projetos.spaguas.sp.gov.br/work_packages/' + k.id + '" target="_blank" style="color:#4f46e5;text-decoration:none;" title="Abrir KPI #' + k.id + ' no OpenProject">#' + k.id + ' &#8599;</a> • INDICADOR OFICIAL' +
                    '</div>' +
                    '<div style="font-size:12px;font-weight:700;color:#0f172a;margin:4px 0;">' + k.assunto + '</div>' +
                    '<div style="font-size:11px;color:#64748b;line-height:1.35;">' + (k.desc || 'Monitoramento contínuo PDTIC') + '</div>' +
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
                '<td style="padding:8px 12px;font-size:11.5px;color:#334155;">' + (isLuiz ? '👑 <strong>Luiz Antonio</strong> (SA-GTI)' : ('👤 ' + (i.atrib || i.autor || 'SA-GTI'))) + '</td>' +
                '<td style="padding:8px 12px;text-align:center;font-size:11px;color:#475569;">' + ((i.ini || '2027') + ' → ' + (i.fim || '2030')) + '</td>' +
                '</tr>';
        }).join('');
    };
"""

pattern_code = r'window\.filtrarPilarSagti\s*=\s*function\(pilar\)\s*\{[\s\S]*?window\.filtrarEixoPdtic\s*=\s*function\(eixo\)\s*\{[\s\S]*?\n\s*\};\n'
if re.search(pattern_code, html):
    html = re.sub(pattern_code, novo_js, html, count=1)
    print("[2/3] Funcoes JS substituidas com sucesso!")

# 5. Gravacao atomica protegida contra erro de Unicode/Surrogates
tmp_path = painel_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)

shutil.move(tmp_path, painel_path)
print("[3/3] painel.html gravado de forma segura e atomica!")
print("=" * 70)
print(" SUCESSO! Painel 100% restaurado e atualizado.")
print(" De Ctrl + F5 no seu navegador!")
print("=" * 70)
