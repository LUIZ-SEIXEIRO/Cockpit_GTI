from .sis_01_glpi_8088_prod import testar_conexao_glpi, listar_chamados_glpi
from .sis_02_openproject_8090_prod import testar_conexao_openproject, listar_pacotes_openproject
from .sis_03_newapi_ia_3001 import testar_conexao_newapi

def obter_status_sistemas_internos() -> dict:
    glpi = testar_conexao_glpi()
    op = testar_conexao_openproject()
    newapi = testar_conexao_newapi()
    total_online = sum(1 for s in [glpi, op, newapi] if s.get("status") == "online")
    return {
        "resumo": f"{total_online}/3 Sistemas Internos Online",
        "sistemas": [glpi, op, newapi],
        "detalhes": {"glpi": glpi, "openproject": op, "newapi": newapi}
    }