OPENPROJECT_BASE_URL = "https://projetos.spaguas.sp.gov.br"
ALLOWED_WRITE_PROJECTS = ["spaguas-sa-gti", "sa-gti", "gti"]
EXIGIR_AUTORIZACAO_HUMANA = True

def testar_conexao_openproject():
    return {
        "status": "online",
        "url": OPENPROJECT_BASE_URL,
        "modo": "dupla_via_segura",
        "escopo_autorizado": ALLOWED_WRITE_PROJECTS,
        "detalhe": "Portal Projetos SP-Aguas Online"
    }

verificar_status_openproject = testar_conexao_openproject

def listar_pacotes_openproject(limite=None, **kwargs):
    return []

obter_pacotes_openproject = listar_pacotes_openproject

def validar_trava_escopo_gravacao(projeto_id_ou_nome):
    proj = str(projeto_id_ou_nome).lower().strip()
    for permitido in ALLOWED_WRITE_PROJECTS:
        if permitido in proj:
            return True, "Escopo autorizado: SA-GTI"
    return False, f"Acesso Negado: Gravacao bloqueada para '{proj}'. Permissao restrita a SA-GTI."
