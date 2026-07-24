# ./app/__init__.py
from flask import Flask, render_template
from flask_login import LoginManager
from app.modules.core.database import init_db
from app.modules.core.config import settings
from app.modules.auth.handlers import auth_bp
from app.modules.dashboard.routes import dashboard_bp
from app.modules.core.oauth import init_oauth
from app.database.models import User
from dotenv import load_dotenv

load_dotenv('neon.env')

def create_app():
    app = Flask(__name__, template_folder='docs')
    app.config.from_object(settings)

    init_db(app)
    init_oauth(app)  # Inicializa o OAuth aqui

    # Inicialização do Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Rota padrão de redirecionamento para login

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/')
    def index():
        return render_template('index.html', site_name=app.config.get('APP_NAME', 'EUFit'))

    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    return app
