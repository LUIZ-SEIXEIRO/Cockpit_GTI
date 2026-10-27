"""Smoke check opcional de leitura do GLPI oficial."""
import argparse
from pathlib import Path

import httpx
from dotenv import load_dotenv

try:
    from backend.glpi_clients import GlpiConfigError, GlpiProdReadOnlyClient, load_prod_config
except ModuleNotFoundError as error:
    if error.name != "backend":
        raise
    from glpi_clients import GlpiConfigError, GlpiProdReadOnlyClient, load_prod_config


def run_smoke_check(client: GlpiProdReadOnlyClient) -> tuple[bool, str]:
    try:
        init_response = client.get("initSession")
        if not 200 <= init_response.status_code < 300:
            return False, f"Inicializacao GLPI falhou (HTTP {init_response.status_code})."
        payload = init_response.json()
        session_token = payload.get("session_token") if isinstance(payload, dict) else None
        if not isinstance(session_token, str) or not session_token:
            return False, "GLPI respondeu sem iniciar uma sessao; conteudo omitido."

        try:
            read_response = client.get(
                "Ticket/?range=0-0",
                session_token=session_token,
            )
            if not 200 <= read_response.status_code < 300:
                return False, f"Leitura GLPI falhou (HTTP {read_response.status_code})."
            return (
                True,
                "GET de leitura respondeu com sucesso (HTTP "
                f"{read_response.status_code}); limite de 1 item, conteudo omitido.",
            )
        finally:
            try:
                client.get("killSession", session_token=session_token)
            except Exception:
                pass
    except httpx.RequestError:
        return False, "Falha de conectividade GLPI; detalhes omitidos."
    except (ValueError, TypeError):
        return False, "Resposta GLPI inesperada; conteudo omitido."
    except Exception:
        return False, "Falha no smoke check GLPI; detalhes omitidos."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verificacao GET-only opcional do GLPI oficial.")
    parser.add_argument(
        "--confirm-prod-read",
        action="store_true",
        help="autoriza uma sessao de leitura e uma amostra limitada a 1 chamado",
    )
    args = parser.parse_args(argv)
    if not args.confirm_prod_read:
        print("Nenhuma requisicao efetuada. Use --confirm-prod-read para autorizar o smoke check.")
        return 2

    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
    try:
        client = GlpiProdReadOnlyClient(load_prod_config(), timeout=5.0)
    except GlpiConfigError as error:
        print(f"Configuracao GLPI invalida: {error}")
        return 2

    success, message = run_smoke_check(client)
    print(message)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
