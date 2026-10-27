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

## GLPI local (Sprint 2)

O Compose inclui uma instância **GLPI local**, separada do GLPI oficial, para
receber futuras gravações do Cockpit. Ela está pronta para configuração
inicial; **nenhum endpoint de gravação do Cockpit está habilitado** e não há
integração de escrita com o GLPI oficial.

**Decisão de versão.** `html/` contém o código-fonte do GLPI 12.0.0, mas o
Compose não tem PHP/Apache, cron nem a configuração de diretórios do GLPI para
servir essa árvore, que também não deve ser alterada. Por isso o serviço usa a
imagem oficial de versão fixa `ghcr.io/glpi-project/glpi:12.0.0` (mesma versão
de `html/`), sem `latest`, com MariaDB 10.11. Para atualizar, altere a tag de
forma deliberada e faça backup antes.

**Serviços e isolamento.**

| Serviço | Função | Acesso |
|---|---|---|
| `glpi-local` | GLPI 12.0.0 | `http://localhost:8088` |
| `glpi-db` | MariaDB exclusivo do GLPI local (host interno `glpi-db`) | somente rede Docker, sem porta publicada |

O banco e as credenciais (`GLPI_LOCAL_DB_*`) são distintos do banco do
FastAPI (`DB_*`). Todas as variáveis são obrigatórias e sem valor padrão
(`${VAR:?...}`). O contêiner não recebe `GLPI_PROD_*`, tokens oficiais nem o
endereço de produção.

**Volumes persistentes** (nomeados, gerenciados pelo Docker):
`glpi_local_db` (banco) e `glpi_local_data` (`/var/glpi`: configuração, arquivos,
logs).

**Bootstrap.**

1. Preencha em `.env` as variáveis `GLPI_LOCAL_DB_ROOT_PASSWORD`,
   `GLPI_LOCAL_DB_NAME`, `GLPI_LOCAL_DB_USER` e `GLPI_LOCAL_DB_PASSWORD` com
   valores próprios, diferentes das credenciais `DB_*` (o `.env` não é
   versionado). Em volume já inicializado, esses valores não mudam usuários
   existentes.
2. Valide e suba:

   ```sh
   docker compose config --quiet
   docker compose up -d glpi-local
   docker compose ps
   ```

   Na primeira subida a imagem instala o schema automaticamente; o healthcheck
   do `glpi-local` pode levar alguns minutos até ficar `healthy`.
3. Acesse `http://localhost:8088`. A imagem cria usuários de instalação com
   credenciais padrão documentadas pelo GLPI (consulte os logs com
   `docker compose logs glpi-local`). **Troque imediatamente todas as senhas
   padrão e desative/remova os usuários de exemplo** antes de qualquer uso.
4. Tokens da API REST do GLPI local só devem ser criados depois dessa
   configuração e guardados somente no `.env` como `GLPI_LOCAL_APP_TOKEN` e
   `GLPI_LOCAL_USER_TOKEN`; devem ser diferentes dos de produção.

**Backup básico** (sem parar a persistência; guarde os arquivos fora do repositório):

```sh
mkdir -p backups
docker compose exec -T glpi-db sh -c 'mariadb-dump -uroot -p"$MYSQL_ROOT_PASSWORD" --single-transaction "$MYSQL_DATABASE"' > backups/glpi-local-db.sql
docker compose exec -T glpi-local tar -C /var/glpi -cf - . > backups/glpi-local-data.tar
```

**Encerrar sem apagar dados:**

```sh
docker compose stop glpi-local glpi-db
```

`docker compose down` (sem opções de volume) remove apenas os contêineres e
preserva os volumes. Não remova volumes para “corrigir” credenciais.

**Confirmar o isolamento.**

```sh
docker compose config | grep -ci glpi_prod            # esperado: 0
docker compose exec glpi-local env | grep -ci glpi_prod  # esperado: 0
docker compose port glpi-local 80                     # 0.0.0.0:8088
```

O serviço `glpi-local` só recebe variáveis `GLPI_DB_*` apontando para
`glpi-db`; `GLPI_LOCAL_BASE_URL` deve apontar para ele (por exemplo
`http://localhost:8088/apirest.php` fora do Docker) e `get_write_client()`
aceita somente `http://glpi-local/apirest.php` ou
`http://localhost:8088/apirest.php`. A escrita integrada continuará em sprint
posterior.

**Validação:** testes Python (`11 passed`) e `docker compose config` com
valores temporários passaram. O GLPI local foi iniciado em projeto Compose
temporário e isolado (`glpi-local` e `glpi-db` `healthy`; `http://localhost:8088/`
respondeu HTTP 200); os volumes temporários foram descartados. A stack completa
com o `.env` e os volumes do ambiente de destino não foi validada.

## Sprint 3 — complemento do PR #7 (WIP mesclado)

O PR #7 foi mesclado com título e escopo WIP; sua mesclagem não implementou CRUD
persistente para a Mesa. Esta entrega é complementar e registra a decisão
técnica abaixo. **Não há CRUD nem persistência simulada**: até que os pré-requisitos
sejam configurados, `GET /api/mesa/minhas-tarefas` responde HTTP 503 e a aba
identifica seus exemplos como demonstração não persistida.

### Decisão técnica e bloqueio

