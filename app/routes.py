# H:\Cockpit_GTI\app\routes.py

from app import app
from flask import jsonify
from backend.sistemas_internos.sis_01_glpi_8088_prod import GLPIProductionConnector
import asyncio

# Instancia o conector de produção do GLPI
glpi_connector = GLPIProductionConnector()

@app.route('/')
def home():
    # Retorna o painel.html que está dentro de app/static/
    return app.send_static_file('painel.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Rota simples para verificar se o backend está online"""
    return jsonify({"status": "healthy"})

@app.route('/api/glpi/chamados', methods=['GET'])
def listar_chamados_glpi():
    """Endpoint oficial do Flask para consumo dos chamados reais do GLPI de Produção."""
    try:
        # Executa a chamada assíncrona do conector no loop de eventos do Flask
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        dados_brutos = loop.run_until_complete(glpi_connector.get_chamados(range_limit=50))
        loop.close()
        
        chamados_formatados = []
        if isinstance(dados_brutos, list):
            for t in dados_brutos:
                if isinstance(t, dict):
                    chamados_formatados.append({
                        "id": t.get("id"),
                        "titulo": t.get("name", "Sem Título"),
                        "requerente": "Atendimento SP-Águas",
                        "prioridade": str(t.get("priority", "Média")),
                        "status": "Em Andamento" if t.get("status") == 2 else "Novo",
                        "sla": "Monitorado"
                    })
        
        return jsonify({
            "status": "sucesso",
            "total": len(chamados_formatados) if chamados_formatados else (len(dados_brutos) if isinstance(dados_brutos, list) else 0),
            "dados": chamados_formatados if chamados_formatados else dados_brutos
        })
    except Exception as e:
        print(f"❌ Erro ao processar requisição em /api/glpi/chamados: {e}")
        return jsonify({
            "status": "erro",
            "mensagem": str(e),
            "dados": []
        }), 500