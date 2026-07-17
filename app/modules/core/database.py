#17/07
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def init_db(app):
    from app.modules.core.config import settings

    # Debug: imprime o valor antes de atribuir
    print(f"DEBUG: SQLALCHEMY_DATABASE_URI sendo definido como: {settings.SQLALCHEMY_DATABASE_URI}")

    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if app.config["SQLALCHEMY_DATABASE_URI"] is None:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI está None. Verifique o arquivo config.py e o carregamento do .env")

    db.init_app(app)