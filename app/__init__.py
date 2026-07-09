from flask import Flask, render_template
from app.modules.core.database import init_db
from app.modules.core.config import settings


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    init_db(app)

    @app.route('/')
    def index():
        return render_template('index.html', site_name=app.config.get('APP_NAME', 'EUFit'))

    # Importação e registo do Blueprint (sem artimanhas)
    from app.modules.dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    return app