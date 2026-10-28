from .ext_01_doesp_gov_br import buscar_publicacoes_doesp
from .ext_02_pncp_gov_br import consultar_editais_pncp
from .ext_03_sigrh_soi_gov_br import consultar_telemetria_sigrh
from .ext_04_zabbix_noc_bacias import obter_alertas_noc_bacias

def obter_resumo_busca_externa() -> dict:
    """Consolida os 4 robôs de busca ativa externa (Zero CORS)."""
    return {
        "resumo": "4/4 Portais Externos Monitorados",
        "doesp": buscar_publicacoes_doesp(),
        "pncp": consultar_editais_pncp(),
        "sigrh": consultar_telemetria_sigrh(),
        "noc_zabbix": obter_alertas_noc_bacias()
    }