from flask import Blueprint, render_template, request, jsonify
from app.modules.core.database import db
from app.database.models import Eu2016
from app.services.history_service import get_formatted_history  # Maintains JSON generation for the chart
from datetime import datetime
from backup_db import run_backup

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

print("--- Dashboard module is loading! ---")


@dashboard_bp.route('/view', methods=['GET'])
def view_dashboard():
    # Sends data to the table and renders the page
    records = Eu2016.query.order_by(Eu2016.carimbo.desc()).all()
    return render_template('dashboard.html', history=records)


@dashboard_bp.route('/history', methods=['GET'])
def get_history():
    print("--- /history route accessed! ---")
    data = get_formatted_history()
    return jsonify(data)


@dashboard_bp.route('/add', methods=['POST'])
def add_measurement():
    run_backup()
    new_record = Eu2016(
        carimbo=datetime.now(),
        peso=float(request.form.get('weight')),
        gordura=float(request.form.get('fat')),
        viceral=float(request.form.get('visceral')),
        musculo=float(request.form.get('muscle')) if request.form.get('muscle') else None,
        idade=float(request.form.get('age')) if request.form.get('age') else None,
        basal=float(request.form.get('basal')) if request.form.get('basal') else None
    )
    db.session.add(new_record)
    db.session.commit()
    return render_template('success.html', data=new_record)


@dashboard_bp.route('/edit/<string:timestamp>', methods=['GET', 'POST'])
def edit_measurement(timestamp):
    # Try parsing with microseconds, fallback to standard datetime
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    record = Eu2016.query.filter_by(carimbo=dt).first_or_404()

    if request.method == 'POST':
        run_backup()

        # Safely convert to float, handling potential empty strings
        record.peso = float(request.form.get('weight')) if request.form.get('weight') else None
        record.gordura = float(request.form.get('fat')) if request.form.get('fat') else None
        record.viceral = float(request.form.get('viceral')) if request.form.get('viceral') else None
        record.musculo = float(request.form.get('muscle')) if request.form.get('muscle') else None
        record.idade = float(request.form.get('age')) if request.form.get('age') else None
        record.basal = float(request.form.get('basal')) if request.form.get('basal') else None

        db.session.commit()
        return render_template('success.html', data=record)

    return render_template('edit.html', record=record)

@dashboard_bp.route('/inspect', methods=['GET'])
def inspect_history():
    # Fetch all records in descending order to display in the inspection table
    records = Eu2016.query.order_by(Eu2016.carimbo.desc()).all()
    return render_template('inspect.html', history=records)


@dashboard_bp.route('/delete/<string:timestamp>', methods=['POST'])
def delete_measurement(timestamp):
    # Try parsing with microseconds, fallback to standard datetime
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    record = Eu2016.query.filter_by(carimbo=dt).first_or_404()

    # Run backup before deleting data to prevent permanent loss
    run_backup()

    db.session.delete(record)
    db.session.commit()
    return render_template('success.html', data=record)  # Você pode criar um success_delete ou reutilizar