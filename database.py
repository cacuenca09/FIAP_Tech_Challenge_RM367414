from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
#URL de conexão com PostgreSQL
DATABASE_URL = "postgresql+psycopg2://macos@localhost/booksdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()