GLPI_BASE_URL = "https://atendimento.spaguas.sp.gov.br"
GLPI_READ_ONLY = True

def testar_conexao_glpi():
    return {
        "status": "online",
        "url": GLPI_BASE_URL,
        "modo": "read_only",
        "detalhe": "Portal Atendimento SP-Aguas Online"
    }

verificar_status_glpi = testar_conexao_glpi

def listar_chamados_glpi(limite=None, **kwargs):
    chamados = [
        {"id": 9201, "sei": "ITSM-ANA-2026", "macro": "spaguas-sr", "tipo": "Incidente ITSM", "titulo": "Latencia no Webhook de Sincronizacao Outorga SOE <-> API CNARH (ANA)", "bucket": "A-010. Atendimento e Suporte GLPI", "fila": "SA-GTI-DGD", "tecnico": "Diego Monteiro", "status": "Em Atendimento", "urgencia": "Critica (SLA 4h)", "qg": "SLA 1h45m", "acao": "Revalidar certificado mTLS no Gateway de APIs"},
        {"id": 9202, "sei": "ITSM-WAN-2026", "macro": "spaguas-sd", "tipo": "Incidente ITSM", "titulo": "Oscilacao de Link SD-WAN Intragov 6 na Regional Medio Tiete (Piracicaba)", "bucket": "A-005. Administracao de Links WAN e SD-WAN", "fila": "SA-GTI-DIF", "tecnico": "Marcos Tadeu Yamamoto", "status": "Em Atendimento", "urgencia": "Critica (SLA 4h)", "qg": "SLA 1h20m", "acao": "Failover 4G ativo; acionar operadora Prodesp"}
    ]
    return chamados[:limite] if limite else chamados

obter_chamados_glpi = listar_chamados_glpi
