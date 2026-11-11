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

    def test_01_salvar_e_carregar_sessao_dominio_estrito(self):
        cookies = {"PHPSESSID": "sessao_123", "infra_hash": "hash_123"}
        self.motor.salvar_sessao(cookies)
        self.assertTrue(os.path.exists(self.caminho_sessao))
        cookie_obj = self.motor.session.cookies.get("PHPSESSID", domain="sei.sp.gov.br")
        self.assertEqual(cookie_obj, "sessao_123")

    @patch('requests.Session.get')
    def test_02_validar_sessao_ativa(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar&infra_unidade_atual=110050725"
        mock_resp.text = "<html><body>infraMenu id_procedimento Controle de Processos SA-GTI</body></html>"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertTrue(status.get("autenticado"))
        self.assertEqual(status.get("unidade"), "110050725")

    @patch('requests.Session.get')
    def test_03_validar_sessao_erro_500(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))
        self.assertEqual(status.get("codigo"), 500)

    @patch('requests.Session.get')
    def test_04_validar_sessao_corpo_erro_200(self, mock_get):
        """Comprova que resposta HTTP 200 com mensagem de erro no corpo é considerada não autenticada."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar"
        mock_resp.text = "<html><body>InfraException: Sessão inválida ou tempo expirado</body></html>"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))

    @patch('requests.Session.get')
    def test_05_validar_sessao_expirada_govbr(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://minhaarea.sp.gov.br/plataformasp/login"
        mock_resp.text = "<html><body>txtUsuario Gov.br</body></html>"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))

    def test_06_parser_com_atributos_apos_href(self):
        """Comprova extração de processos em links com atributos após href (class, target, etc.)."""
        html = """
        <table>
            <tr><td><a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=501" class="arvore" target="_blank"><span>137.00001234/2026-10</span></a></td></tr>
            <tr><td><a title="Processo" href="controlador.php?acao=procedimento_trabalhar&id_procedimento=502" class="destaque">137.00005678/2026-20</a></td></tr>
        </table>
        """
        res = self.motor.parsear_tabela_caixa(html)
        self.assertTrue(res["sucesso"])
        self.assertEqual(res["total"], 2)
        self.assertEqual(res["processos"][0]["ID_Processo"], "137.00001234/2026-10")
        self.assertEqual(res["processos"][1]["ID_Processo"], "137.00005678/2026-20")

    @patch('requests.Session.get')
    def test_07_caixa_unidade_login_retorna_sucesso_false(self, mock_get):
        """Comprova que redirecionamento para login do Gov.br não retorna falso sucesso."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://minhaarea.sp.gov.br/plataformasp/login"
        mock_resp.text = "<html><body>txtUsuario</body></html>"
        mock_get.return_value = mock_resp

        res = self.motor.listar_caixa_unidade()
        self.assertFalse(res["sucesso"])
        self.assertEqual(res["processos"], [])

if __name__ == '__main__':
    unittest.main()