O código versionado é GLPI 12.0.0. Ele possui uma API REST adequada a tarefas:
`html/apirest.md` documenta criação por `POST /apirest.php/:itemtype/` e
atualização por `PUT`/`PATCH /apirest.php/:itemtype/:id`; a API de alto nível
`/api.php/v2` também documenta `ProjectTask` e OAuth2, recomendando Authorization
Code para aplicações interativas (`html/resources/api_doc.MD` e
`html/src/Glpi/Api/HL/Controller/ProjectController.php`).

Isso não torna seguro habilitar a persistência nesta configuração:

- `ProjectTask::prepareInputForAdd()` exige um `projects_id` real
  (`html/src/ProjectTask.php`). Não há projeto local configurado para a Mesa;
  não será criado um projeto fictício nem usada uma tarefa de Ticket/Change/
  Problem como substituto.
- A API documenta `ProjectTask` com projeto, estado, usuário e equipe, e aplica
  condições de leitura ligadas ao usuário/projeto. Porém, `ProjectTask` não tem
  um campo `is_private`; visibilidade depende das relações e permissões GLPI.
  Projeto, entidade, responsáveis/equipe e direitos precisariam ser definidos
  e verificados na instância local.
- O FastAPI não possui autenticação de usuário. O `get_write_client()` atual usa
  credenciais estáticas de API e não identifica o usuário do Cockpit; a API
  OAuth2 interativa do GLPI ainda não está integrada. Expor escrita usando essa
  identidade compartilhada permitiria que qualquer cliente autorizado a chamar
  o FastAPI atuasse como a mesma conta. O Compose também não injeta tokens
  `GLPI_LOCAL_*` no backend, e esta entrega deliberadamente não os injeta.
- Não há configuração pós-bootstrap de cliente OAuth, projeto/IDs ou permissões
  para essa funcionalidade. A Sprint 1 continua pendente e separada; nada aqui
  depende de acesso ao GLPI institucional.

**Próximo escopo recomendado:** provisionar no GLPI local um projeto real para
essa finalidade e seus estados/equipe; configurar OAuth2 Authorization Code e
uma sessão segura por usuário no Cockpit; validar no servidor a identidade e os
direitos mínimos de leitura/criação/atualização para esse projeto; só então
implementar e testar o fluxo usando exclusivamente o cliente local. Não usar
credenciais de produção, não criar dados de exemplo no GLPI e não tratar o
fallback visual como persistência.

### Verificações reproduzíveis

```sh
python -m pytest -q backend/tests
python -m compileall -q backend
node --check frontend/abas/aba_06_mesa_trabalho.js
```

Para validar somente o Compose, use um arquivo temporário com valores fictícios
para as variáveis obrigatórias de banco, sem iniciar serviços nem tocar volumes:

```sh
cat >/tmp/cockpit-compose-test.env <<'EOF'
DB_ROOT_PASSWORD=test-only
DB_NAME=cockpit_test
DB_USER=cockpit_test
DB_PASSWORD=test-only
GLPI_LOCAL_DB_ROOT_PASSWORD=test-only
GLPI_LOCAL_DB_NAME=glpi_test
GLPI_LOCAL_DB_USER=glpi_test
GLPI_LOCAL_DB_PASSWORD=test-only
EOF
docker compose --env-file /tmp/cockpit-compose-test.env config --quiet
rm /tmp/cockpit-compose-test.env
```

Esse teste de configuração não inicia o GLPI nem usa o `.env`, tokens ou volumes
do ambiente real. Nenhuma requisição ao GLPI oficial é necessária ou realizada.

**Resultados desta entrega (2026-10-27):** `python -m pytest -q backend/tests`
retornou **17 passed** (um aviso preexistente de depreciação Starlette/AnyIO);
`python -m compileall -q backend`, `node --check` da aba Mesa e
`docker compose config --quiet` com os valores temporários acima passaram. Um
teste isolado da UI confirmou escape de conteúdo HTML hostil e os estados
demonstração/HTTP 503. Os testes HTTP mockados confirmam POST/PUT somente para
`glpi-local`, nunca para o host de produção. Nenhum contêiner foi iniciado e
nenhuma configuração, credencial ou volume real foi acessado. Não há lint
JavaScript configurado no repositório.

## Follow-up adiado da Sprint 1

A Sprint 1 permanece aberta (PR #4). Foi decidido seguir para a Sprint 2 e
tratar depois, sem bloquear a infraestrutura local:

- o smoke check de leitura contra o GLPI institucional recebeu **HTTP 302**;
- o administrador do GLPI/proxy deve confirmar o endpoint canônico da API REST
  e que o perfil dos tokens oficiais é somente leitura.

Nenhuma chamada real ao GLPI institucional foi feita na Sprint 2, e tokens ou
dados pessoais não devem ser incluídos em PRs.

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
  (somente leitura) e local, e o GLPI local está no Compose (Sprint 2), mas não há endpoints de
  gravação do Cockpit.
- OpenProject, New API, sincronização real e integração das telas permanecem
  fora do escopo desta validação.

Para produção, o cliente GLPI oficial deve usar credenciais somente de leitura.
As gravações futuras devem usar credenciais distintas do GLPI local; a
configuração de exemplo não substitui permissões e controles de segurança nos
serviços.
