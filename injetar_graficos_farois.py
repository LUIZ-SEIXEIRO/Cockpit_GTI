# -*- coding: utf-8 -*-
import os, sys, re

print("=" * 70)
print(" CORREÇÃO: INJEÇÃO DOS GRÁFICOS REAIS DE FARÓIS E GARGALOS")
print(" Tela: Central de Dashboards ──> Faróis & Gargalos (87)")
print("=" * 70)

caminhos = [
    os.path.join(os.getcwd(), "frontend", "painel.html"),
    os.path.join(os.getcwd(), "painel.html")
]

svg_resp_inner = '''<div class="chart-body" id="chart-radar-resp" style="min-height: 250px; display:flex; flex-direction:column; padding:10px 14px;">
    <svg viewBox="0 0 500 220" width="100%" height="100%" preserveAspectRatio="none" style="font-family:sans-serif;">
        <line x1="160" y1="20" x2="160" y2="180" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />
        <line x1="240" y1="20" x2="240" y2="180" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />
        <line x1="320" y1="20" x2="320" y2="180" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />
        <line x1="400" y1="20" x2="400" y2="180" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />
        <line x1="480" y1="20" x2="480" y2="180" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />

        <text x="150" y="52" fill="#cbd5e1" font-size="11" font-weight="600" text-anchor="end">Marcos Tadeu Yamamoto</text>
        <rect x="160" y="36" width="288" height="24" fill="#0284c7" rx="4" />
        <text x="304" y="52" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">18</text>

        <text x="150" y="102" fill="#cbd5e1" font-size="11" font-weight="600" text-anchor="end">Diego Monteiro</text>
        <rect x="160" y="86" width="240" height="24" fill="#0284c7" rx="4" />
        <text x="280" y="102" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">15</text>

        <text x="150" y="152" fill="#cbd5e1" font-size="11" font-weight="600" text-anchor="end">Rafael Frossard Piteri</text>
        <rect x="160" y="136" width="48" height="24" fill="#0284c7" rx="4" />
        <text x="184" y="152" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">3</text>

        <line x1="160" y1="185" x2="480" y2="185" stroke="rgba(255,255,255,0.2)" />
        <text x="160" y="202" fill="#94a3b8" font-size="10" text-anchor="middle">0</text>
        <text x="240" y="202" fill="#94a3b8" font-size="10" text-anchor="middle">5</text>
        <text x="320" y="202" fill="#94a3b8" font-size="10" text-anchor="middle">10</text>
        <text x="400" y="202" fill="#94a3b8" font-size="10" text-anchor="middle">15</text>
        <text x="480" y="202" fill="#94a3b8" font-size="10" text-anchor="middle">20</text>
    </svg>
</div>'''

