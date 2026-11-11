import os, json, re, time, requests, urllib.parse, posixpath, tempfile, html as html_lib
from html.parser import HTMLParser

class ValidadorFormSEI(HTMLParser):
    """Parser HTML que valida exclusivamente tags <form> ativas com action e host autorizados."""
    def __init__(self, ids_alvo=None):
        super().__init__()
        self.ids_alvo = [i.lower() for i in (ids_alvo or [])]
        self.encontrou = False
        self.em_script = False

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in ('script', 'style'):
            self.em_script = True
            return
        if t == 'form' and not self.em_script:
            attrs_dict = {k.lower(): (v or '').lower() for k, v in attrs}
            f_id = attrs_dict.get('id', '')
            f_name = attrs_dict.get('name', '')
            f_act = attrs_dict.get('action', '')
            
            # PRIORIDADE MÁXIMA: Se houver action com hostname externo, REJEITA IMEDIATAMENTE
            if f_act:
                p_act = urllib.parse.urlparse(f_act)
                if p_act.hostname and p_act.hostname.lower() != 'sei.sp.gov.br':
                    return

            # Valida por ID ou Name do formulário
            for alvo in self.ids_alvo:
                if alvo == f_id or alvo == f_name:
                    self.encontrou = True
                    return

            # Valida por Action autorizada sob sei.sp.gov.br
            if f_act:
                p_act = urllib.parse.urlparse(f_act)
                caminho_act = posixpath.normpath(urllib.parse.unquote(p_act.path))
                if caminho_act in ('controlador.php', '/sei/controlador.php') or re.search(r'^(?:/sei/)?controlador\.php(?:\?|$)', f_act):
                    self.encontrou = True
                    return

    def handle_endtag(self, tag):
        if tag.lower() in ('script', 'style'):
            self.em_script = False

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
        """Gravação atômica transacional: consistência incondicional entre disco e memória."""
        dir_sessao = os.path.dirname(self.caminho_sessao)
        os.makedirs(dir_sessao, exist_ok=True)
        
        conteudo = json.dumps({
            "atualizado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cookies": cookies_dict
        }, indent=2).encode("utf-8")
        
        tmp_fd = None
        tmp_path = None
        backup_fd = None
        backup_path = None
        sucesso_replace = False
        ja_existia = os.path.exists(self.caminho_sessao)
        
        try:
            # 1. Se já existe sessão, cria backup com loop de escrita completa
            if ja_existia:
                try:
                    backup_fd, backup_path = tempfile.mkstemp(dir=dir_sessao, prefix="sessao_backup_", suffix=".tmp")
                    try:
                        os.fchmod(backup_fd, 0o600)
                    except Exception:
                        pass
                    with open(self.caminho_sessao, "rb") as f_src:
                        conteudo_backup = f_src.read()
                    
                    escritos_bkp = 0
                    while escritos_bkp < len(conteudo_backup):
                        n = os.write(backup_fd, conteudo_backup[escritos_bkp:])
                        escritos_bkp += n

                    os.fsync(backup_fd)
                    os.close(backup_fd)
                    backup_fd = None
                except Exception as e:
                    raise OSError(f"Falha ao criar backup integro da sessao: {str(e)}")

            # 2. Cria arquivo temporário novo com 0600
            tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_sessao, prefix="sessao_sei_", suffix=".tmp")
            try:
                os.fchmod(tmp_fd, 0o600)
            except Exception:
                pass
                    
            if hasattr(os, "fstat") and hasattr(os, "getuid"):
                st = os.fstat(tmp_fd)
                if (st.st_mode & 0o077) != 0:
                    raise PermissionError("Insegurança: permissão não restrita para 0600.")

            # 3. Escrita completa em loop
            escritos = 0
            while escritos < len(conteudo):
                n = os.write(tmp_fd, conteudo[escritos:])
                escritos += n

            # 4. fsync obrigatório do arquivo temporário
            try:
                os.fsync(tmp_fd)
            finally:
                os.close(tmp_fd)
                tmp_fd = None

            # 5. Substituição atômica no disco
            os.replace(tmp_path, self.caminho_sessao)
            sucesso_replace = True
            tmp_path = None

            # 6. fsync no diretório pai com rollback imediato se falhar
            if hasattr(os, "O_DIRECTORY"):
                try:
                    dir_fd = os.open(dir_sessao, os.O_RDONLY | os.O_DIRECTORY)
                    try:
                        os.fsync(dir_fd)
                    finally:
                        os.close(dir_fd)
                except Exception:
                    # ROLLBACK IMEDIATO:
                    if ja_existia and backup_path and os.path.exists(backup_path):
                        try:
                            os.replace(backup_path, self.caminho_sessao)
                            backup_path = None
                        except Exception:
                            # Se rollback falhar, limpa a memória para não manter sessão divergente
                            self.session.cookies.clear()
                            raise
                    elif not ja_existia and os.path.exists(self.caminho_sessao):
                        try:
                            os.remove(self.caminho_sessao)
                        except Exception:
                            self.session.cookies.clear()
                            raise
                    raise

            # 7. Recarrega a memória e exige sucesso absoluto (se falhar, levanta exceção e não retorna 200)
            if not self.carregar_sessao():
                raise OSError("Falha crítica ao recarregar a sessão na memória após persistência.")

        finally:
            if backup_fd is not None:
                try: os.close(backup_fd)
                except Exception: pass
            if backup_path and os.path.exists(backup_path):
                try: os.remove(backup_path)
                except Exception: pass
            if tmp_fd is not None:
                try: os.close(tmp_fd)
                except Exception: pass
            if not sucesso_replace and tmp_path and os.path.exists(tmp_path):
                try:
                    with open(tmp_path, "wb") as f_del:
                        f_del.write(b"\x00" * len(conteudo))
                        f_del.truncate(0)
                        f_del.flush()
                        os.fsync(f_del.fileno())
                except Exception: pass
                try: os.remove(tmp_path)
                except Exception: pass

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
            
        parser = ValidadorFormSEI(ids_alvo=["frmprocedimentocontrolar"])
        try:
            parser.feed(texto_limpo)
        except Exception:
            return False
            
        texto_sem_script = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", texto_limpo, flags=re.IGNORECASE)
        texto_sem_script = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", texto_sem_script, flags=re.IGNORECASE).lower()
        
        tem_tabela = "infratabela" in texto_sem_script or "infraareadados" in texto_sem_script or "id_procedimento" in texto_sem_script
        return parser.encontrou and tem_tabela

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
            
        parser = ValidadorFormSEI(ids_alvo=["frmpesquisaprocesso", "frmpesquisarapida"])
        try:
            parser.feed(texto_limpo)
        except Exception:
            return False
            
        texto_sem_script = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", texto_limpo, flags=re.IGNORECASE)
        texto_sem_script = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", texto_sem_script, flags=re.IGNORECASE).lower()
        
        tem_resultado = "infratabela" in texto_sem_script or "procedimento_trabalhar" in texto_sem_script or "nenhum" in texto_sem_script
        return parser.encontrou and tem_resultado

    def _detectar_expiracao(self, resp):
        loc = resp.headers.get("Location", "").lower()
        url = resp.url.lower()
        texto = resp.text.lower()
        termos_login = ["txtusuario", "plataforma.sp.gov.br", "minhaarea.sp.gov.br", "acesso.gov.br", "/login"]
        return any(t in texto or t in loc or t in url for t in termos_login)

    def validar_sessao(self):
        try:
            url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={self.UNIDADE_SAGTI}"
            resp = self._executar_requisicao_segura("GET", url, timeout=6)
            if not self._pagina_caixa_valida(resp):
                is_expired = self._detectar_expiracao(resp)
                return {"autenticado": False, "codigo": resp.status_code, "sessao_expirada": is_expired, "mensagem": "Sessão expirada ou resposta não autorizada."}
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
                is_expired = self._detectar_expiracao(resp)
                return {"sucesso": False, "codigo": resp.status_code, "sessao_expirada": is_expired, "erro": "Sessão expirada ou erro na busca.", "processos": []}
            return self.parsear_tabela_processos(resp.text)
        except Exception as e:
            return {"sucesso": False, "codigo": 502, "erro": f"Falha de conexão: {str(e)}", "processos": []}

    def listar_caixa_unidade(self, unidade=None):
        unidade = unidade or self.UNIDADE_SAGTI
        url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={unidade}"
        try:
            resp = self._executar_requisicao_segura("GET", url, timeout=10)
            if not self._pagina_caixa_valida(resp):
                is_expired = self._detectar_expiracao(resp)
                return {"sucesso": False, "codigo": resp.status_code, "sessao_expirada": is_expired, "erro": "Sessão expirada ou acesso negado.", "processos": []}
            return self.parsear_tabela_processos(resp.text)
        except Exception as e:
            return {"sucesso": False, "codigo": 502, "erro": f"Falha de conexão: {str(e)}", "processos": []}

    def parsear_tabela_processos(self, html):
        processos = []
        tags_a = re.findall(r"<a\s+([^>]+)>(.*?)</a>", html, flags=re.DOTALL | re.IGNORECASE)
        for attrs, texto_bruto in tags_a:
            m_href = re.search(r'href=["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
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
