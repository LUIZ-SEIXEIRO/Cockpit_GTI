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
        "txtusuario", "plataforma.sp.gov.br", "minhaarea.sp.gov.br"
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
        """Cria o arquivo com permissão restrita 0600 em nível de syscall."""
        os.makedirs(os.path.dirname(self.caminho_sessao), exist_ok=True)
        conteudo = json.dumps({
            "atualizado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cookies": cookies_dict
        }, indent=2).encode("utf-8")
        
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        mode = 0o600
        try:
            fd = os.open(self.caminho_sessao, flags, mode)
            with os.fdopen(fd, 'wb') as f:
                f.write(conteudo)
            try:
                os.chmod(self.caminho_sessao, 0o600)
            except Exception:
                pass
        except Exception:
            with open(self.caminho_sessao, "wb") as f:
                f.write(conteudo)
                
        self.carregar_sessao()

    def carregar_sessao(self):
        """Carrega cookies vinculando-os exclusivamente a HTTPS, domínio e path do SEI."""
        if os.path.exists(self.caminho_sessao):
            try:
                with open(self.caminho_sessao, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                cookies = dados.get("cookies", {})
                self.session.cookies.clear()
                for k, v in cookies.items():
                    # Restringe o cookie ao domínio e path estrito
                    self.session.cookies.set(k, v, domain=self.DOMINIO_COOKIE, path="/sei")
                return True
            except Exception:
                pass
        return False

    def validar_sessao(self):
        """Valida a sessão exigindo HTTP 200, ausência de erros e presença de marcadores autenticados."""
        try:
            url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={self.UNIDADE_SAGTI}"
            resp = self.session.get(url, timeout=6, allow_redirects=True)
            if resp.status_code != 200:
                return {"autenticado": False, "codigo": resp.status_code, "mensagem": f"Erro do servidor SEI: HTTP {resp.status_code}"}
            
            texto_lower = resp.text.lower()
            if any(termo in texto_lower for termo in self.TERMOS_ERRO) or "plataforma.sp.gov.br" in resp.url or "minhaarea.sp.gov.br" in resp.url:
                return {"autenticado": False, "mensagem": "Sessão expirada ou página de login reportada pelo SEI."}
            
            if "procedimento_controlar" in resp.url and ("id_procedimento" in resp.text or "infraunidadeatual" in texto_lower or "inframenu" in texto_lower):
                return {"autenticado": True, "unidade": self.UNIDADE_SAGTI, "mensagem": "Sessão ativa na SA-GTI"}
            
            return {"autenticado": False, "mensagem": "Tela de acesso não autenticada."}
        except Exception as e:
            return {"autenticado": False, "erro": str(e), "mensagem": "Falha de conexão com o SEI"}

    def buscar_processos(self, termo="", unidade=None):
        """Busca processos no SEI rejeitando páginas de login ou respostas de erro."""
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
            texto_lower = resp.text.lower()
            if resp.status_code != 200 or any(t in texto_lower for t in self.TERMOS_ERRO) or "plataforma.sp.gov.br" in resp.url:
                return {"sucesso": False, "erro": "Sessão expirada ou erro na busca.", "processos": []}
            return self.parsear_tabela_busca(resp.text)
        except Exception as e:
            return {"sucesso": False, "erro": str(e), "processos": []}

    def listar_caixa_unidade(self, unidade=None):
        """Lista processos da caixa da SA-GTI rejeitando páginas de login ou respostas de erro."""
        unidade = unidade or self.UNIDADE_SAGTI
        url = f"{self.BASE_URL}/controlador.php?acao=procedimento_controlar&infra_sistema={self.SISTEMA_ID}&infra_unidade_atual={unidade}"
        try:
            resp = self.session.get(url, timeout=10)
            texto_lower = resp.text.lower()
            if resp.status_code != 200 or any(t in texto_lower for t in self.TERMOS_ERRO) or "plataforma.sp.gov.br" in resp.url:
                return {"sucesso": False, "erro": "Sessão expirada ou acesso negado.", "processos": []}
            return self.parsear_tabela_caixa(resp.text)
        except Exception as e:
            return {"sucesso": False, "erro": str(e), "processos": []}

    def parsear_tabela_caixa(self, html):
        """Parser resiliente que extrai processos independentemente de atributos antes ou após o href."""
        processos = []
        # Captura links <a> com href para procedimento_trabalhar e extrai id_procedimento
        padrao = r'<a\s+[^>]*href="[^"]*controlador\.php\?[^"]*id_procedimento=(\d+)[^"]*"[^>]*>(.*?)</a>'
        matches = re.findall(padrao, html, flags=re.DOTALL | re.IGNORECASE)
        for id_proc, texto_bruto in matches:
            num_proc = re.sub(r'<[^>]+>', '', texto_bruto).strip()
            if num_proc:
                processos.append({
                    "id_procedimento": id_proc,
                    "ID_Processo": num_proc,
                    "Prefixo_Orgao": num_proc[:3] if "." in num_proc else "137",
                    "link_sei": f"{self.BASE_URL}/controlador.php?acao=procedimento_trabalhar&id_procedimento={id_proc}",
                    "unidade": "SA-GTI"
                })
        return {"sucesso": True, "total": len(processos), "processos": processos}

    def parsear_tabela_busca(self, html):
        return self.parsear_tabela_caixa(html)
