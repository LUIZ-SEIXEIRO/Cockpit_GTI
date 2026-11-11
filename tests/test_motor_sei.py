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
        """Valida que cookies são vinculados exclusivamente ao domínio do SEI com 0600."""
        cookies = {"PHPSESSID": "sessao_123", "infra_hash": "hash_123"}
        self.motor.salvar_sessao(cookies)
        self.assertTrue(os.path.exists(self.caminho_sessao))
        # Verifica se o cookie está limitado ao domínio sei.sp.gov.br
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
        """Comprova que resposta HTTP 500 não é falsamente considerada sessão ativa."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))
        self.assertEqual(status.get("codigo"), 500)

    @patch('requests.Session.get')
    def test_04_validar_sessao_expirada_govbr(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://minhaarea.sp.gov.br/plataformasp/login"
        mock_resp.text = "<html><body>txtUsuario Gov.br</body></html>"
        mock_get.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))

    def test_05_parser_com_tags_span_aninhadas(self):
        """Comprova extração de processos mesmo quando o texto está envelopado em <span>."""
        html_complexo = """
        <table>
            <tr><td><a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=501"><span>137.00001234/2026-10</span></a></td></tr>
            <tr><td><a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=502"><span class="destaque">137.00005678/2026-20</span></a></td></tr>
        </table>
        """
        res = self.motor.parsear_tabela_caixa(html_complexo)
        self.assertTrue(res["sucesso"])
        self.assertEqual(res["total"], 2)
        self.assertEqual(res["processos"][0]["ID_Processo"], "137.00001234/2026-10")
        self.assertEqual(res["processos"][1]["ID_Processo"], "137.00005678/2026-20")

    @patch('requests.Session.get')
    def test_06_caixa_unidade_erro_retorna_sucesso_false(self, mock_get):
        """Comprova que erro na caixa de entrada não retorna falso sucesso."""
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Acesso negado"
        mock_get.return_value = mock_resp

        res = self.motor.listar_caixa_unidade()
        self.assertFalse(res["sucesso"])
        self.assertEqual(res["processos"], [])

if __name__ == '__main__':
    unittest.main()
