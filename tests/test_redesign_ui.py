# -*- coding: utf-8 -*-
import os
import re
import unittest


class TestRedesignUI(unittest.TestCase):
    def test_01_tema_executivo_limpo_e_contratos_preservados(self):
        caminho = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "painel.html"))
        with open(caminho, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertNotIn('id="crypto-executive-theme"', html)
        self.assertIn("inicializarGlassmorphismV11() { return;", html)
        self.assertIn('id="sagti-clean-executive-theme"', html)
        self.assertIn("Hallmark", html)
        self.assertIn("#f8fafc", html)
        self.assertIn("#004b87", html)
        self.assertIn("#01a75f", html)
        self.assertIn("tabular-nums", html)
        self.assertIn("overflow-x: clip !important;", html)
        self.assertIn("background-image: none !important;", html)

        for cor_slop in ("#4f46e5", "#7c3aed", "#8b5cf6", "#ec4899", "#4c1d95", "#4338ca"):
            self.assertNotIn(cor_slop, html.lower(), f"Cor AI-slop residual encontrada: {cor_slop}")

        bloco = re.search(r'<style id="sagti-clean-executive-theme">.*?</style>', html, re.S)
        self.assertIsNotNone(bloco)
        self.assertNotIn("transition: all", bloco.group(0))

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
