# -*- coding: utf-8 -*-
import os
import unittest


class TestRedesignUI(unittest.TestCase):
    def test_01_tema_executivo_limpo_e_contratos_preservados(self):
        caminho = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "painel.html"))
        with open(caminho, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="sagti-clean-executive-theme"', html)
        self.assertIn("tabular-nums", html)
        self.assertIn("background-image: none !important;", html)
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
