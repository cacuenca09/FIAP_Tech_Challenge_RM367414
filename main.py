from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
import repositories as repo
from schemas import BookSchema
from sqlalchemy import text
from models import Book
from typing import Optional, List
from schemas import (
    BookSchema,
    FeatureResponse,
    TrainingDataResponse,
    PredictionRequest,
    PredictionResponse
)

app = FastAPI(title="Books API")

# Dependência para abrir/fechar sessão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints específicos PRIMEIRO (ordem importante para evitar conflitos de rota)

# *** ENDPOINT DE BUSCA JÁ IMPLEMENTADO AQUI ***
#GET /api/v1/books/search?title={title}&category={category}: busca livros por título e/ou categoria.
@app.get("/api/v1/books/search")
def search_books_endpoint(
    title: Optional[str] = Query(None, description="Título do livro para busca parcial"),
    category: Optional[str] = Query(None, description="Categoria do livro para busca parcial"),
    db: Session = Depends(get_db)
):
    """
    Busca livros por título e/ou categoria
    
    - **title**: Busca parcial no título do livro (opcional, case-insensitive)
    - **category**: Busca parcial na categoria do livro (opcional, case-insensitive)  
    - Pelo menos um parâmetro deve ser fornecido
    
    Retorna uma lista de livros que correspondem aos critérios de busca.
    A busca é case-insensitive e permite correspondências parciais.
    """
    try:
        # Validação: pelo menos um parâmetro deve ser fornecido
        if not title and not category:
            raise HTTPException(
                status_code=400, 
                detail="Pelo menos um parâmetro de busca deve ser fornecido (title ou category)"
            )
        
        # Chama a função do repository
        books = repo.search_books(db, title=title, category=category)
        
        # Monta mensagem informativa sobre os filtros aplicados
        filters_applied = []
        if title:
            filters_applied.append(f"título contém '{title}'")
        if category:
            filters_applied.append(f"categoria contém '{category}'")
        
        filter_message = " e ".join(filters_applied)
        
        # Retorna resultado vazio se nenhum livro for encontrado
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
        
        # Retorna os livros encontrados
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

#GET /api/v1/books/top-rated: lista os livros com melhor avaliação (rating mais alto) 
@app.get("/api/v1/books/top-rated")
def get_top_rated_books_endpoint(db: Session = Depends(get_db)):
    """
    Lista os livros com melhor avaliação (rating mais alto)
    
    Retorna os livros ordenados por rating em ordem decrescente.
    Apenas livros com rating válido são considerados.
    """
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

#GET /api/v1/books/price-range?min={min}&max={max}: filtra livros dentro de uma faixa de preço específica.
@app.get("/api/v1/books/price-range")
def get_books_by_price_range(
    min_price: float = Query(None, alias="min", description="Preço mínimo"),
    max_price: float = Query(None, alias="max", description="Preço máximo"),
    db: Session = Depends(get_db)
):
    """
    Filtra livros dentro de uma faixa de preço específica
    
    - **min**: Preço mínimo (opcional, não pode ser negativo)
    - **max**: Preço máximo (opcional, não pode ser negativo nem menor que o mínimo)
    - Pelo menos um parâmetro deve ser fornecido
    
    Retorna livros ordenados por preço crescente dentro da faixa especificada.
    """
    try:
        # Validação: pelo menos um parâmetro deve ser fornecido
        if min_price is None and max_price is None:
            raise HTTPException(
                status_code=400, 
                detail="Pelo menos um parâmetro deve ser fornecido (min ou max)"
            )
        
        # Validação: min não pode ser maior que max
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=400,
                detail="O preço mínimo não pode ser maior que o preço máximo"
            )
        
        # Validação: preços não podem ser negativos
        if (min_price is not None and min_price < 0) or (max_price is not None and max_price < 0):
            raise HTTPException(
                status_code=400,
                detail="Os preços não podem ser negativos"
            )
        
        query = db.query(Book)

        # Aplica filtros de preço usando o campo correto 'preco'
        if min_price is not None:
            query = query.filter(Book.preco >= min_price)
        if max_price is not None:
            query = query.filter(Book.preco <= max_price)

        # Ordena por preço
        books = query.order_by(Book.preco).all()
        
        # Retorna resultado estruturado
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

