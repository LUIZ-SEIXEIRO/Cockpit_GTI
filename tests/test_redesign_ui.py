# -*- coding: utf-8 -*-
import glob
import os
import unittest


class TestRedesignUI(unittest.TestCase):
    def test_01_arquitetura_modular_hallmark_e_contratos_preservados(self):
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(raiz, "painel.html"), "r", encoding="utf-8") as f:
            html = f.read()

        # CSS modular presente e painel.html enxuto
        for css_rel in ("base-legado.css", "tokens.css", "components.css"):
            caminho_css = os.path.join(raiz, "static", "css", css_rel)
            self.assertTrue(os.path.exists(caminho_css), f"CSS ausente: {css_rel}")
            self.assertIn(f"/static/css/{css_rel}", html)

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

        self.assertIn("Hallmark", tokens)
        self.assertIn("#f8fafc", tokens)
        self.assertIn("id=\"sagti-topbar\"", html)
        self.assertIn("#sidebar {\n    display: none !important;", components)
        self.assertIn("#004b87", tokens)
        self.assertIn("#01a75f", tokens)
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


if __name__ == "__main__":
    unittest.main()
