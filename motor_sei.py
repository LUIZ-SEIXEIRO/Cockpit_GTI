import os, json, re, time, requests, urllib.parse, posixpath, tempfile, html as html_lib

class MotorSEI:
    """Motor de Scraping, Busca e Classificação do SEI SP (v4.1.5 Oficial) para a SA-GTI."""
    
    BASE_URL = "https://sei.sp.gov.br/sei"
    HOST_PERMITIDO = "sei.sp.gov.br"
    UNIDADE_SAGTI = "110050725"
    SISTEMA_ID = "100000100"
    
    TERMOS_ERRO = [
        "infraexception", "acesso negado", "sessão inválida", "sessao invalida",
        "não foi possível", "erro no sistema", "falha na autenticação",
        "txtusuario", "plataforma.sp.gov.br", "minhaarea.sp.gov.br", "acesso.gov.br",
        "erro no processamento", "sistema indisponível", "erro interno", "falha na execução"
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
        """Gravação atômica com arquivo temporário terminando compulsoriamente em .tmp."""
        dir_sessao = os.path.dirname(self.caminho_sessao)
        os.makedirs(dir_sessao, exist_ok=True)
        
        conteudo = json.dumps({
            "atualizado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cookies": cookies_dict
        }, indent=2).encode("utf-8")
        
        tmp_path = None
        try:
            # Cria temporário com prefixo e sufixo .tmp para cobertura no .dockerignore
            with tempfile.NamedTemporaryFile(dir=dir_sessao, prefix="sessao_sei_", suffix=".tmp", delete=False, mode="wb") as f_tmp:
                tmp_path = f_tmp.name
                f_tmp.write(conteudo)
                
            try:
                os.chmod(tmp_path, 0o600)
            except Exception:
                pass
                
            if hasattr(os, "stat") and hasattr(os, "getuid"):
                st = os.stat(tmp_path)
                if (st.st_mode & 0o077) != 0:
                    raise PermissionError("Insegurança: impossível garantir permissão 0600.")

            # Substituição atômica
            os.replace(tmp_path, self.caminho_sessao)
            tmp_path = None
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                    
        self.carregar_sessao()

    def carregar_sessao(self):
        """Carrega cookies vinculando-os exclusivamente ao host sei.sp.gov.br e path /sei."""
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
        """Valida destino normalizado com unquote e bloqueia vazamento em redirects."""
        parsed = urllib.parse.urlparse(url)
        path_decodificado = urllib.parse.unquote(parsed.path)
        norm_path = posixpath.normpath(path_decodificado)
        
        if parsed.scheme != "https" or parsed.hostname != self.HOST_PERMITIDO or (not norm_path.startswith("/sei/") and norm_path != "/sei"):
            raise ValueError(f"Destino não autorizado: {url}")
            
        resp = self.session.request(metodo, url, allow_redirects=False, **kwargs)
        if resp.is_redirect:
            loc = resp.headers.get("Location", "")
            loc_url = urllib.parse.urljoin(url, loc)
            p_loc = urllib.parse.urlparse(loc_url)
            p_loc_norm = posixpath.normpath(urllib.parse.unquote(p_loc.path))
            if p_loc.scheme != "https" or p_loc.hostname != self.HOST_PERMITIDO or (not p_loc_norm.startswith("/sei/") and p_loc_norm != "/sei"):
                return resp
            return self.session.request(metodo, loc_url, allow_redirects=False, **kwargs)
        return resp

    def _pagina_caixa_valida(self, resp):
        """Validação positiva exigindo form real do SEI (por id, name ou action)."""
        if resp.status_code != 200:
            return False
        parsed = urllib.parse.urlparse(resp.url)
        norm_path = posixpath.normpath(urllib.parse.unquote(parsed.path))
        if parsed.scheme != "https" or parsed.hostname != self.HOST_PERMITIDO or (not norm_path.startswith("/sei/") and norm_path != "/sei"):
            return False
            
        # Descarta comentários HTML
        texto_limpo = re.sub(r"<!--.*?-->", "", resp.text, flags=re.DOTALL)
        texto_lower = texto_limpo.lower()
        if any(t in texto_lower for t in self.TERMOS_ERRO):
            return False
            
        # Procura form legítimo ativo
        tem_form = False
        for tag in re.findall(r"<form[^>]+>", texto_limpo, flags=re.IGNORECASE):
            t_low = tag.lower()
            if "frmprocedimentocontrolar" in t_low or "procedimento_controlar" in t_low or "controlador.php" in t_low:
                tem_form = True
                break
                
        tem_tabela = "infratabela" in texto_lower or "infraareadados" in texto_lower or "id_procedimento" in texto_lower
        return tem_form and tem_tabela

    def _pagina_busca_valida(self, resp):
        if resp.status_code != 200:
            return False
        parsed = urllib.parse.urlparse(resp.url)
        norm_path = posixpath.normpath(urllib.parse.unquote(parsed.path))
        if parsed.scheme != "https" or parsed.hostname != self.HOST_PERMITIDO or (not norm_path.startswith("/sei/") and norm_path != "/sei"):
            return False
            
        texto_limpo = re.sub(r"<!--.*?-->", "", resp.text, flags=re.DOTALL)
        texto_lower = texto_limpo.lower()
        if any(t in texto_lower for t in self.TERMOS_ERRO):
            return False
            
        tem_form = False
        for tag in re.findall(r"<form[^>]+>", texto_limpo, flags=re.IGNORECASE):
            t_low = tag.lower()
            if "frmpesquisa" in t_low or "pesquisa_processo" in t_low or "controlador.php" in t_low:
                tem_form = True
                break
                
        tem_resultado = "infratabela" in texto_lower or "procedimento_trabalhar" in texto_lower or "nenhum" in texto_lower
        return tem_form and tem_resultado

    def validar_sessao(self):
        try:
            url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={self.UNIDADE_SAGTI}"
            resp = self._executar_requisicao_segura("GET", url, timeout=6)
            if not self._pagina_caixa_valida(resp):
                return {"autenticado": False, "codigo": resp.status_code, "mensagem": "Sessão expirada ou resposta não autorizada."}
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
        """Parser preciso sem SyntaxError: trata &amp;, aspas simples/duplas e acao estrita."""
        processos = []
        tags_a = re.findall(r"<a\s+([^>]+)>(.*?)</a>", html, flags=re.DOTALL | re.IGNORECASE)
        for attrs, texto_bruto in tags_a:
            m_href = re.search(r'''href=["']([^"']+)["']''', attrs, flags=re.IGNORECASE)
            if not m_href:
                continue
            href = html_lib.unescape(m_href.group(1))

            if not re.search(r"(?:^|[?&])acao=procedimento_trabalhar(?:&|$)", href):
                continue

            m_id = re.search(r"(?:^|[?&])id_procedimento=(\d+)(?:&|$)", href)
            if not m_id:
                continue
            id_proc = m_id.group(1)

            num_proc = re.sub(r"<[^>]+>", "", texto_bruto).strip()
            if num_proc and not any(ign in num_proc.lower() for ign in ["excluir", "anotação", "post-it"]):
                processos.append({
                    "id_procedimento": id_proc,
                    "ID_Processo": num_proc,
                    "Prefixo_Orgao": num_proc[:3] if "." in num_proc else "137",
                    "link_sei": f"{self.BASE_URL}/controlador.php?acao=procedimento_trabalhar&id_procedimento={id_proc}",
                    "unidade": "SA-GTI"
                })
        return {"sucesso": True, "total": len(processos), "processos": processos}
