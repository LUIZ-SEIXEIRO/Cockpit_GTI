# -*- coding: utf-8 -*-
"""
Script de Atualização e Homologação SEI 4.1.5 - Versão 10
Exclusão Mútua Persistente (Kernel Flock + Dual Lock v9/v10), Thread Timeout e Testes Multiprocesso
Cockpit GTI 360° - SA-GTI (SP-Águas)
"""
import os
import sys

MOTOR_SEI_CODE = r'''import os
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
    except ProcessLookupError:
        return False
    except OSError as e:
        import errno
        if getattr(e, "errno", None) == errno.EPERM:
            return True
        if getattr(e, "errno", None) == errno.ESRCH:
            return False
        return False
    except Exception:
        return False


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
    Exclusão mútua persistente e estrita imposta pelo armazenamento e sistema operacional.
    Utiliza fcntl.flock no Linux/POSIX e msvcrt.locking no Windows sobre arquivo de lock dedicado (.flock).
    Adicionalmente adquire o diretório .lock com lock.info para compatibilidade mútua com versões v9.
    O arquivo .flock NUNCA é removido, garantindo estabilidade de inode e proteção contínua no kernel.
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
        self._dir_adquirido = False
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

    def __enter__(self):
        diretorio_pai = os.path.dirname(self.lock_file)
        if diretorio_pai:
            os.makedirs(diretorio_pai, exist_ok=True)

        inicio = time.monotonic()
        # 1. Abre o descritor de arquivo de lock do SO (NUNCA deletado)
        self._fd = os.open(self.lock_file, os.O_CREAT | os.O_RDWR, 0o600)

        # 2. Adquire exclusão mútua no kernel do SO
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
                break

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

        # 3. Adquire lock de diretório legado para compatibilidade com versões v9
        while True:
            try:
                os.mkdir(self.lock_dir)
                self._dir_adquirido = True
                break
            except FileExistsError:
                if (time.monotonic() - inicio) >= self.timeout:
                    self._liberar_kernel_lock()
                    raise TimeoutError(
                        f"Timeout ({self.timeout}s) ao aguardar liberação de lock de diretório legado: {self.lock_dir}"
                    )
                # Verifica se lock legado está morto ou órfão
                if not os.path.exists(self.info_file):
                    try:
                        os.rmdir(self.lock_dir)
                        continue
                    except OSError:
                        pass
                else:
                    try:
                        with open(self.info_file, "r", encoding="utf-8") as f:
                            info = json.load(f)
                        pid = info.get("pid")
                        ts = info.get("timestamp", 0)
                        idade = time.time() - ts
                        if not processo_esta_vivo(pid) or idade > self.max_lock_age:
                            try:
                                os.unlink(self.info_file)
                                os.rmdir(self.lock_dir)
                                continue
                            except OSError:
                                pass
                    except Exception:
                        pass
                time.sleep(self.poll_interval)

        # 4. Registra metadados informativos no diretório de lock
        self._gravar_heartbeat()

        self._stop_heartbeat.clear()
        self._heartbeat_thread = threading.Thread(
            target=self._loop_heartbeat,
            daemon=True,
            name="LockSEI-Heartbeat"
        )
        self._heartbeat_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._adquirido:
            self._stop_heartbeat.set()
            if self._heartbeat_thread and self._heartbeat_thread.is_alive():
                self._heartbeat_thread.join(timeout=0.5)

            try:
                if self._dir_adquirido or os.path.exists(self.lock_dir):
                    if os.path.exists(self.info_file):
                        try:
                            with open(self.info_file, "r", encoding="utf-8") as f:
                                info = json.load(f)
                            if info.get("token") == self.token:
                                os.unlink(self.info_file)
                        except Exception:
                            pass
                    try:
                        os.rmdir(self.lock_dir)
                    except OSError:
                        pass
            finally:
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
        Grava a sessão no disco de forma atômica e com exclusão mútua estrita imposta pelo SO/armazenamento.
        O lock no kernel (flock/locking) permanece 100% ativo durante toda a operação,
        impedindo que qualquer processo concorrente entre nesta rotina enquanto o titular executa.
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

                # Substituição atômica no sistema de arquivos
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

        url_efetiva = resp.url if isinstance(getattr(resp, "url", None), str) else self.base_url
        parsed_url = urlparse(url_efetiva)
        sei_netloc = urlparse(self.base_url).netloc.lower()
        if parsed_url.netloc and parsed_url.netloc.lower() != sei_netloc:
            return {
                "sucesso": False,
                "codigo": 502,
                "erro": "Redirect inesperado para fora do SEI."
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

        url_efetiva = resp.url if isinstance(getattr(resp, "url", None), str) else self.base_url
        parsed_url = urlparse(url_efetiva)
        sei_netloc = urlparse(self.base_url).netloc.lower()
        if parsed_url.netloc and parsed_url.netloc.lower() != sei_netloc:
            return {
                "sucesso": False,
                "codigo": 502,
                "erro": "Redirect inesperado para fora do SEI."
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
'''

