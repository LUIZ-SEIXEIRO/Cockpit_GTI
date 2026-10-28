def listar_processos_sei(limite: int = 10) -> list:
    return [
        {
            "numero": "137.00011338/2026-99",
            "assunto": "Modernização e Sustentação do SOE (Outorga Eletrônica)",
            "unidade": "SA-GTI-DGD",
            "status": "Em Instrução Técnica (ETP 159/2026)",
            "criticidade": "Alta",
            "fixado": True
        },
        {
            "numero": "137.00004512/2026-31",
            "assunto": "Contratação de Nuvem Pública e Governança FinOps",
            "unidade": "SA-GTI-DIF",
            "status": "Em Cotação de Mercado",
            "criticidade": "Alta",
            "fixado": True
        },
        {
            "numero": "137.00008819/2026-44",
            "assunto": "Fábrica de Software e Sustentação de Sistemas Corporativos",
            "unidade": "SA-GTI-DGD",
            "status": "Execução Contratual (Aferição IMR)",
            "criticidade": "Média",
            "fixado": False
        }
    ]

def listar_processos_fixados() -> list:
    return [p for p in listar_processos_sei() if p.get("fixado")]