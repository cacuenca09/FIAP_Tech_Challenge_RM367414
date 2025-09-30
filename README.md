📚 FIAP - Tech Challenge 1 - Books API

API REST construída com FastAPI para coleta (scraping), armazenamento e consulta de livros do site Books to Scrape
.
O projeto inclui autenticação JWT, endpoints de consulta obrigatórios e opcionais, estatísticas, scraping sob demanda e integração com banco de dados PostgreSQL.

Os dados são armazenados em um PostgreSQL online (Neon), e o deploy foi realizado na Vercel, utilizando api/index.py como entrypoint.

🎯 Objetivo

Este projeto faz parte do FIAP - Tech Challenge 1 e tem como meta:

Coletar dados de livros via web scraping.

Persistir as informações em um banco PostgreSQL.

Disponibilizar uma API para consultas públicas e estatísticas.

Proteger endpoints administrativos com JWT Authentication.

Explorar boas práticas de arquitetura e deploy em nuvem (serverless via Vercel).

🏗 Arquitetura
![Diagrama do projeto](./diagrama.svg)

Estrutura de diretórios:

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

🔧 Tecnologias Utilizadas

Python 3.13

FastAPI (framework web moderno)

SQLAlchemy (ORM)

Pydantic (validação de dados)

PostgreSQL (Neon.tech)

Requests + BeautifulSoup (scraping)

JWT (PyJWT) (autenticação)

Uvicorn (servidor ASGI)

Vercel (deploy serverless)

📦 Pré-requisitos

Python 3.13 (ou versão compatível)

Banco PostgreSQL acessível (local ou online)

🚀 Instalação e Configuração (Local)

Clone o repositório:

git clone https://github.com/<seu-usuario>/tech-challenge-books-api.git
cd tech-challenge-books-api


Crie e ative um virtualenv (opcional):

python3 -m venv venv && source venv/bin/activate


Instale as dependências:

pip install -r requirements.txt


Configure a conexão com o banco:

Defina a variável de ambiente DATABASE_URL

Ou edite o database.py para apontar sua URL Postgres

Crie as tabelas:

python create_tables.py


(Opcional) Popular o banco com scraping inicial:

python scraping.py


Execute o servidor local:

uvicorn main:app --reload --port 8000


Acesse a documentação:

Swagger UI → http://localhost:8000/docs

OpenAPI JSON → http://localhost:8000/openapi.json

🔑 Autenticação

Algoritmo: JWT HS256

Expiração: 1h access token, 7d refresh token

Credenciais de teste (embarcadas):

Usuário: admin

Senha: secret

Fluxo:

POST /api/v1/auth/login → retorna tokens

POST /api/v1/auth/refresh → renova access token

GET /api/v1/auth/verify → valida token ativo

📚 Documentação das Rotas

Públicas: health check, listagem de livros, busca, categorias

Analíticas: top rated, price range, estatísticas

Autenticação: login, refresh, verify

Protegidas: trigger de scraping

(detalhes já descritos no seu README, mantidos acima para clareza)

🌐 Deploy na Vercel

Configuração no vercel.json

Entrypoint → api/index.py

Variáveis de ambiente necessárias:

DATABASE_URL

JWT_SECRET

JWT_ALGORITHM

Deploy manual: