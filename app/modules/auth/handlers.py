# ./app/modules/auth/handlers.py
from flask import Blueprint, url_for, session, redirect, flash
from flask_login import login_user, logout_user # Importações necessárias
from app.modules.core.oauth import oauth
from app.database.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('auth.authorize', _external=True)
    # Adiciona prompt='select_account' para obrigar o Google a exibir a tela de escolha de usuários
    return google.authorize_redirect(redirect_uri, prompt='select_account')


@auth_bp.route('/callback')
def authorize():
    google = oauth.create_client('google')
    # O redirect_uri deve ser idêntico ao configurado no Google Cloud Console
    token = google.authorize_access_token()
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

    # Registra formalmente a sessão do usuário no Flask-Login
    login_user(user)

    session['user'] = user_info
    return redirect(url_for('dashboard.view_dashboard'))


@auth_bp.route('/logout')
def logout():
    # Encerra a sessão no gerenciador do Flask-Login
    logout_user()
    
    # Remove os dados da sessão nativa do Flask
    session.pop('user', None)
    
    # Adiciona uma mensagem flash de confirmação
    flash('Você saiu da sua conta com sucesso.', 'info')
    
    # Redireciona para a página inicial (ou tela de login)
    return redirect('/')
