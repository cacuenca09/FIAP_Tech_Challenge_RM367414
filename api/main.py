from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import repositories as repo
from app.schemas import BookSchema
from sqlalchemy import text
from app.models import Book
from typing import Optional, List
from app.schemas import (
    BookSchema,
    FeatureResponse,
    TrainingDataResponse,
    PredictionRequest,
    PredictionResponse
)
import datetime
import logging
import jwt
from pydantic import BaseModel
from scripts.scraping import scrape_books

#Configuracoes JWT
JWT_SECRET = "MEUSEGREDOAQUI"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # 1 hora
JWT_REFRESH_EXP_DELTA_SECONDS = 604800  # 7 dias

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_modelo")

# Credenciais de teste
TEST_USERNAME = "admin"
TEST_PASSWORD = "secret"

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = JWT_EXP_DELTA_SECONDS

class RefreshRequest(BaseModel):
    refresh_token: str

def create_token(username: str, token_type: str = "access") -> str:
    """
    Cria um token JWT (access ou refresh)
    """
    if token_type == "refresh":
        exp_delta = JWT_REFRESH_EXP_DELTA_SECONDS
    else:
        exp_delta = JWT_EXP_DELTA_SECONDS
    
    payload = {
        "username": username,
        "type": token_type,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=exp_delta),
        "iat": datetime.datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    """
    Decodifica e valida um token JWT
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )


security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Valida o token e retorna os dados do usuário
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido. Use um access token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


def admin_required(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verifica se o usuário tem permissões de admin
    """
    return current_user

#Inicio da aplicacao FASTAPI
app = FastAPI(title="Books API")

