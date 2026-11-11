import os, json, re, time, requests

class MotorSEI:
    """Motor de Scraping, Busca e Classificação do SEI SP (v4.1.5 Oficial) para a SA-GTI."""
    
    BASE_URL = "https://sei.sp.gov.br/sei"
    UNIDADE_SAGTI = "110050725"
    SISTEMA_ID = "100000100"
    
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
        """Salva cookies de sessão autenticados em arquivo seguro."""
        os.makedirs(os.path.dirname(self.caminho_sessao), exist_ok=True)
        with open(self.caminho_sessao, "w", encoding="utf-8") as f:
            json.dump({
                "atualizado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "cookies": cookies_dict
            }, f, indent=2)
        self.carregar_sessao()

    def carregar_sessao(self):
        """Carrega os cookies salvos para a sessão HTTP."""
        if os.path.exists(self.caminho_sessao):
            try:
                with open(self.caminho_sessao, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                cookies = dados.get("cookies", {})
                self.session.cookies.update(cookies)
                return True
            except Exception:
                pass
        return False

    def validar_sessao(self):
        """Verifica se a sessão atual no SEI está ativa ou expirada."""
        try:
            url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={self.UNIDADE_SAGTI}"
            resp = self.session.get(url, timeout=6, allow_redirects=True)
            if "plataforma.sp.gov.br" in resp.url or "minhaarea.sp.gov.br" in resp.url or "txtUsuario" in resp.text:
                return {"autenticado": False, "mensagem": "Sessão expirada. Autenticação Gov.br requerida."}
            if "procedimento_controlar" in resp.url or "infra_unidade_atual" in resp.url:
                return {"autenticado": True, "unidade": self.UNIDADE_SAGTI, "mensagem": "Sessão ativa na SA-GTI"}
            return {"autenticado": False, "mensagem": "Resposta não conclusiva do SEI"}
        except Exception as e:
            return {"autenticado": False, "erro": str(e), "mensagem": "Erro de conexão com o SEI"}

    def buscar_processos(self, termo="", unidade=None):
        """Executa busca de processos no SEI por termo, número ou interessado."""
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
            return self.parsear_tabela_busca(resp.text)
        except Exception as e:
            return {"sucesso": False, "erro": str(e), "processos": []}

    def listar_caixa_unidade(self, unidade=None):
        """Lista os processos abertos na caixa de entrada da SA-GTI."""
        unidade = unidade or self.UNIDADE_SAGTI
        url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={unidade}"
        try:
            resp = self.session.get(url, timeout=10)
            return self.parsear_tabela_caixa(resp.text)
        except Exception as e:
            return {"sucesso": False, "erro": str(e), "processos": []}

    def parsear_tabela_caixa(self, html):
        """Extrai os dados da tabela de processos da caixa de entrada."""
        processos = []
        linhas = re.findall(r'href="controlador\.php\?acao=procedimento_trabalhar&id_procedimento=(\d+)[^"]*"\s*>([^<]+)</a>', html)
        for id_proc, num_proc in linhas:
            num_proc_limpo = num_proc.strip()
            processos.append({
                "id_procedimento": id_proc,
                "ID_Processo": num_proc_limpo,
                "Prefixo_Orgao": num_proc_limpo[:3] if "." in num_proc_limpo else "137",
                "link_sei": f"{self.BASE_URL}/controlador.php?acao=procedimento_trabalhar&id_procedimento={id_proc}",
                "unidade": "SA-GTI"
            })
        return {"sucesso": True, "total": len(processos), "processos": processos}

    def parsear_tabela_busca(self, html):
        """Extrai os resultados da tela de pesquisa de processos."""
        return self.parsear_tabela_caixa(html)
