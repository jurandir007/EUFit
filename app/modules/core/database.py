from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from app.modules.core.config import settings


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
#migrate = Migrate()

def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    #migrate.init_app(app, db)