import os
import sys
import json
import stat
import time
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from urllib.parse import urlparse
from requests import Request

from motor_sei import (
    MotorSEI,
    ValidadorFormSEI,
    ParserProcessosSEI,
    LockProcessosSEI,
    ResultadoProcessosSEI
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

    def test_03_rejeitar_action_em_dominio_externo(self):
        self.assertFalse(self.motor.validar_action_segura("https://malicioso.com/controlador.php"))
        self.assertFalse(self.motor.validar_action_segura("http://phishing.sp.gov.br/hack"))
        self.assertFalse(self.motor.validar_action_segura("/sei/../etc/passwd"))
        self.assertFalse(self.motor.validar_action_segura("controlador.php?acao=../../perigo"))

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
            self.assertTrue(os.path.exists(lock1.lock_dir))

            inicio_t = time.monotonic()
            with self.assertRaises(TimeoutError):
                with lock2:
                    pass
            duracao = time.monotonic() - inicio_t
            self.assertGreaterEqual(duracao, 0.08)

            self.assertTrue(os.path.exists(lock1.lock_dir))

        self.assertFalse(os.path.exists(lock1.lock_dir))

        with lock2:
            self.assertTrue(os.path.exists(lock2.lock_dir))
        self.assertFalse(os.path.exists(lock2.lock_dir))

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
        self.assertFalse(os.path.exists(caminho_aninhado + ".lock"))

    def test_13_escopo_rigoroso_cookies_seguranca(self):
        self.motor.salvar_sessao({"PHPSESSID": "segredo_sei_xyz"})
        
        req_sei = self.motor.sessao.prepare_request(
            Request("GET", "https://sei.sp.gov.br/sei/controlador.php")
        )
        self.assertIn("segredo_sei_xyz", req_sei.headers.get("Cookie", ""))

        req_externo = self.motor.sessao.prepare_request(
            Request("GET", "https://malicioso.com/controlador.php")
        )
        self.assertNotIn("segredo_sei_xyz", req_externo.headers.get("Cookie", ""))

        req_inseguro = self.motor.sessao.prepare_request(
            Request("GET", "http://sei.sp.gov.br/sei/controlador.php")
        )
        self.assertNotIn("segredo_sei_xyz", req_inseguro.headers.get("Cookie", ""))

    def test_14_rejeitar_pagina_acesso_negado_e_form_externo(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_bloqueada"})

        html_negado = """
        <html>
            <body>
                <h1>Acesso Negado</h1>
                <form id="frmProcedimentoControlar" action="controlador.php"></form>
            </body>
        </html>
        """
        mock_resp1 = MagicMock(status_code=200, text=html_negado, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp1):
            self.assertFalse(self.motor.validar_sessao_ativa())

        html_externo = """
        <html>
            <body>
                <form id="frmLogin" action="https://phishing.com/login.php"></form>
            </body>
        </html>
        """
        mock_resp2 = MagicMock(status_code=200, text=html_externo, url="https://sei.sp.gov.br/sei/controlador.php")
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

    def test_16_recuperacao_stale_lock_processo_morto(self):
        lock_dir = self.caminho_sessao + ".lock"
        os.makedirs(lock_dir, exist_ok=True)
        with open(os.path.join(lock_dir, "lock.info"), "w", encoding="utf-8") as f:
            json.dump({"pid": 999999, "timestamp": time.time() - 100}, f)

        novo_lock = LockProcessosSEI(self.caminho_sessao, timeout=2.0)
        with novo_lock:
            self.assertTrue(os.path.exists(lock_dir))
        self.assertFalse(os.path.exists(lock_dir))

    def test_17_contrato_rotas_status_e_processos(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_contrato"})
        
        mock_resp_status = MagicMock(
            status_code=200,
            text='<form id="frmProcedimentoControlar" action="controlador.php"></form>',
            url="https://sei.sp.gov.br/sei/controlador.php"
        )
        with patch.object(self.motor.sessao, "get", return_value=mock_resp_status):
            status_info = self.motor.obter_status_sessao()
            self.assertIsInstance(status_info, dict)
            self.assertTrue(status_info.get("ativa"))
            self.assertIn("cookies", status_info)

        html_lista = """
        <html>
            <body>
                <a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=111">SP-111</a>
                <a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=222">SP-222</a>
            </body>
        </html>
        """
        mock_resp = MagicMock(status_code=200, text=html_lista)
        with patch.object(self.motor.sessao, "get", return_value=mock_resp):
            res_caixa = self.motor.listar_caixa_unidade()
            self.assertIsInstance(res_caixa, dict)
            self.assertEqual(res_caixa.get("total"), 2)
            self.assertEqual(len(res_caixa.get("processos")), 2)
            self.assertEqual(len(res_caixa), 2)
            self.assertEqual(res_caixa[0]["id_procedimento"], "111")


if __name__ == "__main__":
    unittest.main()
