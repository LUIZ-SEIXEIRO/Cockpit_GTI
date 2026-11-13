# -*- coding: utf-8 -*-
import os
import unittest


class TestRedesignUI(unittest.TestCase):
    def test_01_arquitetura_modular_hallmark_e_contratos_preservados(self):
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(raiz, "painel.html"), "r", encoding="utf-8") as f:
            html = f.read()
        with open(os.path.join(raiz, "static", "css", "tokens.css"), "r", encoding="utf-8") as f:
            tokens = f.read()
        with open(os.path.join(raiz, "static", "css", "components.css"), "r", encoding="utf-8") as f:
            components = f.read()

        # Links modulares presentes
        self.assertIn('/static/css/tokens.css', html)
        self.assertIn('/static/css/components.css', html)

        # Blocos legados de glassmorphism removidos
        for legado in (
            'id="crypto-executive-theme"',
            'id="cockpit-glassmorphism-v11"',
            'id="cockpit-glass-harmony-v11"',
            'id="glassmorphism-ultimate-v11"',
            'id="glassmorphism-enforcer-v11"',
        ):
            self.assertNotIn(legado, html, f"Bloco legado ainda presente: {legado}")

        # Tokens e regras Hallmark Floor
        self.assertIn("Hallmark", tokens)
        self.assertIn("#f8fafc", tokens)
        self.assertIn("#004b87", tokens)
        self.assertIn("#01a75f", tokens)
        self.assertIn("tabular-nums", components)
        self.assertIn("overflow-x: clip !important;", components)
        self.assertNotIn("transition: all", components)

        for cor_slop in ("#4f46e5", "#7c3aed", "#8b5cf6", "#ec4899", "#4c1d95", "#4338ca"):
            self.assertNotIn(cor_slop, html.lower(), f"Cor AI-slop residual em painel.html: {cor_slop}")
            self.assertNotIn(cor_slop, tokens.lower(), f"Cor AI-slop residual em tokens.css: {cor_slop}")
            self.assertNotIn(cor_slop, components.lower(), f"Cor AI-slop residual em components.css: {cor_slop}")

        # Contratos criticos preservados
        for marcador in (
            'id="cockpit-motor-sei-widget"',
            'id="input-usuario-sei-pw"',
            "/api/v1/sei/login",
            "/api/v1/sei/status",
            "/api/v1/ia/chat",
            "/api/v1/ia/revisar_processo",
        ):
            self.assertIn(marcador, html, f"Marcador ausente apos redesign: {marcador}")


if __name__ == "__main__":
    unittest.main()
