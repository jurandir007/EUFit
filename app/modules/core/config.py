import os
from pathlib import Path
from dotenv import load_dotenv

# Localiza a raiz do projeto (subindo 3 níveis a partir deste arquivo)
# /app/modules/core/config.py -> /app/modules/core -> /app/modules -> /app -> / (raiz)
base_path = Path(__file__).resolve().parent.parent.parent.parent

# Define o caminho do arquivo .env
env_file = base_path / "neon.env"

# Carrega o arquivo explicitamente
load_dotenv(dotenv_path=env_file)

class Config:
    # Agora o os.getenv deve ler as variáveis carregadas pelo load_dotenv
    DATABASE_URL = os.getenv("DATABASE_URL_Neon")

    if not DATABASE_URL:
        # Apenas para debug, vamos imprimir o caminho que ele tentou usar
        print(f"DEBUG: Tentando carregar .env de: {env_file}")
        raise ValueError("A variável de ambiente DATABASE_URL_Neon não foi configurada.")

    SECRET_KEY = os.getenv("SECRET_KEY", "uma-chave-secreta-muito-segura")

settings = Config()