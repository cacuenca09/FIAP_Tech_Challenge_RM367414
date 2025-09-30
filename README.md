## FIAP - Tech Challenge 1 - Books API

API REST construída com **FastAPI** para coleta (scraping), armazenamento e consulta de livros do site [Books to Scrape](https://books.toscrape.com).
O projeto inclui **autenticação JWT**, endpoints de consulta obrigatórios e opcionais, estatísticas, scraping sob demanda e integração com banco de dados **PostgreSQL**.

Os dados são armazenados em um **PostgreSQL online (Neon)**, e o deploy foi realizado na **Vercel**, utilizando `api/index.py` como entrypoint.

Acessar a API (em deploy público) : `https://fiap-tech-challenge-rm-367414-6sm8.vercel.app/docs#/`

### Objetivo

Este projeto faz parte do **FIAP - Tech Challenge 1** e tem como meta:

* Coletar dados de livros via **web scraping**
* Persistir as informações em um banco **PostgreSQL**
* Disponibilizar uma API para consultas públicas e estatísticas
* Proteger endpoints administrativos com **JWT Authentication**
* Explorar boas práticas de arquitetura e deploy em nuvem (serverless via Vercel)

### Arquitetura

![Diagrama do projeto](./diagrama.svg)

* Scraping (requests + BeautifulSoup) → PostgreSQL (Neon)
* FastAPI + SQLAlchemy → API RESTful
* JWT Authentication → segurança de endpoints
* Vercel → deploy serverless

Estrutura de diretórios:

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

### Tecnologias Utilizadas

* Python 3.13
* FastAPI
* SQLAlchemy
* Pydantic
* PostgreSQL (Neon.tech)
* Requests + BeautifulSoup
* PyJWT
* Uvicorn
* Vercel

### Pré-requisitos

* Python 3.13 (ou versão compatível)
* Banco PostgreSQL acessível (local ou online)

### Instalação e Configuração (Local)

1. Clone o repositório:

```bash
git clone https://github.com/<seu-usuario>/tech-challenge-books-api.git
cd tech-challenge-books-api
```

2. Crie e ative um virtualenv (opcional):

```bash
python3 -m venv venv && source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure a conexão com o banco no `database.py` ou via variável de ambiente.

5. Crie as tabelas:

```bash
python create_tables.py
```

6. (Opcional) Popular o banco com scraping:

```bash
python scraping.py
```

7. Execute localmente:

```bash
uvicorn main:app --reload --port 8000
```

8. Acesse a documentação automática:

* Swagger UI: `https://fiap-tech-challenge-rm-367414-6sm8.vercel.app/docs#/`

### Autenticação

* JWT HS256 com expiração (1h access, 7d refresh)
* Credenciais de teste: `admin` / `secret`
* Fluxo:

  * POST `/api/v1/auth/login` → retorna `access_token` e `refresh_token`
  * POST `/api/v1/auth/refresh` → emite novo `access_token`
  * GET `/api/v1/auth/verify` → valida token (Bearer)

### Documentação das Rotas

Rotas públicas:

* `GET /` → ping raiz
* `GET /api/v1/health` → status API e DB
* `GET /api/v1/books` → lista todos os livros
* `GET /api/v1/books/{book_id}` → detalhes por ID
* `GET /api/v1/books/search?title={t}&category={c}` → busca por título/categoria
* `GET /api/v1/categories` → lista categorias únicas

Rotas opcionais (analíticas):

* `GET /api/v1/books/top-rated` → livros com maior rating
* `GET /api/v1/books/price-range?min={min}&max={max}` → filtra por faixa de preço
* `GET /api/v1/stats/overview` → total, preço médio, distribuição de ratings
* `GET /api/v1/stats/categories` → métricas por categoria

Rotas de autenticação:

* `POST /api/v1/auth/login` → autentica e retorna tokens
* `POST /api/v1/auth/refresh` → renova access token
* `GET /api/v1/auth/verify` → verifica validade do token

Rota protegida (requer Bearer access token):

* `POST /api/v1/scraping/trigger` → dispara scraping (admin)

### Exemplos de Requests/Responses

Login:

```bash
curl -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}'
```

Resposta:

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

Resposta:

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

Resposta:

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

* O projeto já está configurado com `vercel.json`:

  * Builds: `@vercel/python` com `api/index.py`
  * Rotas: todo tráfego direcionado para `api/index.py`
* Variáveis de ambiente requeridas na Vercel:

  * `DATABASE_URL` → ex.: `postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME`
  * `JWT_SECRET` → segredo para assinar tokens
  * `JWT_ALGORITHM` → normalmente `HS256`

Passos para deploy:

```bash
npm i -g vercel
vercel
vercel env add DATABASE_URL
vercel env add JWT_SECRET
vercel env add JWT_ALGORITHM
vercel --prod
```

### Licença

Uso educacional/acadêmico no escopo do Tech Challenge.
