import unittest, os, json
from unittest.mock import patch, MagicMock
from motor_sei import MotorSEI

class TestMotorSEI(unittest.TestCase):
    def setUp(self):
        self.motor = MotorSEI(caminho_sessao="tests/sessao_teste.json")

    def tearDown(self):
        if os.path.exists("tests/sessao_teste.json"):
            os.remove("tests/sessao_teste.json")

    def test_01_salvar_e_carregar_sessao(self):
        """Valida salvamento e leitura segura de cookies."""
        cookies = {"PHPSESSID": "sessao_teste_123", "infra_hash": "hash_teste"}
        self.motor.salvar_sessao(cookies)
        self.assertTrue(os.path.exists("tests/sessao_teste.json"))
        self.assertEqual(self.motor.session.cookies.get("PHPSESSID"), "sessao_teste_123")

    @patch('requests.Session.get')
    def test_02_validar_sessao_ativa(self, mock_get):
        """Valida detecção de sessão autenticada na SA-GTI."""
        mock_resp = MagicMock()
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar&infra_unidade_atual=110050725"
        mock_resp.text = "<html><body>Controle de Processos SA-GTI</body></html>"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertTrue(status.get("autenticado"))
        self.assertEqual(status.get("unidade"), "110050725")

    @patch('requests.Session.get')
    def test_03_validar_sessao_expirada(self, mock_get):
        """Valida detecção de redirecionamento para o Gov.br / Plataforma SP."""
        mock_resp = MagicMock()
        mock_resp.url = "https://minhaarea.sp.gov.br/plataformasp/login"
        mock_resp.text = "<html><body>txtUsuario Gov.br</body></html>"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))

    def test_04_parsear_tabela_processos(self):
        """Valida extração de processos em HTML padrão do SEI 4.1.5."""
        html_simulado = """
        <table>
            <tr><td><a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=101&infra_unidade=110050725">137.00001111/2026-10</a></td></tr>
            <tr><td><a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=102&infra_unidade=110050725">137.00002222/2026-20</a></td></tr>
        </table>
        """
        resultado = self.motor.parsear_tabela_caixa(html_simulado)
        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["total"], 2)
        self.assertEqual(resultado["processos"][0]["ID_Processo"], "137.00001111/2026-10")
        self.assertEqual(resultado["processos"][0]["id_procedimento"], "101")

if __name__ == '__main__':
    unittest.main()
