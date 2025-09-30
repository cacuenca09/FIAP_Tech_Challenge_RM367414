from sqlalchemy.orm import Session
from app.models import Book
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
    query = db.query(Book)
    
    if title and title.strip():
        query = query.filter(Book.titulo.ilike(f"%{title.strip()}%"))
    
    if category and category.strip():
        query = query.filter(Book.categoria.ilike(f"%{category.strip()}%"))
    
    return query.order_by(Book.titulo).all()

def get_categories(db: Session):
    """SELECT DISTINCT categoria FROM books"""
    return [row[0] for row in db.query(Book.categoria).distinct().all()]


def get_overview_stats(db: Session):
        total_books = db.query(func.count(Book.id)).scalar()
        avg_price = db.query(func.avg(Book.preco)).scalar()

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

def get_top_rated_books(db: Session):
    """
    Retorna todos os livros ordenados pelo rating em ordem decrescente
    """
    try:
        return (
            db.query(Book)
            .filter(Book.rating.is_not(None))
            .order_by(Book.rating.desc())
            .all()
        )
    except Exception as e:
        print(f"Erro ao buscar livros com melhor avaliação: {str(e)}")
        return []

def get_books_by_price_range (db: Session):
    """
    Retorna todos os livros ordenados pelo rating em ordem decrescente
    """
    try:
        return (
            db.query(Book)
            .filter(Book.rating.is_not(None))
            .order_by(Book.rating.desc())
            .all()
        )
    except Exception as e:
        print(f"Erro ao buscar livros com melhor avaliação: {str(e)}")
        return []


