from sqlalchemy.orm import Session
from models import Book
from sqlalchemy import func

def get_books(db: Session):
    """Retorna todos os livros da base"""
    return db.query(Book).all()

def get_book_by_id(db: Session, book_id: int):
    """Retorna um livro específico pelo ID"""
    return db.query(Book).filter(Book.id == book_id).first()

def search_books(db: Session, title: str = None, category: str = None):
    """
    Busca livros por título e/ou categoria
    
    Args:
        db: Sessão do banco de dados
        title: Título do livro (busca parcial/like)
        category: Categoria do livro (busca exata ou parcial)
    
    Returns:
        Lista de livros que atendem aos critérios
    """
    query = db.query(Book)  # Substitua 'Book' pelo nome do seu modelo
    
    # Aplica filtro por título se fornecido
    if title and title.strip():
        query = query.filter(Book.titulo.ilike(f"%{title.strip()}%"))
    
    # Aplica filtro por categoria se fornecido  
    if category and category.strip():
        query = query.filter(Book.categoria.ilike(f"%{category.strip()}%"))
    
    # Ordena por título para resultados consistentes
    return query.order_by(Book.titulo).all()

def get_categories(db: Session):
    """SELECT DISTINCT categoria FROM books"""
    return [row[0] for row in db.query(Book.categoria).distinct().all()]


#Endpoints opcionais
#GET /api/v1/stats/overview: estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings).

def get_overview_stats(db: Session):
        total_books = db.query(func.count(Book.id)).scalar()
        avg_price = db.query(func.avg(Book.preco)).scalar()

        # Distribuição de ratings: retorna lista de tuplas [(rating, count), ...]
        rating_distribution = (
            db.query(Book.rating, func.count(Book.rating))
            .group_by(Book.rating)
            .all()
        )

        return {
            "total_books": total_books or 0,
            "avg_price": float(avg_price) if avg_price is not None else 0.0,
            "rating_distribution": {
                str(rating): count for rating, count in rating_distribution
            },
        }

#GET /api/v1/stats/categories: estatiscas detalhadas por categoria (quantidade de livros, precos por categoria)
def get_category_stats(db: Session):
    results = (
        db.query(
            Book.categoria.label("categoria"),
            func.count(Book.id).label("total_books"),
            func.avg(Book.preco).label("avg_price"),
            func.min(Book.preco).label("min_price"),
            func.max(Book.preco).label("max_price"),
        )
        .group_by(Book.categoria)
        .all()
    )

    stats = []
    for row in results:
        stats.append({
            "categoria": row.categoria,
            "total_books": row.total_books,
            "avg_price": float(row.avg_price) if row.avg_price else 0.0,
            "min_price": float(row.min_price) if row.min_price else 0.0,
            "max_price": float(row.max_price) if row.max_price else 0.0,
        })

    return stats

#GET /api/v1/books/top-rated: lista os livros com melhor avaliação (rating mais alto)
def get_top_rated_books(db: Session):
    """
    Retorna todos os livros ordenados pelo rating em ordem decrescente
    """
    try:
        return (
            db.query(Book)
            .filter(Book.rating.is_not(None))  # Filtra apenas livros com rating
            .order_by(Book.rating.desc())
            .all()
        )
    except Exception as e:
        print(f"Erro ao buscar livros com melhor avaliação: {str(e)}")
        return []

#GET /api/v1/books/price-range?min={min}&max={max}: filtra livros dentro de uma faixa de preço específica.
def get_books_by_price_range (db: Session):
    """
    Retorna todos os livros ordenados pelo rating em ordem decrescente
    """
    try:
        return (
            db.query(Book)
            .filter(Book.rating.is_not(None))  # Filtra apenas livros com rating
            .order_by(Book.rating.desc())
            .all()
        )
    except Exception as e:
        print(f"Erro ao buscar livros com melhor avaliação: {str(e)}")
        return []

#