import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# A Vercel precisa encontrar uma variável chamada `app`
try:
    # Se existir módulo em api/main.py
    from api.main import app as app  # type: ignore
except Exception:
    # Fallback para app/main.py
    from app.main import app as app  # type: ignore
