import os, re

paths = [r"C:\Cockpit_GTI\frontend\painel.html", r"C:\Cockpit_GTI\painel.html"]

css_patch = """    .subaba-eixo1-btn, .pill-filtro-dash, .pill-filtro-farol, .pill-cfg, .subtab-conector-btn {
        border-radius: 9999px !important;
        padding: 7px 16px !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        cursor: pointer !important;
    }
    .subaba-eixo1-btn.active, .pill-filtro-dash.active, .pill-filtro-farol.active, .pill-cfg.active, .subtab-conector-btn.active,
    .btn-primary.subaba-eixo1-btn, .btn-primary.pill-filtro-farol, .btn-primary.pill-filtro-dash, .btn-primary.pill-cfg, .btn-primary.subtab-conector-btn {
        background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: 1px solid rgba(56, 189, 248, 0.6) !important;
        box-shadow: 0 4px 18px rgba(14, 165, 233, 0.42), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    }
    .subaba-eixo1-btn:not(.active):not(.btn-primary), 
    .pill-filtro-dash:not(.active):not(.btn-primary), 
    .pill-filtro-farol:not(.active):not(.btn-primary), 
    .pill-cfg:not(.active):not(.btn-primary),
    .subtab-conector-btn:not(.active):not(.btn-primary),
    .btn-secondary.subaba-eixo1-btn, .btn-secondary.pill-filtro-farol, .btn-secondary.pill-filtro-dash, .btn-secondary.pill-cfg, .btn-secondary.subtab-conector-btn {
        background: rgba(15, 23, 42, 0.65) !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: none !important;
    }
    .subaba-eixo1-btn:not(.active):not(.btn-primary):hover, 
    .pill-filtro-dash:not(.active):not(.btn-primary):hover, 
    .pill-filtro-farol:not(.active):not(.btn-primary):hover, 
    .pill-cfg:not(.active):not(.btn-primary):hover,
    .subtab-conector-btn:not(.active):not(.btn-primary):hover {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
    }"""

js_patch = """    window.alternarSubConfig = function(modo) {
        window.subConfigAtivo = modo;
        document.querySelectorAll('.subview-cfg').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.pill-cfg').forEach(btn => {
            btn.classList.remove('btn-primary', 'active');
            btn.classList.add('btn-secondary');
        });

        const target = document.getElementById('subview-cfg-' + modo);
        if (target) target.style.display = 'block';

        const btn = document.getElementById('btn-cfg-' + modo);
        if (btn) {
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-primary', 'active');
        }

        const titulosCfg = {
            'rbac': '🛡️ 1. MATRIZ DE CONTROLE DE ACESSO POR PERFIL (RBAC)',
            'parametros': '⚖️ 2. PARÂMETROS DE GOVERNANÇA, AGING & SPRINTS',
            'conectores': '🔌 3. CONECTORES & CENTRAL DE VARREDURA MULTISSISTÊMICA',
            'agentes': '🤖 4. HUB DE AGENTES DE INTELIGÊNCIA ARTIFICIAL',
            'backup': '💾 5. POLÍTICA DE BACKUP & DRP'
        };

        const tit = document.getElementById('cfg-banner-titulo');
        if (tit) tit.innerText = titulosCfg[modo] || 'CONFIGURAÇÕES SA-GTI';
    };

    window.alternarSubAbaConectores = function(subAba) {
        const paineis = {
            'matriz': document.getElementById('subcon-painel-matriz'),
            'endpoints': document.getElementById('subcon-painel-endpoints'),
            'flags': document.getElementById('subcon-painel-flags')
        };
        for (const k in paineis) {
            if (paineis[k]) {
                paineis[k].style.display = (k === subAba) ? 'block' : 'none';
            }
        }

        const btns = {
            'matriz': document.getElementById('btn-subcon-matriz'),
            'endpoints': document.getElementById('btn-subcon-endpoints'),
            'flags': document.getElementById('btn-subcon-flags')
        };
        for (const k in btns) {
            const btn = btns[k];
            if (btn) {
                if (k === subAba) {
                    btn.classList.add('active', 'btn-primary');
                    btn.classList.remove('btn-secondary');
                } else {
                    btn.classList.remove('active', 'btn-primary');
                    btn.classList.add('btn-secondary');
                }
            }
        }
    };"""

for p in paths:
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()

    is_crlf = '\r\n' in content
    content_norm = content.replace('\r\n', '\n')

    # 1. Atualizar CSS de pílulas ativas e inativas
    old_css_pat = r'\.subaba-eixo1-btn,\s*\.pill-filtro-dash[^{]*\{[^}]*\}[\s\S]*?\.pill-cfg:hover\s*\{[^}]*\}'
    if re.search(old_css_pat, content_norm):
        content_norm = re.sub(old_css_pat, css_patch.strip(), content_norm, count=1)
    else:
        pos_crypto = content_norm.find('id="crypto-executive-theme"')
        if pos_crypto != -1:
            pos_end_style = content_norm.find('</style>', pos_crypto)
            if pos_end_style != -1:
                content_norm = content_norm[:pos_end_style] + "\n" + css_patch + "\n" + content_norm[pos_end_style:]

    # 2. Atualizar JS alternarSubConfig e injetar alternarSubAbaConectores
    js_pat = r'window\.alternarSubConfig\s*=\s*function\s*\(modo\)\s*\{[\s\S]*?cfg-banner-titulo[\s\S]*?\};(?:\s*window\.alternarSubAbaConectores\s*=\s*function[\s\S]*?\};)?'
    if re.search(js_pat, content_norm):
        content_norm = re.sub(js_pat, js_patch, content_norm, count=1)

    # 3. Sincronizar abertura do Eixo 4
    content_norm = content_norm.replace("window.subConfigAtivo = 'rbac';", "window.subConfigAtivo = 'conectores';")
    if "if (typeof window.alternarSubConfig === 'function') window.alternarSubConfig(window.subConfigAtivo || 'conectores');" not in content_norm:
        old_switch = "if (window.renderizarTabelaMotores) window.renderizarTabelaMotores();"
        new_switch = "if (window.renderizarTabelaMotores) window.renderizarTabelaMotores();\n            if (typeof window.alternarSubConfig === 'function') window.alternarSubConfig(window.subConfigAtivo || 'conectores');"
        content_norm = content_norm.replace(old_switch, new_switch, 1)

    final_content = content_norm.replace('\n', '\r\n') if is_crlf else content_norm
    with open(p, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"✅ Arquivo atualizado com sucesso: {p}")
