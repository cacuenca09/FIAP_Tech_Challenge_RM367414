from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Book(Base):
    __tablename__= "books"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    disponibilidade = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    categoria = Column(String, nullable=False)
    imagem = Column(String, nullable=False)


