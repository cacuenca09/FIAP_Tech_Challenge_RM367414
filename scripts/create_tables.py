from app.database import engine, Base
import app.models  # noqa: F401 - garante carga dos modelos

print("Criando tabelas no banco...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas!")


