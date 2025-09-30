# FIAP - Tech Challenge 1 - RM367414

API de livros construída com FastAPI, SQLAlchemy e scraping do site Books to Scrape. Inclui autenticação via JWT, endpoints de consulta e estatísticas, além de um disparo protegido para executar o scraping.

## Objetivos
- Coletar dados de livros via scraping (título, preço, disponibilidade, rating, categoria e imagem)
- Persistir dados em banco PostgreSQL via SQLAlchemy
- Disponibilizar API REST com filtros, listagem, estatísticas e dados para ML
- Autenticação com JWT (login e refresh)
- Deploy serverless (Vercel)

## Arquitetura (arquivos principais)
- `main.py`: aplicação FastAPI (rotas, autenticação, endpoints)
- `database.py`: engine, `SessionLocal` e `Base` (SQLAlchemy)
- `models.py`: modelo `Book`
- `repositories.py`: consultas ao banco
- `schemas.py`: Pydantic models (responses/requests)
- `scraping.py`: rotina de scraping e persistência
- `create_tables.py`: criação de tabelas
- `requirements.txt`: dependências Python
- `api/index.py`: entrypoint para Vercel (expõe `app` do FastAPI)
- `vercel.json`: configuração de deploy na Vercel

## Requisitos
- Python 3.11+ (3.13 usado localmente)
- PostgreSQL acessível (local ou gerenciado)
- Pip e virtualenv

## Configuração do ambiente
1) Crie e ative um ambiente virtual (opcional, recomendado):
```bash
python3 -m venv venv
source venv/bin/activate
```

2) Instale dependências:
```bash
pip install -r requirements.txt
```

3) Ajuste variáveis de ambiente (local):
- A aplicação usa constantes no código para JWT por padrão, mas é recomendado sobrepor via ambiente na Vercel.
- Configure o banco em `database.py` (ou via `DATABASE_URL` na Vercel). Formato suportado:
```
postgresql+psycopg2://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
```
Atualmente em `database.py`:
```python
DATABASE_URL = "postgresql+psycopg2://macos@localhost/booksdb"
```
Ajuste conforme seu ambiente.

4) Crie as tabelas:
```bash
python create_tables.py
```

## Executando localmente
Inicie a API com Uvicorn:
```bash
uvicorn main:app --reload
```
Acesse:
- Raiz: `/` (mensagem e links)
- Docs (Swagger): `/docs`
- OpenAPI JSON: `/openapi.json`

## Autenticação (JWT)
- Login: `POST /api/v1/auth/login`
  - Body: `{ "username": "admin", "password": "secret" }`
  - Resposta: `access_token` (1h) e `refresh_token` (7 dias)
- Refresh: `POST /api/v1/auth/refresh`
  - Body: `{ "refresh_token": "<token>" }`
- Verificar token: `GET /api/v1/auth/verify` (Authorization: `Bearer <access_token>`)

Use `Authorization: Bearer <access_token>` nas rotas protegidas.

## Endpoints
- Obrigatórios
  - `GET /api/v1/books` — lista todos os livros
  - `GET /api/v1/categories` — lista categorias distintas
  - `GET /api/v1/health` — status da API e DB
  - `GET /api/v1/books/{book_id}` — detalhe do livro por ID
  - `GET /api/v1/books/search?title=...&category=...` — busca por título e/ou categoria
- Opcionais
  - `GET /api/v1/books/top-rated` — livros com maior rating
  - `GET /api/v1/books/price-range?min=...&max=...` — livros por faixa de preço
  - `GET /api/v1/stats/overview` — estatísticas gerais (total, preço médio, distribuição de ratings)
  - `GET /api/v1/stats/categories` — estatísticas por categoria (médias e extremos de preço)
- Admin
  - `POST /api/v1/scraping/trigger` — dispara o scraping (protegido, exige token)

## Scraping
- Implementado em `scraping.py` na função `scrape_books()`
- A rota `POST /api/v1/scraping/trigger` chama `scrape_books()`
- Origem dos dados: `https://books.toscrape.com/`
- Campos salvos: `titulo`, `preco`, `disponibilidade`, `rating`, `categoria`, `imagem`

### Executar scraping manualmente (opcional)
```bash
python scraping.py
```

## Banco de Dados
Modelo `Book` (`models.py`):
- `id: int`
- `titulo: str`
- `preco: float`
- `disponibilidade: str`
- `rating: int`
- `categoria: str`
- `imagem: str`

Migração simplificada (sem Alembic): `python create_tables.py`

## Variáveis de Ambiente (Deploy)
Configure no painel da Vercel (Project Settings > Environment Variables):
- `DATABASE_URL`: conexão PostgreSQL (produção/serviço gerenciado)
- `JWT_SECRET`: segredo para assinar tokens
- `JWT_ALGORITHM`: ex. `HS256`

## Deploy na Vercel
Arquivos necessários:
- `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    { "src": "api/index.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "api/index.py" }
  ],
  "env": {
    "DATABASE_URL": "postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME",
    "JWT_SECRET": "CHANGE_ME",
    "JWT_ALGORITHM": "HS256"
  }
}
```
- `api/index.py`:
```python
from main import app as fastapi_app

app = fastapi_app
```

Passos:
1) Importar o repositório no Vercel (project root apontando para a raiz do repo)
2) Definir variáveis de ambiente (`DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`)
3) Deploy

Após o deploy:
- Acesse `/` (deve retornar mensagem "API online")
- Acesse `/docs` para testar os endpoints

## Teste rápido via curl
- Health:
```bash
curl -s https://SEU_DOMINIO.vercel.app/api/v1/health | jq
```
- Login:
```bash
curl -s -X POST https://SEU_DOMINIO.vercel.app/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"secret"}' | jq
```
- Scraping (com token):
```bash
ACCESS=SEU_TOKEN_AQUI
curl -s -X POST https://SEU_DOMINIO.vercel.app/api/v1/scraping/trigger \
  -H "Authorization: Bearer $ACCESS" | jq
```

## Dicas e resolução de problemas
- 404 no `/`: adicionamos rota raiz em `main.py`; garanta que `api/index.py` está importando `app` corretamente
- Erros de dependências: confira `requirements.txt` na raiz
- Erro de conexão com DB: verifique `DATABASE_URL` e segurança de rede do serviço PostgreSQL
- Timeout no scraping: a Vercel tem limites de execução; para cargas grandes, considere rodar o scraping localmente ou via job externo e apenas servir a API na Vercel

## Licença
Projeto acadêmico para o Tech Challenge FIAP. Uso educacional.
