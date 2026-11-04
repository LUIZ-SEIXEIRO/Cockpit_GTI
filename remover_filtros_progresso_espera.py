# -*- coding: utf-8 -*-
import os, sys, re

print("=" * 70)
print(" REMOÇÃO DOS FILTROS RÁPIDOS 'EM PROGRESSO' E 'EM ESPERA'")
print(" Tela: Portfólio OpenProject (500 Pacotes)")
print("=" * 70)

caminhos = [
    os.path.join(os.getcwd(), "frontend", "painel.html"),
    os.path.join(os.getcwd(), "painel.html")
]

for caminho in caminhos:
    if not os.path.exists(caminho):
        continue

    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # 1. Remover os dois botões no HTML
    pattern_botoes = r'\s*<button[^>]*id="btn-op-progresso"[^>]*>.*?</button>\s*<button[^>]*id="btn-op-espera"[^>]*>.*?</button>'
    html_mod = re.sub(pattern_botoes, '', html, count=1)

    # Caso estejam separados
    if 'id="btn-op-progresso"' in html_mod:
        html_mod = re.sub(r'\s*<button[^>]*id="btn-op-progresso"[^>]*>.*?</button>', '', html_mod, count=1)
    if 'id="btn-op-espera"' in html_mod:
        html_mod = re.sub(r'\s*<button[^>]*id="btn-op-espera"[^>]*>.*?</button>', '', html_mod, count=1)

    # 2. Injetar a lógica JS atualizada para os 3 botões restantes de escopo
    js_limpo = '''
<script>
(function() {
    window.opModoRapidoAtivo = 'todos';

    window.filtrarModoRapidoOP = function(modo) {
        window.opModoRapidoAtivo = modo || 'todos';

        var ids = ['btn-op-todos', 'btn-op-sagti', 'btn-op-pdtic'];
        var mapa = {
            'todos': 'btn-op-todos',
            'sagti': 'btn-op-sagti',
            'pdtic': 'btn-op-pdtic'
        };

        ids.forEach(function(bid) {
            var b = document.getElementById(bid);
            if (b) {
                if (bid === mapa[modo]) {
                    b.className = 'btn btn-primary pill-filtro-op active';
                    b.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                    b.style.color = '#ffffff';
                    b.style.fontWeight = '700';
                } else {
                    b.className = 'btn btn-secondary pill-filtro-op';
                    b.style.background = 'rgba(255,255,255,0.06)';
                    b.style.color = '#cbd5e1';
                    b.style.fontWeight = '600';
                }
            }
        });

        var selMacro = document.getElementById('op-filtro-macro');
        var inpBusca = document.getElementById('op-filtro-busca');

        if (modo === 'sagti') {
            if (selMacro) selMacro.value = 'spaguas-sa-gti';
            if (inpBusca) inpBusca.value = '';
        } else if (modo === 'pdtic') {
            if (selMacro) selMacro.value = '';
            if (inpBusca) inpBusca.value = 'PDTIC';
        } else {
            if (selMacro) selMacro.value = '';
            if (inpBusca) inpBusca.value = '';
        }

        window.filtrarPortfolioOpenProject(modo);
    };

    window.filtrarPortfolioOpenProject = function(modoOpcional) {
        var tbody = document.getElementById('tbody-portfolio-openproject');
        if (!tbody) return;

        var modo = modoOpcional || window.opModoRapidoAtivo || 'todos';
        var dados = window.OP_PACOTES_OFICIAIS || [];

        var fMacro = (document.getElementById('op-filtro-macro') || {}).value || '';
        var fProj = (document.getElementById('op-filtro-projeto') || {}).value || '';
        var fTipo = (document.getElementById('op-filtro-tipo') || {}).value || '';
        var fStatus = (document.getElementById('op-filtro-status') || {}).value || '';
        var fResp = (document.getElementById('op-filtro-resp') || {}).value || '';
        var fBusca = ((document.getElementById('op-filtro-busca') || {}).value || '').toLowerCase().trim();

        var filtrados = dados.filter(function(p) {
            if (modo === 'sagti') {
                if (p.macro !== 'spaguas-sa-gti') return false;
            } else if (modo === 'pdtic') {
                var bPdtic = ((p.assunto||'') + ' ' + (p.projeto||'') + ' ' + (p.backlog||'')).toLowerCase();
                if (bPdtic.indexOf('pdtic') === -1) return false;
            }

            if (fStatus) {
                var stLower = (p.status || '').toLowerCase();
                var fsLower = fStatus.toLowerCase();
                if (fsLower === 'em espera') {
                    if (stLower.indexOf('espera') === -1 && stLower.indexOf('agendado') === -1) return false;
                } else if (stLower.indexOf(fsLower) === -1) {
                    return false;
                }
            }

            if (fMacro && modo !== 'sagti' && p.macro !== fMacro) return false;
            if (fProj && p.projeto !== fProj) return false;
            if (fTipo && (p.tipo || '').indexOf(fTipo) === -1) return false;
            if (fResp && p.atrib !== fResp && p.autor !== fResp && p.encarr !== fResp) return false;
            if (fBusca && modo !== 'pdtic') {
                var blob = ('#' + p.id + ' ' + (p.assunto||'') + ' ' + (p.projeto||'') + ' ' + (p.pai||'') + ' ' + (p.atrib||'')).toLowerCase();
                if (blob.indexOf(fBusca) === -1) return false;
            }

            return true;
        });

        var esc = window.escapeHtml || function(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); };
        var html = '';

        filtrados.slice(0, 300).forEach(function(p) {
            var crono = (p.ini || p.fim) ? ((p.ini || '?') + ' → ' + (p.fim || '?')) : '<span style="color:#64748b;">Contínuo</span>';
            var paiTxt = p.pai ? '<span style="color:#38bdf8; font-weight:600; font-size:11px;">↳ ' + esc(p.pai) + '</span>' : '<span style="color:#64748b; font-size:11px;">Raiz do Projeto</span>';

            var sL = (p.status || '').toLowerCase();
            var stBadge = '';
            if (sL.indexOf('progresso') !== -1) {
                stBadge = '<span style="background:rgba(16,185,129,0.18); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:2px 8px; border-radius:12px; font-weight:700; font-size:10.5px;">🚀 Em progresso</span>';
            } else if (sL.indexOf('espera') !== -1 || sL.indexOf('agendado') !== -1) {
                stBadge = '<span style="background:rgba(245,158,11,0.18); color:#fbbf24; border:1px solid rgba(245,158,11,0.4); padding:2px 8px; border-radius:12px; font-weight:700; font-size:10.5px;">⏳ Em espera</span>';
            } else if (sL.indexOf('novo') !== -1) {
                stBadge = '<span style="background:rgba(56,189,248,0.18); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); padding:2px 8px; border-radius:12px; font-weight:700; font-size:10.5px;">💡 Novo</span>';
            } else {
                stBadge = '<span style="background:rgba(148,163,184,0.15); color:#cbd5e1; border:1px solid rgba(148,163,184,0.3); padding:2px 8px; border-radius:12px; font-weight:700; font-size:10.5px;">' + esc(p.status) + '</span>';
            }

            var tipoBadge = '<span style="background:rgba(255,255,255,0.06); color:#e2e8f0; border:1px solid rgba(255,255,255,0.12); padding:2px 8px; border-radius:8px; font-size:11px; font-weight:600;">' + esc(p.tipo) + '</span>';
            var linkOP = 'https://projetos.spaguas.sp.gov.br/work_packages/' + p.id;

            html += '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">' +
                '<td style="padding:10px 12px; font-family:monospace; font-weight:800;"><a href="' + linkOP + '" target="_blank" rel="noopener noreferrer" style="color:#38bdf8; text-decoration:none;">#' + p.id + '</a></td>' +
                '<td style="padding:10px 12px; color:#e2e8f0; font-weight:600;">' + esc(p.projeto) + '</td>' +
                '<td style="padding:10px 12px;">' + tipoBadge + '</td>' +
                '<td style="padding:10px 12px; color:#ffffff; font-weight:700;">' + esc(p.assunto) + '</td>' +
                '<td style="padding:10px 12px;">' + paiTxt + '</td>' +
                '<td style="padding:10px 12px;">' + stBadge + '</td>' +
                '<td style="padding:10px 12px; color:#94a3b8; font-size:11.5px;">👤 ' + esc(p.atrib || p.autor || 'Equipe') + '</td>' +
                '<td style="padding:10px 12px; text-align:center; font-family:monospace; font-size:11px; color:#cbd5e1;">' + crono + '</td>' +
                '</tr>';
        });

        tbody.innerHTML = html;
    };
})();
</script>
'''

    if 'window.opModoRapidoAtivo' in html_mod:
        pattern_old_script = r'<script>\s*window\.opModoRapidoAtivo[\s\S]*?</script>'
        html_mod = re.sub(pattern_old_script, js_limpo.strip(), html_mod, count=1)
    else:
        idx_body = html_mod.rfind('</body>')
        if idx_body != -1:
            html_mod = html_mod[:idx_body] + js_limpo + '\n' + html_mod[idx_body:]

    open_divs = len(re.findall(r'<div\b', html_mod, re.IGNORECASE))
    close_divs = len(re.findall(r'</div\b', html_mod, re.IGNORECASE))
    diff = open_divs - close_divs

    if diff == 0:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html_mod)
        print(f"[*] {caminho}: Botões removidos e script saneado com sucesso! (Div balance = 0)")
    else:
        print(f"[!] Erro de balanceamento de divs em {caminho}: diff={diff}")

print("\n" + "=" * 70)
print(" REMOÇÃO CONCLUÍDA")
print("=" * 70)