# GET /api/v1/books  lista todos os livros
@app.get("/api/v1/books", response_model=list[BookSchema])
def read_books(db: Session = Depends(get_db)):
    """
    Lista todos os livros disponíveis no sistema
    
    Retorna a lista completa de livros cadastrados no banco de dados.
    """
    return repo.get_books(db)

#GET /api/v1/categories: lista todas as categorias de livros disponíveis.
@app.get("/api/v1/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db)):
    """
    Lista todas as categorias de livros disponíveis
    
    Retorna uma lista única de todas as categorias existentes no sistema,
    sem duplicatas e ordenadas alfabeticamente.
    """
    categories = repo.get_categories(db)
    if not categories:
        raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada")
    return categories

# GET /api/v1/health: verifica status da API e conectividade com os dados.
@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    """
    Verifica o status da API e conectividade com o banco de dados
    
    Endpoint de health check para monitoramento da aplicação.
    Testa a conexão com o banco de dados e retorna o status geral do sistema.
    """
    try:
        # Testa conexão com o banco usando SQLAlchemy 2.x
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

#Endpoints opcionais
#GET /api/v1/stats/overview: estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings).
@app.get("/api/v1/stats/overview")
def get_overview_stats(db: Session = Depends(get_db)):
    """
    Estatísticas gerais da coleção de livros
    
    Retorna informações agregadas como:
    - Total de livros no sistema
    - Preço médio dos livros
    - Distribuição de ratings
    - Outras métricas relevantes da coleção
    """
    stats = repo.get_overview_stats(db) 
    return stats

#GET /api/v1/stats/categories: estatiscas detalhadas por categoria (quantidade de livros, precos por categoria)
@app.get("/api/v1/stats/categories")
def get_stats_categories(db: Session = Depends(get_db)):
    """
    Estatísticas detalhadas por categoria
    
    Retorna análises por categoria incluindo:
    - Quantidade de livros por categoria
    - Preço médio por categoria
    - Rating médio por categoria
    - Outras métricas segmentadas por categoria
    """
    stats = repo.get_category_stats(db)
    return stats

# Endpoints com parâmetros POR ÚLTIMO (para evitar conflitos de rota)

# GET /api/v1/books/{id}  retorna um livro específico
@app.get("/api/v1/books/{book_id}", response_model=BookSchema)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """
    Retorna um livro específico pelo ID
    
    - **book_id**: ID único do livro no sistema
    
    Retorna todos os detalhes do livro solicitado ou erro 404 se não encontrado.
    """
    book = repo.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

#Pipelines de ML
# GET /api/v1/ml/features
@app.get("/api/v1/ml/features", response_model=List[FeatureResponse])
def get_features(db: Session = Depends(get_db)):
    """
    Retorna dados formatados apenas para features de modelos ML
    (id, preco, rating).
    """
    books = db.query(Book).all()
    return [
        FeatureResponse(
            id=b.id,
            preco=float(b.preco or 0.0),
            rating=float(b.rating or 0.0)
        )
        for b in books
    ]


# GET /api/v1/ml/training-data
@app.get("/api/v1/ml/training-data", response_model=List[TrainingDataResponse])
def get_training_data(db: Session = Depends(get_db)):
    """
    Retorna dataset completo para treinamento de modelos ML.
    """
    books = db.query(Book).all()
    return [
        TrainingDataResponse(
            id=b.id,
            titulo=b.titulo,
            preco=float(b.preco or 0.0),
            rating=float(b.rating or 0.0),
            categoria=getattr(b, "categoria", None)
        )
        for b in books
    ]


# POST /api/v1/ml/predictions
@app.post("/api/v1/ml/predictions", response_model=PredictionResponse)
def predict(data: PredictionRequest):
    """
    Recebe features e retorna uma predição.
    (Mock: soma os valores das features).
    """
    prediction = sum(data.features.values())
    return {"prediction": prediction}