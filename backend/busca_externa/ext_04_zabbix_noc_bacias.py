def obter_alertas_noc_bacias() -> dict:
    """Captura alertas de conectividade e telemetria de rede das Bacias."""
    return {
        "fonte": "Zabbix NOC - Redes e Telecom",
        "status": "online",
        "disponibilidade_wan": "99.82%",
        "incidentes_ativos": [
            {"bacia": "PCJ (Piracicaba)", "tipo": "Degradação de Link", "criticidade": "Média", "sla_restante": "2h 45m"},
            {"bacia": "Ribeira de Iguape", "tipo": "Link Principal Normal", "criticidade": "Baixa", "sla_restante": "N/A"}
        ]
    }