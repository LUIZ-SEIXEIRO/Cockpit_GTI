import os
import sys
import json
import time
import shutil
import tempfile
import logging
import hashlib
import threading
import socket
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse, parse_qs, unquote
import posixpath
import http.cookiejar
from html.parser import HTMLParser
import requests

logger = logging.getLogger("CockpitGTI.MotorSEI")


def _verificar_pid_so(pid: int) -> bool:
    """Consulta direta ao SO para verificar se o processo está em execução."""
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        STILL_ACTIVE = 259
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h_process:
            err = kernel32.GetLastError()
            if err == 5:  # ERROR_ACCESS_DENIED = processo existe e está vivo
                return True
            return False
        exit_code = ctypes.c_ulong()
        success = kernel32.GetExitCodeProcess(h_process, ctypes.byref(exit_code))
        kernel32.CloseHandle(h_process)
        return bool(success and exit_code.value == STILL_ACTIVE)
    else:
        os.kill(pid, 0)
        return True


def processo_esta_vivo(pid: int) -> bool:
    """
    Verifica se um processo com o PID fornecido ainda está em execução no host local.
    Falhas de permissão (EPERM / ERROR_ACCESS_DENIED) comprovam que o processo
    está vivo e impedem compulsoriamente a tomada indevida do lock.
    """
    if not pid or pid <= 0:
        return False
    if pid == os.getpid():
        return True

    try:
        return _verificar_pid_so(pid)
    except PermissionError:
        return True
    except OSError as e:
        import errno
        if getattr(e, "errno", None) == errno.EPERM:
            return True
        if getattr(e, "errno", None) == errno.ESRCH:
            return False
        return True
    except Exception:
        return True


def obter_fingerprint_armazenamento(caminho: str) -> Optional[tuple]:
    """Retorna tupla (mtime, size, sha256) garantindo fencing estrito no armazenamento."""
    if not os.path.exists(caminho):
        return None
    try:
        st = os.stat(caminho)
        with open(caminho, "rb") as f:
            conteudo = f.read()
        h = hashlib.sha256(conteudo).hexdigest()
        return (st.st_mtime, st.st_size, h)
    except OSError:
        return None


