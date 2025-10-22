## FIAP - Tech Challenge 1 - Books API

API REST construída com **FastAPI** para coletar (scraping), armazenar e consultar livros do site [Books to Scrape](https://books.toscrape.com). O projeto inclui **autenticação JWT**, endpoints obrigatórios e opcionais, estatísticas, scraping sob demanda e integração com **PostgreSQL**.

- **Docs (deploy público)**: [`/docs` na Vercel](https://fiap-tech-challenge-rm-367414.vercel.app/docs)

### Objetivo

Este projeto faz parte do **FIAP - Tech Challenge 1** e tem como metas:

- Coletar dados de livros via web scraping
- Persistir as informações em um banco PostgreSQL
- Disponibilizar uma API para consultas e estatísticas
- Proteger endpoints administrativos com JWT
- Aplicar boas práticas de arquitetura e deploy serverless (Vercel)

### Arquitetura

![Diagrama do projeto](./diagrama.svg)

- Scraping (Requests + BeautifulSoup) → PostgreSQL (Neon)
- FastAPI + SQLAlchemy → API RESTful
- JWT Authentication → proteção de endpoints
- Vercel → deploy serverless (entrypoint `api/index.py`)

Estrutura principal de diretórios/arquivos:

```
api/
  index.py           # Entrypoint da Vercel (exporta `app` do FastAPI)
  main.py            # Definição dos endpoints
app/
  database.py        # Engine, SessionLocal e Base (SQLAlchemy)
  models.py          # Modelo ORM (Book)
  repositories.py    # Regras de acesso a dados/estatísticas
  schemas.py         # Pydantic Schemas
scripts/
  scraping.py        # Coletor de livros (requests + BeautifulSoup)
  create_tables.py   # Criação de tabelas
vercel.json          # Configuração do deploy
requirements.txt     # Dependências
```

### Tecnologias Utilizadas

- Python 3.13
- FastAPI, Starlette
- SQLAlchemy
- Pydantic
- PostgreSQL (Neon.tech)
- Requests, BeautifulSoup4
- PyJWT
- Uvicorn
- Vercel (Serverless Python)

### Pré-requisitos

- Python 3.13 (ou compatível)
- Banco PostgreSQL acessível (local/online)

### Instalação e Configuração (Local)

1) Clone o repositório:

```bash
git clone https://github.com/<seu-usuario>/tech-challenge-books-api.git
cd tech-challenge-books-api
```

2) Crie e ative um ambiente virtual (opcional):

```bash
python3 -m venv venv
source venv/bin/activate
```

3) Instale as dependências:

```bash
pip install -r requirements.txt
```

4) Configure as variáveis de ambiente (recomendado):

```bash
export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME"
export JWT_SECRET="sua_chave_segura"
export JWT_ALGORITHM="HS256"
```

5) Crie as tabelas:

```bash
python scripts/create_tables.py
```

6) (Opcional) Popular o banco com scraping localmente:

```bash
python scripts/scraping.py
```

7) Suba o servidor localmente:

```bash
uvicorn api.main:app --reload --port 8000
```

8) Acesse a documentação local: `http://localhost:8000/docs`

9) Acesse a documentação do deploy: [`/docs` na Vercel](https://fiap-tech-challenge-rm-367414.vercel.app/docs)

### Autenticação (JWT)

- Algoritmo: HS256
- Padrão: Bearer Token no header `Authorization`
- Credenciais de teste: `admin` / `secret`

Fluxo básico:

- POST `/api/v1/auth/login` → retorna `access_token` e `refresh_token`
- POST `/api/v1/auth/refresh` → emite novo `access_token`
- GET `/api/v1/auth/verify` → valida token atual

### Documentação das Rotas (Resumo)

Rotas públicas:

- `GET /` → ping raiz
- `GET /api/v1/health` → status da API e banco
- `GET /api/v1/books` → lista todos os livros
- `GET /api/v1/books/{book_id}` → detalhes por ID
- `GET /api/v1/books/search?title={t}&category={c}` → busca por título/categoria
- `GET /api/v1/categories` → categorias únicas

Rotas opcionais (analíticas):

- `GET /api/v1/books/top-rated` → livros com maior rating
- `GET /api/v1/books/price-range?min={min}&max={max}` → filtra por preço
- `GET /api/v1/stats/overview` → total, preço médio, distribuição de ratings
- `GET /api/v1/stats/categories` → métricas por categoria

Autenticação:

- `POST /api/v1/auth/login` → autentica e retorna tokens
- `POST /api/v1/auth/refresh` → renova access token
- `GET /api/v1/auth/verify` → valida token

Protegida (Bearer token necessário):

- `POST /api/v1/scraping/trigger` → dispara scraping

### Exemplos de Requests/Responses

Defina a URL base do deploy para testar diretamente a versão publicada:

```bash
BASE_URL="https://fiap-tech-challenge-rm-367414.vercel.app"
```

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

Exemplo de item:

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

Scraping (protegido):

```bash
ACCESS_TOKEN="<seu_access_token>"
curl -X POST "$BASE_URL/api/v1/scraping/trigger" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Execução e Deploy

Execução local (resumo):

```bash
python scripts/create_tables.py      # cria tabelas
python scripts/scraping.py           # opcional: popula o banco
uvicorn api.main:app --reload        # inicia a API
```

Deploy na Vercel:

- `vercel.json` já aponta para `api/index.py` (Python serverless)
- Variáveis de ambiente (configure em Settings → Environment Variables):
  - `DATABASE_URL`
  - `JWT_SECRET`
  - `JWT_ALGORITHM` (ex.: HS256)

Passos sugeridos:

```bash
npm i -g vercel
vercel                      # configura o projeto
vercel env add DATABASE_URL
vercel env add JWT_SECRET
vercel env add JWT_ALGORITHM
vercel --prod               # publica em produção
```

### Licença

Uso educacional/acadêmico no escopo do Tech Challenge.
