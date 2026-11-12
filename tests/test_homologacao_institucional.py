import unittest, json, os, urllib.error
from unittest.mock import patch, mock_open
from main import app, resolver_chave_real, mascarar_chaves_recursivo, mesclar_preservando_segredos

class TestHomologacaoInstitucional(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('main.checar_porta', return_value=True)
    def test_01_telemetria_endpoints_isolados(self, mock_porta):
        """Valida que todos os endpoints de telemetria retornam status 200 isolados de socket físico."""
        for servico in ['mariadb', 'ollama', 'glpi', 'openproject', 'newapi']:
            res = self.client.get(f'/api/v1/{servico}/status')
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIn('status', data)
        mock_porta.assert_called()

    def test_02_autorizacao_estrita_mutacao(self):
        """Valida que rotas mutáveis sem token recebem HTTP 401."""
        res = self.client.post('/api/v1/ia/chat', json={'messages': []})
        self.assertEqual(res.status_code, 401)

    def test_03_sync_card_rejeita_json_invalido(self):
        with patch.dict(os.environ, {'API_TOKEN': 'token_sync_teste'}):
            for dados in ('{"', '["lista"]'):
                res = self.client.post(
                    '/api/v1/openproject/sync_card',
                    headers={'Authorization': 'Bearer token_sync_teste'},
                    data=dados,
                    content_type='application/json',
                )
                self.assertEqual(res.status_code, 400)

    def test_04_mascaramento_pool_get(self):
        """Comprova ativamente que o GET /api/v1/ia/pool mascara chaves reais substituindo por '***'."""
        pool_com_segredo = {
            "ias": {
                "slot_teste": {
                    "id": "slot_teste",
                    "agent": "qwen2.5:14b",
                    "apiKey": "sk-chave-real-secreta-123456"
                }
            }
        }
        with patch.dict(os.environ, {'API_TOKEN': 'token_pool_teste'}), \
             patch('builtins.open', mock_open(read_data=json.dumps(pool_com_segredo))), \
             patch('os.path.exists', return_value=True):
            res = self.client.get('/api/v1/ia/pool', headers={'Authorization': 'Bearer token_pool_teste'})
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIn('ias', data)
            self.assertEqual(data['ias']['slot_teste']['apiKey'], '***')
            self.assertNotIn('sk-chave-real-secreta-123456', json.dumps(data))

    def test_05_isolamento_chaves_ausentes_ou_mascaradas_em_slot_existente(self):
        """Valida que um slot sem chave não toma emprestada chave de outro slot."""
        pool_ficticio = {
            "ias": {
                "slot_sem_chave": {
                    "id": "slot_sem_chave",
                    "agent": "qwen2.5:14b",
                    "apiKey": ""
                },
                "slot_com_chave": {
                    "id": "slot_com_chave",
                    "agent": "qwen2.5:14b",
                    "apiKey": "sk-chave-outro-slot"
                }
            }
        }
        for chave_ausente in ('', '***', 'sk-CHAVE-SANITIZADA-INSTITUCIONAL'):
            with self.subTest(api_key=chave_ausente):
                pool_ficticio["ias"]["slot_sem_chave"]["apiKey"] = chave_ausente
                with patch('builtins.open', mock_open(read_data=json.dumps(pool_ficticio))), \
                     patch('os.path.exists', return_value=True), \
                     patch.dict(os.environ, {'NEWAPI_API_KEY': '', 'NEW_API_KEY': ''}):
                    chave = resolver_chave_real(modelo='qwen2.5:14b', slot='slot_sem_chave')
                    self.assertEqual(chave, '')

    @patch('urllib.request.urlopen')
    def test_06_sync_batch_falha_rede_isolada(self, mock_urlopen):
        """Simula falha de rede no OpenProject e comprova que urlopen foi invocado e retornou 502."""
        mock_urlopen.side_effect = urllib.error.URLError('Falha simulada de conexao em sandbox')
        with patch.dict(os.environ, {'COCKPIT_API_TOKEN': 'token_teste_hermetico', 'OPENPROJECT_URL': 'https://openproject.spaguas.sp.gov.br'}):
            headers = {'Authorization': 'Bearer token_teste_hermetico'}
            res = self.client.post('/api/v1/openproject/sync_batch', headers=headers, json={'itens': [{'id': 99999, 'descricao': 'Teste'}]})
            self.assertEqual(res.status_code, 502)
            data = res.get_json()
            self.assertFalse(data.get('sucesso'))
            mock_urlopen.assert_called()

    @patch('urllib.request.urlopen')
    def test_07_glpi_falha_rede_isolada(self, mock_urlopen):
        """Simula falha de rede no GLPI com tokens configurados e comprova chamada de urlopen e retorno 502."""
        mock_urlopen.side_effect = urllib.error.URLError('Falha simulada GLPI')
        with patch('os.path.exists', return_value=False), \
             patch.dict(os.environ, {
                 'API_TOKEN': 'token_glpi_teste',
                 'GLPI_URL': 'https://glpi.fake.spaguas.sp.gov.br',
                 'GLPI_APP_TOKEN': 'token_app_fake',
                 'GLPI_USER_TOKEN': 'token_user_fake',
             }):
            res = self.client.get(
                '/api/v1/glpi/tickets',
                headers={'Authorization': 'Bearer token_glpi_teste'},
            )
            self.assertEqual(res.status_code, 502)
            self.assertNotIn('Falha simulada GLPI', res.get_data(as_text=True))
            mock_urlopen.assert_called()

if __name__ == '__main__':
    unittest.main()
