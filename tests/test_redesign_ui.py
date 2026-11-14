# -*- coding: utf-8 -*-
import glob
import os
import re
import unittest


class TestRedesignUI(unittest.TestCase):
    @staticmethod
    def _contraste(foreground, background):
        def luminancia(cor):
            canais = [int(cor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            canais = [
                canal / 12.92 if canal <= 0.04045 else ((canal + 0.055) / 1.055) ** 2.4
                for canal in canais
            ]
            return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]

        clara, escura = sorted(
            (luminancia(foreground), luminancia(background)),
            reverse=True,
        )
        return (clara + 0.05) / (escura + 0.05)

    def test_tokens_de_cor_atendem_contraste_wcag_aa(self):
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(raiz, "static", "css", "tokens.css"), "r", encoding="utf-8") as f:
            tokens = f.read()

        self.assertIn("--sagti-success-contrast: #00502e;", tokens)
        self.assertIn("color: #052e1b;", tokens)
        self.assertIn("color: #006b3c;", tokens)
        for foreground, background in (
            ("#004b87", "#ffffff"),
            ("#0369a1", "#ffffff"),
            ("#006b3c", "#ffffff"),
            ("#ffffff", "#004b87"),
            ("#020617", "#0284c7"),
            ("#052e1b", "#01a75f"),
        ):
            self.assertGreaterEqual(
                self._contraste(foreground, background),
                4.5,
                f"Contraste insuficiente: {foreground} sobre {background}",
            )

    def test_01_arquitetura_modular_hallmark_e_contratos_preservados(self):
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(raiz, "painel.html"), "r", encoding="utf-8") as f:
            html = f.read()

        # Foundation local Tabler and structural compatibility are present.
        for css_rel in ("base-legado.css", "tokens.css", "components.css"):
            caminho_css = os.path.join(raiz, "static", "css", css_rel)
            self.assertTrue(os.path.exists(caminho_css), f"CSS ausente: {css_rel}")

        tabler_css = os.path.join(raiz, "static", "vendor", "tabler", "tabler.min.css")
        tabler_js = os.path.join(raiz, "static", "vendor", "tabler", "tabler.min.js")
        self.assertTrue(os.path.isfile(tabler_css), "Tabler CSS local ausente")
        self.assertTrue(os.path.isfile(tabler_js), "Tabler JavaScript local ausente")
        self.assertIn('/static/vendor/tabler/tabler.min.css', html)
        self.assertIn('/static/vendor/tabler/tabler.min.js', html)
        self.assertNotIn('/static/css/base-legado.css', html)
        self.assertNotIn('/static/estilo_spaguas.css', html)
        self.assertLess(html.index('/static/vendor/tabler/tabler.min.css'), html.index('/static/css/tokens.css'))
        self.assertLess(html.index('/static/css/tokens.css'), html.index('/static/css/components.css'))
        with open(os.path.join(raiz, "static", "css", "base-legado.css"), "r", encoding="utf-8") as f:
            compat = f.read()
        self.assertLess(len(compat), 2000, "CSS de compatibilidade deve conter apenas estrutura")
        self.assertNotRegex(compat, r"(?i)(?:color|background|font-family)\s*:")

        visual_corpus = html
        for js_rel in (
            "cockpit-core.js",
            "relatorio-openproject.js",
            "relatorio-dashboards.js",
            "esteira-ia.js",
            "mesa-trabalho.js",
        ):
            caminho_js = os.path.join(raiz, "static", "js", js_rel)
            self.assertTrue(os.path.exists(caminho_js), f"JS ausente: {js_rel}")
            self.assertIn(f"/static/js/{js_rel}", html)
            with open(caminho_js, "r", encoding="utf-8") as f:
                visual_corpus += "\n" + f.read()

        estilo_visual_inline_legado = re.compile(
            r"""style\s*=\s*["'][^"']*(?:background(?:-color)?\s*:|color\s*:|"""
            r"""border(?:-color)?\s*:|box-shadow\s*:|backdrop-filter\s*:|linear-gradient|"""
            r"""font-size\s*:\s*(?:9|10)px)|"""
            r"""\.style\.(?:background(?:Color)?|color|border(?:Color)?|boxShadow)\s*=|"""
            r"""style\.cssText\s*=\s*["'][^"']*(?:background|color\s*:|border\s*:|"""
            r"""box-shadow\s*:|backdrop-filter\s*:|linear-gradient)""",
            re.IGNORECASE,
        )
        self.assertNotRegex(visual_corpus, estilo_visual_inline_legado)

        self.assertLess(html.count("\n"), 10000, "painel.html ainda esta monolitico")

        # Blocos legados de glassmorphism removidos
        for legado in (
            'id="crypto-executive-theme"',
            'id="cockpit-glassmorphism-v11"',
            'id="cockpit-glass-harmony-v11"',
            'id="glassmorphism-ultimate-v11"',
            'id="glassmorphism-enforcer-v11"',
        ):
            self.assertNotIn(legado, html, f"Bloco legado ainda presente: {legado}")

        with open(os.path.join(raiz, "static", "css", "tokens.css"), "r", encoding="utf-8") as f:
            tokens = f.read()
        with open(os.path.join(raiz, "static", "css", "components.css"), "r", encoding="utf-8") as f:
            components = f.read()

        self.assertIn("--tblr-primary: #004b87;", tokens)
        self.assertIn("--tblr-info: #0369a1;", tokens)
        self.assertIn("--tblr-success: #01a75f;", tokens)
        self.assertIn("--tblr-body-bg: #f8fafc;", tokens)
        self.assertIn("--tblr-bg-surface: #ffffff;", tokens)
        self.assertIn("--tblr-border-color: #e2e8f0;", tokens)
        self.assertIn("--tblr-font-sans-serif:", tokens)
        self.assertIn("id=\"sagti-topbar\"", html)
        self.assertIn('class="navbar navbar-expand-md d-print-none"', html)
        self.assertIn('class="sagti-top-nav nav nav-pills"', html)
        self.assertIn("#sidebar {\n    display: none;", components)
        self.assertIn("tabular-nums", components)
        self.assertNotIn("transition: all", components)

        for cor_slop in ("#4f46e5", "#7c3aed", "#8b5cf6", "#ec4899", "#4c1d95", "#4338ca"):
            self.assertNotIn(cor_slop, html.lower())
            self.assertNotIn(cor_slop, tokens.lower())
            self.assertNotIn(cor_slop, components.lower())

        # Contratos criticos preservados (HTML + JS modular)
        js_corpus = html
        for p in glob.glob(os.path.join(raiz, "static", "js", "*.js")):
            with open(p, "r", encoding="utf-8") as fj:
                js_corpus += "\n" + fj.read()

        for marcador_html in ('id="cockpit-motor-sei-widget"', 'id="input-usuario-sei-pw"'):
            self.assertIn(marcador_html, html)

        for rota in ("/api/v1/sei/login", "/api/v1/sei/status", "/api/v1/ia/chat", "/api/v1/ia/revisar_processo"):
            self.assertIn(rota, js_corpus)

    def test_cockpit_dashboard_views_are_compact_tabler_controls(self):
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(raiz, "painel.html"), "r", encoding="utf-8") as f:
            html = f.read()
        with open(os.path.join(raiz, "static", "css", "components.css"), "r", encoding="utf-8") as f:
            components = f.read()
        with open(os.path.join(raiz, "static", "js", "cockpit-core.js"), "r", encoding="utf-8") as f:
            cockpit_js = f.read()

        nav = re.search(
            r'<div class="sagti-dashboard-views"[^>]*>(.*?)</div>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(nav)
        self.assertEqual(len(re.findall(r"<button\b", nav.group(1))), 6)
        for button_id in (
            "btn-dash-consolidado",
            "btn-dash-esteira",
            "btn-dash-rotina",
            "btn-dash-portfolio",
            "btn-dash-farois",
            "btn-dash-relatorio",
        ):
            self.assertIn(f'id="{button_id}"', nav.group(1))

        self.assertRegex(components, r"\.sagti-dashboard-views\s*\{[^}]*flex-wrap:\s*nowrap")
        self.assertRegex(components, r"\.sagti-dashboard-views\s*\{[^}]*overflow-x:\s*auto")
        self.assertIn("padding: 5px 10px;", components)
        self.assertIn("font-size: 12px;", components)
        self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr));", components)
        self.assertIn("window.abrirRelatorioMensalExecutivo = function()", cockpit_js)
        self.assertIn("atualizarBotaoModoDashboard(botao, botao.id === 'btn-dash-' + modo)", cockpit_js)
        self.assertIn("'/api/v1/processos', '/api/v1/sei/processos'", cockpit_js)
        self.assertIn("function possuiIndicadoresExecutivos()", cockpit_js)


if __name__ == "__main__":
    unittest.main()
