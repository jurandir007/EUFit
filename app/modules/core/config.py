import os
from pathlib import Path
from dotenv import load_dotenv

base_path = Path(__file__).resolve().parent.parent.parent.parent
env_file = base_path / "neon.env"

load_dotenv(dotenv_path=env_file)


class Config:
    database_url = os.getenv("DATABASE_URL_Neon")
    sqlalchemy_database_uri = os.getenv("DATABASE_URL_Neon")

    if not database_url:
        print(f"DEBUG: Tentando carregar .env de: {env_file}")
        raise ValueError("A variável de ambiente DATABASE_URL_Neon não foi configurada.")

    SECRET_KEY = os.getenv("SECRET_KEY", "uma-chave-secreta-muito-segura")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    google_client_id = GOOGLE_CLIENT_ID
    google_client_secret = GOOGLE_CLIENT_SECRET

    app_name = 'EUFit'

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_Neon")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


settings = Config()