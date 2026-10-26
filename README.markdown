# Dashboard Visual

Este é um exemplo básico de um dashboard visualizado usando HTML, CSS e JavaScript.

### Configuração

1. Clone este repositório ou crie uma nova pasta e insira os arquivos de acordo com a estrutura de diretórios.
2. Substitua `your_access_token` no arquivo `js/script.js` pelo token de acesso real para o backend GLPI.

### Execução

1. Abra o arquivo `index.html` em um navegador web.

## Infraestrutura (Docker Compose: `db` + `backend`)

1. `cp .env.example .env` e preencha `DB_ROOT_PASSWORD`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (o `.env` é ignorado pelo git).
2. Valide: `docker compose config --quiet`
3. Suba: `docker compose up --build -d` (o backend aguarda o MariaDB ficar saudável).
4. Verifique: `GET http://localhost:8000/api/health` (backend) e `GET http://localhost:8000/api/health/db` (executa `SELECT 1`; retorna 503 genérico em caso de falha).

Atenção: um volume MariaDB já inicializado (`volumes_docker/mariadb_3306`) mantém as credenciais originais; alterar o `.env` não as modifica. Não apague o volume sem backup.

Testes: `cd backend && pip install -r requirements.txt pytest && python -m pytest tests`
