from flask import Blueprint, url_for, session, redirect
from app.modules.core.oauth import oauth
from app.database.models import db, User

# 1. Definição do Blueprint primeiro
auth_bp = Blueprint('auth', __name__)

# 2. Rotas depois
@auth_bp.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('auth.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/callback')
def authorize():
    google = oauth.create_client('google')
    # Ajustamos para manter a consistência com o que o Google espera
    redirect_uri = url_for('auth.authorize', _external=True)
    token = google.authorize_access_token()

    # Em vez de passar apenas o token, tente passar o 'id_token' extraído do dicionário token:
    # user_info = google.parse_id_token(token, nonce=google.server_metadata.get('jwks_uri'))
    # Tente capturar o nonce diretamente do token se existir, ou passe uma string vazia se permitido
    # user_info = google.parse_id_token(token, token.get('nonce', None))
    # user_info = google.parse_id_token(token, nonce=None)
    user_info = google.parse_id_token(token, None)

    user = User.query.filter_by(google_id=user_info['sub']).first()
    if not user:
        user = User(
            google_id=user_info['sub'],
            email=user_info['email'],
            name=user_info['name']
        )
        db.session.add(user)
        db.session.commit()

    session['user'] = user_info
    return redirect(url_for('dashboard.view_dashboard'))


@auth_bp.route('/logout')
def logout():
    # Remove os dados do usuário da sessão atual
    session.pop('user', None)
    # Redireciona para a página inicial
    return redirect('/')