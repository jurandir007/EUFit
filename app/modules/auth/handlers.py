# ./app/modules/auth/handlers.py
#https://chat.deepseek.com/share/s8sv6ye74v4v7m3j2x
from flask import Blueprint, url_for, session, redirect, flash
from flask_login import login_user, logout_user # Importações necessárias
from app.modules.core.oauth import oauth
from app.database.models import db, User
import uuid
from flask import make_response, request, redirect, url_for
from flask_login import login_user
from app.database.models import User
from app.modules.core.database import db

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
    
    
@auth_bp.route('/anonymous-login')
def anonymous_login():
    """
    Check for an existing anonymous cookie token. If it doesn't exist,
    generate a unique UUID, create a new anonymous user profile, and save the cookie.
    If it exists, log in the corresponding user.
    """
    anon_token = request.cookies.get('anon_token')
    user = None

    if anon_token:
        user = User.query.filter_by(google_id=anon_token).first()

    if not user:
        anon_token = str(uuid.uuid4())
        
        user = User(
            google_id=anon_token,
            email=f"anon_{anon_token[:8]}@eufit.local",
            name="Anonymous"
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    
    # Corrected endpoint name from 'dashboard.view' to 'dashboard.view_dashboard'
    response = make_response(redirect(url_for('dashboard.view_dashboard')))
    response.set_cookie('anon_token', anon_token, max_age=60*60*24*365)
    
    return response
