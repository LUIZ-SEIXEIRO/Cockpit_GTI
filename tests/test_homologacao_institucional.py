import unittest, json, os, urllib.error
from unittest.mock import patch
from main import app, resolver_chave_real, mascarar_chaves_recursivo, mesclar_preservando_segredos

class TestHomologacaoInstitucional(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_telemetria_endpoints(self):
        """Valida que todos os 5 endpoints de infra retornam status 200 e campo 'status'."""
        for servico in ['mariadb', 'ollama', 'glpi', 'openproject', 'newapi']:
            res = self.client.get(f'/api/v1/{servico}/status')
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIn('status', data)

    def test_02_autorizacao_estrita_mutacao(self):
        """Valida que rotas mutáveis exigem token e rejeitam chamadas sem credencial com HTTP 401."""
        res = self.client.post('/api/v1/ia/chat', json={'messages': []})
        self.assertEqual(res.status_code, 401)

    def test_03_mascaramento_pool_get(self):
        """Valida que o GET /api/v1/ia/pool mascara 100% das chaves ativas com '***'."""
        res = self.client.get('/api/v1/ia/pool')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        def checar_mascara(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if any(t in k.lower() for t in ('apikey', 'api_key', 'chave', 'secret', 'token')):
                        self.assertIn(v, ('', '***'))
                    else:
                        checar_mascara(v)
            elif isinstance(obj, list):
                for i in obj: checar_mascara(i)
        checar_mascara(data)

    def test_04_isolamento_chave_vazia_sem_fallback(self):
        """Valida que slot com chave vazia retorna expressamente string vazia sem empréstimo."""
        chave = resolver_chave_real(modelo='modelo_inexistente_xyz', slot='slot_inexistente_abc')
        self.assertEqual(chave, '')

    @patch('urllib.request.urlopen')
    def test_05_sync_batch_falha_rede_isolada(self, mock_urlopen):
        """Simula falha de rede isolada (mock) no OpenProject e comprova resposta HTTP 502."""
        mock_urlopen.side_effect = urllib.error.URLError('Falha simulada de conexao em sandbox')
        token = os.getenv('COCKPIT_API_TOKEN') or 'token_teste_spaguas'
        os.environ['COCKPIT_API_TOKEN'] = token
        headers = {'Authorization': f'Bearer {token}'}
        res = self.client.post('/api/v1/openproject/sync_batch', headers=headers, json={'itens': [{'id': 99999, 'descricao': 'Teste'}]})
        self.assertEqual(res.status_code, 502)
        data = res.get_json()
        self.assertFalse(data.get('sucesso'))

    @patch('urllib.request.urlopen')
    def test_06_glpi_falha_rede_isolada(self, mock_urlopen):
        """Simula falha de rede isolada (mock) no GLPI sem cache e comprova resposta HTTP 502."""
        mock_urlopen.side_effect = urllib.error.URLError('Falha simulada de conexao GLPI')
        with patch('os.path.exists', return_value=False):
            res = self.client.get('/api/v1/glpi/tickets')
            self.assertEqual(res.status_code, 502)

if __name__ == '__main__':
    unittest.main()
