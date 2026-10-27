# Cockpit GTI

## Runtime oficial

O runtime suportado é **FastAPI**, definido em `backend/main.py`. O serviço
`backend` do `docker-compose.yml` constrói `backend/Dockerfile`, que inicia
`uvicorn main:app` na porta 8000. Esse servidor entrega a SPA em `frontend/` e
expõe os endpoints de saúde. O Compose também inicia MariaDB (`db`), e o
backend aguarda o healthcheck do banco.

Não há runtime Flask suportado. O launcher, as rotas Flask e as dependências
legadas foram removidos para não sugerir um segundo servidor. `html/` contém
código do GLPI e não é o backend FastAPI do Cockpit.

## Executar com Docker Compose

1. Copie `.env.example` para `.env` e preencha `DB_ROOT_PASSWORD`, `DB_NAME`,
   `DB_USER` e `DB_PASSWORD` com valores locais.
2. Valide o Compose:

   ```sh
   docker compose config --quiet
   ```

3. Construa e inicie os serviços:

   ```sh
   docker compose up --build -d
   ```

4. Verifique as respostas:

   ```sh
   curl -i http://localhost:8000/api/health
   curl -i http://localhost:8000/api/health/db
   curl -I http://localhost:8000/
   ```

   `/api/health/db` executa `SELECT 1` no MariaDB e retorna 503 genérico se o
   banco estiver indisponível. A raiz entrega `frontend/painel.html`.

O Compose persiste os dados em `volumes_docker/mariadb_3306`. Um diretório
MariaDB já inicializado mantém as credenciais originais; alterar `.env` não
altera usuários existentes. Faça backup antes de qualquer operação nos dados e
não apague esse diretório para “corrigir” credenciais.

## Testes automatizados

Na raiz do repositório, instale as dependências do backend e o pytest:

```sh
python -m pip install -r backend/requirements.txt pytest
python -m pytest -q backend/tests
```

O teste de contrato confirma que a aplicação é FastAPI, que o Compose constrói
o backend, que o Dockerfile inicia `uvicorn main:app` e que não existe launcher
Flask na raiz.

## Validações executadas neste ambiente

Em 2026-10-27, com Python 3.12.3, Docker 28.0.4 e Docker Compose 2.38.2:

| Comando/verificação | Resultado |
|---|---|
| `python -m pip install -r backend/requirements.txt pytest` | Concluído |
| `python -m pytest -q backend/tests` | **10 passed**; 1 aviso de depreciação Starlette/AnyIO |
| `python -m compileall -q backend` | Concluído |
| `docker compose --env-file /tmp/cockpit-sprint0.env config --quiet` | Concluído com valores temporários de teste, sem credenciais do usuário |
| `docker build -t cockpit-gti-sprint0:validation ./backend` | Imagem construída |
| Smoke test do Compose isolado | MariaDB ficou saudável; `/api/health` e `/api/health/db` retornaram `200`; `/` e `/static/painel.html` retornaram `200` |

O smoke test Docker usou uma cópia temporária do Compose e redirecionou o volume
MariaDB para `/tmp`; os contêineres e dados temporários foram removidos após o
teste. Portanto, **não alterou nem validou o volume versionado**
`volumes_docker/mariadb_3306`, as credenciais ou a instalação Docker Desktop do
usuário. O Compose foi realmente iniciado neste ambiente; a validação com o
`.env` e os dados persistentes do ambiente de destino continua pendente.

## Pendências fora da Sprint 0

- Não há endpoint FastAPI `/api/glpi/chamados`. O código Flask removido apontava
  para `backend.sistemas_internos.sis_01_glpi_8088_prod`, que não existe no
  repositório; o conector de produção e sua integração continuam pendentes e
  não foram simulados.
- `backend/glpi_clients.py` contém clientes separados para GLPI de produção
  (somente leitura) e local, mas não há GLPI local no Compose nem endpoints de
  gravação do Cockpit.
- OpenProject, New API, sincronização real e integração das telas permanecem
  fora do escopo desta validação.

Para produção, o cliente GLPI oficial deve usar credenciais somente de leitura.
As gravações futuras devem usar credenciais distintas do GLPI local; a
configuração de exemplo não substitui permissões e controles de segurança nos
serviços.