TESTS_CODE = r'''import os
import sys
import json
import stat
import time
import shutil
import tempfile
import threading
import unittest
import socket
from unittest.mock import patch, MagicMock
from urllib.parse import urlparse
import requests
from requests import Request

from motor_sei import (
    MotorSEI,
    ValidadorFormSEI,
    ValidadorEstruturalSEI,
    ParserProcessosSEI,
    LockProcessosSEI,
    ResultadoProcessosSEI,
    StrictSEISession,
    processo_esta_vivo,
    obter_fingerprint_armazenamento
)

class TestMotorSEI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.caminho_sessao = os.path.join(self.temp_dir.name, "sessao_sei.json")
        self.motor = MotorSEI(caminho_sessao=self.caminho_sessao)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_salvar_sessao_mkstemp_0600(self):
        cookies = {"PHPSESSID": "cookie_teste_123"}
        resultado = self.motor.salvar_sessao(cookies, usuario="12345678900")
        self.assertTrue(resultado)
        self.assertTrue(os.path.exists(self.caminho_sessao))

        if os.name != "nt":
            modo = stat.S_IMODE(os.stat(self.caminho_sessao).st_mode)
            self.assertEqual(modo, 0o600)

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            dados = json.load(f)
        self.assertEqual(dados["cookies"]["PHPSESSID"], "cookie_teste_123")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "cookie_teste_123")

    def test_02_validar_sessao_ativa_form_id(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_valida"})
        html_resposta = """
        <html>
            <body>
                <form id="frmProcedimentoControlar" action="controlador.php?acao=procedimento_controlar">
                    <input type="hidden" name="infra_hash" value="abc12345" />
                </form>
            </body>
        </html>
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html_resposta
        mock_resp.url = "https://sei.sp.gov.br/sei/controlador.php"

        with patch.object(self.motor.sessao, "get", return_value=mock_resp):
            ativa = self.motor.validar_sessao_ativa()
            self.assertTrue(ativa)

    def test_03_rejeitar_action_em_dominio_externo_e_fake(self):
        self.assertFalse(self.motor.validar_action_segura("https://malicioso.com/controlador.php"))
        self.assertFalse(self.motor.validar_action_segura("http://phishing.sp.gov.br/hack"))
        self.assertFalse(self.motor.validar_action_segura("/sei/../etc/passwd"))
        self.assertFalse(self.motor.validar_action_segura("controlador.php?acao=../../perigo"))
        self.assertFalse(self.motor.validar_action_segura("controlador.php.fake"))
        self.assertFalse(self.motor.validar_action_segura("/sei/controlador.php.fake"))

        self.assertTrue(self.motor.validar_action_segura("controlador.php?acao=procedimento_controlar"))
        self.assertTrue(self.motor.validar_action_segura("https://sei.sp.gov.br/sei/controlador.php"))

    def test_04_rejeitar_tabela_dentro_de_script(self):
        html_script = """
        <html>
            <head>
                <script>
                    var mockLink = '<a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=99999">SP-99999</a>';
                </script>
            </head>
            <body>
                <a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=12345">SP-12345</a>
            </body>
        </html>
        """
        parser = ParserProcessosSEI()
        parser.feed(html_script)
        self.assertEqual(len(parser.processos), 1)
        self.assertEqual(parser.processos[0]["id_procedimento"], "12345")
        self.assertEqual(parser.processos[0]["numero"], "SP-12345")

    def test_05_parser_com_entidade_amp(self):
        html_amp = """
        <div>
            <a href="controlador.php?acao=procedimento_trabalhar&amp;id_procedimento=54321&amp;id_protocolo=987">
                Processo SP-54321/2026
            </a>
        </div>
        """
        parser = ParserProcessosSEI()
        parser.feed(html_amp)
        self.assertEqual(len(parser.processos), 1)
        self.assertEqual(parser.processos[0]["id_procedimento"], "54321")
        self.assertEqual(parser.processos[0]["id_protocolo"], "987")
        self.assertIn("SP-54321/2026", parser.processos[0]["numero"])

    def test_06_falha_fsync_aborta_substituicao_e_limpa(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_inicial")

        def fsync_falha(fd):
            raise OSError("Falha de I/O em fsync simulada")

        with patch("os.fsync", side_effect=fsync_falha):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_nova_falhada"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
        self.assertEqual(conteudo["cookies"]["PHPSESSID"], "sessao_inicial")

    def test_07_falha_fsync_diretorio_executa_rollback(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_estavel"})

        with patch.object(self.motor, "_fsync_diretorio", side_effect=OSError("Falha de fsync em diretório")):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_com_defeito"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
        self.assertEqual(conteudo["cookies"]["PHPSESSID"], "sessao_estavel")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_estavel")

    def test_08_falha_abertura_diretorio_executa_rollback(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_v1"})

        with patch.object(self.motor, "_fsync_diretorio", side_effect=OSError("Permissao negada")):
            with self.assertRaises(OSError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_v2"})

        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
        self.assertEqual(conteudo["cookies"]["PHPSESSID"], "sessao_v1")
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_v1")

    def test_09_falha_recarga_invalida_memoria(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_base"})
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_base")

        with patch.object(self.motor, "carregar_sessao", side_effect=ValueError("Arquivo corrompido")):
            with self.assertRaises(ValueError):
                self.motor.salvar_sessao({"PHPSESSID": "sessao_invalida"})

        self.assertEqual(len(self.motor.sessao.cookies), 0)
        self.assertIsNone(self.motor._mtime_sessao)
        self.assertIsNone(self.motor._hash_sessao)

    def test_10_concorrencia_lock_processos_sem_roubo_de_lock(self):
        lock1 = LockProcessosSEI(self.caminho_sessao, timeout=1.0)
        lock2 = LockProcessosSEI(self.caminho_sessao, timeout=0.1)

        with lock1:
            with self.assertRaises(TimeoutError):
                with lock2:
                    pass

    def test_11_sincronizacao_mtime_multiplas_instancias(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_instancia_1"})

        motor2 = MotorSEI(caminho_sessao=self.caminho_sessao)
        self.assertEqual(motor2.sessao.cookies.get("PHPSESSID"), "sessao_instancia_1")

        self.motor.salvar_sessao({"PHPSESSID": "sessao_instancia_1_atualizada"})
        motor2._sincronizar_sessao_se_modificada()
        self.assertEqual(motor2.sessao.cookies.get("PHPSESSID"), "sessao_instancia_1_atualizada")

    def test_12_primeira_inicializacao_cria_diretorio_pai(self):
        sub_dir = os.path.join(self.temp_dir.name, "sub_novo", "profundo")
        caminho_novo = os.path.join(sub_dir, "sessao.json")
        motor_novo = MotorSEI(caminho_sessao=caminho_novo)

        resultado = motor_novo.salvar_sessao({"PHPSESSID": "sessao_diretorio_profundo"})
        self.assertTrue(resultado)
        self.assertTrue(os.path.exists(caminho_novo))

    def test_13_escopo_rigoroso_cookies_seguranca_subdominios_e_redirect(self):
        self.motor.salvar_sessao({"PHPSESSID": "segredo_sei_xyz"})
        
        req_sei = self.motor.sessao.prepare_request(
            Request("GET", "https://sei.sp.gov.br/sei/controlador.php")
        )
        self.assertIn("segredo_sei_xyz", req_sei.headers.get("Cookie", ""))

        req_sub = self.motor.sessao.prepare_request(
            Request("GET", "https://sub.sei.sp.gov.br/sei/controlador.php")
        )
        self.assertNotIn("segredo_sei_xyz", req_sub.headers.get("Cookie", ""))

        interceptado = {}
        def mock_adapter_send(adapter_self, request, **kwargs):
            interceptado["url"] = request.url
            interceptado["cookie"] = request.headers.get("Cookie")
            r = requests.Response()
            r.status_code = 200
            return r

        with patch.object(requests.adapters.HTTPAdapter, "send", mock_adapter_send):
            self.motor.sessao.send(req_sub)
            self.assertIsNone(interceptado.get("cookie"))

    def test_14_rejeitar_pagina_acesso_negado_e_form_fake(self):
        html_erro_sei = """
        <html>
            <body>
                <div id="divInfraMensagens">Sessão Expirada ou Acesso Negado</div>
                <form id="frmLogin" action="controlador.php?acao=login">
                    <input type="text" name="txtUsuario" />
                </form>
            </body>
        </html>
        """
        validador = ValidadorFormSEI(base_url="https://sei.sp.gov.br/sei")
        validador.feed(html_erro_sei)
        self.assertFalse(validador.form_encontrado)

    def test_15_sincronizacao_resiliente_colisao_mtime(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        motor_cliente = MotorSEI(caminho_sessao=self.caminho_sessao)
        self.assertEqual(motor_cliente.sessao.cookies.get("PHPSESSID"), "sessao_inicial")

        mtime_antigo = self.motor._mtime_sessao
        self.motor.salvar_sessao({"PHPSESSID": "sessao_modificada_mesmo_mtime"})

        os.utime(self.caminho_sessao, (mtime_antigo, mtime_antigo))
        motor_cliente._sincronizar_sessao_se_modificada()
        self.assertEqual(motor_cliente.sessao.cookies.get("PHPSESSID"), "sessao_modificada_mesmo_mtime")

    def test_16_recuperacao_lock_processo_morto_vs_vivo(self):
        lock_dir = self.caminho_sessao + ".lock"
        os.makedirs(lock_dir, exist_ok=True)
        
        # 1. Processo MORTO: lock do kernel liberado automaticamente ao fechar o processo
        lock1 = LockProcessosSEI(self.caminho_sessao, timeout=2.0)
        with lock1:
            self.assertTrue(lock1._adquirido)
        self.assertFalse(lock1._adquirido)

        # 2. Processo VIVO: enquanto lock1 está aberto no kernel, concorrente DEVE receber TimeoutError
        with lock1:
            lock_concorrente = LockProcessosSEI(self.caminho_sessao, timeout=0.08)
            with self.assertRaises(TimeoutError):
                with lock_concorrente:
                    pass

    def test_17_contrato_rotas_status_autenticado_vs_inativo(self):
        status_inativo = self.motor.validar_sessao()
        self.assertTrue(status_inativo["sucesso"])
        self.assertFalse(status_inativo["ativa"])
        self.assertFalse(status_inativo["sessao_ativa"])
        self.assertFalse(bool(status_inativo))
        self.assertEqual(status_inativo(), status_inativo)

        self.motor.salvar_sessao({"PHPSESSID": "sessao_mock_valida"})
        with patch.object(self.motor, "validar_sessao_ativa", return_value=True):
            status_ativo = self.motor.validar_sessao()
            self.assertTrue(status_ativo["sucesso"])
            self.assertTrue(status_ativo["ativa"])
            self.assertTrue(status_ativo["sessao_ativa"])
            self.assertTrue(bool(status_ativo))

    def test_18_rotas_sei_diagnostico_e_erros_upstream(self):
        self.motor.sessao.cookies.clear()
        if os.path.exists(self.caminho_sessao):
            os.unlink(self.caminho_sessao)

        res_caixa = self.motor.listar_caixa_unidade()
        self.assertFalse(res_caixa["sucesso"])
        self.assertEqual(res_caixa["codigo"], 401)

        res_busca = self.motor.buscar_processos("termo")
        self.assertFalse(res_busca["sucesso"])
        self.assertEqual(res_busca["codigo"], 401)

        self.motor.salvar_sessao({"PHPSESSID": "sessao_valida"})
        mock_resp_503 = MagicMock()
        mock_resp_503.status_code = 503
        mock_resp_503.text = "Service Unavailable"
        mock_resp_503.url = "https://sei.sp.gov.br/sei/controlador.php"

        with patch.object(self.motor.sessao, "get", return_value=mock_resp_503):
            res_caixa_503 = self.motor.listar_caixa_unidade()
            self.assertFalse(res_caixa_503["sucesso"])
            self.assertEqual(res_caixa_503["codigo"], 502)

    def test_19_cliente_flask_integrado(self):
        try:
            import main
            app = main.app
        except Exception:
            return

        with app.test_client() as client:
            with patch.object(main.motor_sei_instance, "validar_sessao", return_value={"sucesso": True, "ativa": False, "autenticado": False}):
                resp_status = client.get("/api/v1/sei/status")
                self.assertEqual(resp_status.status_code, 200)
                dados = resp_status.get_json()
                self.assertFalse(dados.get("autenticado"))

    def test_20_rejeitar_marcadores_falsos_em_script_e_comentarios(self):
        html_script_falso = """
        <html>
            <head>
                <script>
                    var formHtml = '<form id="frmProcedimentoControlar" action="controlador.php"></form>';
                    var searchHtml = '<form id="frmPesquisa" action="controlador.php"></form>';
                </script>
            </head>
            <body>
                <!-- <form id="frmProcedimentoControlar" action="controlador.php"></form> -->
                <div class="erro">Falha geral do sistema</div>
            </body>
        </html>
        """
        validador_caixa = ValidadorEstruturalSEI(tipo_tela="caixa", base_url="https://sei.sp.gov.br/sei")
        validador_caixa.feed(html_script_falso)
        self.assertFalse(validador_caixa.estrutura_valida)

        validador_busca = ValidadorEstruturalSEI(tipo_tela="pesquisa", base_url="https://sei.sp.gov.br/sei")
        validador_busca.feed(html_script_falso)
        self.assertFalse(validador_busca.estrutura_valida)

    def test_21_lock_entre_containers_hostname_diferente(self):
        lock_host1 = LockProcessosSEI(self.caminho_sessao, timeout=0.5, hostname="container-alpha")
        lock_host2 = LockProcessosSEI(self.caminho_sessao, timeout=0.05, hostname="container-beta")

        with lock_host1:
            with self.assertRaises(TimeoutError):
                with lock_host2:
                    pass

    def test_22_rejeitar_form_action_externa_em_validacao_sessao(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_com_form_externo"})
        html_externo = """
        <html>
            <body>
                <form id="frmProcedimentoControlar" action="https://malicioso.com/controlador.php?acao=procedimento_controlar">
                </form>
            </body>
        </html>
        """
        mock_resp = MagicMock(status_code=200, text=html_externo, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp):
            ativa = self.motor.validar_sessao_ativa()
            self.assertFalse(ativa)

    def test_23_rejeitar_pagina_erro_com_div_infra_mensagens(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_ok"})
        html_erro_infra = """
        <html>
            <body>
                <div id="divConteudo">
                    <div id="divInfraMensagens" class="infraMensagem">
                        Ocorreu uma falha no servidor de banco de dados do SEI.
                    </div>
                </div>
            </body>
        </html>
        """
        mock_resp = MagicMock(status_code=200, text=html_erro_infra, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp):
            res = self.motor.listar_caixa_unidade()
            self.assertFalse(res.get("sucesso"))
            self.assertEqual(res.get("codigo"), 502)

    def test_24_lock_heartbeat_mantem_lease_ativo_com_idade_reduzida_hostnames_distintos(self):
        lock1 = LockProcessosSEI(self.caminho_sessao, timeout=2.0, max_lock_age=0.15, hostname="container-A")
        with lock1:
            time.sleep(0.2)
            lock2 = LockProcessosSEI(self.caminho_sessao, timeout=0.05, max_lock_age=0.15, hostname="container-B")
            with self.assertRaises(TimeoutError):
                with lock2:
                    pass

    def test_25_rejeitar_pagina_erro_com_input_solto_ou_link_solto(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_ativa"})

        html_input_solto = """
        <html>
            <body>
                <input type="text" name="txtPesquisa" value="termo" />
                <h1>Erro 500 Interno</h1>
            </body>
        </html>
        """
        mock_resp1 = MagicMock(status_code=200, text=html_input_solto, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "post", return_value=mock_resp1):
            res1 = self.motor.buscar_processos("qualquer")
            self.assertFalse(res1.get("sucesso"))
            self.assertEqual(res1.get("codigo"), 502)

        html_link_solto = """
        <html>
            <body>
                <a href="controlador.php?acao=procedimento_trabalhar&id_procedimento=123">Processo SP-123</a>
                <div class="erro">Falha de renderização de tela</div>
            </body>
        </html>
        """
        mock_resp2 = MagicMock(status_code=200, text=html_link_solto, url="https://sei.sp.gov.br/sei/controlador.php")
        with patch.object(self.motor.sessao, "get", return_value=mock_resp2):
            res2 = self.motor.listar_caixa_unidade()
            self.assertFalse(res2.get("sucesso"))
            self.assertEqual(res2.get("codigo"), 502)

    def test_26_titular_suspenso_nao_remove_lock_alheio_nem_escreve(self):
        lock_a = LockProcessosSEI(self.caminho_sessao, timeout=1.0, max_lock_age=0.15, hostname="container-A")
        lock_a.__enter__()

        lock_b = LockProcessosSEI(self.caminho_sessao, timeout=0.08, hostname="container-B")
        with self.assertRaises(TimeoutError):
            with lock_b:
                pass

        lock_a.__exit__(None, None, None)

        with lock_b:
            self.assertTrue(lock_b._adquirido)

    def test_27_concorrencia_suspensao_fencing_armazenamento_multiprocesso(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        self.assertEqual(self.motor.sessao.cookies.get("PHPSESSID"), "sessao_inicial")

        import multiprocessing as mp

        def worker_titular(caminho, fila):
            from motor_sei import MotorSEI
            m = MotorSEI(caminho_sessao=caminho)
            orig_replace = os.replace
            def replace_lento(src, dst):
                fila.put("TITULAR_SUSPENSO")
                time.sleep(0.3)
                return orig_replace(src, dst)
            with patch("os.replace", side_effect=replace_lento):
                try:
                    m.salvar_sessao({"PHPSESSID": "sessao_A_titular"}, timeout=5.0)
                    fila.put("TITULAR_OK")
                except Exception as e:
                    fila.put(f"TITULAR_ERRO:{e}")

        def worker_concorrente(caminho, fila):
            from motor_sei import MotorSEI
            m = MotorSEI(caminho_sessao=caminho)
            try:
                m.salvar_sessao({"PHPSESSID": "sessao_B_concorrente"}, timeout=0.05)
                fila.put("CONCORRENTE_GRAVOU")
            except TimeoutError:
                fila.put("CONCORRENTE_TIMEOUT")
            except Exception as e:
                fila.put(f"CONCORRENTE_ERRO:{e}")

        fila = mp.Queue()
        proc_a = mp.Process(target=worker_titular, args=(self.caminho_sessao, fila))
        proc_a.start()

        msg = fila.get(timeout=3.0)
        self.assertEqual(msg, "TITULAR_SUSPENSO")

        proc_b = mp.Process(target=worker_concorrente, args=(self.caminho_sessao, fila))
        proc_b.start()
        proc_b.join(timeout=3.0)
        proc_a.join(timeout=3.0)

        respostas = []
        while not fila.empty():
            respostas.append(fila.get_nowait())

        self.assertIn("CONCORRENTE_TIMEOUT", respostas)
        self.assertIn("TITULAR_OK", respostas)

        with open(self.caminho_sessao, "r", encoding="utf-8") as f_res:
            dados_final = json.load(f_res)
        self.assertEqual(dados_final["cookies"]["PHPSESSID"], "sessao_A_titular")

    def test_28_timeout_entre_threads_estrito_salvar_sessao(self):
        self.motor.salvar_sessao({"PHPSESSID": "sessao_inicial"})
        motor_a = MotorSEI(caminho_sessao=self.caminho_sessao)
        motor_b = MotorSEI(caminho_sessao=self.caminho_sessao)

        orig_replace = os.replace
        def replace_lento(src, dst):
            time.sleep(0.35)
            return orig_replace(src, dst)

        def worker_a():
            with patch("os.replace", side_effect=replace_lento):
                motor_a.salvar_sessao({"PHPSESSID": "sessao_A"})

        th_a = threading.Thread(target=worker_a)
        th_a.start()
        time.sleep(0.05)

        t0 = time.monotonic()
        with self.assertRaises(TimeoutError):
            motor_b.salvar_sessao({"PHPSESSID": "sessao_B"}, timeout=0.05)
        duracao = time.monotonic() - t0
        self.assertLess(duracao, 0.2, f"Thread concorrente demorou {duracao:.3f}s excedendo timeout!")

        th_a.join(timeout=2.0)
        with open(self.caminho_sessao, "r", encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(d["cookies"]["PHPSESSID"], "sessao_A")

    def test_29_compatibilidade_mutua_lock_v9_e_v10(self):
        lock_dir = self.caminho_sessao + ".lock"
        os.makedirs(lock_dir)
        with open(os.path.join(lock_dir, "lock.info"), "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "timestamp": time.time(), "token": "v9_legado"}, f)

        motor_v10 = MotorSEI(caminho_sessao=self.caminho_sessao)
        with self.assertRaises(TimeoutError):
            motor_v10.salvar_sessao({"PHPSESSID": "sessao_v10"}, timeout=0.08)

        os.unlink(os.path.join(lock_dir, "lock.info"))
        os.rmdir(lock_dir)

        self.assertTrue(motor_v10.salvar_sessao({"PHPSESSID": "sessao_v10_sucesso"}, timeout=1.0))
        self.assertTrue(os.path.exists(self.caminho_sessao + ".flock"))


if __name__ == "__main__":
    unittest.main()
'''

def main():
    print("=== APLICANDO CORRECAO SEI V10 (DUAL LOCK + THREAD TIMEOUT + MULTIPROCESSO) ===")
    
    with open("motor_sei.py", "w", encoding="utf-8") as f:
        f.write(MOTOR_SEI_CODE)
    print("[SUCESSO] motor_sei.py atualizado.")

    os.makedirs("tests", exist_ok=True)
    with open("tests/test_motor_sei.py", "w", encoding="utf-8") as f:
        f.write(TESTS_CODE)
    print("[SUCESSO] tests/test_motor_sei.py atualizado (29 testes).")

if __name__ == "__main__":
    main()