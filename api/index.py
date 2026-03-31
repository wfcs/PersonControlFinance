import sys
import os

# Adiciona o diretório 'backend' ao path para que o Python encontre o pacote 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
