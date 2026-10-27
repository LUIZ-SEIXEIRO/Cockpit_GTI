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

## Isolamento GLPI e smoke check opcional

O cliente oficial (`GLPI_PROD_*`) aceita somente `GET`; o cliente local
(`GLPI_LOCAL_*`) é o único que expõe escrita. A escrita exige a configuração
local completa e nunca recorre à oficial. Se nenhuma variável oficial estiver
definida, a configuração local continua independente; se houver configuração
oficial parcial, URL equivalente à local ou token repetido entre ambientes, a
criação do cliente de escrita falha. URLs oficiais devem usar HTTPS, exceto
hosts loopback usados em testes locais.

### Perfil de leitura no GLPI oficial

Um administrador do GLPI institucional deve criar um usuário de integração
dedicado, sem usar uma conta pessoal ou de administração, e atribuir somente um
perfil de menor privilégio que permita a leitura necessária de chamados. No
perfil, confirme que criar, atualizar e excluir chamados e administrar usuários,
perfis, configurações ou a API não estão autorizados. Restrinja também as
entidades e o acesso recursivo ao mínimo necessário; remova perfis e direitos
adicionais herdados ou atribuídos ao usuário.

Configure um cliente de API próprio para essa integração, habilite a API e
restrinja o cliente por origem/IP quando a instalação oferecer essa opção.
Guarde o App-Token e o User-Token apenas no `.env` local, sem copiá-los para
issues, logs, screenshots ou arquivos versionados. O administrador deve
confirmar no servidor:

- o usuário de integração e os perfis efetivamente atribuídos/ativos;
- os direitos de leitura e a ausência de direitos de criar, atualizar e excluir,
  inclusive para os tipos de objeto abrangidos pela integração;
- os limites de entidade e acesso recursivo;
- o estado e as restrições do cliente de API, além dos registros de autenticação
  que identifiquem a conta usada no smoke check.

Essas evidências administrativas são necessárias para confirmar a autorização
de leitura mínima. Uma chamada `GET` bem-sucedida comprova apenas conectividade,
autenticação e acesso de leitura ao recurso consultado; **não prova que o
usuário não possui permissões de escrita**. Não faça chamadas de escrita para
testar permissões no GLPI oficial.

### Executar o smoke check

Na raiz do repositório, configure `GLPI_PROD_BASE_URL`,
`GLPI_PROD_APP_TOKEN` e `GLPI_PROD_USER_TOKEN` no `.env` local. O smoke check
carrega esse arquivo automaticamente; não exige o MariaDB nem o GLPI local.
Ele não faz nenhuma requisição sem a confirmação explícita abaixo:

```sh
python -m backend.glpi_smoke_check --confirm-prod-read
```

O comando usa timeout de 5 segundos, autentica com `GET /initSession`, consulta
no máximo um item (`GET /Ticket/?range=0-0`) e encerra a sessão com `GET
/killSession`. Só informa o status/conectividade e nunca exibe tokens, conteúdo
de chamados ou dados pessoais. A confirmação `--confirm-prod-read` autoriza
essas requisições ao GLPI oficial; execute apenas com autorização institucional.
Sem a opção, o programa informa que não fez requisições.

O Compose passa somente essas três variáveis GLPI para o serviço `backend`;
valores ausentes permanecem vazios e não impedem a inicialização normal. Depois
de iniciar a stack, o check pode ser executado dentro do contêiner:

```sh
docker compose exec backend python glpi_smoke_check.py --confirm-prod-read
```

Para separar problemas de DNS/TLS/rota antes da autenticação, compare o host e
o contêiner real na rede/VPN necessária. Estes comandos não enviam credenciais,
não seguem redirecionamentos e não exibem o destino:

```sh
python -c "import socket; print('DNS=ok' if socket.getaddrinfo('atendimento.spaguas.sp.gov.br', 443) else 'DNS=falhou')"
python -c "import httpx; r=httpx.get('https://atendimento.spaguas.sp.gov.br/apirest.php/initSession', timeout=10, follow_redirects=False); print('HTTP=' + str(r.status_code))"
docker compose exec backend python -c "import socket; print('DNS=ok' if socket.getaddrinfo('atendimento.spaguas.sp.gov.br', 443) else 'DNS=falhou')"
docker compose exec backend python -c "import httpx; r=httpx.get('https://atendimento.spaguas.sp.gov.br/apirest.php/initSession', timeout=10, follow_redirects=False); print('HTTP=' + str(r.status_code))"
```

O `httpx` mantém a validação TLS padrão. `HTTP=000` não é status do servidor:
indica que a conexão não produziu resposta HTTP; o comando pode encerrar com
erro de DNS, conexão ou certificado. Em um `302`, classifique o destino somente
localmente sem publicá-lo e peça ao administrador para identificar se o
redirecionamento é do GLPI, proxy ou SSO.

As variáveis do Compose ficam visíveis a usuários que podem inspecionar o
contêiner. Restrinja o acesso ao host Docker e ao `.env`. Se a política
operacional exigir segredo montado em arquivo em vez de variáveis de ambiente,
adote Docker secrets em uma alteração própria; não passe o `.env` inteiro ao
contêiner. Os nomes legados `GLPI_URL`, `GLPI_APP_TOKEN` e `GLPI_USER_TOKEN`
não são consumidos pelo cliente.

Os testes automatizados usam transporte HTTP mockado para comprovar método,
host, cabeçalhos, limite e saída sanitizada; nenhuma requisição real foi feita
nesta validação. A revisão do perfil e o smoke check ao vivo no GLPI
institucional permanecem **pendentes do operador**, pois este ambiente não tem
credenciais nem autorização para acessar o sistema.

### Validação desta etapa

| Comando | Resultado |
|---|---|
| `python -m pytest -q backend/tests/test_glpi_clients.py` | **19 passed** |
| `python -m pytest -q backend/tests` | **23 passed**, 1 aviso de depreciação Starlette/AnyIO |
| `python -m compileall -q backend` | Concluído |
| `python -m backend.glpi_smoke_check` | Nenhuma requisição; saída de opt-in e código 2 |

As requisições cobertas pelos testes foram capturadas por transporte HTTP
mockado. Nenhum chamado foi consultado e nenhuma chamada foi feita ao GLPI
institucional. A configuração de perfil no servidor e a execução opt-in ao vivo
não foram validadas neste ambiente.

## Pendências de implementação após esta etapa

- Não há endpoint FastAPI `/api/glpi/chamados`. O código Flask removido apontava
  para `backend.sistemas_internos.sis_01_glpi_8088_prod`, que não existe no
  repositório; o conector de produção e sua integração continuam pendentes e
  não foram simulados.
- `backend/glpi_clients.py` valida a separação e limita produção a GET, mas não
  há GLPI local no Compose nem endpoints de gravação do Cockpit. A validação
  administrativa do perfil oficial e o smoke check ao vivo continuam pendentes
  do operador.
- OpenProject, New API, sincronização real e integração das telas permanecem
  fora do escopo desta validação.

Para produção, o cliente GLPI oficial deve usar credenciais somente de leitura.
As gravações futuras devem usar credenciais distintas do GLPI local; a
configuração de exemplo não substitui permissões e controles de segurança nos
serviços.
