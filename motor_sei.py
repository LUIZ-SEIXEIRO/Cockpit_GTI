import os, json, re, time, requests, urllib.parse

class MotorSEI:
    """Motor de Scraping, Busca e Classificação do SEI SP (v4.1.5 Oficial) para a SA-GTI."""
    
    BASE_URL = "https://sei.sp.gov.br/sei"
    HOST_PERMITIDO = "sei.sp.gov.br"
    UNIDADE_SAGTI = "110050725"
    SISTEMA_ID = "100000100"
    
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
        """Remove arquivo preexistente e cria arquivo atômico com permissão 0600."""
        os.makedirs(os.path.dirname(self.caminho_sessao), exist_ok=True)
        if os.path.exists(self.caminho_sessao):
            try:
                os.remove(self.caminho_sessao)
            except Exception:
                pass

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
        """Carrega cookies estritamente para https://sei.sp.gov.br/sei."""
        if os.path.exists(self.caminho_sessao):
            try:
                with open(self.caminho_sessao, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                cookies = dados.get("cookies", {})
                self.session.cookies.clear()
                for k, v in cookies.items():
                    self.session.cookies.set(k, v, domain=self.HOST_PERMITIDO, path="/sei", secure=True)
                return True
            except Exception:
                pass
        return False

    def _executar_requisicao_segura(self, metodo, url, **kwargs):
        """Garante que a requisição siga estritamente para HTTPS e host permitido."""
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != self.HOST_PERMITIDO:
            raise ValueError(f"Destino não autorizado: {url}")
        return self.session.request(metodo, url, **kwargs)

    def _pagina_caixa_valida(self, resp):
        """Validação positiva rigorosa exigindo host HTTPS exato e marcadores estruturais do SEI."""
        if resp.status_code != 200:
            return False
        parsed = urllib.parse.urlparse(resp.url)
        if parsed.scheme != "https" or parsed.hostname != self.HOST_PERMITIDO:
            return False
        texto = resp.text.lower()
        if any(t in texto for t in self.TERMOS_ERRO):
            return False
        # Exige múltiplos marcadores estruturais simultâneos
        tem_controlar = "procedimento_controlar" in texto or "controle de processos" in texto
        tem_tabela = "infratabela" in texto or "infraareadados" in texto or "id_procedimento" in texto
        return tem_controlar and tem_tabela

    def _pagina_busca_valida(self, resp):
        """Validação positiva da tela de pesquisa."""
        if resp.status_code != 200:
            return False
        parsed = urllib.parse.urlparse(resp.url)
        if parsed.scheme != "https" or parsed.hostname != self.HOST_PERMITIDO:
            return False
        texto = resp.text.lower()
        if any(t in texto for t in self.TERMOS_ERRO):
            return False
        tem_busca = "pesquisa_processo" in texto or "resultado da pesquisa" in texto
        tem_resultado = "infratabela" in texto or "procedimento_trabalhar" in texto or "nenhum" in texto
        return tem_busca and tem_resultado

    def validar_sessao(self):
        try:
            url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={self.UNIDADE_SAGTI}"
            resp = self._executar_requisicao_segura("GET", url, timeout=6, allow_redirects=True)
            if not self._pagina_caixa_valida(resp):
                return {"autenticado": False, "codigo": resp.status_code, "mensagem": "Sessão expirada ou página de login/erro reportada pelo SEI."}
            return {"autenticado": True, "unidade": self.UNIDADE_SAGTI, "mensagem": "Sessão ativa na SA-GTI"}
        except Exception as e:
            return {"autenticado": False, "erro": str(e), "mensagem": "Falha de conexão com o SEI"}

    def buscar_processos(self, termo="", unidade=None):
        unidade = unidade or self.UNIDADE_SAGTI
        url = f"{self.BASE_URL}/controlador.php?acao=pesquisa_processo_pesquisar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={unidade}"
        payload = {
            "txtPalavraChave": termo,
            "chkSinonimo": "S",
            "optData": "0",
            "btnPesquisar": "Pesquisar"
        }
        try:
            resp = self._executar_requisicao_segura("POST", url, data=payload, timeout=10)
            if not self._pagina_busca_valida(resp):
                return {"sucesso": False, "codigo": resp.status_code, "erro": "Sessão expirada ou erro na busca.", "processos": []}
            return self.parsear_tabela_processos(resp.text)
        except Exception as e:
            return {"sucesso": False, "codigo": 502, "erro": f"Falha de conexão: {str(e)}", "processos": []}

    def listar_caixa_unidade(self, unidade=None):
        unidade = unidade or self.UNIDADE_SAGTI
        url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={unidade}"
        try:
            resp = self._executar_requisicao_segura("GET", url, timeout=10)
            if not self._pagina_caixa_valida(resp):
                return {"sucesso": False, "codigo": resp.status_code, "erro": "Sessão expirada ou acesso negado.", "processos": []}
            return self.parsear_tabela_processos(resp.text)
        except Exception as e:
            return {"sucesso": False, "codigo": 502, "erro": f"Falha de conexão: {str(e)}", "processos": []}

    def parsear_tabela_processos(self, html):
        """Parser preciso: suporta aspas simples/duplas, parâmetros em qualquer ordem e acao estrita."""
        processos = []
        tags_a = re.findall(r'<a\s+([^>]+)>(.*?)</a>', html, flags=re.DOTALL | re.IGNORECASE)
        for attrs, texto_bruto in tags_a:
            m_href = re.search(r'href=['"]([^'"]+)['"]', attrs, flags=re.IGNORECASE)
            if not m_href:
                continue
            href = m_href.group(1)

            # Valida que acao é ESTRITAMENTE procedimento_trabalhar (não aceita prefixos derivados)
            if not re.search(r'(?:^|[?&])acao=procedimento_trabalhar(?:&|$)', href):
                continue

            # Extrai id_procedimento em qualquer posição da query string
            m_id = re.search(r'(?:^|[?&])id_procedimento=(\d+)(?:&|$)', href)
            if not m_id:
                continue
            id_proc = m_id.group(1)

            num_proc = re.sub(r'<[^>]+>', '', texto_bruto).strip()
            if num_proc and not any(ign in num_proc.lower() for ign in ['excluir', 'anotação', 'post-it']):
                processos.append({
                    "id_procedimento": id_proc,
                    "ID_Processo": num_proc,
                    "Prefixo_Orgao": num_proc[:3] if "." in num_proc else "137",
                    "link_sei": f"{self.BASE_URL}/controlador.php?acao=procedimento_trabalhar&id_procedimento={id_proc}",
                    "unidade": "SA-GTI"
                })
        return {"sucesso": True, "total": len(processos), "processos": processos}
