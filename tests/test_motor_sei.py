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
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.is_redirect = False
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php"
        mock_resp.text = "<html><body><form id='frmProcedimentoControlar' action='https://fake.com/sei/controlador.php'><table class='infraTabela'>id_procedimento</table></form></body></html>"
        mock_req.return_value = mock_resp

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("autenticado"))

    @patch('requests.Session.request')
    def test_04_rejeitar_tabela_dentro_de_script(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.is_redirect = False
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php"
        mock_resp.text = "<html><body><form id='frmProcedimentoControlar'><script>var html = '<table class=infraTabela>id_procedimento</table>';</script>Sem tabela ativa</form></body></html>"
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

    def test_06_falha_fsync_aborta_substituicao_e_limpa(self):
        """Valida que erro de fsync aborta os.replace, preserva a sessão e remove temporários."""
        cookies_iniciais = {"PHPSESSID": "sessao_original"}
        self.motor.salvar_sessao(cookies_iniciais)
        self.assertEqual(self.motor.session.cookies.get("PHPSESSID", domain="sei.sp.gov.br"), "sessao_original")

        with patch('os.fsync', side_effect=OSError("Falha simulada de fsync")):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_nova_corrompida"})

        # 1. Garante que a sessão original permaneceu intacta
        self.motor.carregar_sessao()
        self.assertEqual(self.motor.session.cookies.get("PHPSESSID", domain="sei.sp.gov.br"), "sessao_original")

        # 2. Comprova formalmente que nenhum arquivo temporário .tmp sobrou no diretório
        arquivos_tmp = [f for f in os.listdir(self.temp_dir.name) if f.endswith('.tmp')]
        self.assertEqual(arquivos_tmp, [], f"Resíduos temporários não foram limpos: {arquivos_tmp}")

def test_07_falha_fsync_diretorio_executa_rollback(self):
        """Comprova que falha de fsync do diretório reverte o arquivo para a sessão anterior no disco e na memória."""
        cookies_iniciais = {"PHPSESSID": "sessao_original_estavel"}
        self.motor.salvar_sessao(cookies_iniciais)
        self.assertEqual(self.motor.session.cookies.get("PHPSESSID", domain="sei.sp.gov.br"), "sessao_original_estavel")

        fsync_orig = os.fsync
        chamadas_fsync = []
        def fake_fsync(fd):
            chamadas_fsync.append(fd)
            if len(chamadas_fsync) > 1:
                raise OSError("Falha simulada no fsync do diretório pós-replace")
            return fsync_orig(fd)

        with patch('os.O_DIRECTORY', create=True, new=1), patch('os.fsync', side_effect=fake_fsync):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_nova_corrompida"})

        # 1. Comprova que o arquivo em disco sofreu rollback para o estado original
        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            dados_disco = json.load(f)
        self.assertEqual(dados_disco["cookies"]["PHPSESSID"], "sessao_original_estavel")

        # 2. Comprova que a memória da sessão permaneceu estritamente no estado original
        self.assertEqual(self.motor.session.cookies.get("PHPSESSID", domain="sei.sp.gov.br"), "sessao_original_estavel")

if __name__ == '__main__':
    unittest.main()
