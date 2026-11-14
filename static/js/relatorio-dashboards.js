(function() {
    function cardKpiDash(titulo, valor, sub, corTexto, corBorda, bg) {
        return '<div class="card card-sm card-body">' +
            '<div class="subheader">' + titulo + '</div>' +
            '<div class="h1 mb-0 mt-1">' + valor + '</div>' +
            '<div class="text-secondary small mt-1">' + sub + '</div></div>';
    }

    function cardMacroEixo(icone, titulo, qtd, pct, cor, desc, buckets) {
        return '<div class="card card-body">' +
            '<div style="display:flex;justify-content:space-between;align-items:center">' +
            '<span style="font-size:12px;font-weight:800;text-transform:uppercase">' +
            icone + ' ' + titulo + '</span>' +
            '<span style="font-size:11px;font-weight:700;' +
            'padding:2px 8px;border-radius:12px">' + pct + ' do Acervo</span></div>' +
            '<div style="font-size:26px;font-weight:800;margin:8px 0 4px 0">' + qtd + '</div>' +
            '<p style="font-size:11.5px;margin:0 0 10px 0;line-height:1.45">' + desc + '</p>' +
            '<div style="font-size:10.5px;padding-top:8px">' +
            '<strong>Buckets Dominantes:</strong> ' + buckets + '</div></div>';
    }

    function linhaBucket(cod, nome, eixo, qtd, pct, corBarra, statusPrincipal) {
        return '<tr >' +
            '<td style="padding:10px 12px;font-weight:800">' + cod + '</td>' +
            '<td style="padding:10px 12px;font-weight:600">' + nome + '</td>' +
            '<td style="padding:10px 12px;font-size:11.5px">' + eixo + '</td>' +
            '<td style="padding:10px 12px;text-align:center;font-weight:800">' + qtd + '</td>' +
            '<td style="padding:10px 12px;width:180px">' +
            '<div style="display:flex;align-items:center;gap:8px">' +
            '<div class="progress flex-fill">' +
            '<div class="progress-bar bg-primary" style="width:' + pct + '%"></div></div>' +
            '<span style="font-size:11px;width:36px">' + pct + '%</span>' +
            '</div></td>' +
            '<td style="padding:10px 12px;text-align:center"><span class="badge bg-blue-lt">' +
            statusPrincipal + '</span></td></tr>';
    }

    function linhaSeiCritico(sei, assunto, bucket, farol, corFarol, aging, resp) {
        return '<tr >' +
            '<td style="padding:10px 12px;font-weight:800;white-space:nowrap">' +
            sei + '</td>' +
            '<td style="padding:10px 12px;font-weight:600">' + assunto + '</td>' +
            '<td style="padding:10px 12px;font-size:11px">' + bucket + '</td>' +
            '<td style="padding:10px 12px;text-align:center"><span class="badge bg-amber-lt">' +
            farol + '</span></td>' +
            '<td style="padding:10px 12px;text-align:center;font-size:11.5px">' +
            aging + '</td>' +
            '<td style="padding:10px 12px;font-size:11.5px">' + resp + '</td>' +
            '<td style="padding:10px 12px;text-align:center">' +
            '<button type="button" data-sei="' + sei + '" ' +
            'onclick="if(window.abrirDetalhesProcesso)window.abrirDetalhesProcesso(this.getAttribute(\'data-sei\'))" ' +
            'class="btn btn-ghost-secondary btn-sm">' +
            'Dossiê SEI ↗</button></td></tr>';
    }

    function cardCustodiaTecnica(nome, cargo, total, est, rot, port, destaques, cor) {
        return '<div class="card card-body">' +
            '<div style="display:flex;justify-content:space-between;align-items:flex-start">' +
            '<div><div style="font-size:14px;font-weight:800">' + nome + '</div>' +
            '<div style="font-size:11px;margin-top:2px">' + cargo + '</div></div>' +
            '<span style="font-size:18px;font-weight:800;' +
            'padding:4px 10px;border-radius:8px">' + total + ' proc.</span></div>' +
            '<div class="sagti-stats-grid">' +
            '<div><div >CONTRATAÇÃO</div>' +
            '<div style="font-size:13px;font-weight:800">' + est + '</div></div>' +
            '<div><div >ROTINA OP.</div>' +
            '<div style="font-size:13px;font-weight:800">' + rot + '</div></div>' +
            '<div><div >PORTFÓLIO</div>' +
            '<div style="font-size:13px;font-weight:800">' + port + '</div></div></div>' +
            '<div style="font-size:11px;line-height:1.45"><strong>Frentes Chave:</strong> ' +
            destaques + '</div></div>';
    }

    function montarRelatorioDashHtml() {
        var h = '';
        h += '<div class="card card-body mb-3">';
        h += '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px"><div>';
        h += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">' +
             '<span style="font-size:11px;font-weight:800;' +
             'border:1px solid rgba(56,189,248,0.4);padding:3px 10px;border-radius:20px">' +
             'SP-ÁGUAS · DIRETORIA COLEGIADA</span>' +
             '<span style="font-size:11px;font-weight:700;' +
             'border:1px solid rgba(16,185,129,0.4);padding:3px 10px;border-radius:20px">' +
             'GESTÃO À VISTA 360° (SEI-SP &amp; SOE)</span>' +
             '<span style="font-size:11px">SA-GTI · GOVERNANÇA DIGITAL</span></div>';
        h += '<h2 style="margin:0;font-size:22px;font-weight:800">' +
             '📑 Relatório Mensal Executivo — Governança 360° de Processos SEI &amp; Contratos de TIC</h2>';
        h += '<p style="margin:6px 0 0 0;font-size:13px">Período de Apuração: ' +
             '<strong >Competência Novembro/2026</strong> • ' +
             '<strong>179 Processos Administrativos Monitorados em 3 Macrofluxos</strong></p></div>';
        h += '<div class="badge bg-green-lt">' +
             'Status: <strong >Base SEI Higienizada (UPSERT)</strong></div></div></div>';

        // SECAO 1
        h += '<div class="card card-body mb-3">';
        h += '<h3 style="margin:0 0 14px 0;font-size:15px;font-weight:700">' +
             '📊 1. Sumário Executivo &amp; Termômetro de Criticidade do Acervo SEI-SP (179 Processos)</h3>';
        h += '<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:16px">' +
             cardKpiDash('Acervo Total SEI', '179', '100% Rastreado SA-GTI',
                         '#38bdf8', 'rgba(56,189,248,0.3)', 'rgba(2,132,199,0.15)') +
             cardKpiDash('Intervenção (F1)', '0', 'Zero processos travados',
                         '#4ade80', 'rgba(74,222,128,0.3)', 'rgba(16,185,129,0.12)') +
             cardKpiDash('Saneamento (F2)', '26', '14.5% do backlog (Ação)',
                         '#fb923c', 'rgba(251,146,60,0.3)', 'rgba(234,88,12,0.15)') +
             cardKpiDash('Monitoramento (F3)', '50', '27.9% em acompanhamento',
                         '#facc15', 'rgba(250,204,21,0.3)', 'rgba(202,138,4,0.15)') +
             cardKpiDash('Fluxo Normal (F4)', '11', '6.1% dentro do SLA',
                         '#34d399', 'rgba(52,211,153,0.3)', 'rgba(16,185,129,0.15)') +
             cardKpiDash('Rotina Padrão', '92', '51.4% atestes e faturas',
                         '#94a3b8', 'rgba(148,163,184,0.3)', 'rgba(100,116,139,0.15)') +
             '</div>';
        h += '<p style="font-size:12.5px;line-height:1.6;margin:0">A consolidação mensal do acervo ' +
             'administrativo da Gerência de Tecnologia da Informação (SA-GTI) evidencia <strong>zero processos em ' +
             'estado de paralisação crítica imediata (Farol 1)</strong>, resultado direto do ciclo de saneamento e ' +
             'conciliação documental entre o SEI-SP, o barramento SOE e os quadros do OpenProject.</p></div>';

        // SECAO 2
        h += '<div class="card card-body mb-3">';
        h += '<h3 style="margin:0 0 14px 0;font-size:15px;font-weight:700">' +
             '🧩 2. Decomposição por Eixo de Gestão (Macrofluxo Operacional SA-GTI)</h3>';
        h += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px">' +
             cardMacroEixo('⚙️', 'Rotina Operacional & Sustentação', '93 Processos', '52.0%', '#38bdf8',
                           'Atestes mensais de serviços contínuos (PRODESP), faturas de telecom/links DMO e suporte.',
                           'A-001 (41), A-002 (32), A-010 (19) e A-004 (1)') +
             cardMacroEixo('📑', 'Esteira de Contratação (Lei 14.133)', '55 Processos', '30.7%', '#818cf8',
                           'Instrução processual de novas aquisições de TIC, elaboração de DFD, ETP, TR e Riscos.',
                           'A-011 Elaboração de ETP, TR e Riscos (55)') +
             cardMacroEixo('🚀', 'Portfólio Estratégico & PDTIC', '31 Processos', '17.3%', '#c084fc',
                           'Projetos estruturantes de transformação digital, infraestrutura crítica e PDTIC.',
                           'A-017 Modernização (16) e A-016 Governança/PDTIC (15)') +
             '</div></div>';

        // SECAO 3
        h += '<div class="card card-body mb-3">';
        h += '<h3 style="margin:0 0 14px 0;font-size:15px;font-weight:700">' +
             '📂 3. Distribuição Taxonômica pelos Buckets Canônicos do OpenProject</h3>';
        h += '<div class="table-responsive"><table style="width:100%;border-collapse:collapse;font-size:12px" class="table table-vcenter card-table table-hover"><thead>' +
             '<tr style="font-size:11px;' +
             'text-transform:uppercase">' +
             '<th style="padding:10px 12px;text-align:left">Código</th>' +
             '<th style="padding:10px 12px;text-align:left">Bucket Canônico SA-GTI</th>' +
             '<th style="padding:10px 12px;text-align:left">Macrofluxo Vinculado</th>' +
             '<th style="padding:10px 12px;text-align:center">Processos</th>' +
             '<th style="padding:10px 12px;text-align:left">Participação (%)</th>' +
             '<th style="padding:10px 12px;text-align:center">Estágio Predominante</th></tr></thead><tbody>' +
             linhaBucket('A-011', 'Elaboração de ETP, Termo de Referência e Riscos',
                         'Esteira de Contratação', '55', '30.7', '#6366f1', '🧩 Em Instrução Técnica') +
             linhaBucket('A-001', 'Atestes e Medições Mensais de Serviços PRODESP',
                         'Rotina Operacional', '41', '22.9', '#0ea5e9', '🚀 Em Execução / Medição') +
             linhaBucket('A-002', 'Faturas e Pagamentos Regulares de Concessionárias / TI',
                         'Rotina Operacional', '32', '17.9', '#38bdf8', '💳 Conciliação DMO/SIAFEM') +
             linhaBucket('A-010', 'Atendimento a Solicitações Internas e Suporte Técnico',
                         'Rotina Operacional', '19', '10.6', '#10b981', '🛠️ Suporte / Fornecimento') +
             linhaBucket('A-017', 'Portfólio: Modernização de Sistemas e Infraestrutura',
                         'Portfólio Estratégico', '16', '8.9', '#a855f7', '🏗️ Engenharia & Infra') +
             linhaBucket('A-016', 'Portfólio: Governança Digital, PDTIC 2027–2030 e Inovação',
                         'Portfólio Estratégico', '15', '8.4', '#0369a1', '🧭 Normatização & Comitê') +
             linhaBucket('A-004', 'Gestão e Suporte de Licenciamento de Software',
                         'Rotina Operacional', '1', '0.6', '#f59e0b', '⚖️ Auditoria / Regularização') +
             '</tbody></table></div></div>';

        // SECAO 4
        h += '<div class="card card-body mb-3">';
        h += '<div style="display:flex;justify-content:space-between;align-items:center;' +
             'margin-bottom:14px;flex-wrap:wrap;gap:8px">' +
             '<h3 style="margin:0;font-size:15px;font-weight:700">' +
             '🎯 4. Radar de Risco Alto, Regra dos &ldquo;Poréns&rdquo; &amp; Saneamento Prioritário</h3>' +
             '<span class="badge bg-red-lt">' +
             '9 Processos Risco Alto • 26 Saneamento Prioritário</span></div>';
        h += '<div class="table-responsive"><table style="width:100%;border-collapse:collapse;font-size:12px" class="table table-vcenter card-table table-hover"><thead>' +
             '<tr style="font-size:11px;' +
             'text-transform:uppercase">' +
             '<th style="padding:10px 12px;text-align:left">Processo SEI</th>' +
             '<th style="padding:10px 12px;text-align:left">Objeto / Especificação</th>' +
             '<th style="padding:10px 12px;text-align:left">Bucket</th>' +
             '<th style="padding:10px 12px;text-align:center">Farol / Risco</th>' +
             '<th style="padding:10px 12px;text-align:center">Aging</th>' +
             '<th style="padding:10px 12px;text-align:left">Responsável / Alocação</th>' +
             '<th style="padding:10px 12px;text-align:center">Inspeção</th></tr></thead><tbody>' +
             linhaSeiCritico('137.00012361/2026-00',
                             'Contratação de Serviços de Outsourcing de Impressão (Sinalizado Diretoria)',
                             'A-011. ETP e Riscos', '🚩 Diretoria / Alto', '#f87171', 'Crítico', 'Marcos Tadeu Yamamoto') +
             linhaSeiCritico('137.00013810/2025-47',
                             'Atendimento ao TCE-SP — Regularização de Licenças Autodesk (Parecer Externo)',
                             'A-004. Licenciamento', '🟠 Saneamento / Alto', '#fb923c', 'Crítico', 'Governança SA-GTI') +
             linhaSeiCritico('137.00012783/2025-95',
                             'Processo de Aquisição de 485 Computadores e Notebooks (Parque Informática)',
                             'A-011. ETP e Riscos', '🟡 Monitoramento', '#facc15', 'Atenção', 'SA-GTI / DGD') +
             linhaSeiCritico('018.00004147/2026-63',
                             'Implementação do Decreto Estadual nº 69.540/2025 — Mapeamento de Sistemas',
                             'A-016. Governança/PDTIC', '🟡 Monitoramento', '#facc15', 'Atenção', 'Marcos Tadeu Yamamoto') +
             linhaSeiCritico('137.00013840/2025-53',
                             'Plano Diretor de Tecnologia da Informação e Comunicação (PDTIC 2027–2030)',
                             'A-016. Governança/PDTIC', '🟠 Saneamento (F2)', '#fb923c', '345 dias', 'Luiz Seixeiro / Comitê') +
             linhaSeiCritico('137.00012207/2025-48',
                             'Apuração e Liquidação de Serviços Prestados — Hywork (Intranet SP-Águas)',
                             'A-002. Faturas TI', '🔴 Risco Contratual', '#f87171', 'Crítico', 'Diego Monteiro') +
             linhaSeiCritico('137.00004201/2025-05',
                             'Pagamento de Fatura INTRAGOV por Indenização (Transição Contratual Vivo)',
                             'A-002. Faturas TI', '🔴 Indenizatório', '#f87171', 'Crítico', 'SA-GTI / DIF') +
             linhaSeiCritico('137.00014822/2025-99',
                             'Regularização de Período de Cobertura Contratual — Locação Notebooks DaaS',
                             'A-002. Faturas TI', '🔴 Indenizatório', '#f87171', 'Crítico', 'SA-GTI / DIF') +
             '</tbody></table></div></div>';

        // SECAO 5
        h += '<div class="card card-body mb-3">';
        h += '<h3 style="margin:0 0 14px 0;font-size:15px;font-weight:700">' +
             '👥 5. Distribuição Nominal da Força de Trabalho Técnica &amp; Parecer de Governança</h3>';
        h += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px">' +
             cardCustodiaTecnica('Marcos Tadeu Yamamoto', 'Especialista em Infraestrutura, Redes & Governança',
                                 '18', '4', '4', '10',
                                 'Contrato Intragov V (#19295/2024), Decreto 69.540/2025, Impressão e VRC.', '#38bdf8') +
             cardCustodiaTecnica('Diego Monteiro', 'Especialista em Sistemas, Cloud & Suporte Operacional',
                                 '15', '6', '6', '3',
                                 'Suíte Microsoft Office 365 (#10436/2025), Consultoria, Comitê TI e Hywork.', '#34d399') +
             cardCustodiaTecnica('Rafael Frossard Piteri', 'Analista de Contratações & Softwares Especializados',
                                 '3', '3', '0', '0',
                                 'Licenciamento Autodesk AutoCAD (#11105/2025), ArcGIS (#12421/2026) e TIC.', '#c084fc') +
             '</div>';
        h += '<div class="card card-body mb-3">' +
             '<div style="font-size:12px;font-weight:800;margin-bottom:4px">' +
             '⚖️ Diretriz de Governança e Regra Jurídica dos &ldquo;Poréns&rdquo; (Suspensões Externas):</div>' +
             '<p style="font-size:12px;margin:0;line-height:1.55">Os 143 processos de rotina padrão ' +
             '(atestes PRODESP e faturas mensais de concessionárias) permanecem sob fluxo automatizado de ' +
             'conferência financeira e conciliação SIAFEM. Os processos com pendência de parecer jurídico externo ' +
             '(PGE/TCE-SP) ou transição contratual indenizatória encontram-se isolados na matriz de risco, ' +
             'garantindo transparência integral à Diretoria Colegiada.</p></div>';
        h += '<div style="display:flex;justify-content:space-between;align-items:flex-end;padding-top:14px;' +
             'border-top:1px solid rgba(255,255,255,0.06);font-size:11px">' +
             '<div><strong>Autarquia de Águas do Estado de São Paulo — SP-Águas</strong><br>' +
             'Superintendência de Administração • Gerência de Tecnologia da Informação (SA-GTI)</div>' +
             '<div style="text-align:right"><strong>Luiz Antonio Seixeiro</strong><br>' +
             'Gestor de Projetos Sênior / Governança SA-GTI</div></div></div>';

        return h;
    }

    window.configurarRelatorioDashboard360 = function() {
        var viewDash = document.getElementById('view-dashboards');
        if (!viewDash) return;

        var btnCons = document.getElementById('btn-dash-consolidado');
        if (!btnCons) return;
        var barraPills = btnCons.parentElement;
        if (!barraPills) return;

        if (!document.getElementById('btn-dash-relatorio')) {
            var btnRel = document.createElement('button');
            btnRel.type = 'button';
            btnRel.id = 'btn-dash-relatorio';
            btnRel.className = 'btn btn-secondary pill-filtro-dash';
            btnRel.setAttribute('onclick', "window.alternarModoDashboard('relatorio')");
            btnRel.innerHTML = '📑 Relatório Mensal Executivo (Novembro/2026)';
            barraPills.appendChild(btnRel);
        }

        if (!document.getElementById('subview-dash-relatorio')) {
            var divRel = document.createElement('div');
            divRel.id = 'subview-dash-relatorio';
            divRel.className = 'subview-dash';
            divRel.style.cssText = 'display:none;margin-top:8px;';
            divRel.innerHTML = montarRelatorioDashHtml();
            viewDash.appendChild(divRel);
        }
    };

    var origAlternarDash = window.alternarModoDashboard;
    window.alternarModoDashboard = function(modo) {
        window.configurarRelatorioDashboard360();
        window.modoDashboardAtivo = modo || 'consolidado';

        var viewDash = document.getElementById('view-dashboards');
        var vRelatorio = document.getElementById('subview-dash-relatorio');

        if (modo === 'relatorio') {
            document.querySelectorAll('.pill-filtro-dash').forEach(function(btn) {
                btn.classList.remove('btn-primary', 'active');
                btn.classList.add('btn-secondary');
            });
            var btnRel = document.getElementById('btn-dash-relatorio');
            if (btnRel) {
                btnRel.classList.remove('btn-secondary');
                btnRel.classList.add('btn-primary', 'active');
            }

            if (viewDash) {
                viewDash.querySelectorAll('.subview-dash').forEach(function(el) {
                    if (el.id !== 'subview-dash-relatorio') {
                        el.style.setProperty('display', 'none', 'important');
                    }
                });
            }
            if (vRelatorio) {
                vRelatorio.style.setProperty('display', 'block', 'important');
                vRelatorio.style.opacity = '1';
            }

            var scroller = document.querySelector('.content-scroll') ||
                           document.querySelector('.main-content') || window;
            if (scroller && scroller.scrollTo) {
                try { scroller.scrollTo({ top: 0, behavior: 'smooth' }); } catch(e) {}
            }
            return;
        }

        if (vRelatorio) {
            vRelatorio.style.setProperty('display', 'none', 'important');
        }
        if (viewDash) {
            viewDash.querySelectorAll('.subview-dash').forEach(function(el) {
                if (el.id !== 'subview-dash-relatorio') {
                    el.style.removeProperty('display');
                    el.style.display = 'none';
                }
            });
            var target = document.getElementById('subview-dash-' + modo);
            if (target) {
                target.style.display = 'block';
            }
        }

        if (typeof origAlternarDash === 'function') {
            origAlternarDash(modo);
        }
    };

    window.configurarRelatorioDashboard360();
    document.addEventListener('DOMContentLoaded', function() {
        window.configurarRelatorioDashboard360();
        setTimeout(window.configurarRelatorioDashboard360, 250);
        setTimeout(window.configurarRelatorioDashboard360, 800);
    });
    setInterval(window.configurarRelatorioDashboard360, 800);
})();
