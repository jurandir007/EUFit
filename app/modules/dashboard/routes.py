#app/modules/dashboard/routes.py
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, make_response, jsonify
from datetime import datetime
from flask_login import login_required, current_user, login_user
from app.database.models import Eu2016, User
from app.modules.core.database import db
from backup_db import run_backup    
from datetime import datetime, timedelta
from app.services.history_service import receber_e_processar_dados
import sys
print("Módulo de models carregado na rota:", sys.modules.get('app.database.models'))

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/view', methods=['GET'])
def view_dashboard():
    """Render the main dashboard ensuring strict data isolation and correct button visibility."""
    is_anonymous = False
    is_dummy_user = False
    
    if current_user.is_authenticated:
        if current_user.id == 3:
            is_dummy_user = True
        elif current_user.name == "Anonymous User" or request.cookies.get('anon_token'):
            is_anonymous = True

    if current_user.is_authenticated:
        records = Eu2016.query.filter_by(fk_user_id=current_user.id).order_by(Eu2016.carimbo.desc()).all()
    else:
        records = []

    return render_template(
        'dashboard.html', 
        history=records, 
        is_anonymous=is_anonymous,
        is_dummy_user=is_dummy_user
    )

@dashboard_bp.route('/inspect', methods=['GET'])
@login_required
def inspect_history():
    """Render inspection page showing records filtered exclusively for the current user."""
    records = Eu2016.query.filter_by(fk_user_id=current_user.id).order_by(Eu2016.carimbo.desc()).all()
    is_dummy_user = (current_user.id == 3)
    return render_template('inspect.html', history=records, current_user=current_user, is_dummy_user=is_dummy_user)

