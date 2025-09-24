from database import engine, Base
import models

print("Criando tabelas no banco...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas!")
