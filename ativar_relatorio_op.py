# -*- coding: utf-8 -*-
import os, glob

op_script_block = """
<script id="script-relatorio-openproject-v11">
(function() {
    window.subAbaOpAtiva = 'operacional';

    function cardKpi(titulo, valor, sub, corTexto, corBorda, bg) {
        return '<div style="background:' + bg + ';border:1px solid ' + corBorda + ';border-radius:8px;padding:12px;">' +
            '<div style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;">' + titulo + '</div>' +
            '<div style="font-size:24px;font-weight:800;color:' + corTexto + ';margin-top:4px;">' + valor + '</div>' +
            '<div style="font-size:10.5px;color:#64748b;margin-top:2px;">' + sub + '</div></div>';
    }

    function linhaOp(id, titulo, desc, papel, corPapel, status, pillClass) {
        var url = 'https://projetos.spaguas.sp.gov.br/work_packages/' + id;
        return '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">' +
            '<td style="padding:10px 12px;font-family:monospace;font-weight:800;color:#38bdf8;">#' + id + '</td>' +
            '<td style="padding:10px 12px;font-weight:600;color:#ffffff;">' + titulo +
            '<div style="font-size:11px;color:#94a3b8;font-weight:400;margin-top:2px;">' + desc + '</div></td>' +
            '<td style="padding:10px 12px;color:#cbd5e1;">SA-GTI - Gerência de TI</td>' +
            '<td style="padding:10px 12px;"><span style="background:rgba(255,255,255,0.06);color:' + corPapel +
            ';padding:2px 8px;border-radius:6px;font-size:11px;">' + papel + '</span></td>' +
            '<td style="padding:10px 12px;text-align:center;"><span class="pill-tag ' + pillClass + '">' + status + '</span></td>' +
            '<td style="padding:10px 12px;text-align:center;"><a href="' + url + '" target="_blank" ' +
            'style="color:#38bdf8;text-decoration:none;font-weight:700;">Abrir OP ↗</a></td></tr>';
    }

    function cardEixo(eixo, titulo, desc, qtd, cor) {
        return '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);' +
            'border-top:3px solid ' + cor + ';border-radius:8px;padding:14px;">' +
            '<div style="font-size:11px;font-weight:700;color:' + cor + ';">' + eixo + '</div>' +
            '<div style="font-size:12.5px;font-weight:700;color:#ffffff;margin-top:4px;">' + titulo + '</div>' +
            '<div style="font-size:11px;color:#94a3b8;margin-top:6px;line-height:1.4;">' + desc + '</div>' +
            '<div style="font-size:11.5px;font-weight:700;color:' + cor + ';margin-top:10px;">' + qtd + '</div></div>';
    }

    function cardTrack(titulo, desc, cor) {
        return '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);' +
            'border-radius:8px;padding:14px;">' +
            '<div style="font-size:13px;font-weight:700;color:' + cor + ';">' + titulo + '</div>' +
            '<p style="font-size:11.5px;color:#cbd5e1;margin:8px 0 0 0;line-height:1.5;">' + desc + '</p></div>';
    }

    function montarRelatorioHtml() {
        var h = '';
        h += '<div style="background:linear-gradient(135deg,rgba(15,23,42,0.95) 0%,rgba(30,41,59,0.95) 100%);' +
             'border:1px solid rgba(56,189,248,0.25);border-left:5px solid #0284c7;border-radius:12px;' +
             'padding:20px 24px;margin-bottom:20px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.5);">';
        h += '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;"><div>';
        h += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">' +
             '<span style="font-size:11px;font-weight:800;background:rgba(2,132,199,0.25);color:#38bdf8;' +
             'border:1px solid rgba(56,189,248,0.4);padding:3px 10px;border-radius:20px;">SP-ÁGUAS · DIRETORIA COLEGIADA</span>' +
             '<span style="font-size:11px;font-weight:700;background:rgba(16,185,129,0.2);color:#4ade80;' +
             'border:1px solid rgba(16,185,129,0.4);padding:3px 10px;border-radius:20px;">DOCUMENTO DE GOVERNANÇA DE TIC</span>' +
             '<span style="font-size:11px;color:#94a3b8;font-family:monospace;">SA-GTI · GESTÃO DE PROJETOS</span></div>';
        h += '<h2 style="margin:0;font-size:22px;font-weight:800;color:#ffffff;">' +
             '📑 Relatório Mensal Executivo — Governança do Portfólio OpenProject &amp; PDTIC 2027–2030</h2>';
        h += '<p style="margin:6px 0 0 0;font-size:13px;color:#cbd5e1;">Período de Apuração: ' +
             '<strong style="color:#38bdf8;">Competência Novembro/2026</strong> • ' +
             '<strong>500 Pacotes de Trabalho em 29 Projetos Oficiais</strong></p></div>';
        h += '<div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.1);' +
             'border-radius:8px;padding:6px 12px;font-size:11.5px;color:#94a3b8;font-family:monospace;">' +
             'Status: <strong style="color:#4ade80;">100% Homologado (OpenProject v14)</strong></div></div></div>';

        h += '<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.08);' +
             'border-radius:12px;padding:20px;margin-bottom:20px;">';
        h += '<h3 style="margin:0 0 14px 0;font-size:15px;color:#ffffff;font-weight:700;">' +
             '📊 1. Sumário Executivo &amp; Volumetria Consolidada do Portfólio</h3>';
        h += '<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:16px;">' +
             cardKpi('Total de Pacotes', '500', '29 Projetos Ativos', '#38bdf8', 'rgba(56,189,248,0.3)', 'rgba(2,132,199,0.15)') +
             cardKpi('Macroentregas', '134', '99 Proj + 35 PDTIC', '#818cf8', 'rgba(129,140,248,0.3)', 'rgba(99,102,241,0.15)') +
             cardKpi('Em Progresso', '111', '22.2% em Execução', '#34d399', 'rgba(52,211,153,0.3)', 'rgba(16,185,129,0.15)') +
             cardKpi('Em Espera / Fila', '90', '76 Espera + 14 Agend', '#fbbf24', 'rgba(251,191,36,0.3)', 'rgba(245,158,11,0.15)') +
             cardKpi('Marcos & KPIs', '34', '26 DOE/BID + 8 KPIs', '#f87171', 'rgba(248,113,113,0.3)', 'rgba(239,68,68,0.15)') +
             cardKpi('Orçamento TI', 'R$ 2,0 Mi', 'Parque Informática #42', '#c084fc', 'rgba(167,139,250,0.3)', 'rgba(139,92,246,0.15)') +
             '</div>';
        h += '<p style="font-size:12.5px;color:#cbd5e1;line-height:1.6;margin:0;">O Portfólio Oficial da SP-Águas ' +
             'estruturado no OpenProject v14 reflete a totalidade das iniciativas de transformação institucional e ' +
             'sustentação operacional da autarquia, consolidando <strong>500 pacotes de trabalho</strong> em ' +
             '<strong>29 projetos estratégicos</strong> sob governança da SA-GTI.</p></div>';

        h += '<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.08);' +
             'border-left:4px solid #10b981;border-radius:12px;padding:20px;margin-bottom:20px;">';
        h += '<h3 style="margin:0 0 14px 0;font-size:15px;color:#ffffff;font-weight:700;">' +
             '👤 2. Carteira Tática sob Responsabilidade Nominal Direta (Luiz Antonio Seixeiro — 4 Pacotes)</h3>';
        h += '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead>' +
             '<tr style="border-bottom:1px solid rgba(255,255,255,0.1);color:#94a3b8;font-size:11px;text-transform:uppercase;">' +
             '<th style="padding:10px 12px;text-align:left;">ID OP</th>' +
             '<th style="padding:10px 12px;text-align:left;">Iniciativa / Pacote de Trabalho</th>' +
             '<th style="padding:10px 12px;text-align:left;">Projeto Oficial</th>' +
             '<th style="padding:10px 12px;text-align:left;">Tipo / Papel</th>' +
             '<th style="padding:10px 12px;text-align:center;">Status</th>' +
             '<th style="padding:10px 12px;text-align:center;">Ações</th></tr></thead><tbody>' +
             linhaOp('1185', 'PDTIC-E1-I01 - Programa corporativo de backup, retenção e restauração por criticidade',
                     'Regra 3-2-1-1-0, cópias imutáveis WORM/Object Lock contra ransomware, RPO <= 1h e RTO <= 4h.',
                     'Iniciativa PDTIC', '#a5b4fc', '🚀 Em progresso', 'pill-blue') +
             linhaOp('1231', 'Track 1 (Operação Atual) — Sustentação e Gestão dos Contratos Vigentes',
                     'Atestes mensais PRODESP, links Intragov 6 SD-WAN e telefonia móvel/fixa DMO.',
                     'Fase / Track', '#7dd3fc', '🚀 Em progresso', 'pill-blue') +
             linhaOp('1232', 'Track 2: Renegociação e Readequação Contratual',
                     'Apuração de glosas IMR, repactuações de preços, economicidade e FinOps em nuvem pública.',
                     'Fase / Track', '#fde68a', '🚀 Em progresso', 'pill-blue') +
             linhaOp('1233', 'Configuração Estrutural e Parametrização de Métricas do Portfólio',
                     'Hierarquia Pai -> Filho, WBS/EAP canônica e alinhamento do Kanban de 22 status.',
                     'Entregável / Tarefa', '#86efac', '✔️ Concluído', 'pill-green') +
             '</tbody></table></div>';

        h += '<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.08);' +
             'border-radius:12px;padding:20px;margin-bottom:20px;">';
        h += '<h3 style="margin:0 0 14px 0;font-size:15px;color:#ffffff;font-weight:700;">' +
             '🧭 3. Alinhamento ao PDTIC 2027–2030: Decomposição pelos 5 Eixos Estratégicos (35 Iniciativas)</h3>';
        h += '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;">' +
             cardEixo('EIXO 1', 'Infraestrutura & Resiliência', 'Retrofit CPD Sede (#530), Nuvem Híbrida e Backup WORM (#1185).', '8 Iniciativas', '#38bdf8') +
             cardEixo('EIXO 2', 'Governança de Dados & SIGRH', 'Data Lakehouse, RLS no Power BI, barramentos ANA e LGPD.', '7 Iniciativas', '#818cf8') +
             cardEixo('EIXO 3', 'Sistemas & Serviços Digitais', 'Modernização do SOE, outorgas online e integração SEI.', '9 Iniciativas', '#34d399') +
             cardEixo('EIXO 4', 'Gestão, IMR & Conformidade', 'Adequação à Lei 14.133, glosas IMR e liquidação SIAFEM.', '6 Iniciativas', '#fbbf24') +
             cardEixo('EIXO 5', 'Cultura Digital & IA', 'Cockpit GTI, agentes IA multissistêmicos e rituais ágeis.', '5 Iniciativas', '#c084fc') +
             '</div></div>';

        h += '<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.08);' +
             'border-radius:12px;padding:20px;margin-bottom:20px;">';
        h += '<h3 style="margin:0 0 14px 0;font-size:15px;color:#ffffff;font-weight:700;">' +
             '⚡ 4. Tracks Contratuais SA-GTI (97 Pacotes) &amp; Parecer Conclusivo de Governança</h3>';
        h += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:16px;">' +
             cardTrack('🛠️ Track 1: Operação & Sustentação',
                       'Sustentação de 30 circuitos Intragov 6 (SD-WAN) nas bacias hidrográficas, faturas DMO e suporte N1/N2 GLPI.', '#38bdf8') +
             cardTrack('⚖️ Track 2: Repactuação & IMR',
                       'Fiscalização técnica rigorosa sob a Lei 14.133/2021, disponibilidade >= 99,5%, glosas objetivas e atestes SEI.', '#fbbf24') +
             cardTrack('🚀 Track 3: Modernização (A-017)',
                       'Retrofit do CPD da Sede (#530), licitação de R$ 2,0 milhões para 485 computadores (#42) e NOC Zabbix (#552).', '#34d399') +
             '</div>';
        h += '<div style="display:flex;justify-content:space-between;align-items:flex-end;padding-top:14px;' +
             'border-top:1px solid rgba(255,255,255,0.06);font-size:11px;color:#94a3b8;">' +
             '<div><strong>Autarquia de Águas do Estado de São Paulo — SP-Águas</strong><br>' +
             'Superintendência de Administração • Gerência de Tecnologia da Informação (SA-GTI)</div>' +
             '<div style="text-align:right;"><strong>Luiz Antonio Seixeiro</strong><br>' +
             'Gestor de Projetos Sênior / Governança SA-GTI</div></div></div>';
        return h;
    }

    function localizarBotaoTodosPacotes() {
        var el = document.getElementById('btn-op-subaba-operacional') || document.getElementById('btn-op-todos');
        if (el) return el;
        var candidatos = document.querySelectorAll('button, .btn, .pill-filtro-op');
        for (var i = 0; i < candidatos.length; i++) {
            var t = (candidatos[i].innerText || candidatos[i].textContent || '').trim();
            if (t.indexOf('Todos os Pacotes') !== -1) {
                return candidatos[i];
            }
        }
        return null;
    }

    window.obterBarraTopoOpenProject = function() {
        var btnOp = localizarBotaoTodosPacotes();
        if (!btnOp) return null;
        var viewOp = btnOp.closest('.tab-view') || document.getElementById('view-portfolio_openproject');
        var curr = btnOp.parentElement;
        while (curr && curr !== viewOp && curr !== document.body) {
            if ((curr.innerText || '').indexOf('Trava de Segurança') !== -1 || curr.parentElement === viewOp) {
                return curr;
            }
            curr = curr.parentElement;
        }
        return btnOp.parentElement;
    };

    window.configurarBotoesRelatorioOpenProject = function() {
        var btnTodos = localizarBotaoTodosPacotes();
        if (!btnTodos) return;

        var viewOp = btnTodos.closest('.tab-view') || document.getElementById('view-portfolio_openproject') || btnTodos.parentElement.parentElement;

        var barraPai = btnTodos.parentElement;
        var botoes = Array.prototype.slice.call(barraPai.querySelectorAll('button, .btn, .pill-filtro-op'));
        botoes.forEach(function(btn) {
            var txt = (btn.innerText || btn.textContent || '').trim();
            if (txt.indexOf('Tracks SA-GTI') !== -1 || txt.indexOf('Governança PDTIC') !== -1 ||
                txt.indexOf('PDTIC 2027-2030') !== -1 || btn.id === 'btn-op-sagti' || btn.id === 'btn-op-pdtic') {
                btn.remove();
            }
        });

        btnTodos.id = 'btn-op-subaba-operacional';
        btnTodos.setAttribute('onclick', "window.alternarSubAbaOpenProject('operacional')");

        if (!document.getElementById('btn-op-subaba-relatorio')) {
            var btnRel = document.createElement('button');
            btnRel.type = 'button';
            btnRel.id = 'btn-op-subaba-relatorio';
            btnRel.className = 'btn btn-secondary';
            btnRel.setAttribute('onclick', "window.alternarSubAbaOpenProject('relatorio')");
            btnRel.style.cssText = 'background:rgba(255,255,255,0.06);color:#cbd5e1;font-weight:600;' +
                'font-size:12px;padding:7px 16px;border-radius:8px;border:1px solid rgba(255,255,255,0.12);' +
                'cursor:pointer;display:inline-flex;align-items:center;gap:6px;transition:all 0.2s ease;';
            btnRel.innerHTML = '<span>📑</span> Relatório Mensal Executivo do Portfólio OpenProject (Novembro/2026)';
            if (btnTodos.nextSibling) {
                barraPai.insertBefore(btnRel, btnTodos.nextSibling);
            } else {
                barraPai.appendChild(btnRel);
            }
        }

        if (!document.getElementById('subview-op-relatorio') && viewOp) {
            var divRel = document.createElement('div');
            divRel.id = 'subview-op-relatorio';
            divRel.className = 'subview-op';
            divRel.style.cssText = 'display:none;margin-top:16px;';
            divRel.innerHTML = montarRelatorioHtml();

            var barraTopo = window.obterBarraTopoOpenProject();
            if (barraTopo && barraTopo.parentElement) {
                barraTopo.parentElement.appendChild(divRel);
            } else {
                viewOp.appendChild(divRel);
            }
        }
    };

    window.alternarSubAbaOpenProject = function(subAba) {
        window.subAbaOpAtiva = subAba || 'operacional';
        window.configurarBotoesRelatorioOpenProject();

        var btnOperacional = document.getElementById('btn-op-subaba-operacional');
        if (!btnOperacional) return;
        var viewOp = btnOperacional.closest('.tab-view') || document.getElementById('view-portfolio_openproject');
        if (!viewOp) return;

        var vRelatorio = document.getElementById('subview-op-relatorio');
        var btnRelatorio = document.getElementById('btn-op-subaba-relatorio');
        var barraTopo = window.obterBarraTopoOpenProject();

        var blocosOperacionais = [];
        if (barraTopo) {
            var paiBarra = barraTopo.parentElement;
            Array.prototype.slice.call(paiBarra.children).forEach(function(el) {
                if (el !== barraTopo && el !== vRelatorio && !el.classList.contains('page-banner')) {
                    blocosOperacionais.push(el);
                }
            });
            if (paiBarra !== viewOp) {
                Array.prototype.slice.call(viewOp.children).forEach(function(el) {
                    if (el !== paiBarra && el !== vRelatorio && !el.classList.contains('page-banner')) {
                        blocosOperacionais.push(el);
                    }
                });
            }
        }

        if (subAba === 'relatorio') {
            blocosOperacionais.forEach(function(el) {
                if (el.style.display !== 'none') {
                    el.setAttribute('data-op-display', el.style.display || '');
                }
                el.style.display = 'none';
            });
            if (vRelatorio) {
                vRelatorio.style.display = 'block';
                vRelatorio.style.opacity = '1';
            }
            if (btnOperacional) {
                btnOperacional.className = 'btn btn-secondary';
                btnOperacional.style.background = 'rgba(255,255,255,0.06)';
                btnOperacional.style.color = '#cbd5e1';
                btnOperacional.style.fontWeight = '600';
                btnOperacional.style.border = '1px solid rgba(255,255,255,0.12)';
                btnOperacional.style.boxShadow = 'none';
            }
            if (btnRelatorio) {
                btnRelatorio.className = 'btn btn-primary active';
                btnRelatorio.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                btnRelatorio.style.color = '#ffffff';
                btnRelatorio.style.fontWeight = '700';
                btnRelatorio.style.border = '1px solid rgba(56,189,248,0.5)';
                btnRelatorio.style.boxShadow = '0 2px 8px rgba(2,132,199,0.3)';
            }
        } else {
            if (vRelatorio) vRelatorio.style.display = 'none';
            blocosOperacionais.forEach(function(el) {
                var orig = el.getAttribute('data-op-display');
                el.style.display = orig !== null ? orig : '';
            });
            if (btnOperacional) {
                btnOperacional.className = 'btn btn-primary active';
                btnOperacional.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
                btnOperacional.style.color = '#ffffff';
                btnOperacional.style.fontWeight = '700';
                btnOperacional.style.border = '1px solid rgba(56,189,248,0.5)';
                btnOperacional.style.boxShadow = '0 2px 8px rgba(2,132,199,0.3)';
            }
            if (btnRelatorio) {
                btnRelatorio.className = 'btn btn-secondary';
                btnRelatorio.style.background = 'rgba(255,255,255,0.06)';
                btnRelatorio.style.color = '#cbd5e1';
                btnRelatorio.style.fontWeight = '600';
                btnRelatorio.style.border = '1px solid rgba(255,255,255,0.12)';
                btnRelatorio.style.boxShadow = 'none';
            }
            if (typeof window.filtrarModoRapidoOP === 'function') {
                try { window.filtrarModoRapidoOP('todos'); } catch(e) {}
            } else if (typeof window.filtrarPortfolioOpenProject === 'function') {
                try { window.filtrarPortfolioOpenProject(); } catch(e) {}
            }
        }
    };

    window.configurarBotoesRelatorioOpenProject();
    document.addEventListener('DOMContentLoaded', function() {
        window.configurarBotoesRelatorioOpenProject();
        setTimeout(window.configurarBotoesRelatorioOpenProject, 250);
        setTimeout(window.configurarBotoesRelatorioOpenProject, 800);
    });
    setInterval(window.configurarBotoesRelatorioOpenProject, 800);
})();
</script>
"""

arquivos = []
for padrao in ["*.html", "frontend/*.html", "templates/*.html", "static/*.html"]:
    arquivos.extend(glob.glob(padrao))

vistos = set()
alvos = []
for a in arquivos:
    caminho_abs = os.path.abspath(a)
    if caminho_abs not in vistos and os.path.isfile(caminho_abs) and "backup" not in a.lower():
        vistos.add(caminho_abs)
        alvos.append(a)

for caminho in alvos:
    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        conteudo = f.read()

    if 'id="script-relatorio-openproject-v11"' in conteudo:
        p_ini = conteudo.find('<script id="script-relatorio-openproject-v11">')
        p_fim = conteudo.find('</script>', p_ini) + 9
        conteudo = conteudo[:p_ini] + op_script_block.strip() + conteudo[p_fim:]
    else:
        if '</body>' in conteudo:
            p_body = conteudo.rfind('</body>')
            conteudo = conteudo[:p_body] + '\n' + op_script_block.strip() + '\n</body>' + conteudo[p_body + 7:]
        else:
            conteudo = conteudo + '\n' + op_script_block.strip() + '\n'

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"✅ Relatório OpenProject ativado em: {caminho}")

print("\n🎉 Concluído com sucesso!")
