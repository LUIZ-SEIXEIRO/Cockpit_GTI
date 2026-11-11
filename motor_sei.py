import os
import sys
import json
import time
import shutil
import tempfile
import logging
import threading
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse, parse_qs, unquote
import posixpath
from html.parser import HTMLParser

logger = logging.getLogger("CockpitGTI.MotorSEI")

class ValidadorFormSEI(HTMLParser):
    def __init__(self, action_esperada: Optional[str] = None):
        super().__init__()
        self.action_esperada = action_esperada
        self.form_encontrado = False
        self.ignorar_conteudo = False

    def handle_starttag(self, tag: str, attrs: list):
        tag_lower = tag.lower()
        if tag_lower in ("script", "style"):
            self.ignorar_conteudo = True
            return

        if not self.ignorar_conteudo and tag_lower == "form":
            attr_dict = {k.lower(): v for k, v in attrs if k is not None}
            form_id = attr_dict.get("id", "")
            form_name = attr_dict.get("name", "")
            action = attr_dict.get("action", "")

            if "frm" in form_id or "frm" in form_name or "controlador.php" in action:
                if self.action_esperada:
                    if self.action_esperada in action:
                        self.form_encontrado = True
                else:
                    self.form_encontrado = True

    def handle_endtag(self, tag: str):
        if tag.lower() in ("script", "style"):
            self.ignorar_conteudo = False


class ParserProcessosSEI(HTMLParser):
    def __init__(self):
        super().__init__()
        self.processos = []
        self.ignorar_conteudo = False
        self._dentro_de_link = False
        self._link_atual = None
        self._texto_link = []

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
    def __init__(self, caminho_sessao: str, timeout: float = 10.0, poll_interval: float = 0.05):
        self.caminho_sessao = os.path.abspath(caminho_sessao)
        self.lock_dir = self.caminho_sessao + ".lock"
        self.timeout = float(timeout)
        self.poll_interval = float(poll_interval)
        self._adquirido = False

    def __enter__(self):
        diretorio_pai = os.path.dirname(self.lock_dir)
        if diretorio_pai:
            os.makedirs(diretorio_pai, exist_ok=True)

        inicio = time.monotonic()
        while True:
            try:
                os.mkdir(self.lock_dir)
                self._adquirido = True
                return self
            except FileExistsError:
                if (time.monotonic() - inicio) >= self.timeout:
                    raise TimeoutError(
                        f"Timeout ({self.timeout}s) ao aguardar lock de concorrência do SEI: {self.lock_dir}"
                    )
                time.sleep(self.poll_interval)
            except FileNotFoundError:
                if diretorio_pai:
                    os.makedirs(diretorio_pai, exist_ok=True)
                time.sleep(self.poll_interval)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._adquirido:
            try:
                os.rmdir(self.lock_dir)
            except FileNotFoundError:
                pass
            except Exception as e:
                logger.warning(f"Erro ao liberar lock de processos {self.lock_dir}: {e}")
            finally:
                self._adquirido = False


