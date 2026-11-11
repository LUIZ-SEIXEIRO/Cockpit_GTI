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

    def test_01_salvar_sessao_mkstemp_0600(self):
        cookies = {"PHPSESSID": "sessao_123"}
        self.motor.salvar_sessao(cookies)
        self.assertTrue(os.path.exists(self.caminho_sessao))
        cookie_obj = self.motor.session.cookies.get("PHPSESSID", domain="sei.sp.gov.br")
        self.assertEqual(cookie_obj, "sessao_123")

    @patch('requests.Session.request')
    def test_02_validar_sessao_ativa_form_id(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.is_redirect = False
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php?acao=procedimento_controlar&infra_unidade_atual=110050725"
        mock_resp.text = "<html><body><form id='frmProcedimentoControlar'><table class='infraTabela'>Controle de Processos id_procedimento</table></form></body></html>"
        mock_req.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertTrue(status.get("autenticado"))

    @patch('requests.Session.request')
    def test_03_rejeitar_action_em_dominio_externo(self, mock_req):
        """Comprova que action em domínio externo (mesmo com path /sei/controlador.php) é rejeitada."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.is_redirect = False
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php"
        mock_resp.text = "<html><body><form action='https://fake.com/sei/controlador.php'><table class='infraTabela'>id_procedimento</table></form></body></html>"
        mock_req.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))

    @patch('requests.Session.request')
    def test_04_rejeitar_tabela_apenas_em_script(self, mock_req):
        """Comprova que marcador infratabela contido exclusivamente dentro de <script> é descartado."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.is_redirect = False
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php"
        mock_resp.text = "<html><body><form id='frmProcedimentoControlar'><script>var x = 'infraTabela id_procedimento';</script>Sem tabela no DOM</form></body></html>"
        mock_req.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))

    def test_05_parser_com_entidade_amp(self):
        html = """
        <table>
            <tr><td><a href='controlador.php?acao=procedimento_trabalhar&amp;id_procedimento=701'>137.00001111/2026-10</a></td></tr>
        </table>
        """
        res = self.motor.parsear_tabela_processos(html)
        self.assertTrue(res["sucesso"])
        self.assertEqual(res["total"], 1)
        self.assertEqual(res["processos"][0]["ID_Processo"], "137.00001111/2026-10")

if __name__ == '__main__':
    unittest.main()
