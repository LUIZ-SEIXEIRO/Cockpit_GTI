# -*- coding: utf-8 -*-
import os
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import conector_sei_playwright
import main
from motor_sei import MotorSEI


class TestConectorSEIPlaywright(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.caminho_sessao = os.path.join(self.temp_dir, "sessao_sei.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_extrair_urls_assinadas_html(self):
        html = (
            '<a href="controlador.php?acao=procedimento_controlar&amp;infra_unidade_atual=110050725&amp;infra_hash=abc123def456">Caixa</a>'
            '<a href="https://sei.sp.gov.br/sei/controlador.php?acao=protocolo_pesquisar&infra_hash=999aaa888">Pesquisa</a>'
            '<a href="https://evil.com/sei/controlador.php?acao=procedimento_controlar&infra_hash=deadbeef">Externo</a>'
        )
        urls = conector_sei_playwright.extrair_urls_assinadas_html(html)
        self.assertIn("procedimento_controlar", urls)
        self.assertIn("infra_hash=abc123def456", urls["procedimento_controlar"])
        self.assertIn("protocolo_pesquisar", urls)
        self.assertNotIn("deadbeef", str(urls))

    def test_02_autenticar_sei_playwright_validacao_e_sucesso(self):
        r_vazio = conector_sei_playwright.autenticar_sei_playwright("", "")
        self.assertEqual(r_vazio["codigo"], 400)

        mock_page = MagicMock()
        mock_page.url = "https://sei.sp.gov.br/sei/controlador.php?acao=principal&infra_hash=111222"
        mock_page.content.return_value = '<a href="controlador.php?acao=procedimento_controlar&infra_hash=aaabbbccc111">Caixa</a>'
        mock_page.locator.return_value.all_inner_texts.return_value = ["AGEM", "SPAGUAS"]

        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page
        mock_context.cookies.return_value = [
            {"name": "PRODSEI", "value": "sessao_ok_123", "domain": "sei.sp.gov.br"},
            {"name": "ROUTEID", "value": ".9", "domain": "sei.sp.gov.br"},
            {"name": "OUTRO", "value": "x", "domain": "google.com"},
        ]

        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context
        mock_p = MagicMock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_p
        mock_cm.__exit__.return_value = False

        fake_mod = types.ModuleType("playwright.sync_api")
        fake_mod.sync_playwright = lambda: mock_cm
        fake_pkg = types.ModuleType("playwright")
        fake_pkg.sync_api = fake_mod

        with patch.dict(sys.modules, {"playwright": fake_pkg, "playwright.sync_api": fake_mod}):
            res = conector_sei_playwright.autenticar_sei_playwright("luiz.seixeiro", "senha_sigilosa", orgao="SPAGUAS")

        self.assertTrue(res["sucesso"])
        self.assertEqual(res["cookies"], {"PRODSEI": "sessao_ok_123", "ROUTEID": ".9"})
        self.assertIn("procedimento_controlar", res["urls_assinadas"])
        mock_browser.close.assert_called_once()

        mock_page.url = "https://sei.sp.gov.br/sip/login.php?sigla_sistema=SEI"
        mock_page.content.return_value = '<form id="frmLogin"></form>'
        with patch.dict(sys.modules, {"playwright": fake_pkg, "playwright.sync_api": fake_mod}):
            res_401 = conector_sei_playwright.autenticar_sei_playwright("luiz.seixeiro", "errada")
        self.assertEqual(res_401["codigo"], 401)

    def test_03_motor_sei_persiste_e_usa_urls_assinadas(self):
        motor = MotorSEI(caminho_sessao=self.caminho_sessao)
        url_assinada = "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar&infra_hash=hash_real_999"
        motor.salvar_sessao({"PRODSEI": "abc", "ROUTEID": ".9"}, usuario="luiz", urls_assinadas={"procedimento_controlar": url_assinada})

        motor2 = MotorSEI(caminho_sessao=self.caminho_sessao)
        self.assertEqual(motor2.urls_assinadas.get("procedimento_controlar"), url_assinada)

        html_caixa = '<html><body><form id="frmProcedimentoControlar" action="controlador.php"></form></body></html>'
        mock_resp = MagicMock(status_code=200, text=html_caixa, url=url_assinada)
        with patch.object(motor2.sessao, "get", return_value=mock_resp) as mock_get:
            res = motor2.listar_caixa_unidade()
            self.assertTrue(res.get("sucesso"))
            mock_get.assert_called_once_with(url_assinada, timeout=15)

    def test_04_rota_flask_sei_login_autenticacao_e_contrato(self):
        with main.app.test_client() as client:
            with patch.dict(os.environ, {"API_TOKEN": "token_pw_teste"}):
                self.assertEqual(client.post("/api/v1/sei/login", json={"usuario": "u", "senha": "s"}).status_code, 401)

                with patch("conector_sei_playwright.autenticar_sei_playwright", return_value={
                    "sucesso": True,
                    "codigo": 200,
                    "cookies": {"PRODSEI": "xyz", "ROUTEID": ".9"},
                    "urls_assinadas": {"procedimento_controlar": "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar&infra_hash=h1"},
                    "unidade": "110050725",
                }):
                    with patch.object(main.motor_sei_instance, "salvar_sessao", return_value=True) as mock_save:
                        r_ok = client.post(
                            "/api/v1/sei/login",
                            headers={"Authorization": "Bearer token_pw_teste"},
                            json={"usuario": "luiz.seixeiro", "senha": "segredo_nao_logar", "orgao": "SPAGUAS"},
                        )
                self.assertEqual(r_ok.status_code, 200)
                dados = r_ok.get_json()
                self.assertTrue(dados.get("sucesso"))
                self.assertNotIn("segredo_nao_logar", str(dados))
                mock_save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
