## FIAP - Tech Challenge 1 - Books API

API REST construída com FastAPI para coleta (scraping), armazenamento e consulta de livros do site "Books to Scrape". O projeto inclui autenticação JWT, endpoints obrigatórios e opcionais de consulta, estatísticas e integração com Postgres. Os dados são armazenados em um PostgreSQL online hospedado na Neon. O deploy foi realizado na Vercel, utilizando `api/index.py` como entrypoint.

### Arquitetura
- **Framework**: FastAPI (`main.py`)
- **WSGI/ASGI Adapter para Vercel**: `api/index.py` expõe `app` importando de `main.py`
- **Banco de dados**: PostgreSQL (Neon) via SQLAlchemy 2.0 configurado em `database.py`
- **ORM/Modelos**: `models.py` define `Book`
- **Repositórios**: `repositories.py` concentra consultas/estatísticas
- **Esquemas (DTOs)**: `schemas.py` com `BookSchema` e respostas auxiliares
- **Scraping**: `scraping.py` coleta dados do site e persiste
- **Infra de deploy**: `vercel.json` configura runtime Python e rotas

Fluxo principal:
1. `scraping.py` pode popular o banco com livros
2. Endpoints em `main.py` usam `repositories.py` para consultar `Book`
3. Autenticação JWT simples para rotas protegidas (admin)

Estrutura de diretórios relevante:
```
api/index.py          # Entrypoint Vercel (importa app do main)
main.py               # Definição dos endpoints FastAPI
database.py           # Engine, SessionLocal e Base (SQLAlchemy)
models.py             # Modelo Book (ORM)
repositories.py       # Funções de consulta e estatísticas
schemas.py            # Pydantic schemas
scraping.py           # Coletor (requests + BeautifulSoup)
create_tables.py      # Script para criar tabelas
vercel.json           # Configuração do deploy na Vercel
requirements.txt      # Dependências
```

### Pré-requisitos
- Python 3.13 (ou compatível com as libs)
- PostgreSQL acessível via URL

### Instalação e Configuração (Local)
1. Crie e ative um virtualenv (opcional):
```bash
python3 -m venv venv && source venv/bin/activate
```
2. Instale dependências:
```bash
pip install -r requirements.txt
```
3. Configure o banco em `database.py` (ou via variável de ambiente). Atualmente o projeto utiliza uma URL Postgres no arquivo. Para uso em produção, defina via env e leia no `database.py`.
4. Crie as tabelas:
```bash
python create_tables.py
```
5. (Opcional) Popular o banco com scraping:
```bash
python scraping.py
```
6. Execute localmente:
```bash
uvicorn main:app --reload --port 8000
```
7. Acesse a documentação automática:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Autenticação
- JWT HS256 com expiração (1h access, 7d refresh)
- Credenciais de teste (embarcadas): `admin` / `secret`
- Fluxo:
  - POST `/api/v1/auth/login` → retorna `access_token` e `refresh_token`
  - POST `/api/v1/auth/refresh` → emite novo `access_token`
  - GET `/api/v1/auth/verify` → valida token (Bearer)

### Documentação das Rotas

Rotas públicas:
- `GET /` → ping raiz (útil para Vercel)
- `GET /api/v1/health` → status API e DB
- `GET /api/v1/books` → lista todos os livros
- `GET /api/v1/books/{book_id}` → detalhes por ID
- `GET /api/v1/books/search?title={t}&category={c}` → busca por título/categoria (parciais, case-insensitive; requer ao menos 1 parâmetro)
- `GET /api/v1/categories` → lista categorias únicas

Rotas opcionais (analíticas):
- `GET /api/v1/books/top-rated` → livros com maior rating
- `GET /api/v1/books/price-range?min={min}&max={max}` → filtra por faixa de preço
- `GET /api/v1/stats/overview` → total, preço médio, distribuição de ratings
- `GET /api/v1/stats/categories` → métricas por categoria

Rotas de autenticação:
- `POST /api/v1/auth/login` → autentica e retorna tokens
- `POST /api/v1/auth/refresh` → renova access token
- `GET /api/v1/auth/verify` → verifica validade do token

Rota protegida (requer Bearer access token):
- `POST /api/v1/scraping/trigger` → dispara scraping (admin)

### Exemplos de Requests/Responses

Login:
```bash
curl -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}'
```
Resposta (200):
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Buscar livros por título:
```bash
curl "$BASE_URL/api/v1/books/search?title=python"
```
Resposta (200):
```json
{
  "message": "N livro(s) encontrado(s) com os critérios: título contém 'python'",
  "data": [
    { "id": 1, "titulo": "...", "preco": 51.99, "rating": 4, "categoria": "..." }
  ],
  "total": 1,
  "filters": { "title": "python", "category": null }
}
```

Listar livros:
```bash
curl "$BASE_URL/api/v1/books"
```
Resposta (200) — esquema por item (`BookSchema`):
```json
{
  "id": 1,
  "titulo": "...",
  "preco": 51.99,
  "disponibilidade": "In stock",
  "rating": 4,
  "categoria": "Fiction",
  "imagem": "https://...jpg"
}
```

Faixa de preço:
```bash
curl "$BASE_URL/api/v1/books/price-range?min=10&max=50"
```

Top rated:
```bash
curl "$BASE_URL/api/v1/books/top-rated"
```

Stats gerais:
```bash
curl "$BASE_URL/api/v1/stats/overview"
```

Disparar scraping (protegido):
```bash
curl -X POST "$BASE_URL/api/v1/scraping/trigger" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Execução na Vercel (Deploy)
- O projeto já está configurado com `vercel.json`:
  - Builds: `@vercel/python` com `api/index.py`
  - Rotas: todo tráfego direcionado para `api/index.py`
- Variáveis de ambiente requeridas na Vercel:
  - `DATABASE_URL` → ex.: `postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME`
  - `JWT_SECRET` → segredo para assinar tokens
  - `JWT_ALGORITHM` → normalmente `HS256`

Passos para deploy:
1. Instale a CLI (opcional):
```bash
npm i -g vercel
```
2. Faça login e deploy na raiz do projeto:
```bash
vercel
```
3. Configure as variáveis no painel da Vercel (ou via CLI):
```bash
vercel env add DATABASE_URL
vercel env add JWT_SECRET
vercel env add JWT_ALGORITHM
```
4. Promova para produção:
```bash
vercel --prod
```

### Observações Importantes
- Em produção, evite manter credenciais/segredos dentro do código (`database.py` possui uma URL hardcoded para desenvolvimento). Prefira variáveis de ambiente.
- A rota raiz `/` foi adicionada para evitar 404 no ambiente Vercel e apontar `docs`.
- O scraping faz muitas requisições; use com parcimônia em produção.
- Os dados estão armazenados em um PostgreSQL online na Neon (Neon.tech).

### Licença
Uso educacional/acadêmico no escopo do Tech Challenge.


