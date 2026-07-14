from flask import Blueprint, render_template, request, redirect, url_for
from app.database.models import Eu2016
from app.modules.core.database import db
from flask import request, redirect, url_for, flash
from datetime import datetime # Adicione este import no topo do arquivo


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/view', methods=['GET'])
def view_dashboard():
    records = Eu2016.query.order_by(Eu2016.carimbo.desc()).all()
    return render_template('dashboard.html', history=records)

# Rota para carregar a página de inspeção (listagem completa)
@dashboard_bp.route('/inspect', methods=['GET'])
def inspect_history():
    records = Eu2016.query.order_by(Eu2016.carimbo.desc()).all()
    return render_template('inspect.html', history=records)


@dashboard_bp.route('/delete', methods=['POST'])
def delete_measurement():
    timestamp_str = request.form.get('timestamp')

    if not timestamp_str:
        return "Erro: Timestamp não enviado.", 400

    try:
        # Converte a string exata recebida do formulário
        dt_object = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')

        # Busca no banco usando o objeto datetime convertido
        record = Eu2016.query.filter_by(carimbo=dt_object).first()

        if record:
            db.session.delete(record)
            db.session.commit()

    except Exception as e:
        print(f"Erro na deleção: {e}")
        db.session.rollback()

    return redirect(url_for('dashboard.inspect_history'))


@dashboard_bp.route('/add', methods=['POST'])
def add_measurement():
    # 1. Coleta dos dados do formulário
    peso = request.form.get('weight')
    gordura = request.form.get('fat')
    visceral = request.form.get('visceral')

    # 2. Validação de campos obrigatórios
    if not peso or not gordura or not visceral:
        return "Erro: Peso, Gordura e Visceral são obrigatórios.", 400

    # 3. Conversão e Validação Numérica
    try:
        peso_val = float(peso)
        gordura_val = float(gordura)
        visceral_val = float(visceral)
    except ValueError:
        return "Erro: Os valores numéricos são inválidos.", 400

    # 4. Validação do filtro de peso (100 a 10.000)
    if peso_val < 100 or peso_val > 10000:
        return "Erro: O peso deve estar entre 100 e 10.000.", 400

    # 5. Persistência dos dados com o carimbo gerado automaticamente
    new_record = Eu2016(
        carimbo=datetime.now(),  # Resolvendo o erro de NotNullViolation
        peso=peso_val,
        gordura=gordura_val,
        viceral=visceral_val,
        musculo=request.form.get('muscle') or None,
        idade=request.form.get('age') or None,
        basal=request.form.get('basal') or None
    )

    db.session.add(new_record)
    db.session.commit()

    return redirect(url_for('dashboard.view_dashboard'))


# Mantenha o nome da função igual ao que o seu edit.html espera
@dashboard_bp.route('/edit/<path:timestamp>', methods=['GET', 'POST'])
def edit_measurement(timestamp):
    dt_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    record = Eu2016.query.filter_by(carimbo=dt_object).first_or_404()

    if request.method == 'POST':
        # Função auxiliar para converter valores ou retornar None se vazio
        def safe_float(value):
            return float(value) if value and value.strip() != '' else None

        # Atualiza os campos com segurança
        record.peso = safe_float(request.form.get('peso'))
        record.gordura = safe_float(request.form.get('gordura'))
        record.musculo = safe_float(request.form.get('musculo'))
        record.basal = safe_float(request.form.get('basal'))
        record.idade = safe_float(request.form.get('idade'))
        record.viceral = safe_float(request.form.get('viceral'))

        # Salva no banco
        db.session.commit()

        return redirect(url_for('dashboard.inspect_history'))

    return render_template('edit.html', record=record)