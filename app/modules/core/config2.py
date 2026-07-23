import os
from dotenv import load_dotenv

# Força o carregamento do arquivo específico antes de ler as variáveis
load_dotenv('neon.env')

class Settings:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    SECRET_KEY = os.getenv('SECRET_KEY', 'uma-chave-secreta-qualquer')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL_Neon')
    DATABASE_URL = os.getenv('DATABASE_URL_Neon')
    APP_NAME = 'EUFit'

settings = Settings()