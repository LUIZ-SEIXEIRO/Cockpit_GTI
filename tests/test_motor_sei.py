# -*- coding: utf-8 -*-
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
        html_amp = '<a href="controlador.php?acao=procedimento_trabalhar&amp;id_procedimento=54321">SP-54321</a>'
        parser = ParserProcessosSEI()
        parser.feed(html_amp)
        self.assertEqual(len(parser.processos), 1)
        self.assertEqual(parser.processos[0]["id_procedimento"], "54321")

    def test_06_falha_fsync_aborta_substituicao_e_limpa(self):
        self.motor.salvar_sessao({"PHPSESSID": "original_valido"})
        with patch("os.fsync", side_effect=OSError("Falha simulada de I/O em fsync")):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "novo_invalido"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            dados = json.load(f)
        self.assertEqual(dados["cookies"]["PHPSESSID"], "original_valido")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "original_valido")

    def test_07_falha_fsync_diretorio_executa_rollback(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_estavel"})
        with patch.object(self.motor, "_fsync_diretorio", side_effect=OSError("Falha de fsync em diretório")):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_com_erro_dir"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            dados = json.load(f)
        self.assertEqual(dados["cookies"]["PHPSESSID"], "sessao_estavel")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_estavel")

    def test_08_falha_abertura_diretorio_executa_rollback(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_base"})
        with patch.object(self.motor, "_fsync_diretorio", side_effect=PermissionError("Permissao negada")):
            with self.assertRaises(PermissionError):
                self.motor.salvar_sessao({"PHPSESSID": "tentativa_falha"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            dados = json.load(f)
        self.assertEqual(dados["cookies"]["PHPSESSID"], "sessao_base")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_base")

    def test_09_falha_recarga_invalida_memoria(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_antes_do_erro"})
        with patch("json.loads", side_effect=ValueError("Arquivo corrompido")):
            with self.assertRaises(ValueError):
                self.motor.salvar_sessao({"PHPSESSID": "corrompido"})

        self.assertEqual(len(self.motor.sessao.cookies), 0)
        self.assertIsNone(self.motor._mtime_sessao)
        self.assertIsNone(self.motor._hash_sessao)

    def test_10_concorrencia_lock_processos_sem_roubo_de_lock(self):
        lock1 = LockProcessosSEI(self.caminho_sessao, timeout=1.0)
        lock2 = LockProcessosSEI(self.caminho_sessao, timeout=0.1)

        with lock1:
            with self.assertRaises(TimeoutError):
                with lock2:
                    pass

    def test_11_sincronizacao_mtime_multiplas_instancias(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_instancia_1"})

        motor2 = MotorSEI(caminho_sessao=self.caminho_sessao)
        self.assertEqual(motor2.sessao.cookies.get("PHPSESSID"), "sessao_instancia_1")

        self.motor.salvar_sessao({"PHPSESSID": "sessao_instancia_1_atualizada"})
        motor2._sincronizar_sessao_se_modificada()
        self.assertEqual(motor2.sessao.cookies.get("PHPSESSID"), "sessao_instancia_1_atualizada")

    def test_12_primeira_inicializacao_cria_diretorio_pai(self):
        sub_dir = os.path.join(self.temp_dir.name, "sub_novo", "profundo")
        caminho_novo = os.path.join(sub_dir, "sessao.json")
        motor_novo = MotorSEI(caminho_sessao=caminho_novo)

        resultado = motor_novo.salvar_sessao({"PHPSESSID": "sessao_diretorio_profundo"})
        self.assertTrue(resultado)
        self.assertTrue(os.path.exists(caminho_novo))

    def test_13_escopo_rigoroso_cookies_seguranca_subdominios_e_redirect(self):
        session = StrictSEISession(host_permitido="sei.sp.gov.br")
        session.cookies.set("SEI_AUTH", "super_secreto", domain="sei.sp.gov.br", path="/sei")

        req_valido = Request("GET", "https://sei.sp.gov.br/sei/controlador.php").prepare()
        session.cookies.set_cookie_header(req_valido)
        req_valido = session.prepare_request(req_valido)
        self.assertIn("Cookie", req_valido.headers)
        self.assertIn("SEI_AUTH=super_secreto", req_valido.headers["Cookie"])

        req_subdominio = Request("GET", "https://sub.sei.sp.gov.br/sei/controlador.php").prepare()
        session.cookies.set_cookie_header(req_subdominio)
        req_subdominio = session.prepare_request(req_subdominio)
        self.assertNotIn("Cookie", req_subdominio.headers)

        req_http = Request("GET", "http://sei.sp.gov.br/sei/controlador.php").prepare()
        session.cookies.set_cookie_header(req_http)
        req_http = session.prepare_request(req_http)
        self.assertNotIn("Cookie", req_http.headers)

        req_externo = Request("GET", "https://malicioso.com/captura").prepare()
        session.cookies.set_cookie_header(req_externo)
        req_externo = session.prepare_request(req_externo)
        self.assertNotIn("Cookie", req_externo.headers)

    def test_14_rejeitar_pagina_acesso_negado_e_form_fake(self):
        html_erro_sei = """
        <html>
            <body>
                <div id="divInfraMensagens">Sessão Expirada ou Acesso Negado</div>
                <form id="frmLogin" action="controlador.php?acao=login">
                    <input type="text" name="txtUsuario" />
                </form>
            </body>
        </html>
        """
        validador = ValidadorFormSEI(base_url="https://sei.sp.gov.br/sei")
        validador.feed(html_erro_sei)
        self.assertFalse(validador.form_encontrado)

    def test_15_sincronizacao_resiliente_colisao_mtime(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        motor_cliente = MotorSEI(caminho_sessao=self.caminho_sessao)
        self.assertEqual(motor_cliente.sessao.cookies.get("PHPSESSID"), "sessao_inicial")

        mtime_antigo = self.motor._mtime_sessao
        self.motor.salvar_sessao({"PHPSESSID": "sessao_modificada_mesmo_mtime"})

        os.utime(self.caminho_sessao, (mtime_antigo, mtime_antigo))
        motor_cliente._sincronizar_sessao_se_modificada()
        self.assertEqual(motor_cliente.sessao.cookies.get("PHPSESSID"), "sessao_modificada_mesmo_mtime")

    def test_16_recuperacao_lock_processo_morto_vs_vivo(self):
        pid_falso_morto = 999999
        with patch("motor_sei._verificar_pid_so", side_effect=OSError):
            self.assertFalse(processo_esta_vivo(pid_falso_morto))

        pid_protegido = 1234
        with patch("motor_sei._verificar_pid_so", side_effect=PermissionError):
            self.assertTrue(processo_esta_vivo(pid_protegido))

    def test_17_contrato_rotas_status_autenticado_vs_inativo(self):
        status_inativo = self.motor.validar_sessao()
        self.assertTrue(status_inativo["sucesso"])
        self.assertFalse(status_inativo["ativa"])
        self.assertFalse(status_inativo["possui_cookies"])
        self.assertFalse(bool(status_inativo))
        self.assertEqual(status_inativo(), status_inativo)

        self.motor.salvar_sessao({"PHPSESSID": "sessao_mock_valida"}, usuario="luiz.seixeiro")
        with patch.object(self.motor, "validar_sessao_ativa", return_value=True):
            status_ativo = self.motor.validar_sessao()
            self.assertTrue(status_ativo["sucesso"])
            self.assertTrue(status_ativo["ativa"])
            self.assertTrue(status_ativo["possui_cookies"])
            self.assertEqual(status_ativo["usuario"], "luiz.seixeiro")
            self.assertTrue(bool(status_ativo))

    def test_18_rotas_sei_diagnostico_e_erros_upstream(self):
        self.motor.sessao.cookies.clear()
        if os.path.exists(self.caminho_sessao):
            os.unlink(self.caminho_sessao)

        res_caixa = self.motor.listar_caixa_unidade()
        self.assertFalse(res_caixa["sucesso"])
        self.assertEqual(res_caixa["codigo"], 401)

        res_busca = self.motor.buscar_processos("termo")
        self.assertFalse(res_busca["sucesso"])
        self.assertEqual(res_busca["codigo"], 401)

        self.motor.salvar_sessao({"PHPSESSID": "sessao_valida"})
        mock_resp_503 = MagicMock()
        mock_resp_503.status_code = 503
        mock_resp_503.text = "Service Unavailable"

        with patch.object(self.motor.sessao, "get", return_value=mock_resp_503):
            res_caixa_503 = self.motor.listar_caixa_unidade()
            self.assertFalse(res_caixa_503["sucesso"])
            self.assertEqual(res_caixa_503["codigo"], 502)

    def test_19_cliente_flask_integrado(self):
        import main
        cliente = main.app.test_client()

        resp_status = cliente.get("/api/v1/sei/status")
        self.assertEqual(resp_status.status_code, 200)
        dados_status = resp_status.get_json()
        self.assertTrue(dados_status["sucesso"])
        self.assertIn("ativa", dados_status)

        headers_auth = {"X-API-Key": main.API_SECRET_KEY} if hasattr(main, "API_SECRET_KEY") else {}
        resp_post = cliente.post("/api/v1/sei/sessao", json={
            "cookies": {"PHPSESSID": "flask_teste_cookie"},
            "usuario": "gestor.gti"
        }, headers=headers_auth)
        self.assertIn(resp_post.status_code, (200, 201))

        resp_caixa = cliente.get("/api/v1/sei/processos")
        self.assertIn(resp_caixa.status_code, (200, 401, 502))

    def test_20_rejeitar_marcadores_falsos_em_script_e_comentarios(self):
        html_script_falso = """
        <html>
            <head>
                <script>
                    var formHtml = '<form id="frmProcedimentoControlar" action="controlador.php"></form>';
                    var searchHtml = '<form id="frmPesquisa" action="controlador.php"></form>';
                </script>
            </head>
            <body>
                <!-- <form id="frmProcedimentoControlar" action="controlador.php"></form> -->
                <div class="erro">Falha geral do sistema</div>
            </body>
        </html>
        """
        validador_caixa = ValidadorEstruturalSEI(tipo_tela="caixa", base_url="https://sei.sp.gov.br/sei")
        validador_caixa.feed(html_script_falso)
        self.assertFalse(validador_caixa.estrutura_valida)

        validador_busca = ValidadorEstruturalSEI(tipo_tela="busca", base_url="https://sei.sp.gov.br/sei")
        validador_busca.feed(html_script_falso)
        self.assertFalse(validador_busca.estrutura_valida)

    def test_21_lock_entre_containers_hostname_diferente(self):
        lock_host1 = LockProcessosSEI(self.caminho_sessao, timeout=0.5, hostname="container-alpha")
        lock_host2 = LockProcessosSEI(self.caminho_sessao, timeout=0.05, hostname="container-beta")

        with lock_host1:
            with self.assertRaises(TimeoutError):
                with lock_host2:
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
        mock_resp = MagicMock(status_code=200, text=html_erro_infra)
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

        html_input_solto = """
        <html>
            <body>
                <input type="text" name="txtPesquisa" value="termo" />
                <h1>Erro 500 Interno</h1>
            </body>
        </html>
        """
        mock_resp1 = MagicMock(status_code=200, text=html_input_solto)
        with patch.object(self.motor.sessao, "post", return_value=mock_resp1):
            res1 = self.motor.buscar_processos("qualquer")
            self.assertFalse(res1.get("sucesso"))
            self.assertEqual(res1.get("codigo"), 502)

        html_link_solto = """
        <html>
            <body>
                <a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=123">Processo SP-123</a>
                <div class="erro">Falha de renderização de tela</div>
            </body>
        </html>
        """
        mock_resp2 = MagicMock(status_code=200, text=html_link_solto)
        with patch.object(self.motor.sessao, "get", return_value=mock_resp2):
            res2 = self.motor.listar_caixa_unidade()
            self.assertFalse(res2.get("sucesso"))
            self.assertEqual(res2.get("codigo"), 502)

    def test_26_titular_suspenso_nao_remove_lock_alheio_nem_escreve(self):
        lock_a = LockProcessosSEI(self.caminho_sessao, timeout=1.0, max_lock_age=0.15, hostname="container-A")
        lock_a.__enter__()

        lock_b = LockProcessosSEI(self.caminho_sessao, timeout=0.08, hostname="container-B")
        with self.assertRaises(TimeoutError):
            with lock_b:
                pass

        lock_a.__exit__(None, None, None)

        with lock_b:
            self.assertTrue(lock_b._adquirido)

    def test_27_concorrencia_suspensao_fencing_armazenamento(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_inicial")

        motor_a = MotorSEI(caminho_sessao=self.caminho_sessao)
        motor_b = MotorSEI(caminho_sessao=self.caminho_sessao)

        def simular_suspensao_titular():
            time.sleep(0.05)
            with self.assertRaises(TimeoutError):
                motor_b.salvar_sessao({"PHPSESSID": "sessao_B_tentativa_bloqueada"}, timeout=0.05)

        original_replace = os.replace
        def mock_replace_com_suspensao(origem, destino):
            simular_suspensao_titular()
            return original_replace(origem, destino)

        with patch("os.replace", side_effect=mock_replace_com_suspensao):
            motor_a.salvar_sessao({"PHPSESSID": "sessao_A_titular"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f_res:
            dados_final = json.load(f_res)
        self.assertEqual(dados_final["cookies"]["PHPSESSID"], "sessao_A_titular")


if __name__ == "__main__":
    unittest.main()
