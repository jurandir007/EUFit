"""
EUFit - Application Configuration Module
=======================================
This module handles all configuration settings for the EUFit application,
including loading credentials from secure locations outside the project.

Credentials are stored in:
    - /opt/Keys/Google/credentials.json  (Google OAuth 2.0)
    - /opt/Keys/Neon/Neon.txt            (Neon Database + Secret Key)
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


# =============================================================================
# CONSTANTS - SECURE PATHS
# =============================================================================

# Google OAuth 2.0 credentials (JSON format)
GOOGLE_CREDENTIALS_PATH = "/opt/Keys/Google/credentials.json"

# Neon Database credentials (TXT format - as you preferred)
NEON_CREDENTIALS_PATH = "/opt/Keys/Neon/Neon.txt"


# =============================================================================
# LOAD FUNCTIONS
# =============================================================================

def load_google_credentials():
    """Load Google OAuth 2.0 credentials from the secure JSON file."""
    if os.path.exists(GOOGLE_CREDENTIALS_PATH):
        try:
            with open(GOOGLE_CREDENTIALS_PATH, 'r') as f:
                data = json.load(f)
                creds = data.get('web', data.get('installed', {}))
                client_id = creds.get('client_id')
                client_secret = creds.get('client_secret')
                if client_id and client_secret:
                    print(f"✅ Google credentials loaded from: {GOOGLE_CREDENTIALS_PATH}")
                    return client_id, client_secret
        except Exception as e:
            print(f"⚠️ Error reading Google credentials: {e}")
    
    print("⚠️ Using Google credentials from .env as fallback")
    return None, None


def load_neon_credentials():
    """Load Neon Database credentials from the secure .txt file."""
    if os.path.exists(NEON_CREDENTIALS_PATH):
        try:
            load_dotenv(dotenv_path=NEON_CREDENTIALS_PATH, override=True)
            database_url = os.getenv("DATABASE_URL_Neon")
            secret_key = os.getenv("SECRET_KEY")
            if database_url:
                print(f"✅ Neon credentials loaded from: {NEON_CREDENTIALS_PATH}")
                return database_url, secret_key
        except Exception as e:
            print(f"⚠️ Error reading Neon credentials: {e}")
    
    print("⚠️ Using Neon credentials from local .env as fallback")
    return None, None


def load_local_env_fallback():
    """Load credentials from the local neon.env file as a fallback."""
    base_path = Path(__file__).resolve().parent.parent.parent.parent
    env_file = base_path / "neon.env"
    
    if env_file.exists():
        try:
            load_dotenv(dotenv_path=env_file, override=True)
            database_url = os.getenv("DATABASE_URL_Neon")
            secret_key = os.getenv("SECRET_KEY")
            if database_url:
                print(f"⚠️ Using fallback credentials from: {env_file}")
                return database_url, secret_key
        except Exception as e:
            print(f"⚠️ Error reading local .env: {e}")
    
    return None, None


# =============================================================================
# CONFIGURATION CLASS
# =============================================================================

class Config:
    """
    Main configuration class for the EUFit application.
    
    Configuration hierarchy:
        1. /opt/Keys/Neon/Neon.txt         (primary - Neon credentials)
        2. /opt/Keys/Google/credentials.json (primary - Google credentials)
        3. neon.env (local fallback)
        4. Environment variables (fallback)
    """
    
    # Google OAuth 2.0
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET = load_google_credentials()
    if not GOOGLE_CLIENT_ID:
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    
    google_client_id = GOOGLE_CLIENT_ID
    google_client_secret = GOOGLE_CLIENT_SECRET
    
    # Neon Database
    database_url, secret_key = load_neon_credentials()
    if not database_url:
        database_url, secret_key = load_local_env_fallback()
    
    DATABASE_URL_Neon = database_url
    SQLALCHEMY_DATABASE_URI = database_url
    
    if not database_url:
        raise ValueError(
            "❌ DATABASE_URL_Neon is not configured!\n"
            "Please ensure credentials are set in:\n"
            f"  - {NEON_CREDENTIALS_PATH}\n"
            "  - or neon.env (local fallback)"
        )
    
    SECRET_KEY = secret_key or os.getenv("SECRET_KEY", "uma-chave-secreta-muito-segura")
    app_name = 'EUFit'
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


settings = Config()


if __name__ == "__main__":
    """Quick test to verify configuration is loading correctly."""
    print("\n" + "=" * 60)
    print("EUFit Configuration Test")
    print("=" * 60)
    print(f"✅ Google Client ID loaded: {bool(settings.GOOGLE_CLIENT_ID)}")
    print(f"✅ Google Client Secret loaded: {bool(settings.GOOGLE_CLIENT_SECRET)}")
    print(f"✅ Database URL loaded: {bool(settings.DATABASE_URL_Neon)}")
    print(f"✅ SECRET_KEY loaded: {bool(settings.SECRET_KEY)}")
    print(f"✅ App Name: {settings.app_name}")
    print("=" * 60)
