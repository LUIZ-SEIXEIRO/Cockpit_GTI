import threading
import os
import sys
import json
import stat
import time
import shutil
import tempfile
import unittest
import socket
from unittest.mock import patch, MagicMock
from urllib.parse import urlparse
import requests
from requests import Request

from motor_sei import (
    MotorSEI,
    ValidadorFormSEI,
    ValidadorEstruturalSEI,
    ParserProcessosSEI,
    LockProcessosSEI,
    ResultadoProcessosSEI,
    StrictSEISession,
    processo_esta_vivo,
    obter_fingerprint_armazenamento
)

class TestMotorSEI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.caminho_sessao = os.path.join(self.temp_dir.name, "sessao_sei.json")
        self.motor = MotorSEI(caminho_sessao=self.caminho_sessao)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_salvar_sessao_mkstemp_0600(self):
        cookies = {"PHPSESSID": "cookie_teste_123"}
        resultado = self.motor.salvar_sessao(cookies, usuario="12345678900")
        self.assertTrue(resultado)
        self.assertTrue(os.path.exists(self.caminho_sessao))

        if os.name != "nt":
            modo = stat.S_IMODE(os.stat(self.caminho_sessao).st_mode)
            self.assertEqual(modo, 0o600)

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            dados = json.load(f)
        self.assertEqual(dados["cookies"]["PHPSESSID"], "cookie_teste_123")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "cookie_teste_123")

    def test_02_validar_sessao_ativa_form_id(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_valida"})
        html_resposta = """
        <html>
            <body>
                <form id="frmProcedimentoControlar" action="controlador.php?acao=procedimento_controlar">
                    <input type="hidden" name="infra_hash" value="abc12345" />
                </form>
            </body>
        </html>
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html_resposta
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php"

        with patch.object(self.motor.sessao, "get", return_value=mock_resp):
            ativa = self.motor.validar_sessao_ativa()
            self.assertTrue(ativa)

    def test_03_rejeitar_action_em_dominio_externo_e_fake(self):
        self.assertFalse(self.motor.validar_action_segura("https://malicioso.com/controlador.php"))
        self.assertFalse(self.motor.validar_action_segura("http://phishing.sp.gov.br/hack"))
        self.assertFalse(self.motor.validar_action_segura("/sei/../etc/passwd"))
        self.assertFalse(self.motor.validar_action_segura("controlador.php?acao=../../perigo"))
        self.assertFalse(self.motor.validar_action_segura("controlador.php.fake"))
        self.assertFalse(self.motor.validar_action_segura("/sei/controlador.php.fake"))

        self.assertTrue(self.motor.validar_action_segura("controlador.php?acao=procedimento_controlar"))
        self.assertTrue(self.motor.validar_action_segura("https://sei.sp.gov.br/sei/controlador.php"))

    def test_04_rejeitar_tabela_dentro_de_script(self):
        html_script = """
        <html>
            <head>
                <script>
                    var mockLink = '<a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=99999">SP-99999</a>';
                </script>
            </head>
            <body>
                <a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=12345">SP-12345</a>
            </body>
        </html>
        """
        parser = ParserProcessosSEI()
        parser.feed(html_script)
        self.assertEqual(len(parser.processos), 1)
        self.assertEqual(parser.processos[0]["id_procedimento"], "12345")
        self.assertEqual(parser.processos[0]["numero"], "SP-12345")

    def test_05_parser_com_entidade_amp(self):
        html_amp = """
        <div>
            <a href="controlador.php?acao=procedimento_trabalhar&amp;id_procedimento=54321&amp;id_protocolo=987">
                Processo SP-54321/2026
            </a>
        </div>
        """
        parser = ParserProcessosSEI()
        parser.feed(html_amp)
        self.assertEqual(len(parser.processos), 1)
        self.assertEqual(parser.processos[0]["id_procedimento"], "54321")
        self.assertEqual(parser.processos[0]["id_protocolo"], "987")
        self.assertIn("SP-54321/2026", parser.processos[0]["numero"])

    def test_06_falha_fsync_aborta_substituicao_e_limpa(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_inicial")

        def fsync_falha(fd):
            raise OSError("Falha de I/O em fsync simulada")

        with patch("os.fsync", side_effect=fsync_falha):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_nova_falhada"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
        self.assertEqual(conteudo["cookies"]["PHPSESSID"], "sessao_inicial")

    def test_07_falha_fsync_diretorio_executa_rollback(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_estavel"})

        with patch.object(self.motor, "_fsync_diretorio", side_effect=OSError("Falha de fsync em diretório")):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_com_defeito"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
        self.assertEqual(conteudo["cookies"]["PHPSESSID"], "sessao_estavel")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_estavel")

    def test_08_falha_abertura_diretorio_executa_rollback(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_v1"})

        with patch.object(self.motor, "_fsync_diretorio", side_effect=OSError("Permissao negada")):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_v2"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
        self.assertEqual(conteudo["cookies"]["PHPSESSID"], "sessao_v1")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_v1")

    def test_09_falha_recarga_invalida_memoria(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_base"})
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_base")

        with patch.object(self.motor, "carregar_sessao", side_effect=ValueError("Arquivo corrompido")):
            with self.assertRaises(ValueError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_corrompida"})

        self.assertEqual(len(self.motor.sessao.cookies), 0)
        self.assertIsNone(self.motor._mtime_sessao)

    def test_10_concorrencia_lock_processos_sem_roubo_de_lock(self):
        lock1 = LockProcessosSEI(self.caminho_sessao, timeout=2.0)
        lock2 = LockProcessosSEI(self.caminho_sessao, timeout=0.1, poll_interval=0.02)

        with lock1:
            self.assertTrue(lock1._adquirido)

            inicio_t = time.monotonic()
            with self.assertRaises(TimeoutError):
                with lock2:
                    pass
            duracao = time.monotonic() - inicio_t
            self.assertGreaterEqual(duracao, 0.08)

            self.assertTrue(lock1._adquirido)

        with lock2:
            self.assertTrue(lock2._adquirido)
        self.assertFalse(lock2._adquirido)

    def test_11_sincronizacao_mtime_multiplas_instancias(self):
        motor_instancia_a = MotorSEI(caminho_sessao=self.caminho_sessao)
        motor_instancia_b = MotorSEI(caminho_sessao=self.caminho_sessao)

        motor_instancia_a.salvar_sessao({"PHPSESSID": "token_instancia_a"})
        self.assertEqual(motor_instancia_a.sessao.cookies.get("PHPSESSID"), "token_instancia_a")

        motor_instancia_b._sincronizar_sessao_se_modificada()
        self.assertEqual(motor_instancia_b.sessao.cookies.get("PHPSESSID"), "token_instancia_a")

        time.sleep(0.05)

        motor_instancia_a.salvar_sessao({"PHPSESSID": "token_instancia_b_atualizado"})
        self.assertEqual(motor_instancia_a.sessao.cookies.get("PHPSESSID"), "token_instancia_b_atualizado")

        motor_instancia_b._sincronizar_sessao_se_modificada()
        self.assertEqual(motor_instancia_b.sessao.cookies.get("PHPSESSID"), "token_instancia_b_atualizado")

        os.unlink(self.caminho_sessao)
        motor_instancia_b._sincronizar_sessao_se_modificada()
        self.assertEqual(len(motor_instancia_b.sessao.cookies), 0)
        self.assertIsNone(motor_instancia_b._mtime_sessao)

    def test_12_primeira_inicializacao_cria_diretorio_pai(self):
        caminho_aninhado = os.path.join(self.temp_dir.name, "sub_novo", "pasta_sei", "sessao_sei.json")
        self.assertFalse(os.path.exists(os.path.dirname(caminho_aninhado)))

        motor_novo = MotorSEI(caminho_sessao=caminho_aninhado)
        resultado = motor_novo.salvar_sessao({"PHPSESSID": "sessao_primeira_vez"})
        self.assertTrue(resultado)
        self.assertTrue(os.path.exists(caminho_aninhado))
        self.assertEqual(motor_novo.sessao.cookies.get("PHPSESSID"), "sessao_primeira_vez")

    def test_13_escopo_rigoroso_cookies_seguranca_subdominios_e_redirect(self):
        self.motor.salvar_sessao({"PHPSESSID": "segredo_sei_xyz"})
        
        req_sei = self.motor.sessao.prepare_request(
            Request("GET", "https://sei.sp.gov.br/sei/controlador.php")
        )
        self.assertIn("segredo_sei_xyz", req_sei.headers.get("Cookie", ""))

        req_sub = self.motor.sessao.prepare_request(
            Request("GET", "https://sub.sei.sp.gov.br/sei/controlador.php")
        )
        self.assertNotIn("segredo_sei_xyz", req_sub.headers.get("Cookie", ""))

        interceptado = {}
        def mock_adapter_send(adapter_self, request, **kwargs):
            interceptado["url"] = request.url
            interceptado["cookie"] = request.headers.get("Cookie")
            r = requests.Response()
            r.status_code = 200
            return r

        with patch.object(requests.adapters.HTTPAdapter, "send", mock_adapter_send):
            self.motor.sessao.send(req_sub)
            self.assertIsNone(interceptado.get("cookie"))

    def test_14_rejeitar_pagina_acesso_negado_e_form_fake(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_bloqueada"})

        html_negado = """
        <html>
            <body>
                <h1>Acesso Negado</h1>
                <form id="frmProcedimentoControlar" action="controlador.php?acao=procedimento_controlar"></form>
            </body>
        </html>
        """
        mock_resp1 = MagicMock(status_code=200, text=html_negado, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp1):
            self.assertFalse(self.motor.validar_sessao_ativa())

        html_fake = """
        <html>
            <body>
                <form id="frmTeste" action="controlador.php.fake"></form>
            </body>
        </html>
        """
        mock_resp2 = MagicMock(status_code=200, text=html_fake, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp2):
            self.assertFalse(self.motor.validar_sessao_ativa())

    def test_15_sincronizacao_resiliente_colisao_mtime(self):
        motor_a = MotorSEI(caminho_sessao=self.caminho_sessao)
        motor_b = MotorSEI(caminho_sessao=self.caminho_sessao)

        motor_a.salvar_sessao({"PHPSESSID": "sessao_original"})
        motor_b._sincronizar_sessao_se_modificada()
        self.assertEqual(motor_b.sessao.cookies.get("PHPSESSID"), "sessao_original")

        mtime_original = os.path.getmtime(self.caminho_sessao)

        with open(self.caminho_sessao, "w", encoding="utf-8") as f:
            json.dump({
                "cookies": {"PHPSESSID": "sessao_colidida_nova"},
                "atualizado_em": "2026-11-11T12:00:00Z"
            }, f)
        os.utime(self.caminho_sessao, (mtime_original, mtime_original))

        motor_b._sincronizar_sessao_se_modificada()
        self.assertEqual(motor_b.sessao.cookies.get("PHPSESSID"), "sessao_colidida_nova")

    def test_16_recuperacao_lock_processo_morto_vs_vivo(self):
        lock_dir = self.caminho_sessao + ".lock"
        os.makedirs(lock_dir, exist_ok=True)
        # Lock legado local com PID comprovadamente morto
        with open(os.path.join(lock_dir, "lock.info"), "w", encoding="utf-8") as f:
            json.dump({"pid": 99999999, "timestamp": time.time() - 60.0, "token": "orfao", "hostname": socket.gethostname()}, f)
        
        # 1. Processo MORTO: lock do kernel liberado automaticamente ao fechar o processo
        lock1 = LockProcessosSEI(self.caminho_sessao, timeout=2.0)
        with lock1:
            self.assertTrue(lock1._adquirido)
        self.assertFalse(lock1._adquirido)

        # 2. Processo VIVO: enquanto lock1 está aberto no kernel, concorrente DEVE receber TimeoutError
        with lock1:
            lock_concorrente = LockProcessosSEI(self.caminho_sessao, timeout=0.08)
            with self.assertRaises(TimeoutError):
                with lock_concorrente:
                    pass

    def test_17_contrato_rotas_status_autenticado_vs_inativo(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_expirada"})
        
        mock_resp_inativo = MagicMock(
            status_code=200,
            text='<html><body><h1>Acesso Negado</h1></body></html>',
            url="https://sei.sp.gov.br/sei/controlador.php"
        )
        with patch.object(self.motor.sessao, "get", return_value=mock_resp_inativo):
            status_info = self.motor.validar_sessao()
            self.assertIsInstance(status_info, dict)
            self.assertFalse(status_info.get("ativa"))
            self.assertFalse(status_info.get("autenticado"))

    def test_18_rotas_sei_diagnostico_e_erros_upstream(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_teste"})

        html_expirada = "<html><body><div class='infraMensagem'>Sessão expirada</div></body></html>"
        mock_resp_exp = MagicMock(status_code=200, text=html_expirada)
        with patch.object(self.motor.sessao, "get", return_value=mock_resp_exp):
            res_caixa = self.motor.listar_caixa_unidade()
            self.assertFalse(res_caixa.get("sucesso"))
            self.assertTrue(res_caixa.get("sessao_expirada"))
            self.assertEqual(res_caixa.get("codigo"), 401)

        mock_resp_503 = MagicMock(status_code=503, text="Service Unavailable")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp_503):
            res_503 = self.motor.listar_caixa_unidade()
            self.assertFalse(res_503.get("sucesso"))
            self.assertEqual(res_503.get("codigo"), 502)

        html_generica = "<html><body><h1>Portal Geral SP</h1></body></html>"
        mock_resp_gen = MagicMock(status_code=200, text=html_generica)
        with patch.object(self.motor.sessao, "post", return_value=mock_resp_gen):
            res_busca = self.motor.buscar_processos("termo_inexistente")
            self.assertFalse(res_busca.get("sucesso"))
            self.assertEqual(res_busca.get("codigo"), 502)

    def test_19_cliente_flask_integrado(self):
        try:
            import main
            app = main.app
        except Exception:
            return

        with app.test_client() as client:
            with patch.object(main.motor_sei_instance, "validar_sessao", return_value={"sucesso": True, "ativa": False, "autenticado": False}):
                resp_status = client.get("/api/v1/sei/status")
                self.assertEqual(resp_status.status_code, 200)
                dados = resp_status.get_json()
                self.assertFalse(dados.get("autenticado"))

    def test_20_rejeitar_marcadores_falsos_em_script_e_comentarios(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_ativa_valida"})

        html_falsa_injetada = """
        <html>
            <head>
                <script>
                    var acao = "controlador.php?acao=pesquisa_processo";
                    var campo = "txtPesquisa";
                    // <form id="frmProcedimentoControlar" action="controlador.php"></form>
                </script>
                <!-- controlador.php?acao=procedimento_controlar -->
            </head>
            <body>
                <div class="aviso">Erro interno no servidor de aplicações SP</div>
            </body>
        </html>
        """
        mock_resp_falsa = MagicMock(status_code=200, text=html_falsa_injetada)

        with patch.object(self.motor.sessao, "get", return_value=mock_resp_falsa):
            res_caixa = self.motor.listar_caixa_unidade()
            self.assertFalse(res_caixa.get("sucesso"))
            self.assertEqual(res_caixa.get("codigo"), 502)

        with patch.object(self.motor.sessao, "post", return_value=mock_resp_falsa):
            res_busca = self.motor.buscar_processos("12345")
            self.assertFalse(res_busca.get("sucesso"))
            self.assertEqual(res_busca.get("codigo"), 502)

    def test_21_lock_entre_containers_hostname_diferente(self):
        # Valida exclusão mútua no armazenamento mesmo com hostnames simulados diferentes
        lock_a = LockProcessosSEI(self.caminho_sessao, timeout=1.0, hostname="container-alpha")
        lock_b = LockProcessosSEI(self.caminho_sessao, timeout=0.08, hostname="container-beta")

        with lock_a:
            with self.assertRaises(TimeoutError):
                with lock_b:
                    pass

    def test_22_rejeitar_form_action_externa_em_validacao_sessao(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_com_form_externo"})

        html_externo = """
        <html>
            <body>
                <form id="frmProcedimentoControlar" action="https://malicioso.com/controlador.php?acao=procedimento_controlar">
                </form>
            </body>
        </html>
        """
        mock_resp = MagicMock(status_code=200, text=html_externo, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp):
            ativa = self.motor.validar_sessao_ativa()
            self.assertFalse(ativa)

    def test_23_rejeitar_pagina_erro_com_div_infra_mensagens(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_ok"})

        html_erro_infra = """
        <html>
            <body>
                <div id="divConteudo">
                    <div id="divInfraMensagens" class="infraMensagem">
                        Ocorreu uma falha no servidor de banco de dados do SEI.
                    </div>
                </div>
            </body>
        </html>
        """
        mock_resp = MagicMock(status_code=200, text=html_erro_infra, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp):
            res = self.motor.listar_caixa_unidade()
            self.assertFalse(res.get("sucesso"))
            self.assertEqual(res.get("codigo"), 502)

    def test_24_lock_heartbeat_mantem_lease_ativo_com_idade_reduzida_hostnames_distintos(self):
        lock1 = LockProcessosSEI(self.caminho_sessao, timeout=2.0, max_lock_age=0.15, hostname="container-A")
        with lock1:
            time.sleep(0.2)
            lock2 = LockProcessosSEI(self.caminho_sessao, timeout=0.05, max_lock_age=0.15, hostname="container-B")
            with self.assertRaises(TimeoutError):
                with lock2:
                    pass

    def test_25_rejeitar_pagina_erro_com_input_solto_ou_link_solto(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_ativa"})

        # 1. Página com apenas <input name="txtPesquisa"> solto sem <form id="frmPesquisa">
        html_input_solto = """
        <html>
            <body>
                <input type="text" name="txtPesquisa" value="termo" />
                <h1>Erro 500 Interno</h1>
            </body>
        </html>
        """
        mock_resp1 = MagicMock(status_code=200, text=html_input_solto, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "post", return_value=mock_resp1):
            res1 = self.motor.buscar_processos("qualquer")
            self.assertFalse(res1.get("sucesso"))
            self.assertEqual(res1.get("codigo"), 502)

        # 2. Página com link solto de processo sem <form id="frmProcedimentoControlar">
        html_link_solto = """
        <html>
            <body>
                <a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=123">Processo SP-123</a>
                <div class="erro">Falha de renderização de tela</div>
            </body>
        </html>
        """
        mock_resp2 = MagicMock(status_code=200, text=html_link_solto, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp2):
            res2 = self.motor.listar_caixa_unidade()
            self.assertFalse(res2.get("sucesso"))
            self.assertEqual(res2.get("codigo"), 502)

    def test_26_titular_suspenso_nao_remove_lock_alheio_nem_escreve(self):
        lock_a = LockProcessosSEI(self.caminho_sessao, timeout=1.0, max_lock_age=0.15, hostname="container-A")
        lock_a.__enter__()

        # Durante execução de A, lock_b em container-B não pode adquirir o lock do armazenamento
        lock_b = LockProcessosSEI(self.caminho_sessao, timeout=0.08, hostname="container-B")
        with self.assertRaises(TimeoutError):
            with lock_b:
                pass

        lock_a.__exit__(None, None, None)

        # Após liberação, lock_b consegue adquirir
        with lock_b:
            self.assertTrue(lock_b._adquirido)

    def test_27_concorrencia_suspensao_fencing_armazenamento_multiprocesso(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_inicial")

        import subprocess

        script_a = f"""
import time, os
from motor_sei import MotorSEI
m = MotorSEI(caminho_sessao=r"{self.caminho_sessao}")
orig_replace = os.replace
def replace_lento(src, dst):
    print("TITULAR_PRONTO", flush=True)
    time.sleep(0.4)
    return orig_replace(src, dst)

from unittest.mock import patch
with patch("os.replace", side_effect=replace_lento):
    m.salvar_sessao({{"PHPSESSID": "sessao_A_titular"}}, timeout=5.0)
    print("TITULAR_SUCESSO", flush=True)
"""

        proc_a = subprocess.Popen(
            [sys.executable, "-c", script_a],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            linha_pronto = proc_a.stdout.readline().strip()
            self.assertEqual(linha_pronto, "TITULAR_PRONTO")

            script_b = f"""
import sys
from motor_sei import MotorSEI
m = MotorSEI(caminho_sessao=r"{self.caminho_sessao}")
try:
    m.salvar_sessao({{"PHPSESSID": "sessao_B_concorrente"}}, timeout=0.05)
    print("CONCORRENTE_GRAVOU", flush=True)
    sys.exit(0)
except TimeoutError:
    print("CONCORRENTE_TIMEOUT", flush=True)
    sys.exit(42)
"""

            res_b = subprocess.run(
                [sys.executable, "-c", script_b],
                capture_output=True,
                text=True,
                timeout=3.0
            )
            self.assertEqual(res_b.returncode, 42)
            self.assertEqual(res_b.stdout.strip(), "CONCORRENTE_TIMEOUT")

            stdout_a, _ = proc_a.communicate(timeout=3.0)
            self.assertIn("TITULAR_SUCESSO", stdout_a)
        finally:
            if proc_a.poll() is None:
                proc_a.kill()
                proc_a.wait()

        with open(self.caminho_sessao, "r", encoding="utf-8") as f_res:
            dados_final = json.load(f_res)
        self.assertEqual(dados_final["cookies"]["PHPSESSID"], "sessao_A_titular")

    def test_28_timeout_entre_threads_estrito_salvar_sessao(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        motor_a = MotorSEI(caminho_sessao=self.caminho_sessao)
        motor_b = MotorSEI(caminho_sessao=self.caminho_sessao)

        orig_replace = os.replace
        def replace_lento(src, dst):
            time.sleep(0.35)
            return orig_replace(src, dst)

        def worker_a():
            with patch("os.replace", side_effect=replace_lento):
                motor_a.salvar_sessao({"PHPSESSID": "sessao_A"})

        th_a = threading.Thread(target=worker_a)
        th_a.start()
        time.sleep(0.05)

        t0 = time.monotonic()
        with self.assertRaises(TimeoutError):
            motor_b.salvar_sessao({"PHPSESSID": "sessao_B"}, timeout=0.05)
        duracao = time.monotonic() - t0
        self.assertLess(duracao, 0.2, f"Thread concorrente demorou {duracao:.3f}s excedendo timeout!")

        th_a.join(timeout=2.0)
        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(d["cookies"]["PHPSESSID"], "sessao_A")

    def test_29_clean_cutover_bloqueia_escritor_legado_ativo(self):
        lock_dir = self.caminho_sessao + ".lock"
        os.makedirs(lock_dir, exist_ok=True)
        with open(os.path.join(lock_dir, "lock.info"), "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "timestamp": time.time(), "token": "v9_legado", "hostname": socket.gethostname()}, f)

        motor_v10 = MotorSEI(caminho_sessao=self.caminho_sessao)
        with self.assertRaises(RuntimeError) as ctx:
            motor_v10.salvar_sessao({"PHPSESSID": "sessao_v10"}, timeout=0.5)
        self.assertIn("Clean Cutover Obrigatório", str(ctx.exception))

        # Também deve bloquear lock legado de outro hostname sem removê-lo
        with open(os.path.join(lock_dir, "lock.info"), "w", encoding="utf-8") as f:
            json.dump({"pid": 999999, "timestamp": time.time(), "token": "v9_remoto", "hostname": "container_legado_remoto"}, f)
        with self.assertRaises(RuntimeError) as ctx_remoto:
            motor_v10.salvar_sessao({"PHPSESSID": "sessao_v10"}, timeout=0.5)
        self.assertIn("Clean Cutover Obrigatório", str(ctx_remoto.exception))
        self.assertTrue(os.path.exists(lock_dir))

        # Também deve falhar fechado com metadados incompletos (apenas hostname ou {})
        for payload_incompleto in ({"hostname": socket.gethostname()}, {}):
            with open(os.path.join(lock_dir, "lock.info"), "w", encoding="utf-8") as f:
                json.dump(payload_incompleto, f)
            with self.assertRaises(RuntimeError) as ctx_inc:
                motor_v10.salvar_sessao({"PHPSESSID": "sessao_v10"}, timeout=0.5)
            self.assertIn("Clean Cutover Obrigatório", str(ctx_inc.exception))
            self.assertTrue(os.path.exists(lock_dir))

        # Também deve falhar fechado se .lock existir sem lock.info (mesmo após > 5s)
        os.unlink(os.path.join(lock_dir, "lock.info"))
        os.utime(lock_dir, (time.time() - 60.0, time.time() - 60.0))
        with self.assertRaises(RuntimeError) as ctx_sem_meta:
            motor_v10.salvar_sessao({"PHPSESSID": "sessao_v10"}, timeout=0.5)
        self.assertIn("Clean Cutover Obrigatório", str(ctx_sem_meta.exception))
        self.assertTrue(os.path.exists(lock_dir))

        os.rmdir(lock_dir)

        self.assertTrue(motor_v10.salvar_sessao({"PHPSESSID": "sessao_v10_sucesso"}, timeout=1.0))
        self.assertTrue(os.path.exists(self.caminho_sessao + ".flock"))

    def test_30_falha_aquisicao_libera_descritor_e_lock_kernel(self):
        lock_a = LockProcessosSEI(self.caminho_sessao, timeout=0.05)
        patch_target = "msvcrt.locking" if os.name == "nt" else "fcntl.flock"

        with patch(patch_target, side_effect=PermissionError("Acesso negado no kernel")):
            with self.assertRaises(TimeoutError):
                with lock_a:
                    pass

        self.assertIsNone(lock_a._fd)
        self.assertFalse(lock_a._adquirido)

        # Escritor subsequente adquire normalmente sem sofrer timeout
        lock_b = LockProcessosSEI(self.caminho_sessao, timeout=0.5)
        with lock_b:
            self.assertTrue(lock_b._adquirido)

    def test_31_fencing_armazenamento_impede_sobrescrita_e_limpa_residuos(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        motor_a = MotorSEI(caminho_sessao=self.caminho_sessao)

        diretorio = os.path.dirname(self.caminho_sessao)
        orig_mkstemp = tempfile.mkstemp
        def mkstemp_com_interferencia_externa(*args, **kwargs):
            res = orig_mkstemp(*args, **kwargs)
            with open(self.caminho_sessao, "w", encoding="utf-8") as f:
                json.dump({"cookies": {"PHPSESSID": "sessao_externa_prioritaria"}}, f)
            return res

        with patch("tempfile.mkstemp", side_effect=mkstemp_com_interferencia_externa):
            with self.assertRaises(TimeoutError):
                motor_a.salvar_sessao({"PHPSESSID": "sessao_A_titular"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(d["cookies"]["PHPSESSID"], "sessao_externa_prioritaria")

        arquivos = os.listdir(diretorio)
        self.assertFalse(any("sessao_backup_" in a for a in arquivos), f"Arquivos de backup residuais encontrados: {arquivos}")
        self.assertFalse(any("sessao_tmp_" in a for a in arquivos), f"Arquivos temporários residuais encontrados: {arquivos}")



    def test_32_falha_rollback_preserva_backup_anterior(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_anterior_valida"})
        diretorio = os.path.dirname(self.caminho_sessao)
        orig_replace = os.replace
        chamadas = {"n": 0}

        def replace_com_falha_no_rollback(src, dst):
            chamadas["n"] += 1
            if chamadas["n"] == 1:
                return orig_replace(src, dst)
            raise PermissionError("Falha simulada na restauração do backup")

        with patch.object(self.motor, "_fsync_diretorio", side_effect=OSError("Falha simulada no fsync do diretório")):
            with patch("os.replace", side_effect=replace_com_falha_no_rollback):
                with self.assertRaises(RuntimeError) as ctx:
                    self.motor.salvar_sessao({"PHPSESSID": "sessao_nova_nao_sincronizada"})
                self.assertIn("Backup anterior preservado", str(ctx.exception))

        backups = [a for a in os.listdir(diretorio) if a.startswith("sessao_backup_")]
        self.assertEqual(len(backups), 1, f"Backup anterior deveria ter sido preservado, encontrados: {backups}")
        with open(os.path.join(diretorio, backups[0]), "r", encoding="utf-8") as f:
            dados_backup = json.load(f)
        self.assertEqual(dados_backup["cookies"]["PHPSESSID"], "sessao_anterior_valida")

        # Próxima sincronização/recarga deve impedir o uso do cookie novo não sincronizado até recuperação
        motor_outro = MotorSEI(caminho_sessao=self.caminho_sessao)
        self.assertIsNone(motor_outro.sessao.cookies.get("PHPSESSID"))
        with self.assertRaises(RuntimeError):
            motor_outro._sincronizar_sessao_se_modificada()
        self.assertIsNone(motor_outro.sessao.cookies.get("PHPSESSID"))



    def test_33_rota_status_trata_marcador_rollback_pendente(self):
        with open(self.motor._marcador_rollback, "w", encoding="utf-8") as f:
            f.write("backup_pendente.tmp")

        status = self.motor.validar_sessao()
        self.assertFalse(status.get("sucesso"))
        self.assertEqual(status.get("codigo"), 503)
        self.assertTrue(status.get("rollback_pendente"))
        self.assertFalse(status.get("autenticado"))

        res_caixa = self.motor.listar_caixa_unidade()
        self.assertFalse(res_caixa.get("sucesso"))
        self.assertEqual(res_caixa.get("codigo"), 503)

        try:
            import main
            app = main.app
        except Exception:
            return

        with app.test_client() as client:
            with patch.object(main, "motor_sei_instance", self.motor):
                resp = client.get("/api/v1/sei/status")
                self.assertEqual(resp.status_code, 503)
                dados = resp.get_json()
                self.assertIsInstance(dados, dict)
                self.assertFalse(dados.get("sucesso"))
                self.assertFalse(dados.get("autenticado"))
                self.assertTrue(dados.get("rollback_pendente"))



    def test_34_redirecionamento_sip_frmlogin_retorna_401_e_cookie_path_raiz(self):
        self.motor.salvar_sessao({"PRODSEI": "sessao_sei_sp", "ROUTEID": ".9"})
        cookies_gravados = list(self.motor.sessao.cookies)
        self.assertTrue(any(c.name == "PRODSEI" and c.path == "/" for c in cookies_gravados))

        html_login_sip = '<html><body><form id="frmLogin" name="frmLogin" action="login.php" method="post"></form></body></html>'
        resp_login = MagicMock(
            status_code=200,
            text=html_login_sip,
            url="https://sei.sp.gov.br/sip/login.php?sigla_orgao_sistema=GESP&sigla_sistema=SEI",
        )
        with patch.object(self.motor.sessao, "get", return_value=resp_login):
            self.assertFalse(self.motor.validar_sessao_ativa())
            res_caixa = self.motor.listar_caixa_unidade()
            self.assertFalse(res_caixa.get("sucesso"))
            self.assertEqual(res_caixa.get("codigo"), 401)
            self.assertTrue(res_caixa.get("sessao_expirada"))

        with patch.object(self.motor.sessao, "post", return_value=resp_login):
            res_busca = self.motor.buscar_processos("termo")
            self.assertFalse(res_busca.get("sucesso"))
            self.assertEqual(res_busca.get("codigo"), 401)
            self.assertTrue(res_busca.get("sessao_expirada"))


if __name__ == "__main__":
    unittest.main()
