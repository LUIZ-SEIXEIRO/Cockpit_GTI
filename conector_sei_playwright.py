# -*- coding: utf-8 -*-
import logging
import re
from typing import Any, Dict
from urllib.parse import urljoin, urlparse

logger = logging.getLogger("CockpitGTI.PlaywrightSEI")

RE_LINKS_CONTROLADOR = re.compile(
    r"(?:href|action)\s*=\s*[\"']([^\"']*controlador\.php\?[^\"']*infra_hash=[a-fA-F0-9]+[^\"']*)[\"']",
    re.IGNORECASE,
)


def extrair_urls_assinadas_html(html: str, base_url: str = "https://sei.sp.gov.br/sei") -> Dict[str, str]:
    if not isinstance(html, str) or not html:
        return {}
    base_norm = base_url.rstrip("/") + "/"
    sei_netloc = urlparse(base_norm).netloc.lower()
    urls: Dict[str, str] = {}
    for bruto in RE_LINKS_CONTROLADOR.findall(html):
        limpo = bruto.replace("&amp;", "&").strip()
        abs_url = urljoin(base_norm, limpo)
        parsed = urlparse(abs_url)
        if parsed.scheme.lower() != "https" or parsed.netloc.lower() != sei_netloc:
            continue
        m_acao = re.search(r"[?&]acao=([a-zA-Z0-9_]+)", abs_url)
        if m_acao:
            acao = m_acao.group(1)
            if acao not in urls:
                urls[acao] = abs_url
    return urls


def autenticar_sei_playwright(
    usuario: str,
    senha: str,
    orgao: str = "SPAGUAS",
    id_unidade: str = "110050725",
    base_url: str = "https://sei.sp.gov.br/sei",
    login_url: str = "https://sei.sp.gov.br/sip/login.php?sigla_orgao_sistema=GESP&sigla_sistema=SEI",
    timeout_ms: int = 30000,
) -> Dict[str, Any]:
    if not isinstance(usuario, str) or not usuario.strip() or not isinstance(senha, str) or not senha:
        return {"sucesso": False, "codigo": 400, "erro": "Usu\u00e1rio e senha do SEI s\u00e3o obrigat\u00f3rios."}

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as ie:
        return {"sucesso": False, "codigo": 503, "erro": f"Playwright n\u00e3o instalado no ambiente: {ie}"}

    browser = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto(login_url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.fill("#txtUsuario", usuario.strip())
            page.fill("#pwdSenha", senha)

            if orgao and str(orgao).strip():
                org_str = str(orgao).strip()
                try:
                    if org_str.isdigit():
                        page.select_option("#selOrgao", value=org_str)
                    else:
                        opcoes = page.locator("#selOrgao option").all_inner_texts()
                        match_label = next((op.strip() for op in opcoes if org_str.lower() in op.lower()), None)
                        if match_label:
                            page.select_option("#selOrgao", label=match_label)
                except Exception:
                    pass

            submit_btn = page.locator("button[type='submit'], input[type='submit'], #sbmLogin").first
            submit_btn.click()
            page.wait_for_load_state("networkidle", timeout=timeout_ms)

            url_atual = str(page.url or "")
            html_atual = str(page.content() or "")
            if "login.php" in url_atual.lower() or 'id="frmlogin"' in html_atual.lower():
                return {"sucesso": False, "codigo": 401, "erro": "Autentica\u00e7\u00e3o recusada pelo SIP/SEI SP."}

            sei_host = (urlparse(base_url).hostname or "sei.sp.gov.br").lower()
            cookies_dict: Dict[str, str] = {}
            for c in context.cookies():
                dom = str(c.get("domain") or "").lstrip(".").lower()
                if dom == sei_host or dom.endswith("." + sei_host) or sei_host.endswith("." + dom):
                    nome = str(c.get("name") or "")
                    val = str(c.get("value") or "")
                    if nome:
                        cookies_dict[nome] = val

            urls_assinadas = extrair_urls_assinadas_html(html_atual, base_url=base_url)
            url_caixa = urls_assinadas.get("procedimento_controlar")
            if url_caixa:
                try:
                    page.goto(url_caixa, wait_until="domcontentloaded", timeout=timeout_ms)
                    urls_assinadas.update(extrair_urls_assinadas_html(str(page.content() or ""), base_url=base_url))
                except Exception:
                    pass

            if not cookies_dict:
                return {"sucesso": False, "codigo": 502, "erro": "Login conclu\u00eddo, mas nenhum cookie de sess\u00e3o foi capturado."}

            return {
                "sucesso": True,
                "codigo": 200,
                "cookies": cookies_dict,
                "urls_assinadas": urls_assinadas,
                "unidade": str(id_unidade),
            }
    except Exception as e:
        logger.error(f"Erro na autenticacao Playwright do SEI: {type(e).__name__}")
        return {"sucesso": False, "codigo": 502, "erro": f"Falha na automa\u00e7\u00e3o de login do SEI SP: {type(e).__name__}"}
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass
