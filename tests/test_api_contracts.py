# -*- coding: utf-8 -*-
import io
import json
import os
import stat
import sys
import tempfile
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main


def _response_json(payload):
    response = MagicMock()
    response.status = 200
    response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


class TestApiContracts(unittest.TestCase):
    token = "token_contract_teste"

    def setUp(self):
        self.client = main.app.test_client()

    def test_panel_static_assets_are_served_by_flask(self):
        for path, expected in (
            ("/static/estilo_spaguas.css", b"Estilos nativos restaurados"),
            ("/static/conector_api.js", b"atualizarTelemetria"),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                try:
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(expected, response.data)
                finally:
                    response.close()

    def test_cors_is_exact_and_security_headers_are_applied(self):
        with patch("main.checar_porta", return_value=True):
            allowed = self.client.get(
                "/api/v1/mariadb/status",
                headers={"Origin": "http://localhost:5000"},
            )
            self.assertEqual(allowed.headers["Access-Control-Allow-Origin"], "http://localhost:5000")
            self.assertIn("Origin", allowed.headers["Vary"])
            self.assertEqual(allowed.headers["Cache-Control"], "no-store")
            self.assertEqual(allowed.headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(allowed.headers["X-Frame-Options"], "SAMEORIGIN")
            self.assertIn("frame-ancestors 'self'", allowed.headers["Content-Security-Policy"])
            self.assertTrue(allowed.headers["X-Request-ID"])

            for origin in ("https://localhost:5000", "http://localhost:4444", "http://localhost.evil.test:5000"):
                with self.subTest(origin=origin):
                    denied = self.client.get("/api/v1/mariadb/status", headers={"Origin": origin})
                    self.assertNotIn("Access-Control-Allow-Origin", denied.headers)

    def test_cors_preflight_rejects_unlisted_origins(self):
        allowed = self.client.options(
            "/api/v1/ia/chat",
            headers={
                "Origin": "http://localhost:5000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
        self.assertEqual(allowed.status_code, 204)
        self.assertEqual(allowed.headers["Access-Control-Allow-Origin"], "http://localhost:5000")
        self.assertIn("POST", allowed.headers["Access-Control-Allow-Methods"])

        denied = self.client.options(
            "/api/v1/ia/chat",
            headers={"Origin": "https://localhost:5000", "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(denied.status_code, 403)
        self.assertNotIn("Access-Control-Allow-Origin", denied.headers)

    def test_service_telemetry_uses_configured_endpoints_and_marks_unconfigured(self):
        unconfigured = self.client.get("/api/v1/mariadb/status")
        self.assertEqual(unconfigured.status_code, 200)
        self.assertEqual(unconfigured.get_json()["status"], "nao_configurado")

        with patch.dict(os.environ, {
            "MARIADB_HOST": "db.internal",
            "MARIADB_PORT": "3307",
            "OLLAMA_URL": "http://ollama.internal:11434",
            "GLPI_URL": "https://glpi.internal:8443",
            "OPENPROJECT_URL": "https://openproject.internal",
            "NEW_API_URL": "http://new-api.internal:3000/v1",
        }), patch("main.checar_porta", return_value=True) as check_port:
            response = self.client.get("/api/v1/telemetria")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "mariadb": True,
            "ollama": True,
            "glpi": True,
            "openproject": True,
            "newapi": True,
        })
        targets = [call.args[:2] for call in check_port.call_args_list]
        for expected in (
            ("db.internal", 3307),
            ("ollama.internal", 11434),
            ("glpi.internal", 8443),
            ("openproject.internal", 443),
            ("new-api.internal", 3000),
        ):
            self.assertIn(expected, targets)

    def test_request_body_size_limit_returns_json_error(self):
        limite_anterior = main.app.config["MAX_CONTENT_LENGTH"]
        main.app.config["MAX_CONTENT_LENGTH"] = 32
        try:
            with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}):
                response = self.client.post(
                    "/api/v1/ia/chat",
                    headers=self.headers,
                    data=b"x" * 64,
                    content_type="application/json",
                )
        finally:
            main.app.config["MAX_CONTENT_LENGTH"] = limite_anterior

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.get_json()["status"], "erro")
        self.assertTrue(response.headers["X-Request-ID"])

    def test_private_read_routes_require_authentication(self):
        routes = (
            "/api/v1/glpi/tickets",
            "/api/v1/openproject/historico_agendado_v2",
            "/api/v1/processos",
            "/api/v1/sei/status",
        )
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": ""}):
            for path in routes:
                with self.subTest(path=path):
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 401)
                    self.assertFalse(response.get_json()["sucesso"])

    def test_web_session_requires_configured_secret_and_valid_token(self):
        config_secret = main.app.config["SECRET_KEY"]
        secure_cookie = main.app.config["SESSION_COOKIE_SECURE"]
        main.app.config["SECRET_KEY"] = "session-contract-test-secret"
        main.app.config["SESSION_COOKIE_SECURE"] = False
        try:
            with patch.dict(os.environ, {
                "COCKPIT_SESSION_SECRET": "session-contract-test-secret",
                "COCKPIT_API_TOKEN": self.token,
                "API_TOKEN": "",
            }):
                invalid = self.client.post("/api/v1/session", json={"token": "wrong"})
                self.assertEqual(invalid.status_code, 401)

                valid = self.client.post("/api/v1/session", json={"token": self.token})
                self.assertEqual(valid.status_code, 200)
                self.assertIn("HttpOnly", valid.headers["Set-Cookie"])
                self.assertIn("SameSite=Strict", valid.headers["Set-Cookie"])
                self.assertNotIn("Secure", valid.headers["Set-Cookie"])
                painel = self.client.get("/")
                try:
                    self.assertEqual(painel.status_code, 200)
                finally:
                    painel.close()

                with patch.dict(os.environ, {
                    "COCKPIT_PROCESSOS_FILE": os.path.join(tempfile.gettempdir(), "cockpit-missing-processos.json"),
                }):
                    protected = self.client.get("/api/v1/processos")
                self.assertEqual(protected.status_code, 503)

                logout = self.client.delete("/api/v1/session")
                self.assertEqual(logout.status_code, 200)
                painel_apos_logout = self.client.get("/")
                try:
                    self.assertEqual(painel_apos_logout.status_code, 303)
                finally:
                    painel_apos_logout.close()
        finally:
            main.app.config["SECRET_KEY"] = config_secret
            main.app.config["SESSION_COOKIE_SECURE"] = secure_cookie

    def test_all_panel_routes_redirect_without_web_session(self):
        routes = ("/", "/painel", "/frontend/painel.html", "/static/painel.html")
        for path in routes:
            with self.subTest(path=path):
                response = self.client.get(path)
                try:
                    self.assertEqual(response.status_code, 303)
                    self.assertEqual(response.headers["Location"], "/login")
                finally:
                    response.close()

    def test_web_session_is_unavailable_without_session_secret(self):
        with patch.dict(os.environ, {"COCKPIT_SESSION_SECRET": "", "COCKPIT_API_TOKEN": self.token}):
            response = self.client.post("/api/v1/session", json={"token": self.token})
        self.assertEqual(response.status_code, 503)

    def test_authenticated_sei_status_does_not_disclose_storage_details(self):
        private_path = "/srv/cockpit/data/sessao_sei.json"
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
             patch.object(main.motor_sei_instance, "validar_sessao", return_value={
                 "sucesso": False,
                 "codigo": 503,
                 "autenticado": False,
                 "rollback_pendente": True,
                 "caminho_sessao": private_path,
                 "hash": "private-session-fingerprint",
                 "cookies": ["PHPSESSID"],
             }):
            response = self.client.get("/api/v1/sei/status", headers=self.headers)

        self.assertEqual(response.status_code, 503)
        body = response.get_json()
        self.assertTrue(body["rollback_pendente"])
        self.assertEqual(body["erro"], "Sessão do SEI bloqueada por pendência de integridade.")
        self.assertNotIn(private_path, response.get_data(as_text=True))
        self.assertNotIn("private-session-fingerprint", response.get_data(as_text=True))
        self.assertNotIn("PHPSESSID", response.get_data(as_text=True))

    def test_internal_error_is_correlated_without_exposing_exception_text(self):
        secret_diagnostic = "private-upstream-host-and-token"
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
             patch("main.resolver_credencial_ia", return_value=("", "", False)), \
             patch("main.normalizar_endpoint_ia", side_effect=RuntimeError(secret_diagnostic)):
            with self.assertLogs("main", level="ERROR") as captured:
                response = self.client.post(
                    "/api/v1/ia/chat",
                    headers=self.headers,
                    json={"messages": [{"role": "user", "content": "Teste"}]},
                )

        self.assertEqual(response.status_code, 500)
        self.assertNotIn(secret_diagnostic, response.get_data(as_text=True))
        self.assertNotIn(secret_diagnostic, "\n".join(captured.output))
        self.assertEqual(response.get_json()["requestId"], response.headers["X-Request-ID"])
        self.assertIn(response.headers["X-Request-ID"], "\n".join(captured.output))

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def test_protected_routes_reject_missing_authentication(self):
        routes = (
            ("get", "/api/v1/ia/pool", None),
            ("post", "/api/v1/ia/pool", {}),
            ("post", "/api/v1/ia/testar_slot", {}),
            ("post", "/api/v1/ia/chat", {}),
            ("post", "/api/v1/ia/revisar_processo", {}),
            ("post", "/api/v1/openproject/sync_card", {}),
            ("post", "/api/v1/openproject/sync_batch", {}),
        )
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": ""}):
            for method, path, body in routes:
                with self.subTest(method=method, path=path):
                    response = getattr(self.client, method)(path, json=body)
                    self.assertEqual(response.status_code, 401)
                    self.assertFalse(response.get_json()["sucesso"])

    def test_json_routes_reject_malformed_and_non_object_payloads(self):
        routes = (
            "/api/v1/ia/pool",
            "/api/v1/ia/testar_slot",
            "/api/v1/ia/chat",
            "/api/v1/ia/revisar_processo",
            "/api/v1/openproject/sync_card",
            "/api/v1/openproject/sync_batch",
        )
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}):
            for path in routes:
                with self.subTest(path=path, payload="malformed"):
                    response = self.client.post(
                        path,
                        headers=self.headers,
                        data='{"',
                        content_type="application/json",
                    )
                    self.assertEqual(response.status_code, 400)
                    self.assertIsInstance(response.get_json(), dict)
                with self.subTest(path=path, payload="non-object"):
                    response = self.client.post(path, headers=self.headers, json=["not", "an", "object"])
                    self.assertEqual(response.status_code, 400)
                    self.assertIsInstance(response.get_json(), dict)

    def test_pool_io_failures_are_not_success_responses(self):
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}):
            with patch("main.localizar_config_pool", return_value="/pool/config.json"), \
                 patch("main.os.path.exists", return_value=True), \
                 patch("builtins.open", side_effect=OSError("read denied")):
                response = self.client.get("/api/v1/ia/pool", headers=self.headers)
                self.assertEqual(response.status_code, 500)
                self.assertFalse(response.get_json()["sucesso"])

            with patch("main.localizar_config_pool", return_value="/pool/config.json"), \
                 patch("main.os.path.exists", return_value=False), \
                 patch("main.localizar_modelo_pool", return_value="/template/config.json"), \
                 patch("main.salvar_pool_privado", side_effect=OSError("write denied")):
                response = self.client.post("/api/v1/ia/pool", headers=self.headers, json={"ias": {}})
                self.assertEqual(response.status_code, 500)
                self.assertFalse(response.get_json()["sucesso"])

    def test_pool_credentials_are_persisted_outside_tracked_template(self):
        secret = "sk-private-test-credential"
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, "data")
            private_config = os.path.join(data_dir, "config_pool_ias.local.json")
            template = os.path.join(temp_dir, "config_pool_ias.json")
            template_content = {
                "ias": {
                    "principal": {
                        "id": "principal",
                        "agent": "qwen2.5:14b",
                        "endpoint": "http://ollama:11434/v1",
                        "apiKey": "sk-CHAVE-SANITIZADA-INSTITUCIONAL",
                    },
                },
            }
            with open(template, "w", encoding="utf-8") as file:
                json.dump(template_content, file)

            payload = {
                "ias": {
                    "principal": {
                        "id": "principal",
                        "agent": "qwen2.5:14b",
                        "endpoint": "http://ollama:11434/v1",
                        "apiKey": secret,
                    },
                },
            }
            with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
                 patch("main.localizar_config_pool", return_value=private_config), \
                 patch("main.localizar_modelo_pool", return_value=template):
                response = self.client.post("/api/v1/ia/pool", headers=self.headers, json=payload)

            self.assertEqual(response.status_code, 200)
            with open(private_config, encoding="utf-8") as file:
                self.assertEqual(json.load(file)["ias"]["principal"]["apiKey"], secret)
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(os.stat(private_config).st_mode), 0o600)
            with open(template, encoding="utf-8") as file:
                self.assertEqual(
                    json.load(file)["ias"]["principal"]["apiKey"],
                    "***",
                )

    def test_pool_get_migrates_legacy_secrets_to_private_storage(self):
        secret = "sk-legacy-test-credential"
        with tempfile.TemporaryDirectory() as temp_dir:
            private_config = os.path.join(temp_dir, "data", "config_pool_ias.local.json")
            template = os.path.join(temp_dir, "config_pool_ias.json")
            with open(template, "w", encoding="utf-8") as file:
                json.dump({"ias": {"principal": {"apiKey": secret}}}, file)

            with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
                 patch("main.localizar_config_pool", return_value=private_config), \
                 patch("main.localizar_modelo_pool", return_value=template):
                response = self.client.get("/api/v1/ia/pool", headers=self.headers)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["ias"]["principal"]["apiKey"], "***")
            with open(private_config, encoding="utf-8") as file:
                self.assertEqual(json.load(file)["ias"]["principal"]["apiKey"], secret)
            with open(template, encoding="utf-8") as file:
                self.assertEqual(json.load(file)["ias"]["principal"]["apiKey"], "***")
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(os.stat(private_config).st_mode), 0o600)

    def test_masked_slot_credentials_use_their_saved_endpoint(self):
        secret = "sk-slot-private-credential"
        endpoint = "http://100.103.100.98:3001/v1"
        with tempfile.TemporaryDirectory() as temp_dir:
            private_config = os.path.join(temp_dir, "config_pool_ias.local.json")
            pool = {
                "ias": {
                    "principal": {
                        "id": "principal",
                        "agent": "qwen2.5:14b",
                        "endpoint": endpoint,
                        "apiKey": secret,
                    },
                },
            }
            with open(private_config, "w", encoding="utf-8") as file:
                json.dump(pool, file)

            with patch.dict(os.environ, {
                "COCKPIT_API_TOKEN": "",
                "API_TOKEN": self.token,
                "NEWAPI_API_KEY": "",
                "NEW_API_KEY": "",
            }), patch("main.localizar_config_pool", return_value=private_config), \
                 patch("main.motor_ia.executar_chat_ia", return_value={"codigo": 200}) as executar:
                response = self.client.post(
                    "/api/v1/ia/chat",
                    headers=self.headers,
                    json={
                        "slot": "principal",
                        "ia": "principal",
                        "model": "qwen2.5:14b",
                        "apiKey": "***",
                        "endpoint": "http://ollama:11434/v1",
                        "messages": [{"role": "user", "content": "Teste"}],
                    },
                )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(executar.call_args.kwargs["endpoint"], endpoint)
            self.assertEqual(executar.call_args.kwargs["api_key"], secret)

            capturado = {}

            def fake_urlopen(req, timeout=45):
                capturado["url"] = req.full_url
                capturado["authorization"] = req.get_header("Authorization")
                return _response_json({"choices": []})

            with patch.dict(os.environ, {
                "COCKPIT_API_TOKEN": "",
                "API_TOKEN": self.token,
                "NEWAPI_API_KEY": "",
                "NEW_API_KEY": "",
            }), patch("main.localizar_config_pool", return_value=private_config), \
                 patch("main.urllib.request.urlopen", side_effect=fake_urlopen):
                response = self.client.post(
                    "/api/v1/ia/testar_slot",
                    headers=self.headers,
                    json={
                        "slot": "principal",
                        "model": "qwen2.5:14b",
                        "apiKey": "***",
                        "endpoint": "http://ollama:11434/v1",
                    },
                )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(capturado["url"], endpoint + "/chat/completions")
            self.assertEqual(capturado["authorization"], f"Bearer {secret}")

    def test_slot_credential_without_saved_endpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            private_config = os.path.join(temp_dir, "config_pool_ias.local.json")
            with open(private_config, "w", encoding="utf-8") as file:
                json.dump({
                    "ias": {
                        "principal": {
                            "id": "principal",
                            "agent": "qwen2.5:14b",
                            "apiKey": "sk-slot-private-credential",
                        },
                    },
                }, file)

            with patch.dict(os.environ, {
                "COCKPIT_API_TOKEN": "",
                "API_TOKEN": self.token,
                "NEWAPI_API_KEY": "",
                "NEW_API_KEY": "",
            }), patch("main.localizar_config_pool", return_value=private_config), \
                 patch("main.motor_ia.executar_chat_ia") as executar:
                response = self.client.post(
                    "/api/v1/ia/chat",
                    headers=self.headers,
                    json={
                        "slot": "principal",
                        "ia": "principal",
                        "model": "qwen2.5:14b",
                        "apiKey": "***",
                        "messages": [{"role": "user", "content": "Teste"}],
                    },
                )

            self.assertEqual(response.status_code, 400)
            self.assertFalse(response.get_json()["sucesso"])
            executar.assert_not_called()

    def test_review_route_preserves_422_inconsistency_contract(self):
        resultado = {
            "sucesso": False,
            "codigo": 422,
            "bloqueado_por_inconsistencia": True,
            "erro": "Parecer fora do contexto.",
            "consistencia": {"consistente": False, "alertas": ["Prazo fora do contexto"]},
        }
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
             patch("main.motor_ia.obter_endpoint_padrao", return_value="http://ollama:11434/v1"), \
             patch("main.resolver_credencial_ia", return_value=("", "", False)), \
             patch("main.motor_ia.revisar_processo_ia", return_value=resultado) as revisar:
            response = self.client.post(
                "/api/v1/ia/revisar_processo",
                headers=self.headers,
                json={"idProcesso": "137.00029841/2026-14"},
            )
        self.assertEqual(response.status_code, 422)
        body = response.get_json()
        self.assertFalse(body["sucesso"])
        self.assertTrue(body["bloqueado_por_inconsistencia"])
        self.assertFalse(body["consistencia"]["consistente"])
        revisar.assert_called_once()

    def test_chat_route_preserves_gateway_timeout_contract(self):
        resultado = {"sucesso": False, "codigo": 504, "status": "erro", "mensagem": "Timeout no provedor."}
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
             patch("main.resolver_credencial_ia", return_value=("", "", False)), \
             patch("main.normalizar_endpoint_ia", return_value="http://ollama:11434/v1"), \
             patch("main.motor_ia.executar_chat_ia", return_value=resultado):
            response = self.client.post(
                "/api/v1/ia/chat",
                headers=self.headers,
                json={"messages": [{"role": "user", "content": "Teste"}]},
            )
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.get_json(), resultado)

    def test_sync_card_validates_fields_before_network_io(self):
        payloads = (
            {},
            {"cardId": "not-a-number"},
            {"cardId": 10, "comentario": []},
            {"cardId": 10, "descricao": {"raw": "not a string"}},
        )
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
             patch("main.obter_token_openproject", return_value="token-openproject-teste"), \
             patch("main.urllib.request.urlopen") as urlopen:
            for payload in payloads:
                with self.subTest(payload=payload):
                    response = self.client.post("/api/v1/openproject/sync_card", headers=self.headers, json=payload)
                    self.assertEqual(response.status_code, 400)
                    self.assertFalse(response.get_json()["sucesso"])
            urlopen.assert_not_called()

    def test_sync_card_success_uses_lock_version_and_records_activity(self):
        calls = []

        def fake_urlopen(request, **kwargs):
            calls.append(request)
            if request.get_method() == "GET":
                return _response_json({"lockVersion": 3})
            if request.get_method() == "PATCH":
                return _response_json({"lockVersion": 4})
            return _response_json({"id": 99})

        with patch.dict(
            os.environ,
            {
                "COCKPIT_API_TOKEN": "",
                "API_TOKEN": self.token,
                "OPENPROJECT_API_TOKEN": "token-openproject-teste",
                "OPENPROJECT_URL": "https://openproject.example.test",
            },
        ), patch("main.obter_token_openproject", return_value="token-openproject-teste"), \
             patch("main.urllib.request.urlopen", side_effect=fake_urlopen):
            response = self.client.post(
                "/api/v1/openproject/sync_card",
                headers=self.headers,
                json={"cardId": 17, "descricao": "Dossiê", "comentario": "Análise preliminar"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["sucesso"])
        self.assertEqual(response.get_json()["lockVersion"], 4)
        self.assertEqual([request.get_method() for request in calls], ["GET", "PATCH", "POST"])
        self.assertEqual(json.loads(calls[1].data.decode("utf-8"))["lockVersion"], 3)
        self.assertIn("/work_packages/17/activities", calls[2].full_url)

    def test_sync_card_maps_configuration_network_and_timeout_failures(self):
        request_payload = {"cardId": 17, "descricao": "Dossiê", "comentario": "Atividade"}
        cases = (
            ("missing-token", "", None, 503),
            ("network", "token-openproject-teste", urllib.error.URLError("connection refused"), 502),
            ("timeout", "token-openproject-teste", TimeoutError("timeout"), 504),
            (
                "upstream-http",
                "token-openproject-teste",
                urllib.error.HTTPError(
                    "https://openproject.example.test/api/v3/work_packages/17",
                    503,
                    "Unavailable",
                    {},
                    io.BytesIO(b"upstream unavailable"),
                ),
                502,
            ),
        )
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}):
            for label, token, failure, expected_status in cases:
                with self.subTest(case=label):
                    with patch("main.obter_token_openproject", return_value=token), \
                         patch("main.urllib.request.urlopen", side_effect=failure) as urlopen:
                        response = self.client.post(
                            "/api/v1/openproject/sync_card",
                            headers=self.headers,
                            json=request_payload,
                        )
                    self.assertEqual(response.status_code, expected_status)
                    body = response.get_json()
                    self.assertFalse(body["sucesso"])
                    self.assertEqual(body["codigo"], expected_status)
                    if label == "upstream-http":
                        self.assertEqual(body["upstreamStatus"], 503)
                        urlopen.assert_called_once()
                    elif label == "missing-token":
                        urlopen.assert_not_called()
                    else:
                        urlopen.assert_called_once()

    def test_sync_batch_rejects_invalid_item_schema(self):
        payloads = (
            {"itens": {}},
            {"itens": None},
            {"itens": ["not-an-object"]},
            {"cards": {}},
        )
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
             patch("main.urllib.request.urlopen") as urlopen:
            for payload in payloads:
                with self.subTest(payload=payload):
                    response = self.client.post(
                        "/api/v1/openproject/sync_batch",
                        headers=self.headers,
                        json=payload,
                    )
                    self.assertEqual(response.status_code, 400)
                    self.assertFalse(response.get_json()["sucesso"])
            urlopen.assert_not_called()

    def test_sync_batch_accepts_empty_batch_without_network_io(self):
        payloads = ({}, {"itens": []}, {"cards": []})
        with patch.dict(os.environ, {"COCKPIT_API_TOKEN": "", "API_TOKEN": self.token}), \
             patch("main.urllib.request.urlopen") as urlopen:
            for payload in payloads:
                with self.subTest(payload=payload):
                    response = self.client.post(
                        "/api/v1/openproject/sync_batch",
                        headers=self.headers,
                        json=payload,
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.get_json()["sucesso"])
                    self.assertEqual(response.get_json()["total_processado"], 0)
            urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
