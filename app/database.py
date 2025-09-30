import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = (
    "postgresql+psycopg2://neondb_owner:npg_AvnYgKX0MaJ3"
    "@ep-dry-waterfall-ac9f1qb7-pooler.sa-east-1.aws.neon.tech/neondb"
    "?sslmode=require")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


