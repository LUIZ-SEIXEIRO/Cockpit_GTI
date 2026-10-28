def obter_painel_auditoria_tce() -> dict:
    return {
        "orgao_fiscalizador": "Tribunal de Contas do Estado de SP (TCE-SP)",
        "sumula_tcu": "Súmula 269 - Aceite Técnico por Resultados e IMR em TIC",
        "indice_conformidade": "98.4%",
        "pontos_controle": [
            {"item": "Medição de Serviços por Resultados (IMR)", "status": "Conforme", "auditoria": "Aferição mensal sem glosas pendentes"},
            {"item": "Vedação de Remuneração Exclusiva por Posto de Trabalho", "status": "Conforme", "auditoria": "Catálogo de Serviços baseado em UST/PF"},
            {"item": "Matriz de Riscos de TIC (R01 a R12)", "status": "Conforme", "auditoria": "Mitigações revisadas no PDTIC 2027-2030"},
            {"item": "Resiliência e Política de Backup 3-2-1-1-0", "status": "Conforme", "auditoria": "Testes de restore em sandbox validados com RTO <= 4h"}
        ]
    }