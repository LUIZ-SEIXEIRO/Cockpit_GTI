target = r"C:\Cockpit_GTI\frontend\painel.html"
with open(target, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

css_remover_banner = """
<style id="css-remover-banner-topo">
    /* Remove o banner azul pesado de todas as telas */
    .page-banner, #dash-banner-principal {
        display: none !important;
    }
    .content-scroll {
        padding-top: 14px !important;
    }
</style>
"""

import re
html = re.sub(r'<style id="css-remover-banner-topo">[\s\S]*?</style>', '', html)

if "</head>" in html:
    html = html.replace("</head>", css_remover_banner + "\n</head>", 1)
else:
    html = css_remover_banner + "\n" + html

with open(target, "w", encoding="utf-8", errors="ignore") as f:
    f.write(html)
print("✅ Banner azul removido com sucesso!")
