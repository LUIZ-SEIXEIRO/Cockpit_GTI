import os, json, re, time, requests

class MotorSEI:
    """Motor de Scraping, Busca e Classificação do SEI SP (v4.1.5 Oficial) para a SA-GTI."""
    
    BASE_URL = "https://sei.sp.gov.br/sei"
    UNIDADE_SAGTI = "110050725"
    SISTEMA_ID = "100000100"
    DOMINIO_COOKIE = "sei.sp.gov.br"
    
    TERMOS_ERRO = [
        "infraexception", "acesso negado", "sessão inválida", "sessao invalida",
        "não foi possível", "erro no sistema", "falha na autenticação",
        "txtusuario", "plataforma.sp.gov.br", "minhaarea.sp.gov.br", "acesso.gov.br"
    ]
    
    def __init__(self, caminho_sessao=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.caminho_sessao = caminho_sessao or os.path.join(self.base_dir, "data", "sessao_sei.json")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
        })
        self.carregar_sessao()

    def salvar_sessao(self, cookies_dict):
        """Grava a sessão estritamente com permissão 0600 em nível de syscall (sem fallback permissivo)."""
        os.makedirs(os.path.dirname(self.caminho_sessao), exist_ok=True)
        conteudo = json.dumps({
            "atualizado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cookies": cookies_dict
        }, indent=2).encode("utf-8")
        
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        mode = 0o600
        fd = os.open(self.caminho_sessao, flags, mode)
        with os.fdopen(fd, 'wb') as f:
            f.write(conteudo)
        try:
            os.chmod(self.caminho_sessao, 0o600)
        except Exception:
            pass
        self.carregar_sessao()

    def carregar_sessao(self):
        """Carrega cookies vinculando-os com secure=True, domínio e path estritos."""
        if os.path.exists(self.caminho_sessao):
            try:
                with open(self.caminho_sessao, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                cookies = dados.get("cookies", {})
                self.session.cookies.clear()
                for k, v in cookies.items():
                    # Restringe o cookie com secure=True para HTTPS estrito
                    self.session.cookies.set(k, v, domain=self.DOMINIO_COOKIE, path="/sei", secure=True)
                return True
            except Exception:
                pass
        return False

    def _pagina_caixa_valida(self, resp):
        """Validação positiva da tela de controle de processos."""
        if resp.status_code != 200:
            return False
        url_lower = resp.url.lower()
        if any(d in url_lower for d in ['plataforma.sp.gov.br', 'minhaarea.sp.gov.br', 'acesso.gov.br']):
            return False
        texto = resp.text.lower()
        if any(t in texto for t in self.TERMOS_ERRO):
            return False
        # Exige elementos característicos positivos do SEI
        elementos_positivos = ['procedimento_controlar', 'controle de processos', 'infratabela', 'infraareadados', 'id_procedimento']
        return any(el in texto for el in elementos_positivos)

    def _pagina_busca_valida(self, resp):
        """Validação positiva da tela de pesquisa de processos."""
        if resp.status_code != 200:
            return False
        url_lower = resp.url.lower()
        if any(d in url_lower for d in ['plataforma.sp.gov.br', 'minhaarea.sp.gov.br', 'acesso.gov.br']):
            return False
        texto = resp.text.lower()
        if any(t in texto for t in self.TERMOS_ERRO):
            return False
        elementos_positivos = ['pesquisa_processo', 'resultado da pesquisa', 'infratabela', 'procedimento_trabalhar', 'nenhum registro encontrado', 'nenhum processo encontrado']
        return any(el in texto for el in elementos_positivos)

    def validar_sessao(self):
        """Valida sessão exigindo confirmação positiva dos elementos de controle do SEI."""
        try:
            url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={self.UNIDADE_SAGTI}"
            resp = self.session.get(url, timeout=6, allow_redirects=True)
            if not self._pagina_caixa_valida(resp):
                return {"autenticado": False, "codigo": resp.status_code, "mensagem": "Sessão expirada ou página de login/erro reportada pelo SEI."}
            return {"autenticado": True, "unidade": self.UNIDADE_SAGTI, "mensagem": "Sessão ativa na SA-GTI"}
        except Exception as e:
            return {"autenticado": False, "erro": str(e), "mensagem": "Falha de conexão com o SEI"}

    def buscar_processos(self, termo="", unidade=None):
        """Busca processos exigindo validação positiva da tela de pesquisa."""
        unidade = unidade or self.UNIDADE_SAGTI
        url = f"{self.BASE_URL}/controlador.php?acao=pesquisa_processo_pesquisar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={unidade}"
        payload = {
            "txtPalavraChave": termo,
            "chkSinonimo": "S",
            "optData": "0",
            "btnPesquisar": "Pesquisar"
        }
        try:
            resp = self.session.post(url, data=payload, timeout=10)
            if not self._pagina_busca_valida(resp):
                return {"sucesso": False, "erro": "Sessão expirada ou resposta inválida na pesquisa.", "processos": []}
            return self.parsear_tabela_processos(resp.text)
        except Exception as e:
            return {"sucesso": False, "erro": f"Falha de conexão: {str(e)}", "processos": []}

    def listar_caixa_unidade(self, unidade=None):
        """Lista processos da caixa exigindo validação positiva da tela."""
        unidade = unidade or self.UNIDADE_SAGTI
        url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={unidade}"
        try:
            resp = self.session.get(url, timeout=10)
            if not self._pagina_caixa_valida(resp):
                return {"sucesso": False, "erro": "Sessão expirada ou resposta inválida na caixa de entrada.", "processos": []}
            return self.parsear_tabela_processos(resp.text)
        except Exception as e:
            return {"sucesso": False, "erro": f"Falha de conexão: {str(e)}", "processos": []}

    def parsear_tabela_processos(self, html):
        """Parser preciso: suporta aspas simples/duplas e filtra exclusivamente acao=procedimento_trabalhar."""
        processos = []
        # Captura links <a> com href em aspas simples ou duplas contendo explicitamente procedimento_trabalhar
        padrao = r'<a\s+[^>]*href=['"][^'"]*acao=procedimento_trabalhar[^'"]*id_procedimento=(\d+)[^'"]*['"][^>]*>(.*?)</a>'
        matches = re.findall(padrao, html, flags=re.DOTALL | re.IGNORECASE)
        
        # Também verifica caso id_procedimento venha antes de acao=procedimento_trabalhar
        if not matches:
            padrao_alt = r'<a\s+[^>]*href=['"][^'"]*id_procedimento=(\d+)[^'"]*acao=procedimento_trabalhar[^'"]*['"][^>]*>(.*?)</a>'
            matches = re.findall(padrao_alt, html, flags=re.DOTALL | re.IGNORECASE)

        for id_proc, texto_bruto in matches:
            num_proc = re.sub(r'<[^>]+>', '', texto_bruto).strip()
            if num_proc and not any(ign in num_proc.lower() for ign in ['excluir', 'visualizar', 'anotação', 'post-it']):
                processos.append({
                    "id_procedimento": id_proc,
                    "ID_Processo": num_proc,
                    "Prefixo_Orgao": num_proc[:3] if "." in num_proc else "137",
                    "link_sei": f"{self.BASE_URL}/controlador.php?acao=procedimento_trabalhar&id_procedimento={id_proc}",
                    "unidade": "SA-GTI"
                })
        return {"sucesso": True, "total": len(processos), "processos": processos}
