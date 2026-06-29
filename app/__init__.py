# app/__init__.py
from flask import Flask
from app.modules.core.database import init_db


def create_app():
    app = Flask(__name__)

    # Inicializa o banco
    init_db(app)

    # O registro do blueprint PRECISA estar aqui dentro
    from app.modules.dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    return app