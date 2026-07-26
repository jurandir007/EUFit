# ./app/modules/dashboard/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from flask_login import login_required, current_user
from app.database.models import Eu2016
from app.modules.core.database import db
from backup_db import run_backup

dashboard_bp = Blueprint('dashboard', __name__)

# Rota pública para visualização geral (sem exigir login)
@dashboard_bp.route('/view', methods=['GET'])
def view_dashboard():
    """Render the main dashboard without requiring authentication."""
    records = Eu2016.query.order_by(Eu2016.carimbo.desc()).all()
    return render_template('dashboard.html', history=records)

# Rota de inspeção protegida (exibe apenas os dados do usuário logado)
@dashboard_bp.route('/inspect', methods=['GET'])
def inspect_history():
    """Render the inspection page showing the 30 oldest records for user ID 1."""
    records = Eu2016.query.filter_by(fk_user_id=1).order_by(Eu2016.carimbo.asc()).limit(30).all()
    return render_template('inspect.html', history=records)

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

@dashboard_bp.route('/add', methods=['POST'])
@login_required
def add_measurement():
    peso = request.form.get('weight')
    gordura = request.form.get('fat')
    visceral = request.form.get('visceral')

    if not peso or not gordura or not visceral:
        return "Erro: Peso, Gordura e Visceral são obrigatórios.", 400

    try:
        peso_val = float(peso)
        gordura_val = float(gordura)
        visceral_val = float(visceral)
    except ValueError:
        return "Erro: Os valores numéricos são inválidos.", 400

    if peso_val < 100 or peso_val > 10000:
        return "Erro: O peso deve estar entre 100 e 10.000.", 400

    new_record = Eu2016(
        carimbo=datetime.now(),
        peso=peso_val,
        gordura=gordura_val,
        viceral=visceral_val,
        musculo=request.form.get('muscle') or None,
        idade=request.form.get('age') or None,
        basal=request.form.get('basal') or None,
        fk_user_id=current_user.id
    )

    db.session.add(new_record)
    db.session.commit()

    return redirect(url_for('dashboard.view_dashboard'))