class StatusRetorno(dict):
    """
    Objeto de retorno para status da sessão. Funciona como dicionário,
    como booleano e como invocável (callable) para suportar qualquer contrato no Flask.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self

    def __bool__(self):
        return bool(self.get("ativa", False))


class ResultadoProcessosSEI(dict):
    """
    Estrutura de dados híbrida para retorno do SEI.
    Opera como dicionário para o main.py e como lista iterável.
    """
    def __init__(self, processos: list, **kwargs):
        super().__init__(
            sucesso=True,
            total=len(processos),
            processos=processos,
            itens=processos,
            **kwargs
        )
        self._lista = processos

    def __iter__(self):
        return iter(self._lista)

    def __len__(self):
        return len(self._lista)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._lista[item]
        return super().__getitem__(item)


class ValidadorEstruturalSEI(HTMLParser):
    """
    Parser HTML que valida rigorosamente elementos DOM estruturais legítimos do SEI,
    descartando compulsoriamente comentários HTML, blocos <script> e <style>.
    Exige compulsoriamente formulário formal (frmProcedimentoControlar ou frmPesquisa)
    com action segura, rejeitando inputs ou links soltos e containers genéricos.
    """
    def __init__(self, tipo_tela: str = "caixa", base_url: str = "https://sei.sp.gov.br/sei"):
        super().__init__()
        self.tipo_tela = tipo_tela  # 'caixa' ou 'pesquisa'
        self.base_url = base_url
        self.ignorar_conteudo = False
        self.estrutura_valida = False
        self.tem_div_mensagens = False
        self._dentro_div_mensagens = False
        self._mensagens_infra = []
        self._texto_visivel = []

    def handle_comment(self, data):
        pass

    def handle_starttag(self, tag: str, attrs: list):
        tag_lower = tag.lower()
        if tag_lower in ("script", "style"):
            self.ignorar_conteudo = True
            return

        if not self.ignorar_conteudo:
            attr_dict = {k.lower(): (v or "").lower() for k, v in attrs if k is not None}
            form_id = attr_dict.get("id", "")
            form_name = attr_dict.get("name", "")
            action = attr_dict.get("action", "")

            if tag_lower == "div" and attr_dict.get("id") == "divinframensagens":
                self.tem_div_mensagens = True
                self._dentro_div_mensagens = True

            if tag_lower == "form":
                if not self._action_segura(action):
                    return

                ids_invalidos = ("frmlogin", "login", "frmacessonegado", "frmerro")
                if any(inv in form_id or inv in form_name for inv in ids_invalidos):
                    return

                basename = posixpath.basename(posixpath.normpath(urlparse(action).path)).lower()
                if self.tipo_tela == "caixa":
                    if "frmprocedimentocontrolar" in form_id or (basename == "controlador.php" and "procedimento_controlar" in action):
                        self.estrutura_valida = True
                elif self.tipo_tela == "pesquisa":
                    if "frmpesquisa" in form_id or "frmpesquisa" in form_name or (basename == "controlador.php" and "pesquisa" in action):
                        self.estrutura_valida = True

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in ("script", "style"):
            self.ignorar_conteudo = False
        elif tag_lower == "div" and self._dentro_div_mensagens:
            self._dentro_div_mensagens = False

    def handle_data(self, data: str):
        if not self.ignorar_conteudo:
            self._texto_visivel.append(data)
            if self._dentro_div_mensagens:
                self._mensagens_infra.append(data)

    def obter_texto_visivel(self) -> str:
        return " ".join(self._texto_visivel).lower()

    def obter_texto_infra(self) -> str:
        return " ".join(self._mensagens_infra).strip().lower()

    def _action_segura(self, action: str) -> bool:
        if not action:
            return True
        unquoted = unquote(action)
        if ".." in unquoted:
            return False
        parsed = urlparse(unquoted)
        if parsed.netloc:
            sei_netloc = urlparse(self.base_url).netloc.lower()
            if parsed.netloc.lower() != sei_netloc:
                return False
        caminho_norm = posixpath.normpath(parsed.path)
        if parsed.path.startswith("/"):
            sei_path = urlparse(self.base_url).path.rstrip("/")
            if not caminho_norm.startswith(sei_path):
                return False
        basename = posixpath.basename(caminho_norm).lower()
        if basename and basename != "controlador.php":
            return False
        return True


class ValidadorFormSEI(ValidadorEstruturalSEI):
    def __init__(self, base_url: str = "https://sei.sp.gov.br/sei"):
        super().__init__(tipo_tela="caixa", base_url=base_url)

    @property
    def form_encontrado(self):
        return self.estrutura_valida


class ParserProcessosSEI(HTMLParser):
    def __init__(self):
        super().__init__()
        self.processos = []
        self.ignorar_conteudo = False
        self._dentro_de_link = False
        self._link_atual = None
        self._texto_link = []

    def handle_comment(self, data):
        pass

    def handle_starttag(self, tag: str, attrs: list):
        tag_lower = tag.lower()
        if tag_lower in ("script", "style"):
            self.ignorar_conteudo = True
            return

        if not self.ignorar_conteudo and tag_lower == "a":
            attr_dict = {k.lower(): v for k, v in attrs if k is not None}
            href = attr_dict.get("href", "")
            href_unquoted = unquote(href).replace("&amp;", "&")
            
            parsed = urlparse(href_unquoted)
            params = parse_qs(parsed.query)

            acoes = params.get("acao", [])
            if "procedimento_trabalhar" in acoes and "id_procedimento" in params:
                self._dentro_de_link = True
                self._link_atual = {
                    "href": href,
                    "id_procedimento": params["id_procedimento"][0],
                    "id_protocolo": params.get("id_protocolo", [None])[0]
                }
                self._texto_link = []

    def handle_data(self, data: str):
        if self._dentro_de_link:
            self._texto_link.append(data)

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in ("script", "style"):
            self.ignorar_conteudo = False
        elif tag_lower == "a" and self._dentro_de_link:
            numero_formatado = "".join(self._texto_link).strip()
            if self._link_atual:
                self._link_atual["numero"] = numero_formatado
                self.processos.append(self._link_atual)
            self._dentro_de_link = False
            self._link_atual = None
            self._texto_link = []


class LockProcessosSEI:
    """
    Exclusão mútua persistente e contínua imposta pelo kernel do sistema operacional.
    Utiliza fcntl.flock no Linux/POSIX e msvcrt.locking no Windows sobre arquivo de lock dedicado (.flock).
    O lock é mantido pela tabela de arquivos abertos do kernel do SO durante toda a operação,
    sendo 100% imune a pausas, suspensões ou desescalonamentos de processos e threads.
    O arquivo .flock NUNCA é removido, garantindo estabilidade de inode e eliminando corridas de deleção.
    Diretriz de Clean Cutover: todos os escritores antigos (v9 ou anteriores) devem ser interrompidos
    antes da implantação da v10; a coexistência entre versões não é homologada.
    """
    def __init__(
        self,
        caminho_sessao: str,
        timeout: float = 10.0,
        poll_interval: float = 0.05,
        max_lock_age: float = 30.0,
        hostname: Optional[str] = None
    ):
        self.caminho_sessao = os.path.abspath(caminho_sessao)
        self.lock_file = self.caminho_sessao + ".flock"
        self.lock_dir = self.caminho_sessao + ".lock"
        self.info_file = os.path.join(self.lock_dir, "lock.info")
        self.timeout = float(timeout)
        self.poll_interval = float(poll_interval)
        self.max_lock_age = float(max_lock_age)
        self.hostname = hostname or socket.gethostname()
        self.token = str(uuid.uuid4())
        self._adquirido = False
        self._fd: Optional[int] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_heartbeat = threading.Event()

    def verificar_lease_valido(self) -> bool:
        return bool(self._adquirido and self._fd is not None)

    def _liberar_kernel_lock(self):
        if self._fd is not None:
            if os.name == "nt":
                try:
                    import msvcrt
                    os.lseek(self._fd, 0, os.SEEK_SET)
                    msvcrt.locking(self._fd, msvcrt.LK_UNLCK, 1)
                except Exception:
                    pass
            else:
                try:
                    import fcntl
                    fcntl.flock(self._fd, fcntl.LOCK_UN)
                except Exception:
                    pass
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None
            self._adquirido = False

    def _verificar_e_limpar_lock_legado(self):
        """
        Garante conformidade com o Clean Cutover:
        Se houver diretório .lock legado de v9 com processo vivo, emite aviso ou bloqueio.
        Se for lock órfão (processo morto), limpa para permitir inicialização da v10.
        """
        if os.path.exists(self.lock_dir):
            if os.path.exists(self.info_file):
                try:
                    with open(self.info_file, "r", encoding="utf-8") as f:
                        info = json.load(f)
                    if not isinstance(info, dict):
                        raise RuntimeError(
                            "Clean Cutover Obrigatório: Metadados de lock.info inválidos. "
                            "Interrompa todos os processos v9 antes da troca para v10."
                        )
                    pid = info.get("pid")
                    host = info.get("hostname")
                    if not isinstance(host, str) or not host.strip() or not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
                        raise RuntimeError(
                            "Clean Cutover Obrigatório: Metadados incompletos em lock.info (hostname ou PID ausente/inválido). "
                            "Interrompa todos os processos v9 antes da troca para v10."
                        )
                    if host != self.hostname:
                        raise RuntimeError(
                            f"Clean Cutover Obrigatório: Detectado lock SEI legado de outro host ({host}, PID {pid}). "
                            "Interrompa todos os processos v9 antes da troca para v10."
                        )
                    if processo_esta_vivo(pid):
                        raise RuntimeError(
                            f"Clean Cutover Obrigatório: Detectado escritor SEI legado ativo (PID {pid}). "
                            "Interrompa todos os processos v9 antes da troca para v10."
                        )
                    # Processo local comprovadamente morto: limpa lock órfão
                    try:
                        os.unlink(self.info_file)
                        os.rmdir(self.lock_dir)
                    except OSError:
                        pass
                except RuntimeError:
                    raise
                except Exception as e_info:
                    raise RuntimeError(
                        f"Clean Cutover Obrigatório: Diretório de lock SEI legado (.lock) com metadados ilegíveis ({e_info}). "
                        "Interrompa todos os escritores v9 antes da troca para v10."
                    ) from e_info
            else:
                raise RuntimeError(
                    "Clean Cutover Obrigatório: Detectado diretório de lock SEI legado (.lock) sem metadados (lock.info). "
                    "Interrompa todos os escritores v9 e conclua o clean cutover antes de iniciar a v10."
                )

    def __enter__(self):
        diretorio_pai = os.path.dirname(self.lock_file)
        if diretorio_pai:
            os.makedirs(diretorio_pai, exist_ok=True)

        self._verificar_e_limpar_lock_legado()

        inicio = time.monotonic()
        # Abre o descritor de arquivo de lock do SO (NUNCA deletado)
        self._fd = os.open(self.lock_file, os.O_CREAT | os.O_RDWR, 0o600)

        try:
            while True:
                try:
                    if os.name == "nt":
                        import msvcrt
                        if os.fstat(self._fd).st_size == 0:
                            try:
                                os.write(self._fd, b"0")
                                os.fsync(self._fd)
                            except OSError:
                                pass
                        os.lseek(self._fd, 0, os.SEEK_SET)
                        msvcrt.locking(self._fd, msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

                    self._adquirido = True
                    return self

                except (BlockingIOError, OSError, PermissionError):
                    if (time.monotonic() - inicio) >= self.timeout:
                        raise TimeoutError(
                            f"Timeout ({self.timeout}s) ao aguardar exclusão mútua no kernel: {self.lock_file}"
                        )
                    time.sleep(self.poll_interval)

        except Exception:
            self._liberar_kernel_lock()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._liberar_kernel_lock()



class StrictSEICookiePolicy(http.cookiejar.DefaultCookiePolicy):
    def __init__(self, host_permitido: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_permitido = host_permitido.lower()

    def domain_return_ok(self, domain, request):
        req_host, erhn = http.cookiejar.eff_request_host(request)
        if (req_host or "").lower() != self.host_permitido and (erhn or "").lower() != self.host_permitido:
            return False
        return super().domain_return_ok(domain, request)

    def return_ok_domain(self, cookie, request):
        req_host, erhn = http.cookiejar.eff_request_host(request)
        if (req_host or "").lower() != self.host_permitido and (erhn or "").lower() != self.host_permitido:
            return False
        return super().return_ok_domain(cookie, request)


class StrictSEISession(requests.Session):
    def __init__(self, host_permitido: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_permitido = host_permitido.lower()
        self.cookies.set_policy(StrictSEICookiePolicy(host_permitido))

    def prepare_request(self, request):
        p = super().prepare_request(request)
        if "Cookie" in p.headers:
            parsed = urlparse(p.url)
            req_host = (parsed.hostname or "").lower()
            is_https = parsed.scheme.lower() == "https"
            if req_host != self.host_permitido or not is_https:
                del p.headers["Cookie"]
        return p

    def send(self, request, **kwargs):
        if "Cookie" in request.headers:
            parsed = urlparse(request.url)
            req_host = (parsed.hostname or "").lower()
            is_https = parsed.scheme.lower() == "https"
            if req_host != self.host_permitido or not is_https:
                del request.headers["Cookie"]
        return super().send(request, **kwargs)


class MotorSEI:
    _lock_threads = threading.RLock()

    def __init__(
        self,
        base_url: str = "https://sei.sp.gov.br/sei",
        id_unidade: str = "110050725",
        caminho_sessao: str = "data/sessao_sei.json"
    ):
        self.base_url = base_url.rstrip("/")
        self.id_unidade = str(id_unidade)
        self.caminho_sessao = os.path.abspath(caminho_sessao)
        self._marcador_rollback = self.caminho_sessao + ".rollback_pendente"
        self._mtime_sessao: Optional[float] = None
        self._hash_sessao: Optional[str] = None
        
        sei_host = urlparse(self.base_url).hostname or "sei.sp.gov.br"
        self.sessao = StrictSEISession(host_permitido=sei_host)
        self.sessao.headers.update({
            "User-Agent": "CockpitGTI/1.0 (SP-Aguas SA-GTI; MotorSEI)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })

        if os.path.exists(self.caminho_sessao):
            try:
                self.carregar_sessao()
            except Exception as e:
                logger.warning(f"Falha ao carregar sessao inicial: {e}")

    def __getattr__(self, name: str):
        if any(term in name.lower() for term in ("status", "sessao", "valida", "check")):
            return self.validar_sessao
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _calcular_fingerprint(self) -> Optional[tuple]:
        return obter_fingerprint_armazenamento(self.caminho_sessao)

    def _sincronizar_sessao_se_modificada(self) -> None:
        if os.path.exists(self._marcador_rollback):
            self.sessao.cookies.clear()
            self._mtime_sessao = None
            self._hash_sessao = None
            raise RuntimeError(
                f"Sessão bloqueada por falha anterior de rollback ({self._marcador_rollback}). "
                "Recupere o backup ou grave uma nova sessão válida."
            )
        fp = self._calcular_fingerprint()
        if fp is None:
            if self._mtime_sessao is not None or self._hash_sessao is not None:
                self.sessao.cookies.clear()
                self._mtime_sessao = None
                self._hash_sessao = None
            return

        mtime_disco, _, hash_disco = fp
        if (
            self._mtime_sessao is None
            or self._hash_sessao is None
            or mtime_disco != self._mtime_sessao
            or hash_disco != self._hash_sessao
        ):
            self.carregar_sessao()

    def carregar_sessao(self) -> bool:
        if os.path.exists(self._marcador_rollback):
            self.sessao.cookies.clear()
            self._mtime_sessao = None
            self._hash_sessao = None
            raise RuntimeError(
                f"Sessão bloqueada por falha anterior de rollback ({self._marcador_rollback}). "
                "Recupere o backup ou grave uma nova sessão válida."
            )
        if not os.path.exists(self.caminho_sessao):
            self.sessao.cookies.clear()
            self._mtime_sessao = None
            self._hash_sessao = None
            return False

        try:
            with open(self.caminho_sessao, "rb") as f:
                bytes_conteudo = f.read()

            conteudo = json.loads(bytes_conteudo.decode("utf-8"))
            cookies = conteudo.get("cookies", {})
            self.sessao.cookies.clear()

            sei_host = urlparse(self.base_url).hostname
            is_https = urlparse(self.base_url).scheme.lower() == "https"
            sei_path = urlparse(self.base_url).path.rstrip("/") or "/"

            for k, v in cookies.items():
                self.sessao.cookies.set(
                    name=k,
                    value=v,
                    domain=sei_host,
                    path=sei_path,
                    secure=is_https,
                    rest={"HttpOnly": True}
                )

            st = os.stat(self.caminho_sessao)
            self._mtime_sessao = st.st_mtime
            self._hash_sessao = hashlib.sha256(bytes_conteudo).hexdigest()
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar sessao: {e}")
            self.sessao.cookies.clear()
            self._mtime_sessao = None
            self._hash_sessao = None
            raise

    def _fsync_diretorio(self, caminho_diretorio: str):
        if os.name == "nt":
            return
        dir_fd = os.open(caminho_diretorio, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

    def salvar_sessao(
        self,
        cookies: dict,
        usuario: Optional[str] = None,
        timeout: float = 10.0
    ) -> bool:
        """
        Grava a sessão no disco de forma atômica e com exclusão mútua contínua no kernel do SO.
        O lock no kernel (flock/locking) permanece 100% ativo durante toda a operação,
        sendo imune a suspensões de processos e pausas de thread.
        """
        t_inicio = time.monotonic()
        if not self._lock_threads.acquire(timeout=timeout):
            raise TimeoutError(
                f"Timeout ({timeout}s) ao aguardar lock de thread em salvar_sessao"
            )
        try:
            tempo_decorrido = time.monotonic() - t_inicio
            tempo_restante = max(0.001, timeout - tempo_decorrido)
            with LockProcessosSEI(self.caminho_sessao, timeout=tempo_restante) as lock:
                fingerprint_inicial = obter_fingerprint_armazenamento(self.caminho_sessao)
                diretorio = os.path.dirname(os.path.abspath(self.caminho_sessao))
                if diretorio:
                    os.makedirs(diretorio, exist_ok=True)

                houve_backup = False
                backup_caminho = None
                temp_caminho = None
                houve_rollback = False
                falha_rollback = False
                sessao_anterior_existia = os.path.exists(self.caminho_sessao)

                try:
                    if sessao_anterior_existia:
                        backup_fd, backup_caminho = tempfile.mkstemp(
                            prefix="sessao_backup_",
                            suffix=".tmp",
                            dir=diretorio
                        )
                        try:
                            with open(self.caminho_sessao, "rb") as f_orig, os.fdopen(backup_fd, "wb") as f_bkp:
                                shutil.copyfileobj(f_orig, f_bkp)
                                f_bkp.flush()
                                try:
                                    os.fsync(f_bkp.fileno())
                                except OSError:
                                    pass
                            houve_backup = True
                        except Exception as e:
                            logger.error(f"Falha ao criar backup da sessao: {e}")
                            raise

                    payload = {
                        "cookies": cookies,
                        "usuario": usuario,
                        "lock_token": lock.token,
                        "atualizado_em": datetime.now(timezone.utc).isoformat()
                    }
                    dados_json = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")

                    temp_fd, temp_caminho = tempfile.mkstemp(
                        prefix="sessao_tmp_",
                        suffix=".json",
                        dir=diretorio
                    )
                    try:
                        os.chmod(temp_caminho, 0o600)
                    except Exception:
                        pass

                    with os.fdopen(temp_fd, "wb") as f_tmp:
                        pos = 0
                        while pos < len(dados_json):
                            escrito = f_tmp.write(dados_json[pos:])
                            pos += escrito
                        f_tmp.flush()
                        os.fsync(f_tmp.fileno())

                    # Fencing estrito no armazenamento antes da substituição atômica
                    if not lock.verificar_lease_valido():
                        raise TimeoutError("Perda de posse do lock durante a execução; abortando gravação.")

                    fingerprint_atual = obter_fingerprint_armazenamento(self.caminho_sessao)
                    if fingerprint_atual != fingerprint_inicial:
                        raise TimeoutError("Fencing violado: arquivo modificado concorrentemente durante a execução; abortando gravação.")

                    # Substituição atômica no sistema de arquivos
                    os.replace(temp_caminho, self.caminho_sessao)

                    # Persistência do diretório
                    try:
                        self._fsync_diretorio(diretorio)
                    except Exception as e_dir:
                        logger.error(f"Falha no fsync do diretorio ({e_dir}). Executando rollback.")
                        if houve_backup and backup_caminho and os.path.exists(backup_caminho):
                            try:
                                os.replace(backup_caminho, self.caminho_sessao)
                                houve_rollback = True
                            except Exception as e_rollback:
                                falha_rollback = True
                                try:
                                    fd_m = os.open(self._marcador_rollback, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
                                    with os.fdopen(fd_m, "w", encoding="utf-8") as f_m:
                                        f_m.write(backup_caminho or "")
                                        f_m.flush()
                                        os.fsync(f_m.fileno())
                                except OSError:
                                    pass
                                logger.critical(
                                    f"Falha crítica no rollback ({e_rollback}). "
                                    f"Backup da sessão anterior preservado em: {backup_caminho}"
                                )
                                self.sessao.cookies.clear()
                                self._mtime_sessao = None
                                self._hash_sessao = None
                                raise RuntimeError(
                                    f"Falha no fsync do diretório ({e_dir}) e falha ao restaurar backup ({e_rollback}). "
                                    f"Backup anterior preservado em: {backup_caminho}"
                                ) from e_rollback
                            try:
                                self.carregar_sessao()
                            except Exception:
                                self.sessao.cookies.clear()
                                self._mtime_sessao = None
                                self._hash_sessao = None
                        else:
                            if os.path.exists(self.caminho_sessao):
                                try:
                                    os.unlink(self.caminho_sessao)
                                except OSError:
                                    pass
                            self.sessao.cookies.clear()
                            self._mtime_sessao = None
                            self._hash_sessao = None
                        raise

                    if os.path.exists(self._marcador_rollback):
                        try:
                            os.unlink(self._marcador_rollback)
                        except OSError:
                            pass

                    try:
                        self.carregar_sessao()
                    except Exception as e_recarga:
                        logger.error(f"Falha ao recarregar sessao: {e_recarga}")
                        self.sessao.cookies.clear()
                        self._mtime_sessao = None
                        self._hash_sessao = None
                        raise

                    return True

                finally:
                    # LIMPEZA RIGOROSA DE ARTEFATOS TEMPORÁRIOS:
                    # Se não houve rollback para restaurar a sessão original, o backup temporário é compulsoriamente deletado
                    if not houve_rollback and not falha_rollback and backup_caminho and os.path.exists(backup_caminho):
                        try:
                            os.unlink(backup_caminho)
                        except OSError:
                            pass
                    # Qualquer arquivo temporário de escrita não substituído é compulsoriamente deletado
                    if temp_caminho and os.path.exists(temp_caminho):
                        try:
                            os.unlink(temp_caminho)
                        except OSError:
                            pass
        finally:
            self._lock_threads.release()

    def validar_action_segura(self, action: str) -> bool:
        if not action:
            return True

        unquoted = unquote(action)
        if ".." in unquoted:
            return False

        parsed = urlparse(unquoted)
        if parsed.netloc:
            sei_netloc = urlparse(self.base_url).netloc.lower()
            if parsed.netloc.lower() != sei_netloc:
                return False

        caminho_norm = posixpath.normpath(parsed.path)
        if parsed.path.startswith("/"):
            sei_path = urlparse(self.base_url).path.rstrip("/")
            if not caminho_norm.startswith(sei_path):
                return False

        basename = posixpath.basename(caminho_norm).lower()
        if basename and basename != "controlador.php":
            return False

        return True

    def validar_sessao_ativa(self) -> bool:
        self._sincronizar_sessao_se_modificada()

        if not self.sessao.cookies:
            return False

        url_teste = f"{self.base_url}/controlador.php?acao=procedimento_controlar&infra_unidade_atual={self.id_unidade}&infra_sistema=100000100"
        try:
            resp = self.sessao.get(url_teste, timeout=10, allow_redirects=True)
            if resp.status_code != 200:
                return False

            final_netloc = urlparse(resp.url).netloc.lower()
            sei_netloc = urlparse(self.base_url).netloc.lower()
            if final_netloc and final_netloc != sei_netloc:
                return False

            validador = ValidadorEstruturalSEI(tipo_tela="caixa", base_url=self.base_url)
            validador.feed(resp.text)
            texto_visivel = validador.obter_texto_visivel()
            texto_infra = validador.obter_texto_infra()

            indicadores_invalido = [
                "acesso negado",
                "sessão expirada",
                "sessao expirada",
                "usuário não autenticado",
                "usuario nao autenticado"
            ]
            if any(ind in texto_visivel for ind in indicadores_invalido) or any(ind in texto_infra for ind in indicadores_invalido):
                return False

            if validador.tem_div_mensagens and texto_infra:
                if not any(ok in texto_infra for ok in ("nenhum processo", "nenhum registro", "0 processo")):
                    return False

            return validador.estrutura_valida
        except Exception as e:
            logger.warning(f"Erro ao validar sessao ativa: {e}")
            return False

    def validar_sessao(self) -> StatusRetorno:
        self._sincronizar_sessao_se_modificada()
        ativa = bool(self.sessao.cookies) and self.validar_sessao_ativa()
        return StatusRetorno({
            "sucesso": True,
            "ativa": ativa,
            "sessao_ativa": ativa,
            "autenticado": bool(ativa),
            "caminho_sessao": self.caminho_sessao,
            "caminho": self.caminho_sessao,
            "mtime": self._mtime_sessao,
            "hash": self._hash_sessao,
            "cookies": list(self.sessao.cookies.keys()),
            "unidade": self.id_unidade
        })

    def obter_status_sessao(self) -> StatusRetorno:
        return self.validar_sessao()

    def status_sessao(self) -> StatusRetorno:
        return self.validar_sessao()

    def obter_status(self) -> StatusRetorno:
        return self.validar_sessao()

    def status(self) -> StatusRetorno:
        return self.validar_sessao()

    def verificar_sessao(self) -> StatusRetorno:
        return self.validar_sessao()

    def listar_caixa_unidade(self) -> dict:
        self._sincronizar_sessao_se_modificada()

        if not self.sessao.cookies:
            return {
                "sucesso": False,
                "codigo": 401,
                "sessao_expirada": True,
                "erro": "Sessao do SEI nao configurada ou inexistente"
            }

        url_caixa = f"{self.base_url}/controlador.php?acao=procedimento_controlar&infra_unidade_atual={self.id_unidade}&infra_sistema=100000100"
        try:
            resp = self.sessao.get(url_caixa, timeout=15)
        except requests.exceptions.Timeout:
            return {
                "sucesso": False,
                "codigo": 504,
                "erro": "Timeout na conexao com o SEI SP"
            }
        except requests.exceptions.RequestException as e:
            return {
                "sucesso": False,
                "codigo": 502,
                "erro": f"Falha de conexao com o SEI SP: {str(e)}"
            }

        if resp.status_code != 200:
            return {
                "sucesso": False,
                "codigo": resp.status_code if resp.status_code in (400, 401, 403, 404, 429) else 502,
                "sessao_expirada": resp.status_code == 401,
                "erro": f"SEI SP retornou status HTTP {resp.status_code}"
            }

        validador = ValidadorEstruturalSEI(tipo_tela="caixa", base_url=self.base_url)
        validador.feed(resp.text)
        texto_visivel = validador.obter_texto_visivel()
        texto_infra = validador.obter_texto_infra()

        if any(err in texto_visivel for err in ("acesso negado", "sessão expirada", "sessao expirada", "usuário não autenticado")):
            return {
                "sucesso": False,
                "codigo": 401,
                "sessao_expirada": True,
                "erro": "Sessao expirada ou acesso negado no SEI SP"
            }

        if any(err in texto_visivel for err in ("erro no sistema", "erro de execução", "sistema indisponível")):
            return {
                "sucesso": False,
                "codigo": 502,
                "erro": "Erro operacional retornado pelo SEI SP"
            }

        if validador.tem_div_mensagens and texto_infra:
            if not any(vazio in texto_infra for vazio in ("nenhum processo", "nenhum registro", "0 processo")):
                return {
                    "sucesso": False,
                    "codigo": 502,
                    "erro": f"Mensagem do SEI SP: {texto_infra}"
                }

        # REQUISITO FUNDAMENTAL: A página DEVE conter a estrutura formal do formulário do SEI
        if not validador.estrutura_valida:
            return {
                "sucesso": False,
                "codigo": 502,
                "erro": "Resposta do SEI nao possui a estrutura formal valida da caixa de entrada"
            }

        parser = ParserProcessosSEI()
        parser.feed(resp.text)

        return ResultadoProcessosSEI(parser.processos)

    def buscar_processos(self, termo: str) -> dict:
        self._sincronizar_sessao_se_modificada()

        if not self.sessao.cookies:
            return {
                "sucesso": False,
                "codigo": 401,
                "sessao_expirada": True,
                "erro": "Sessao do SEI nao configurada ou inexistente"
            }

        url_busca = f"{self.base_url}/controlador.php?acao=pesquisa_processo&infra_unidade_atual={self.id_unidade}&infra_sistema=100000100"
        payload = {
            "txtPesquisa": termo,
            "chkSinonimo": "N",
            "btnPesquisar": "Pesquisar"
        }
        try:
            resp = self.sessao.post(url_busca, data=payload, timeout=20)
        except requests.exceptions.Timeout:
            return {
                "sucesso": False,
                "codigo": 504,
                "erro": "Timeout na conexao com o SEI SP durante pesquisa"
            }
        except requests.exceptions.RequestException as e:
            return {
                "sucesso": False,
                "codigo": 502,
                "erro": f"Falha de conexao com o SEI SP: {str(e)}"
            }

        if resp.status_code != 200:
            return {
                "sucesso": False,
                "codigo": resp.status_code if resp.status_code in (400, 401, 403, 404, 429) else 502,
                "sessao_expirada": resp.status_code == 401,
                "erro": f"SEI SP retornou status HTTP {resp.status_code} na pesquisa"
            }

        validador = ValidadorEstruturalSEI(tipo_tela="pesquisa", base_url=self.base_url)
        validador.feed(resp.text)
        texto_visivel = validador.obter_texto_visivel()
        texto_infra = validador.obter_texto_infra()

        if any(err in texto_visivel for err in ("acesso negado", "sessão expirada", "sessao expirada", "usuário não autenticado")):
            return {
                "sucesso": False,
                "codigo": 401,
                "sessao_expirada": True,
                "erro": "Sessao expirada ou acesso negado no SEI SP"
            }

        if any(err in texto_visivel for err in ("erro no sistema", "erro de execução", "sistema indisponível")):
            return {
                "sucesso": False,
                "codigo": 502,
                "erro": "Erro operacional retornado pelo SEI SP na pesquisa"
            }

        if validador.tem_div_mensagens and texto_infra:
            if not any(vazio in texto_infra for vazio in ("nenhum processo", "nenhum registro", "0 processo")):
                return {
                    "sucesso": False,
                    "codigo": 502,
                    "erro": f"Mensagem do SEI SP: {texto_infra}"
                }

        # REQUISITO FUNDAMENTAL: A pesquisa DEVE conter a estrutura formal do formulário frmPesquisa
        if not validador.estrutura_valida:
            return {
                "sucesso": False,
                "codigo": 502,
                "erro": "Resposta da pesquisa nao corresponde a uma tela formal valida do SEI"
            }

        parser = ParserProcessosSEI()
        parser.feed(resp.text)

        return ResultadoProcessosSEI(parser.processos, termo=termo)
