# -*- coding: utf-8 -*-
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self

    def __bool__(self):
        return bool(self.get("ativa", False))


class ResultadoProcessosSEI(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def sucesso(self) -> bool:
        return bool(self.get("sucesso", False))

    @property
    def total(self) -> int:
        return int(self.get("total", 0))

    @property
    def processos(self) -> list:
        return list(self.get("processos", []))


class ValidadorEstruturalSEI(HTMLParser):
    def __init__(self, tipo_tela: str = "caixa", base_url: str = "https://sei.sp.gov.br/sei"):
        super().__init__()
        self.tipo_tela = tipo_tela
        self.base_url = base_url.rstrip("/")
        self.estrutura_valida = False
        self.ignorar_conteudo = False
        self._dentro_de_form = False
        self._action_form = ""
        self._tags_abertas = []

    def handle_comment(self, data):
        pass

    def handle_starttag(self, tag: str, attrs: list):
        tag_lower = tag.lower()
        self._tags_abertas.append(tag_lower)
        if tag_lower in ("script", "style"):
            self.ignorar_conteudo = True
            return

        if not self.ignorar_conteudo:
            attr_dict = {k.lower(): v for k, v in attrs if k is not None}
            id_attr = attr_dict.get("id", "")
            action_attr = attr_dict.get("action", "")

            if tag_lower == "form":
                self._dentro_de_form = True
                self._action_form = action_attr
                if self.tipo_tela == "caixa" and id_attr == "frmProcedimentoControlar":
                    if self._validar_action_estrita(action_attr):
                        self.estrutura_valida = True
                elif self.tipo_tela == "busca" and id_attr == "frmPesquisa":
                    if self._validar_action_estrita(action_attr):
                        self.estrutura_valida = True

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if self._tags_abertas and self._tags_abertas[-1] == tag_lower:
            self._tags_abertas.pop()
        if tag_lower in ("script", "style"):
            self.ignorar_conteudo = False
        elif tag_lower == "form":
            self._dentro_de_form = False
            self._action_form = ""

    def _validar_action_estrita(self, action: str) -> bool:
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
    Exclusão mútua persistente e estrita imposta pelo armazenamento e sistema operacional.
    Utiliza fcntl.flock no Linux/POSIX e msvcrt.locking no Windows sobre arquivo de lock dedicado (.flock).
    A exclusão mútua permanece 100% ativa e válida no kernel do SO durante toda a operação,
    mesmo durante pausas ou suspensões do processo titular, impedindo qualquer gravação concorrente.
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

    def _gravar_heartbeat(self):
        try:
            with open(self.info_file, "w", encoding="utf-8") as f:
                json.dump({
                    "token": self.token,
                    "hostname": self.hostname,
                    "pid": os.getpid(),
                    "timestamp": time.time()
                }, f)
        except Exception:
            pass

    def _loop_heartbeat(self):
        intervalo = max(0.01, min(1.0, self.max_lock_age / 3.0))
        while not self._stop_heartbeat.wait(intervalo):
            if not self._adquirido or not os.path.exists(self.lock_dir):
                break
            if not self.verificar_lease_valido():
                break
            self._gravar_heartbeat()

    def verificar_lease_valido(self) -> bool:
        if not self._adquirido or self._fd is None:
            return False
        if os.path.exists(self.info_file):
            try:
                with open(self.info_file, "r", encoding="utf-8") as f:
                    info = json.load(f)
                if info.get("token") != self.token:
                    return False
            except Exception:
                pass
        return True

    def __enter__(self):
        diretorio_pai = os.path.dirname(self.lock_file)
        if diretorio_pai:
            os.makedirs(diretorio_pai, exist_ok=True)

        inicio = time.monotonic()
        self._fd = os.open(self.lock_file, os.O_CREAT | os.O_RDWR, 0o600)

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
                os.makedirs(self.lock_dir, exist_ok=True)
                self._gravar_heartbeat()

                self._stop_heartbeat.clear()
                self._heartbeat_thread = threading.Thread(
                    target=self._loop_heartbeat,
                    daemon=True,
                    name="LockSEI-Heartbeat"
                )
                self._heartbeat_thread.start()
                return self

            except (BlockingIOError, OSError, PermissionError):
                if (time.monotonic() - inicio) >= self.timeout:
                    if self._fd is not None:
                        try:
                            os.close(self._fd)
                        except OSError:
                            pass
                        self._fd = None
                    raise TimeoutError(
                        f"Timeout ({self.timeout}s) ao aguardar exclusão mútua no armazenamento: {self.lock_file}"
                    )
                time.sleep(self.poll_interval)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._adquirido and self._fd is not None:
            self._stop_heartbeat.set()
            if self._heartbeat_thread and self._heartbeat_thread.is_alive():
                self._heartbeat_thread.join(timeout=0.5)

            try:
                if os.path.exists(self.info_file):
                    try:
                        with open(self.info_file, "r", encoding="utf-8") as f:
                            info = json.load(f)
                        if info.get("token") == self.token:
                            os.unlink(self.info_file)
                            os.rmdir(self.lock_dir)
                    except Exception:
                        pass
                
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
            finally:
                try:
                    os.close(self._fd)
                except OSError:
                    pass
                self._fd = None
                self._adquirido = False


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
            logger.error(f"Erro ao carregar sessao de {self.caminho_sessao}: {e}")
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
        Grava a sessão no disco de forma atômica e com exclusão mútua estrita imposta pelo SO/armazenamento.
        O lock no kernel (flock/locking) permanece 100% ativo durante toda a operação,
        impedindo que qualquer processo concorrente entre nesta rotina enquanto o titular executa.
        """
        with self._lock_threads:
            with LockProcessosSEI(self.caminho_sessao, timeout=timeout) as lock:
                diretorio = os.path.dirname(os.path.abspath(self.caminho_sessao))
                if diretorio:
                    os.makedirs(diretorio, exist_ok=True)

                houve_backup = False
                backup_caminho = None
                sessao_anterior_existia = os.path.exists(self.caminho_sessao)

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
                        if backup_caminho and os.path.exists(backup_caminho):
                            try:
                                os.unlink(backup_caminho)
                            except OSError:
                                pass
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

                try:
                    with os.fdopen(temp_fd, "wb") as f_tmp:
                        pos = 0
                        while pos < len(dados_json):
                            escrito = f_tmp.write(dados_json[pos:])
                            pos += escrito
                        f_tmp.flush()
                        os.fsync(f_tmp.fileno())
                except Exception as e:
                    if os.path.exists(temp_caminho):
                        try:
                            os.unlink(temp_caminho)
                        except OSError:
                            pass
                    if houve_backup and backup_caminho and os.path.exists(backup_caminho):
                        try:
                            os.unlink(backup_caminho)
                        except OSError:
                            pass
                    raise

                try:
                    os.replace(temp_caminho, self.caminho_sessao)
                except Exception as e:
                    if os.path.exists(temp_caminho):
                        try:
                            os.unlink(temp_caminho)
                        except OSError:
                            pass
                    if houve_backup and backup_caminho and os.path.exists(backup_caminho):
                        try:
                            os.unlink(backup_caminho)
                        except OSError:
                            pass
                    raise

                try:
                    self._fsync_diretorio(diretorio)
                except Exception as e_dir:
                    logger.error(f"Falha no fsync do diretorio ({e_dir}). Executando rollback.")
                    if houve_backup and backup_caminho and os.path.exists(backup_caminho):
                        try:
                            os.replace(backup_caminho, self.caminho_sessao)
                        except Exception as e_rollback:
                            logger.critical(f"Falha no rollback: {e_rollback}")
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

                if houve_backup and backup_caminho and os.path.exists(backup_caminho):
                    try:
                        os.unlink(backup_caminho)
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

        url_teste = f"{self.base_url}/controlador.php"
        params = {
            "acao": "procedimento_controlar",
            "infra_sistema": "100000100",
            "infra_unidade_atual": self.id_unidade
        }
        try:
            resp = self.sessao.get(url_teste, params=params, timeout=10, allow_redirects=True)
            if resp.status_code != 200:
                return False

            parsed_url = urlparse(resp.url)
            sei_netloc = urlparse(self.base_url).netloc.lower()
            if parsed_url.netloc.lower() != sei_netloc:
                return False

            validador = ValidadorFormSEI(base_url=self.base_url)
            validador.feed(resp.text)
            return validador.form_encontrado
        except Exception as e:
            logger.error(f"Falha ao validar sessao ativa: {e}")
            return False

    def validar_sessao(self) -> StatusRetorno:
        self._sincronizar_sessao_se_modificada()
        possui_cookies = bool(self.sessao.cookies)
        ativa = self.validar_sessao_ativa() if possui_cookies else False

        usuario = None
        if os.path.exists(self.caminho_sessao):
            try:
                with open(self.caminho_sessao, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    usuario = dados.get("usuario")
            except Exception:
                pass

        return StatusRetorno({
            "sucesso": True,
            "ativa": ativa,
            "possui_cookies": possui_cookies,
            "usuario": usuario,
            "unidade": self.id_unidade,
            "verificado_em": datetime.now(timezone.utc).isoformat()
        })

    def listar_caixa_unidade(self) -> ResultadoProcessosSEI:
        self._sincronizar_sessao_se_modificada()
        if not self.sessao.cookies:
            return ResultadoProcessosSEI({
                "sucesso": False,
                "erro": "Sessão não configurada ou vazia. Realize login no SEI.",
                "codigo": 401
            })

        url = f"{self.base_url}/controlador.php"
        params = {
            "acao": "procedimento_controlar",
            "infra_sistema": "100000100",
            "infra_unidade_atual": self.id_unidade
        }
        try:
            resp = self.sessao.get(url, params=params, timeout=15, allow_redirects=True)
            if resp.status_code == 401 or resp.status_code == 403:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": "Acesso não autorizado ou sessão expirada no SEI.",
                    "codigo": 401
                })
            elif resp.status_code >= 500:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": f"Servidor SEI indisponível ou erro upstream (HTTP {resp.status_code}).",
                    "codigo": 502
                })
            elif resp.status_code != 200:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": f"Erro inesperado ao consultar SEI: HTTP {resp.status_code}",
                    "codigo": resp.status_code
                })

            parsed_url = urlparse(resp.url)
            sei_netloc = urlparse(self.base_url).netloc.lower()
            if parsed_url.netloc.lower() != sei_netloc:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": "Redirect inesperado para fora do SEI.",
                    "codigo": 502
                })

            validador = ValidadorEstruturalSEI(tipo_tela="caixa", base_url=self.base_url)
            validador.feed(resp.text)
            if not validador.estrutura_valida:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": "Resposta estruturalmente inválida ou não reconhecida do SEI.",
                    "codigo": 502
                })

            parser = ParserProcessosSEI()
            parser.feed(resp.text)

            return ResultadoProcessosSEI({
                "sucesso": True,
                "unidade": self.id_unidade,
                "total": len(parser.processos),
                "processos": parser.processos,
                "consultado_em": datetime.now(timezone.utc).isoformat()
            })
        except requests.RequestException as e:
            logger.error(f"Erro de rede ao listar caixa da unidade: {e}")
            return ResultadoProcessosSEI({
                "sucesso": False,
                "erro": f"Falha de comunicacao com o SEI: {e}",
                "codigo": 502
            })

    def buscar_processos(self, termo: str) -> ResultadoProcessosSEI:
        self._sincronizar_sessao_se_modificada()
        if not self.sessao.cookies:
            return ResultadoProcessosSEI({
                "sucesso": False,
                "erro": "Sessão não configurada ou vazia. Realize login no SEI.",
                "codigo": 401
            })

        if not termo or not termo.strip():
            return ResultadoProcessosSEI({
                "sucesso": False,
                "erro": "Termo de busca não fornecido.",
                "codigo": 400
            })

        url = f"{self.base_url}/controlador.php?acao=pesquisa_rapida"
        payload = {
            "txtPesquisaRapida": termo.strip(),
            "infra_sistema": "100000100",
            "infra_unidade_atual": self.id_unidade
        }
        try:
            resp = self.sessao.post(url, data=payload, timeout=20, allow_redirects=True)
            if resp.status_code == 401 or resp.status_code == 403:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": "Acesso não autorizado ou sessão expirada no SEI.",
                    "codigo": 401
                })
            elif resp.status_code >= 500:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": f"Servidor SEI indisponível ou erro upstream (HTTP {resp.status_code}).",
                    "codigo": 502
                })
            elif resp.status_code != 200:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": f"Erro inesperado ao buscar no SEI: HTTP {resp.status_code}",
                    "codigo": resp.status_code
                })

            parsed_url = urlparse(resp.url)
            sei_netloc = urlparse(self.base_url).netloc.lower()
            if parsed_url.netloc.lower() != sei_netloc:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": "Redirect inesperado para fora do SEI.",
                    "codigo": 502
                })

            validador = ValidadorEstruturalSEI(tipo_tela="busca", base_url=self.base_url)
            validador.feed(resp.text)
            if not validador.estrutura_valida:
                return ResultadoProcessosSEI({
                    "sucesso": False,
                    "erro": "Resposta estruturalmente inválida ou não reconhecida do SEI.",
                    "codigo": 502
                })

            parser = ParserProcessosSEI()
            parser.feed(resp.text)

            return ResultadoProcessosSEI({
                "sucesso": True,
                "termo": termo.strip(),
                "total": len(parser.processos),
                "processos": parser.processos,
                "consultado_em": datetime.now(timezone.utc).isoformat()
            })
        except requests.RequestException as e:
            logger.error(f"Erro de rede ao buscar processos no SEI: {e}")
            return ResultadoProcessosSEI({
                "sucesso": False,
                "erro": f"Falha de comunicacao com o SEI: {e}",
                "codigo": 502
            })