svg_stacked_inner = '''<div class="chart-body" id="chart-radar-stacked" style="min-height: 280px; display:flex; flex-direction:column; padding:10px 14px;">
    <div style="display:flex; justify-content:center; flex-wrap:wrap; gap:16px; margin-bottom:12px; font-size:11px;">
        <span style="display:inline-flex; align-items:center; gap:5px; color:#cbd5e1;"><span style="width:10px; height:10px; border-radius:2px; background:#64748b;"></span> Rotina Padrão</span>
        <span style="display:inline-flex; align-items:center; gap:5px; color:#cbd5e1;"><span style="width:10px; height:10px; border-radius:2px; background:#f59e0b;"></span> 3 - Monitoramento Ativo</span>
        <span style="display:inline-flex; align-items:center; gap:5px; color:#cbd5e1;"><span style="width:10px; height:10px; border-radius:2px; background:#ea580c;"></span> 2 - Saneamento Prioritário</span>
        <span style="display:inline-flex; align-items:center; gap:5px; color:#cbd5e1;"><span style="width:10px; height:10px; border-radius:2px; background:#10b981;"></span> 4 - Fluxo Normal</span>
    </div>
    <div style="flex:1; width:100%; overflow:hidden;">
        <svg viewBox="0 0 560 210" width="100%" height="100%" preserveAspectRatio="none" style="font-family:sans-serif;">
            <line x1="45" y1="20" x2="545" y2="20" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />
            <text x="38" y="24" fill="#94a3b8" font-size="9" text-anchor="end">60</text>
            <line x1="45" y1="55" x2="545" y2="55" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />
            <text x="38" y="59" fill="#94a3b8" font-size="9" text-anchor="end">40</text>
            <line x1="45" y1="90" x2="545" y2="90" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />
            <text x="38" y="94" fill="#94a3b8" font-size="9" text-anchor="end">20</text>
            <line x1="45" y1="125" x2="545" y2="125" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3" />
            <text x="38" y="129" fill="#94a3b8" font-size="9" text-anchor="end">0</text>
            <line x1="45" y1="125" x2="545" y2="125" stroke="rgba(255,255,255,0.2)" />

            <rect x="60" y="29" width="36" height="16" fill="#10b981" rx="2" />
            <text x="78" y="41" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">9</text>
            <rect x="60" y="45" width="36" height="31" fill="#ea580c" />
            <text x="78" y="64" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">18</text>
            <rect x="60" y="76" width="36" height="49" fill="#f59e0b" rx="2" />
            <text x="78" y="104" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">28</text>
            <text x="78" y="145" fill="#94a3b8" font-size="10" text-anchor="middle">A-011. ETP</text>

            <rect x="130" y="53" width="36" height="72" fill="#64748b" rx="2" />
            <text x="148" y="92" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">41</text>
            <text x="148" y="145" fill="#94a3b8" font-size="10" text-anchor="middle">A-001. Atestes</text>

            <rect x="200" y="69" width="36" height="56" fill="#64748b" rx="2" />
            <text x="218" y="100" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">32</text>
            <text x="218" y="145" fill="#94a3b8" font-size="10" text-anchor="middle">A-002. Faturas</text>

            <rect x="270" y="92" width="36" height="33" fill="#64748b" rx="2" />
            <text x="288" y="112" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">19</text>
            <text x="288" y="145" fill="#94a3b8" font-size="10" text-anchor="middle">A-010. Suporte</text>

            <rect x="340" y="97" width="36" height="4" fill="#10b981" rx="1" />
            <rect x="340" y="101" width="36" height="3" fill="#ea580c" />
            <rect x="340" y="104" width="36" height="21" fill="#f59e0b" rx="2" />
            <text x="358" y="118" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">12</text>
            <text x="358" y="145" fill="#94a3b8" font-size="10" text-anchor="middle">A-017. Infra</text>

            <rect x="410" y="99" width="36" height="9" fill="#ea580c" rx="1" />
            <text x="428" y="107" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">5</text>
            <rect x="410" y="108" width="36" height="17" fill="#f59e0b" rx="2" />
            <text x="428" y="121" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">10</text>
            <text x="428" y="145" fill="#94a3b8" font-size="10" text-anchor="middle">A-016. PDTIC</text>

            <rect x="480" y="123" width="36" height="2" fill="#ea580c" rx="1" />
            <text x="498" y="145" fill="#94a3b8" font-size="10" text-anchor="middle">A-004. Licenças</text>
        </svg>
    </div>
</div>'''

for caminho in caminhos:
    if not os.path.exists(caminho):
        continue

    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # Substituição robusta do Gráfico 1 (Responsável Técnico)
    p1 = r'<div class="chart-header">Processos por Responsável Técnico</div>[\s\S]*?<div class="table-card"'
    r1 = '<div class="chart-header">Processos por Responsável Técnico</div>\n                            ' + svg_resp_inner + '\n                        </div>\n\n                        <div class="table-card"'
    html = re.sub(p1, r1, html, count=1)

    # Substituição robusta do Gráfico 2 (Bucket OpenProject Stacked)
    p2 = r'<div class="chart-header">Bucket OpenProject fatiado por Farol de Criticidade</div>[\s\S]*?<!-- SELETOR DE MODOS DE VISUALIZAÇÃO \(PILLS\) -->'
    r2 = '''<div class="chart-header">Bucket OpenProject fatiado por Farol de Criticidade</div>
                        ''' + svg_stacked_inner + '''
                    </div>
                </div>
            </div>

            <!-- SELETOR DE MODOS DE VISUALIZAÇÃO (PILLS) -->'''
    html = re.sub(p2, r2, html, count=1)

    open_divs = len(re.findall(r'<div\b', html, re.IGNORECASE))
    close_divs = len(re.findall(r'</div\b', html, re.IGNORECASE))
    diff = open_divs - close_divs

    if diff == 0:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[*] {caminho}: 2 Gráficos de Faróis & Gargalos injetados com sucesso! (Div balance = 0)")
    else:
        print(f"[!] Erro de balanceamento de divs em {caminho}: diff={diff}")

print("\n" + "=" * 70)
print(" ATUALIZAÇÃO CONCLUÍDA")
print("=" * 70)
