import os
import sys

# Adiciona a pasta raiz ao sys.path para importar api.main
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Importa a variável app do FastAPI
from api.main import app  # type: ignore
