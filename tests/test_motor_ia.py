# -*- coding: utf-8 -*-
import json
import os
import sys
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import motor_ia


def _mock_urlopen_json(payload: dict):
    resp = MagicMock()
    resp.read.return_value = json.dumps(payload).encode("utf-8")
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    return resp


class TestMotorIA(unittest.TestCase):
    def test_01_normalizacao_temperatura_e_max_tokens(self):
        self.assertEqual(motor_ia.normalizar_temperatura(0.0), 0.0)
        self.assertEqual(motor_ia.normalizar_temperatura(None), 0.0)
        self.assertEqual(motor_ia.normalizar_temperatura(-1.5), 0.0)
        self.assertEqual(motor_ia.normalizar_temperatura(1.9), 0.7)
        self.assertEqual(motor_ia.normalizar_temperatura("0.25"), 0.25)
        self.assertEqual(motor_ia.normalizar_max_tokens(None), 700)
        self.assertEqual(motor_ia.normalizar_max_tokens(10), 64)
        self.assertEqual(motor_ia.normalizar_max_tokens(99999), 4096)

    def test_02_guardiao_grounding_injecao_e_idempotencia(self):
        msgs = [{"role": "user", "content": "Qual o status do processo?"}]
        protegidas = motor_ia.aplicar_guardiao_grounding(msgs)
        self.assertEqual(protegidas[0]["role"], "system")
        self.assertIn("[DIRETRIZ DE GROUNDING ESTRITO SA-GTI]", protegidas[0]["content"])

        com_sys = [{"role": "system", "content": "Assessor SA-GTI."}, {"role": "user", "content": "Resuma."}]
        p1 = motor_ia.aplicar_guardiao_grounding(com_sys)
        p2 = motor_ia.aplicar_guardiao_grounding(p1)
        self.assertIn("Assessor SA-GTI.", p1[0]["content"])
        self.assertEqual(p1[0]["content"].count("[DIRETRIZ DE GROUNDING ESTRITO SA-GTI]"), 1)
        self.assertEqual(p2[0]["content"].count("[DIRETRIZ DE GROUNDING ESTRITO SA-GTI]"), 1)

    def test_03_avaliacao_fidelidade_detecta_processo_alucinado(self):
        ctx = "Processo SEI: 137.00029841/2026-14\nAging L\u00edquido: 12 dias."
        res_ok = motor_ia.avaliar_fidelidade_resposta("O processo 137.00029841/2026-14 tem aging de 12 dias.", ctx)
        self.assertTrue(res_ok["fiel"])
        self.assertEqual(res_ok["score"], 1.0)

        res_bad = motor_ia.avaliar_fidelidade_resposta("O processo 137.00029841/2026-14 depende do 999.00012345/2026-99.", ctx)
        self.assertFalse(res_bad["fiel"])
        self.assertIn("999.00012345/2026-99", res_bad["alertas"][0])

    def test_04_executar_chat_ia_preserva_temperature_zero_e_trata_erros(self):
        capturado = {}
        def fake_urlopen(req, timeout=45):
            capturado["payload"] = json.loads(req.data.decode("utf-8"))
            capturado["auth"] = req.headers.get("Authorization")
            return _mock_urlopen_json({"model": "qwen2.5:14b", "choices": [{"message": {"content": "OK."}}]})

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            res = motor_ia.executar_chat_ia(
                mensagens=[{"role": "user", "content": "Analise."}],
                endpoint="http://127.0.0.1:3001/v1/",
                model="qwen2.5:14b",
                api_key="segredo_teste",
                temperature=0.0,
                max_tokens=500,
            )
        self.assertEqual(res["codigo"], 200)
        self.assertEqual(capturado["payload"]["temperature"], 0.0)
        self.assertEqual(capturado["payload"]["max_tokens"], 500)
        self.assertEqual(capturado["auth"], "Bearer segredo_teste")

        with patch("urllib.request.urlopen", side_effect=TimeoutError("timeout")):
            self.assertEqual(motor_ia.executar_chat_ia([{"role": "user", "content": "oi"}])["codigo"], 504)
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("recusado")):
            self.assertEqual(motor_ia.executar_chat_ia([{"role": "user", "content": "oi"}])["codigo"], 502)
        self.assertEqual(motor_ia.executar_chat_ia([{"role": "user", "content": "oi"}], endpoint="ftp://x")["codigo"], 400)

    def test_05_revisar_processo_ia_contexto_estrito_e_contrato(self):
        self.assertEqual(motor_ia.revisar_processo_ia({})["codigo"], 400)
        dados_proc = {"idProcesso": "137.00029841/2026-14", "especificacao": "Links SD-WAN", "agingLiquido": "10"}
        with patch("urllib.request.urlopen", return_value=_mock_urlopen_json({
            "model": "llama3.2:1b",
            "choices": [{"message": {"content": "Parecer: processo 137.00029841/2026-14 regular."}}],
        })):
            res = motor_ia.revisar_processo_ia(dados_proc)
        self.assertTrue(res["sucesso"])
        self.assertIn("137.00029841/2026-14", res["parecer"])

    def test_06_rotas_flask_ia_autenticacao_e_contrato(self):
        try:
            import main
            app = main.app
        except Exception:
            return
        with app.test_client() as client:
            with patch.dict(os.environ, {"API_TOKEN": "token_ia_teste"}):
                r_unauth = client.post("/api/v1/ia/revisar_processo", json={"idProcesso": "137.00029841/2026-14"})
                self.assertEqual(r_unauth.status_code, 401)
                with patch("urllib.request.urlopen", return_value=_mock_urlopen_json({
                    "model": "llama3.2:1b",
                    "choices": [{"message": {"content": "Parecer fiel 137.00029841/2026-14."}}],
                })):
                    r_ok = client.post(
                        "/api/v1/ia/revisar_processo",
                        headers={"Authorization": "Bearer token_ia_teste"},
                        json={"idProcesso": "137.00029841/2026-14", "especificacao": "SD-WAN"},
                    )
                self.assertEqual(r_ok.status_code, 200)
                self.assertTrue(r_ok.get_json().get("sucesso"))


if __name__ == "__main__":
    unittest.main()
