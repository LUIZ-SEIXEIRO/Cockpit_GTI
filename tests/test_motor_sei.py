import unittest, os, json, tempfile
from unittest.mock import patch, MagicMock
from motor_sei import MotorSEI

class TestMotorSEI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.caminho_sessao = os.path.join(self.temp_dir.name, "sessao.json")
        self.motor = MotorSEI(caminho_sessao=self.caminho_sessao)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_salvar_sessao_0600_e_secure(self):
        cookies = {"PHPSESSID": "sessao_123"}
        self.motor.salvar_sessao(cookies)
        self.assertTrue(os.path.exists(self.caminho_sessao))
        cookie_obj = self.motor.session.cookies.get("PHPSESSID", domain="sei.sp.gov.br")
        self.assertEqual(cookie_obj, "sessao_123")

    @patch('requests.Session.get')
    def test_02_validar_sessao_ativa_com_elementos_positivos(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar&infra_unidade_atual=110050725"
        mock_resp.text = "<html><body><table class='infraTabela'>Controle de Processos id_procedimento</table></body></html>"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertTrue(status.get("autenticado"))
        self.assertEqual(status.get("unidade"), "110050725")

    @patch('requests.Session.get')
    def test_03_rejeitar_pagina_200_sem_elementos_positivos(self, mock_get):
        """Comprova que resposta 200 genérica sem elementos do SEI é considerada não autenticada."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php"
        mock_resp.text = "<html><body>Portal Genérico sem Marcação SEI</body></html>"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))

    @patch('requests.Session.get')
    def test_04_rejeitar_redirecionamento_login(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://minhaarea.sp.gov.br/plataformasp"
        mock_resp.text = "<html><body>txtUsuario Gov.br</body></html>"
        mock_get.return_value = mock_resp

        res = self.motor.listar_caixa_unidade()
        self.assertFalse(res["sucesso"])
        self.assertEqual(res["processos"], [])

    def test_05_parser_aspas_simples_e_filtro_acoes(self):
        """Comprova suporte a aspas simples e descarte de outras ações com id_procedimento."""
        html = """
        <table>
            <!-- Link válido de processo com aspas simples -->
            <tr><td><a href='controlador.php?acao=procedimento_trabalhar&id_procedimento=801' class='arvore'>137.00001111/2026-10</a></td></tr>
            <!-- Outra ação (documento) que NÃO deve ser interpretada como processo -->
            <tr><td><a href="controlador.php?acao=documento_visualizar&id_procedimento=802">Visualizar Documento</a></td></tr>
            <!-- Link válido com aspas duplas e span -->
            <tr><td><a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=803"><span>137.00002222/2026-20</span></a></td></tr>
        </table>
        """
        res = self.motor.parsear_tabela_processos(html)
        self.assertTrue(res["sucesso"])
        self.assertEqual(res["total"], 2)
        self.assertEqual(res["processos"][0]["ID_Processo"], "137.00001111/2026-10")
        self.assertEqual(res["processos"][1]["ID_Processo"], "137.00002222/2026-20")

if __name__ == '__main__':
    unittest.main()
