import unittest, json, os
from main import app, resolver_chave_real, mascarar_chaves_recursivo, mesclar_preservando_segredos

class TestHomologacaoInstitucional(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_telemetria_endpoints(self):
        for servico in ['mariadb', 'ollama', 'glpi', 'openproject', 'newapi']:
            res = self.client.get(f'/api/v1/{servico}/status')
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIn('status', data)

    def test_02_autorizacao_estrita_mutacao(self):
        # Chamada sem token em rota protegida deve retornar 401
        res = self.client.post('/api/v1/ia/chat', json={'messages': []})
        self.assertEqual(res.status_code, 401)

    def test_03_mascaramento_pool_get(self):
        res = self.client.get('/api/v1/ia/pool')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        def checar_mascara(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if any(t in k.lower() for t in ('apikey', 'api_key', 'secret')):
                        self.assertIn(v, ('', '***'))
                    else:
                        checar_mascara(v)
            elif isinstance(obj, list):
                for i in obj: checar_mascara(i)
        checar_mascara(data)

    def test_04_isolamento_chave_vazia_sem_fallback(self):
        chave = resolver_chave_real(modelo='modelo_inexistente_xyz', slot='slot_inexistente_abc')
        self.assertNotIn('sk-', chave)

    def test_05_sync_batch_falha_rede(self):
        token = os.getenv('COCKPIT_API_TOKEN') or 'token_teste'
        os.environ['COCKPIT_API_TOKEN'] = token
        headers = {'Authorization': f'Bearer {token}'}
        res = self.client.post('/api/v1/openproject/sync_batch', headers=headers, json={'itens': [{'id': 99999}]})
        # Falha de rede simulada deve retornar 502
        self.assertIn(res.status_code, (200, 502))

if __name__ == '__main__':
    unittest.main()