class MotorSEI:
    _lock_threads = threading.Lock()

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
        
        import requests
        self.sessao = requests.Session()
        self.sessao.headers.update({
            "User-Agent": "CockpitGTI/1.0 (SP-Aguas SA-GTI; MotorSEI)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })

        if os.path.exists(self.caminho_sessao):
            try:
                self.carregar_sessao()
            except Exception as e:
                logger.warning(f"Falha ao carregar sessão inicial de {self.caminho_sessao}: {e}")

    def _sincronizar_sessao_se_modificada(self) -> None:
        if not os.path.exists(self.caminho_sessao):
            if self._mtime_sessao is not None:
                self.sessao.cookies.clear()
                self._mtime_sessao = None
            return

        try:
            mtime_disco = os.path.getmtime(self.caminho_sessao)
            if self._mtime_sessao is None or mtime_disco != self._mtime_sessao:
                self.carregar_sessao()
        except Exception as e:
            logger.warning(f"Erro ao verificar sincronização de sessão por mtime: {e}")

    def carregar_sessao(self) -> bool:
        if not os.path.exists(self.caminho_sessao):
            self.sessao.cookies.clear()
            self._mtime_sessao = None
            return False

        try:
            with open(self.caminho_sessao, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
            cookies = conteudo.get("cookies", {})
            self.sessao.cookies.clear()
            for k, v in cookies.items():
                self.sessao.cookies.set(k, v)
            self._mtime_sessao = os.path.getmtime(self.caminho_sessao)
            return True
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de sessão {self.caminho_sessao}: {e}")
            self.sessao.cookies.clear()
            self._mtime_sessao = None
            raise

    def _fsync_diretorio(self, caminho_diretorio: str):
        if os.name == "nt":
            return
        dir_fd = os.open(caminho_diretorio, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

    def salvar_sessao(self, cookies: dict, usuario: Optional[str] = None) -> bool:
        with self._lock_threads:
            with LockProcessosSEI(self.caminho_sessao, timeout=10.0):
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
                        logger.error(f"Falha ao criar backup da sessão: {e}")
                        if backup_caminho and os.path.exists(backup_caminho):
                            try:
                                os.unlink(backup_caminho)
                            except OSError:
                                pass
                        raise

                payload = {
                    "cookies": cookies,
                    "usuario": usuario,
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
                    logger.error(f"Falha no fsync do diretório ({e_dir}). Executando rollback.")
                    if houve_backup and backup_caminho and os.path.exists(backup_caminho):
                        try:
                            os.replace(backup_caminho, self.caminho_sessao)
                        except Exception as e_rollback:
                            logger.critical(f"Falha crítica no rollback: {e_rollback}")
                        try:
                            self.carregar_sessao()
                        except Exception:
                            self.sessao.cookies.clear()
                            self._mtime_sessao = None
                    else:
                        if os.path.exists(self.caminho_sessao):
                            try:
                                os.unlink(self.caminho_sessao)
                            except OSError:
                                pass
                        self.sessao.cookies.clear()
                        self._mtime_sessao = None
                    raise

                if houve_backup and backup_caminho and os.path.exists(backup_caminho):
                    try:
                        os.unlink(backup_caminho)
                    except OSError:
                        pass

                try:
                    self.carregar_sessao()
                except Exception as e_recarga:
                    logger.error(f"Falha ao recarregar sessão gravada: {e_recarga}")
                    self.sessao.cookies.clear()
                    self._mtime_sessao = None
                    raise

                return True

    def validar_action_segura(self, action: str) -> bool:
        if not action:
            return False

        unquoted_action = unquote(action)
        if ".." in unquoted_action:
            return False

        parsed = urlparse(unquoted_action)

        if parsed.netloc:
            sei_netloc = urlparse(self.base_url).netloc
            if parsed.netloc.lower() != sei_netloc.lower():
                return False

        if parsed.path.startswith("/"):
            sei_path = urlparse(self.base_url).path.rstrip("/")
            caminho_norm = posixpath.normpath(parsed.path)
            if not caminho_norm.startswith(sei_path):
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

            parser = ValidadorFormSEI()
            parser.feed(resp.text)
            return parser.form_encontrado
        except Exception as e:
            logger.warning(f"Erro ao validar sessão ativa no SEI: {e}")
            return False

    def listar_caixa_unidade(self) -> List[Dict[str, Any]]:
        self._sincronizar_sessao_se_modificada()

        url_caixa = f"{self.base_url}/controlador.php?acao=procedimento_controlar&infra_unidade_atual={self.id_unidade}&infra_sistema=100000100"
        resp = self.sessao.get(url_caixa, timeout=15)
        if resp.status_code != 200:
            resp.raise_for_status()

        parser = ParserProcessosSEI()
        parser.feed(resp.text)
        return parser.processos

    def buscar_processos(self, termo: str) -> List[Dict[str, Any]]:
        self._sincronizar_sessao_se_modificada()

        url_busca = f"{self.base_url}/controlador.php?acao=pesquisa_processo&infra_unidade_atual={self.id_unidade}&infra_sistema=100000100"
        payload = {
            "txtPesquisa": termo,
            "chkSinonimo": "N",
            "btnPesquisar": "Pesquisar"
        }
        resp = self.sessao.post(url_busca, data=payload, timeout=20)
        if resp.status_code != 200:
            resp.raise_for_status()

        parser = ParserProcessosSEI()
        parser.feed(resp.text)
        return parser.processos
