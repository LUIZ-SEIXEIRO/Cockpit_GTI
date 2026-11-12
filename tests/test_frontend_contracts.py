# -*- coding: utf-8 -*-
from pathlib import Path
import re
import unittest


PAINEL = (Path(__file__).resolve().parents[1] / "painel.html").read_text(encoding="utf-8")


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

    def test_api_token_is_tab_scoped_and_removed_on_logout(self):
        self.assertIn("sessionStorage.setItem('cockpit_token', t)", PAINEL)
        self.assertIn("window.obterTokenCockpitSeguro = function()", PAINEL)
        self.assertIn("localStorage.removeItem('cockpit_token')", PAINEL)
        self.assertNotIn("localStorage.setItem('cockpit_token'", PAINEL)
        self.assertIn("window.removerSegredosPoolLocal = function(pool)", PAINEL)
        self.assertIn("window.persistirPoolLocalSemSegredos(pool)", PAINEL)
        self.assertNotIn("localStorage.setItem('newapi_token'", PAINEL)
        self.assertIn("sessionStorage.setItem('newapi_token', limpo)", PAINEL)
        self.assertNotIn(
            "localStorage.setItem(window.STORAGE_KEY_POOL_3_IAS, JSON.stringify(pool))",
            PAINEL,
        )

        logout_start = PAINEL.index("window.executarLogoutSistema = function")
        logout_end = PAINEL.index("window.verificarAutenticacaoCockpit = function", logout_start)
        logout = PAINEL[logout_start:logout_end]
        self.assertIn("localStorage.removeItem('cockpit_token')", logout)
        self.assertIn("localStorage.removeItem('newapi_token')", logout)
        self.assertIn("localStorage.removeItem('sagti_openproject_token')", logout)
        self.assertIn("sessionStorage.clear()", logout)

    def test_sei_status_request_sends_api_authentication(self):
        self.assertIn(
            "fetch('/api/v1/sei/status', { headers: obterHeadersComAuth() })",
            PAINEL,
        )

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