@dashboard_bp.route('/anonymous-login')
def anonymous_login():
    """Handle persistent anonymous identity via cookie and UUID."""
    anon_token = request.cookies.get('anon_token')
    user = None

    if anon_token:
        user = User.query.filter_by(google_id=anon_token).first()

    if not user:
        anon_token = str(uuid.uuid4())
        user = User(
            google_id=anon_token,
            email=f"anon_{anon_token[:8]}@eufit.local",
            name="Anonymous User"
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    
    response = make_response(redirect(url_for('dashboard.view_dashboard')))
    response.set_cookie('anon_token', anon_token, max_age=60*60*24*365)
    
    return response

@dashboard_bp.route('/login-dummy', methods=['POST'])
def login_dummy_user():
    """Log in directly as the fictitious user (ID 3)."""
    dummy_user = User.query.get(3)
    
    if dummy_user:
        login_user(dummy_user)
    
    return redirect(url_for('dashboard.view_dashboard'))

@dashboard_bp.route('/exit-dummy', methods=['POST'])
@login_required
def exit_dummy_user():
    """Switch back from the fictitious user to the original anonymous cookie user."""
    anon_token = request.cookies.get('anon_token')
    user = None

    if anon_token:
        user = User.query.filter_by(google_id=anon_token).first()

    if not user:
        anon_token = str(uuid.uuid4())
        user = User(
            google_id=anon_token,
            email=f"anon_{anon_token[:8]}@eufit.local",
            name="Anonymous User"
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    
    response = make_response(redirect(url_for('dashboard.view_dashboard')))
    response.set_cookie('anon_token', anon_token, max_age=60*60*24*365)
    
    return response

@dashboard_bp.route('/delete-dummy', methods=['POST'])
@login_required
def delete_dummy_data():
    """Delete all records belonging exclusively to the current user."""
    Eu2016.query.filter_by(fk_user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('dashboard.view_dashboard'))



#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

@dashboard_bp.route('/add', methods=['POST'])
@login_required
def add_measurement():
    peso = request.form.get('weight')
    gordura = request.form.get('fat')
    visceral = request.form.get('visceral')
    
    # Captura dos campos opcionais
    muscle = request.form.get('muscle')
    age = request.form.get('age')
    basal = request.form.get('basal')

    if not peso or not gordura or not visceral:
        return "Erro: Peso, Gordura e Visceral são obrigatórios.", 400

    try:
        peso_val = float(peso)
        gordura_val = float(gordura)
        visceral_val = float(visceral)
        
        # Conversão segura (Safe Cast) para os opcionais
        muscle_val = float(muscle) if muscle and muscle.strip() != '' else None
        age_val = float(age) if age and age.strip() != '' else None
        basal_val = float(basal) if basal and basal.strip() != '' else None
        
    except ValueError:
        return "Erro: Os valores numéricos informados são inválidos.", 400

    if peso_val < 100 or peso_val > 10000:
        return "Erro: O peso deve estar entre 100 e 10.000.", 400

    try:
        # Delegação para o serviço unificado com os 6 parâmetros
        receber_e_processar_dados(
            user_id=current_user.id,
            peso=peso_val,
            gordura=gordura_val,
            viceral=visceral_val,
            musculo=muscle_val,
            idade=age_val,
            basal=basal_val
        )
    except Exception as e:
        print(f"Erro no processamento/ML: {e}")
        db.session.rollback()
        return f"Erro interno ao processar predições: {str(e)}", 500

    return redirect(url_for('dashboard.view_dashboard'))
    
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@dashboard_bp.route('/delete', methods=['POST'])
@login_required
def delete_measurement():
    timestamp_str = request.form.get('timestamp')

    if not timestamp_str:
        return "Erro: Timestamp não enviado.", 400

    try:
        dt_object = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        record = Eu2016.query.filter_by(carimbo=dt_object, fk_user_id=current_user.id).first()

        if record:
            run_backup()  
            db.session.delete(record)
            db.session.commit()

    except Exception as e:
        print(f"Erro na deleção: {e}")
        db.session.rollback()

    return redirect(url_for('dashboard.inspect_history'))

@dashboard_bp.route('/edit/<path:timestamp>', methods=['GET', 'POST'])
@login_required
def edit_measurement(timestamp):
    dt_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    record = Eu2016.query.filter_by(carimbo=dt_object, fk_user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        def safe_float(value):
            return float(value) if value and value.strip() != '' else None

        record.peso = safe_float(request.form.get('peso'))
        record.gordura = safe_float(request.form.get('gordura'))
        record.musculo = safe_float(request.form.get('musculo'))
        record.basal = safe_float(request.form.get('basal'))
        record.idade = safe_float(request.form.get('idade'))
        record.viceral = safe_float(request.form.get('viceral'))

        db.session.commit()
        return redirect(url_for('dashboard.inspect_history'))

    return render_template('edit.html', record=record)
    
    
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@dashboard_bp.route('/api/user-metrics-timeline', methods=['GET'])
@login_required
def get_user_metrics_timeline():
    period = request.args.get('period', '30days')
    
    query = Eu2016.query.filter_by(fk_user_id=current_user.id)
    now = datetime.now()
    
    if period == '7days':
        start_date = now - timedelta(days=7)
        query = query.filter(Eu2016.carimbo >= start_date)
    elif period == '30days':
        start_date = now - timedelta(days=30)
        query = query.filter(Eu2016.carimbo >= start_date)
    elif period == 'current_month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(Eu2016.carimbo >= start_date)
    elif period == 'last_year':
        start_date = now - timedelta(days=365)
        query = query.filter(Eu2016.carimbo >= start_date)

    records = query.order_by(Eu2016.carimbo.asc()).all()
    
    timeline_data = {
        "dates": [],
        "weight": [],
        "fat": [],
        "visceral": [],
        "muscle": [],
        "age": [],
        "basal": []
    }
    
    for record in records:
        timeline_data["dates"].append(record.carimbo.strftime('%Y-%m-%d %H:%M:%S'))
        timeline_data["weight"].append(record.peso)
        timeline_data["fat"].append(record.gordura)
        timeline_data["visceral"].append(record.viceral)
        timeline_data["muscle"].append(record.musculo)
        timeline_data["age"].append(record.idade)
        timeline_data["basal"].append(record.basal)
        
    return jsonify(timeline_data)
