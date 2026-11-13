# -*- coding: utf-8 -*-
from pathlib import Path
import re
import unittest


_ROOT = Path(__file__).resolve().parents[1]
_JS_DIR = _ROOT / "static" / "js"
_JS_BUNDLE = "\n".join(
    f.read_text(encoding="utf-8")
    for f in sorted(_JS_DIR.glob("*.js"))
) if _JS_DIR.exists() else ""
PAINEL = (_ROOT / "painel.html").read_text(encoding="utf-8") + "\n" + _JS_BUNDLE
FRONTEND_PAINEL = (Path(__file__).resolve().parents[1] / "frontend" / "painel.html").read_text(encoding="utf-8")


class TestFrontendContracts(unittest.TestCase):
    def test_ai_requests_use_authenticated_same_origin_gateway(self):
        self.assertIn("fetch('/api/v1/ia/chat'", PAINEL)
        self.assertIn("fetch('/api/v1/ia/revisar_processo'", PAINEL)
        self.assertIn("fetch('/api/v1/ia/testar_slot'", PAINEL)

        direct_provider_chat = re.compile(
            r"fetch\s*\(\s*['\"]https?://[^'\"]+/(?:chat|chat/completions)(?:[/?'\"])",
            re.IGNORECASE,
        )
        self.assertIsNone(direct_provider_chat.search(PAINEL))
        self.assertNotIn("var urlDirect", PAINEL)
        self.assertNotIn("var urlChat", PAINEL)

    def test_pool_read_sends_authentication_header(self):
        start = PAINEL.index("window.carregarPoolTresIas = async function")
        end = PAINEL.index("window.sincronizarInputsPoolTresIas = function", start)
        pool_loader = PAINEL[start:end]
        self.assertIn("fetch('/api/v1/ia/pool'", pool_loader)
        self.assertIn("headers: obterHeadersComAuth()", pool_loader)

    def test_pool_save_requires_backend_confirmation_before_success(self):
        start = PAINEL.index("window.salvarPoolTresIas = async function")
        end = PAINEL.index("window.restaurarPoolTresIasPadrao = function", start)
        save_flow = PAINEL[start:end]

        self.assertIn("if (!respostaServidor.ok)", save_flow)
        self.assertIn("retornoServidor.sucesso !== true", save_flow)
        self.assertLess(
            save_flow.index("if (!respostaServidor.ok)"),
            save_flow.index("btn.innerHTML = '<span>✅</span>"),
        )
        self.assertIn("Não foi possível confirmar a gravação do pool no servidor.", save_flow)

    def test_masked_pool_keys_do_not_override_backend_endpoint_or_leave_browser(self):
        self.assertIn("cfg.apiKey !== '***'", PAINEL)
        self.assertIn("endpoint: chaveConfigurada ? cfg.endpoint : undefined", PAINEL)
        self.assertIn("apiKey: chaveConfigurada ? cfg.apiKey : ''", PAINEL)
        self.assertIn("key === '***' || key === 'sk-CHAVE-SANITIZADA-INSTITUCIONAL'", PAINEL)

    def test_web_session_uses_server_cookie_without_storing_api_token(self):
        self.assertIn("window.obterTokenCockpitSeguro = function()", PAINEL)
        self.assertIn("localStorage.removeItem('cockpit_token')", PAINEL)
        self.assertNotIn("localStorage.setItem('cockpit_token'", PAINEL)
        self.assertNotIn("sessionStorage.setItem('cockpit_token'", PAINEL)
        self.assertNotIn("Authorization'] = 'Bearer ' + token", PAINEL)
        self.assertIn("fetch('/api/v1/session', { cache: 'no-store' })", PAINEL)
        self.assertIn("fetch('/api/v1/session', { method: 'DELETE'", PAINEL)
        self.assertNotIn("spaguas2026", PAINEL)
        self.assertNotIn("admin123", PAINEL)

    def test_frontend_copy_uses_same_cookie_session_contract(self):
        self.assertIn("fetch('/api/v1/session', { cache: 'no-store' })", FRONTEND_PAINEL)
        self.assertIn("fetch('/api/v1/session', { method: 'DELETE'", FRONTEND_PAINEL)
        self.assertNotIn("localStorage.getItem('cockpit_token')", FRONTEND_PAINEL)
        self.assertNotIn("Authorization'] = 'Bearer ' + token", FRONTEND_PAINEL)
        self.assertNotIn("spaguas2026", FRONTEND_PAINEL)

    def test_openproject_history_has_no_demo_fallback(self):
        start = PAINEL.index("window.abrirModalLogsSincronizacaoOp = async function")
        end = PAINEL.index("var motores = window.motoresVarredura", start)
        history_loader = PAINEL[start:end]
        self.assertIn("fetch('/api/v1/openproject/historico_agendado'", history_loader)
        self.assertNotIn("sagti_op_historico_agendado", history_loader)
        self.assertNotIn("A8F9B2C4", PAINEL)
        self.assertNotIn("179,", history_loader)

    def test_sei_status_request_sends_api_authentication(self):
        self.assertIn(
            "fetch('/api/v1/sei/status', { headers: obterHeadersComAuth() })",
            PAINEL,
        )

    def test_connector_healthcheck_uses_backend_status_without_demo_fallback(self):
        for painel in (PAINEL, FRONTEND_PAINEL):
            start = painel.index("window.executarHealthcheckGeral = async function")
            end = painel.index("window.restaurarTudoConfig = function", start)
            healthcheck = painel[start:end]

            for endpoint in (
                "/api/v1/glpi/status",
                "/api/v1/mariadb/status",
                "/api/v1/openproject/status",
                "/api/v1/newapi/status",
            ):
                self.assertIn(endpoint, healthcheck)
            self.assertIn("r.ok && body.ok === true", healthcheck)
            self.assertNotIn("localhost:8000", healthcheck)
            self.assertNotIn("Base Local Auditada", healthcheck)

    def test_glpi_alert_filter_handles_missing_optional_fields(self):
        self.assertIn("String(t && t.urgencia || '')", PAINEL)
        self.assertIn("String(t && t.status || '')", PAINEL)

    def test_external_connector_script_is_closed_before_inline_code(self):
        self.assertIn(
            '<script src="/static/conector_api.js"></script>\n    <script>',
            PAINEL,
        )
        self.assertNotIn("iniciarAgendadorSincronizacaoHorariaOpenProject();", PAINEL)

    def test_openproject_review_is_shown_and_confirmed_before_sync(self):
        start = PAINEL.index("window.confirmarGravacaoOrquestradorOp = async function")
        end = PAINEL.index("// MOTOR DE GESTÃO DE MATRIZES RACI", start)
        flow = PAINEL[start:end]

        review = flow.index("revisarCardComIa2Orquestracao(p, cardOp)")
        preview = flow.index("preDossie.textContent = payload.descricao")
        confirmation = flow.index("window.confirm('Confirma que revisou")
        sync = flow.index("enviarAtualizacaoCardApiSilencioso(cardIdFinal, payload, idProcesso)")
        local_persist = flow.index("localStorage.setItem('sagti_op_pacotes_custom'")
        self.assertLess(review, preview)
        self.assertLess(preview, confirmation)
        self.assertLess(confirmation, sync)
        self.assertLess(sync, local_persist)
        self.assertIn("IA_INCONSISTENTE", flow)
        self.assertIn("IA_INDISPONIVEL", PAINEL)

    def test_sync_sender_requires_consistent_review_and_has_no_direct_fallback(self):
        start = PAINEL.index("enviarAtualizacaoCardApiSilencioso: async function")
        end = PAINEL.index("// Copia o Dossiê Markdown", start)
        sender = PAINEL[start:end]
        self.assertIn("payload.revisadoPorIa2 !== true", sender)
        self.assertIn("payload.consistenciaIa2 !== true", sender)
        self.assertIn("fetch('/api/v1/openproject/sync_card'", sender)
        self.assertNotIn("credentials: 'include'", sender)
        self.assertNotIn("urlCard", sender)
        self.assertNotIn("modo: 'local'", sender)


if __name__ == "__main__":
    unittest.main()
