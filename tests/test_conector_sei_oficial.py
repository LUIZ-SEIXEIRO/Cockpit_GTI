# -*- coding: utf-8 -*-
import io
import json
import os
import unittest
from unittest.mock import patch
from urllib import error

import conector_sei_oficial as sei_api


class _FakeResponse:
    def __init__(self, payload: dict):
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestConectorSEIOficial(unittest.TestCase):
    def _config_valida(self):
        return sei_api.SEIOfficialConfig(
            token_url=sei_api.DEFAULT_TOKEN_URL,
            base_url=sei_api.DEFAULT_BASE_URL,
            client_id="semil.TESTE",
            client_secret="segredo-teste",
            sigla_sistema="SOESP",
            identificacao_servico="chave-teste",
            id_unidade="110050725",
        )

    def test_01_status_identifica_campos_faltantes(self):
        cfg = sei_api.SEIOfficialConfig(
            token_url=sei_api.DEFAULT_TOKEN_URL,
            base_url=sei_api.DEFAULT_BASE_URL,
            client_id="semil.SOESP",
            client_secret="abc",
            sigla_sistema="",
            identificacao_servico="",
        )
        cliente = sei_api.SEIOfficialClient(cfg)
        st = cliente.status_configuracao()
        self.assertFalse(st["pronta"])
        self.assertEqual(st["faltantes"], ["SEI_API_SIGLA_SISTEMA", "SEI_API_IDENTIFICACAO_SERVICO"])

    def test_02_allowlist_bloqueia_host_externo(self):
        with self.assertRaises(sei_api.SEIOfficialAPIError):
            sei_api.validar_url_oficial("https://evil.example.com/processos")
        with self.assertRaises(sei_api.SEIOfficialAPIError):
            sei_api.validar_url_oficial("http://idp.sp.gov.br/token")

    def test_03_normalizacao_protocolo_somente_digitos(self):
        self.assertEqual(sei_api.normalizar_protocolo("137.00010608/2025-63"), "13700010608202563")
        with self.assertRaises(sei_api.SEIOfficialAPIError):
            sei_api.normalizar_protocolo("abc---")

    def test_04_cache_token_e_headers_obrigatorios(self):
        cliente = sei_api.SEIOfficialClient(self._config_valida())
        chamadas = []

        def fake_urlopen(req, timeout=20):
            chamadas.append((req.full_url, dict(req.header_items())))
            if "openid-connect/token" in req.full_url:
                return _FakeResponse({"access_token": "tok-123", "expires_in": 3600})
            return _FakeResponse({"total": "1", "processos": [{"protocoloProcedimento": "137.00010608/2025-63"}]})

        with patch.object(sei_api.request, "urlopen", side_effect=fake_urlopen):
            res1 = cliente.listar_processos_unidade(start=0, limit=10)
            res2 = cliente.consultar_processo("137.00010608/2025-63")

        self.assertEqual(res1["total"], "1")
        self.assertEqual(len(chamadas), 3)  # 1 token + 2 chamadas API (reaproveitou cache)
        headers_api = {k.lower(): v for k, v in chamadas[1][1].items()}
        self.assertEqual(headers_api["authorization"], "Bearer tok-123")
        self.assertEqual(headers_api["x-siglasistema"], "SOESP")
        self.assertEqual(headers_api["x-identificacaoservico"], "chave-teste")
        self.assertEqual(headers_api["x-idunidade"], "110050725")
        self.assertIn("x-traceid-sp", headers_api)
        self.assertIn("/processos/13700010608202563", chamadas[2][0])

    def test_05_renova_token_automaticamente_em_401(self):
        cliente = sei_api.SEIOfficialClient(self._config_valida())
        tokens = iter(["tok-velho", "tok-novo"])
        tentativa_api = {"n": 0}

        def fake_urlopen(req, timeout=20):
            if "openid-connect/token" in req.full_url:
                return _FakeResponse({"access_token": next(tokens), "expires_in": 3600})
            tentativa_api["n"] += 1
            if tentativa_api["n"] == 1:
                raise error.HTTPError(req.full_url, 401, "Unauthorized", {}, io.BytesIO(b"expired"))
            return _FakeResponse({"total": "0", "processos": []})

        with patch.object(sei_api.request, "urlopen", side_effect=fake_urlopen):
            res = cliente.listar_processos_unidade()

        self.assertEqual(res["total"], "0")
        self.assertEqual(tentativa_api["n"], 2)



    def test_06_rota_status_expoe_diagnostico_api_oficial(self):
        import main as app_main

        client = app_main.app.test_client()
        headers = {"Authorization": "Bearer token-teste-sei"}
        with patch.dict(os.environ, {"API_TOKEN": "token-teste-sei"}), \
             patch.object(app_main.motor_sei_instance, "validar_sessao", return_value={"sessao_ativa": False}):
            resp = client.get("/api/v1/sei/status", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("api_oficial", data)
        self.assertIn("pronta", data["api_oficial"])

    def test_07_rotas_processos_e_buscar_usam_api_oficial_quando_configurada(self):
        import main as app_main

        cfg_ok = self._config_valida()
        fake_client = sei_api.SEIOfficialClient(cfg_ok)
        client = app_main.app.test_client()
        headers = {"Authorization": "Bearer token-teste-sei"}

        with patch.dict(os.environ, {"API_TOKEN": "token-teste-sei"}), \
             patch.object(app_main, "sei_oficial_client", fake_client), \
             patch.object(fake_client, "listar_processos_unidade", return_value={"total": "2", "processos": [{"idProcedimento": "1"}]}), \
             patch.object(fake_client, "consultar_processo", return_value={"procedimentoFormatado": "137.00010608/2025-63"}):
            r_list = client.get("/api/v1/sei/processos", headers=headers)
            r_find = client.post("/api/v1/sei/buscar", json={"termo": "137.00010608/2025-63"}, headers=headers)

        self.assertEqual(r_list.status_code, 200)
        self.assertEqual(r_list.get_json()["origem"], "api_oficial")
        self.assertEqual(r_find.status_code, 200)
        self.assertEqual(r_find.get_json()["origem"], "api_oficial")


if __name__ == "__main__":
    unittest.main()