# Rota raiz para ambientes como Vercel (evita 404 em "/")
@app.get("/")
def root():
    return {
        "message": "API online",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

# Dependência para abrir/fechar sessão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Endpoints de autenticacao
@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Autenticação"])
def login(credentials: LoginRequest):
    """
    Autentica o usuário e retorna tokens de acesso e refresh
    """
    if credentials.username == TEST_USERNAME and credentials.password == TEST_PASSWORD:
        access_token = create_token(credentials.username, "access")
        refresh_token = create_token(credentials.username, "refresh")
        
        logger.info(f"Login bem-sucedido para usuário: {credentials.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    else:
        logger.warning(f"Tentativa de login falhou para usuário: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )


@app.post("/api/v1/auth/refresh", response_model=TokenResponse, tags=["Autenticação"])
def refresh_token_endpoint(refresh_data: RefreshRequest):
    """
    Renova o access token usando um refresh token válido
    """
    try:
        payload = decode_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido. Use um refresh token.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        username = payload.get("username")
        new_access_token = create_token(username, "access")
        
        logger.info(f"Token renovado para usuário: {username}")
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_data.refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao renovar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao renovar token"
        )


@app.get("/api/v1/auth/verify", tags=["Autenticação"])
def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verifica se o token atual é válido
    """
    return {
        "message": "Token válido",
        "username": current_user.get("username"),
        "expires_at": current_user.get("exp")
    }

#rota protegida
@app.post("/api/v1/scraping/trigger", tags=["Admin"])
def trigger_scraping(current_user: dict = Depends(admin_required)):
    """
    Endpoint protegido - Requer autenticação de admin
    """
    logger.info(f"Scraping disparado por: {current_user.get('username')}")
    scrape_books()
    return {
        "message": "Scraping iniciado com sucesso",
        "triggered_by": current_user.get("username"),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# Endpoints específicos (ordem importante para evitar conflitos de rota)
@app.get("/api/v1/books/search", tags=["Obrigatório"])
def search_books_endpoint(
    title: Optional[str] = Query(None, description="Título do livro para busca parcial"),
    category: Optional[str] = Query(None, description="Categoria do livro para busca parcial"),
    db: Session = Depends(get_db)
):
    try:
        if not title and not category:
            raise HTTPException(
                status_code=400, 
                detail="Pelo menos um parâmetro de busca deve ser fornecido (title ou category)"
            )
        
        books = repo.search_books(db, title=title, category=category)
        
        filters_applied = []
        if title:
            filters_applied.append(f"título contém '{title}'")
        if category:
            filters_applied.append(f"categoria contém '{category}'")
        
        filter_message = " e ".join(filters_applied)
        
        if not books:
            return {
                "message": f"Nenhum livro encontrado com os critérios: {filter_message}",
                "data": [],
                "total": 0,
                "filters": {
                    "title": title,
                    "category": category
                }
            }
        
        return {
            "message": f"{len(books)} livro(s) encontrado(s) com os critérios: {filter_message}",
            "data": [
                {
                    "id": book.id,
                    "titulo": book.titulo,
                    "preco": float(book.preco) if book.preco is not None else 0.0,
                    "rating": float(book.rating) if book.rating is not None else 0.0,
                    "categoria": getattr(book, "categoria", None),
                }
                for book in books
            ],
            "total": len(books),
            "filters": {
                "title": title,
                "category": category
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno na busca: {str(e)}")

@app.get("/api/v1/books/top-rated", tags=["Opcionais"])
def get_top_rated_books_endpoint(db: Session = Depends(get_db)):
    try:
        books = repo.get_top_rated_books(db)
        
        if not books:
            return {"message": "Nenhum livro encontrado", "data": []}
        
        return {
            "message": "Livros com melhor avaliação",
            "data": [
                {
                    "id": book.id,
                    "titulo": book.titulo,
                    "preco": float(book.preco) if book.preco is not None else 0.0,
                    "rating": float(book.rating) if book.rating is not None else 0.0,
                    "categoria": getattr(book, "categoria", None),
                }
                for book in books
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/v1/books/price-range", tags=["Opcionais"])
def get_books_by_price_range(
    min_price: float = Query(None, alias="min", description="Preço mínimo"),
    max_price: float = Query(None, alias="max", description="Preço máximo"),
    db: Session = Depends(get_db)
):
    try:
        if min_price is None and max_price is None:
            raise HTTPException(
                status_code=400, 
                detail="Pelo menos um parâmetro deve ser fornecido (min ou max)"
            )
        
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=400,
                detail="O preço mínimo não pode ser maior que o preço máximo"
            )
        
        if (min_price is not None and min_price < 0) or (max_price is not None and max_price < 0):
            raise HTTPException(
                status_code=400,
                detail="Os preços não podem ser negativos"
            )
        
        query = db.query(Book)

        if min_price is not None:
            query = query.filter(Book.preco >= min_price)
        if max_price is not None:
            query = query.filter(Book.preco <= max_price)

        books = query.order_by(Book.preco).all()
        
        if not books:
            return {
                "message": "Nenhum livro encontrado na faixa de preço especificada",
                "data": [],
                "total": 0,
                "filters": {
                    "min_price": min_price,
                    "max_price": max_price
                }
            }
        
        return {
            "message": f"{len(books)} livro(s) encontrado(s) na faixa de preço",
            "data": [
                {
                    "id": book.id,
                    "titulo": book.titulo,
                    "preco": float(book.preco) if book.preco is not None else 0.0,
                    "rating": float(book.rating) if book.rating is not None else 0.0,
                    "categoria": getattr(book, "categoria", None),
                }
                for book in books
            ],
            "total": len(books),
            "filters": {
                "min_price": min_price,
                "max_price": max_price
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/v1/books", response_model=list[BookSchema], tags=["Obrigatório"])
def read_books(db: Session = Depends(get_db)):
    return repo.get_books(db)

@app.get("/api/v1/categories", response_model=list[str], tags=["Obrigatório"])
def list_categories(db: Session = Depends(get_db)):
    categories = repo.get_categories(db)
    if not categories:
        raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada")
    return categories

@app.get("/api/v1/health", tags=["Obrigatório"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

@app.get("/api/v1/stats/overview", tags=["Opcionais"])
def get_overview_stats(db: Session = Depends(get_db)):
    stats = repo.get_overview_stats(db) 
    return stats

@app.get("/api/v1/stats/categories", tags=["Opcionais"])
def get_stats_categories(db: Session = Depends(get_db)):
    stats = repo.get_category_stats(db)
    return stats

@app.get("/api/v1/books/{book_id}", response_model=BookSchema, tags=["Obrigatório"])
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = repo.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


