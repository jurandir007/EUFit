import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Primeiro definimos o caminho base
base_path = Path(__file__).resolve().parent.parent.parent.parent

# 2. Depois carregamos o arquivo específico
load_dotenv(dotenv_path=base_path / "neon.env")

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL_Neon")

    if not DATABASE_URL:
        raise ValueError("A variável de ambiente DATABASE_URL_Neon não foi configurada.")

    SECRET_KEY = os.getenv("SECRET_KEY", "uma-chave-secreta-muito-segura")

# 3. Finalmente, instanciamos a classe para exportar 'settings'
settings = Config()