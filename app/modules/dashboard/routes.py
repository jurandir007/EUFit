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
from app.ml.m_average import calculate_moving_average
from app.ml.TLR import calculate_trend_line

#Vape
from app.database.models import RecordVape
from app.services.vape_service import create_vape_record, delete_vape_record, update_vape_record


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
    
   
    
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@dashboard_bp.route('/api/user-metrics-timeline', methods=['GET'])
@login_required
def get_user_metrics_timeline():
    period = request.args.get('period', '30days')
    now = datetime.now()
    
    # 1. VALIDATION FOR 3 MONTHS / 40 RECORDS
    three_months_ago = now - timedelta(days=90)
    recent_records_count = Eu2016.query.filter_by(fk_user_id=current_user.id).filter(Eu2016.carimbo >= three_months_ago).count()
    
    sufficient_data = recent_records_count >= 40
    
    # 2. STANDARD USER FILTER
    query = Eu2016.query.filter_by(fk_user_id=current_user.id)
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
    
    # 3. JSON STRUCTURE
    timeline_data = {
        "sufficient_data": sufficient_data,
        "dates": [], "weight": [], "fat": [], "visceral": [], "muscle": [], "age": [], "basal": [],
        "ma_weight": [], "ma_fat": [], "ma_visceral": [], "ma_muscle": [], "ma_age": [], "ma_basal": [],
        "tlr_weight": [], "tlr_fat": [], "tlr_visceral": [], "tlr_muscle": [], "tlr_age": [], "tlr_basal": []
    }
    
    raw_dates = []

    # 4. BASIC DATA EXTRACTION
    for record in records:
        timeline_data["dates"].append(record.carimbo.strftime('%Y-%m-%d %H:%M:%S'))
        raw_dates.append(record.carimbo) 
        
        timeline_data["weight"].append(record.peso)
        timeline_data["fat"].append(record.gordura)
        timeline_data["visceral"].append(record.viceral)
        timeline_data["muscle"].append(record.musculo)
        timeline_data["age"].append(record.idade)
        timeline_data["basal"].append(record.basal)
        
    # 5. CALCULATION IF THERE IS SUFFICIENT DATA
    if sufficient_data and len(records) > 0:
        timeline_data["ma_weight"] = calculate_moving_average(timeline_data["weight"])
        timeline_data["ma_fat"] = calculate_moving_average(timeline_data["fat"])
        timeline_data["ma_visceral"] = calculate_moving_average(timeline_data["visceral"])
        timeline_data["ma_muscle"] = calculate_moving_average(timeline_data["muscle"])
        timeline_data["ma_age"] = calculate_moving_average(timeline_data["age"])
        timeline_data["ma_basal"] = calculate_moving_average(timeline_data["basal"])

        timeline_data["tlr_weight"] = calculate_trend_line(raw_dates, timeline_data["weight"])
        timeline_data["tlr_fat"] = calculate_trend_line(raw_dates, timeline_data["fat"])
        timeline_data["tlr_visceral"] = calculate_trend_line(raw_dates, timeline_data["visceral"])
        timeline_data["tlr_muscle"] = calculate_trend_line(raw_dates, timeline_data["muscle"])
        timeline_data["tlr_age"] = calculate_trend_line(raw_dates, timeline_data["age"])
        timeline_data["tlr_basal"] = calculate_trend_line(raw_dates, timeline_data["basal"])

    return jsonify(timeline_data)
    
    
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# VAPE TRACKING ROUTES
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

@dashboard_bp.route('/add-vape', methods=['POST'])
@login_required
def add_vape_measurement():
    puff_count = request.form.get('puff_count')

    if not puff_count:
        return "Error: Puff count is required.", 400

    try:
        puff_val = int(puff_count)
        if puff_val < 0 or puff_val > 5000:
            return "Error: Puff count must be between 0 and 5000.", 400
            
        create_vape_record(user_id=current_user.id, puff_count=puff_val)
    except ValueError:
        return "Error: Invalid numeric value.", 400
    except Exception as e:
        print(f"Error saving vape record: {e}")
        return "Internal server error.", 500

    return redirect(url_for('dashboard.view_dashboard'))

@dashboard_bp.route('/delete-vape', methods=['POST'])
@login_required
def delete_vape_measurement():
    record_id = request.form.get('record_id')

    if not record_id:
        return "Error: Record ID is required.", 400

    try:
        delete_vape_record(record_id=int(record_id), user_id=current_user.id)
    except Exception as e:
        print(f"Error deleting vape record: {e}")

    return redirect(url_for('dashboard.inspect_history'))

@dashboard_bp.route('/edit-vape/<int:record_id>', methods=['POST'])
@login_required
def edit_vape_measurement(record_id):
    puff_count = request.form.get('puff_count')
    
    if puff_count:
        try:
            update_vape_record(record_id=record_id, user_id=current_user.id, puff_count=int(puff_count))
        except Exception as e:
            print(f"Error updating vape record: {e}")

    return redirect(url_for('dashboard.inspect_history'))

@dashboard_bp.route('/api/vape-metrics-timeline', methods=['GET'])
@login_required
def get_vape_metrics_timeline():
    period = request.args.get('period', '30days')
    now = datetime.now()
    
    query = RecordVape.query.filter_by(user_id=current_user.id)
    
    if period == '7days':
        start_date = now - timedelta(days=7)
        query = query.filter(RecordVape.recorded_at >= start_date)
    elif period == '30days':
        start_date = now - timedelta(days=30)
        query = query.filter(RecordVape.recorded_at >= start_date)
    elif period == 'current_month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(RecordVape.recorded_at >= start_date)
    elif period == 'last_year':
        start_date = now - timedelta(days=365)
        query = query.filter(RecordVape.recorded_at >= start_date)

    records = query.order_by(RecordVape.recorded_at.asc()).all()
    
    timeline_data = {
        "dates": [],
        "puffs": [],
        "ma_puffs": []
    }
    
    for record in records:
        timeline_data["dates"].append(record.recorded_at.strftime('%Y-%m-%d %H:%M:%S'))
        timeline_data["puffs"].append(record.puff_count)
        
    if len(records) > 0:
        timeline_data["ma_puffs"] = calculate_moving_average(timeline_data["puffs"])

    return jsonify(timeline_data)
    
    
    
@dashboard_bp.route('/vape-dashboard', methods=['GET'])
@login_required
def view_vape_dashboard():
    return render_template('vape_dashboard.html')
    
    
    
@dashboard_bp.route('/inspect-vape', methods=['GET'])
@login_required
def inspect_vape_history():
    records = RecordVape.query.filter_by(user_id=current_user.id).order_by(RecordVape.recorded_at.desc()).all()
    is_dummy_user = (current_user.id == 3)
    return render_template('vape_inspect.html', history=records, current_user=current_user, is_dummy_user=is_dummy_user)

@dashboard_bp.route('/edit-vape-page/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_vape_page(record_id):
    record = RecordVape.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        puff_count = request.form.get('puff_count')
        if puff_count:
            try:
                record.puff_count = int(puff_count)
                db.session.commit()
                return redirect(url_for('dashboard.inspect_vape_history'))
            except ValueError:
                return "Error: Invalid numeric value.", 400

    return render_template('vape_edit.html', record=record)
    
    
    
@dashboard_bp.route('/api/vape/consumo-diario-previsao')
@login_required
def get_vape_daily_avg_with_forecast():
    """
    Retorna média diária + previsões para 30, 90 e 120 dias
    - Média atual: soma dos últimos 30 dias / 30
    - Previsões: regressão linear com TODOS os dados históricos
    """
    from datetime import datetime, timedelta
    from sklearn.linear_model import LinearRegression
    import numpy as np
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    user_id = current_user.id
    period = request.args.get('period', '30days')
    
    # ==========================================
    # 1. BUSCAR TODOS OS DADOS HISTÓRICOS (para o ML)
    # ==========================================
    all_records = RecordVape.query.filter_by(user_id=user_id)\
        .order_by(RecordVape.recorded_at.asc()).all()
    
    logger.info(f"📊 Total de registros históricos: {len(all_records)}")
    
    if len(all_records) < 2:
        return jsonify({
            'error': 'Sem dados históricos suficientes para previsão',
            'current_avg': 0,
            'forecast': {},
            'forecast_dates': {}
        }), 200
    
    # ==========================================
    # 2. CALCULAR MÉDIAS DIÁRIAS REAIS (TODOS OS DADOS)
    # Fórmula: média = puffs / dias_desde_ultimo_registro
    # USANDO REGISTROS INDIVIDUAIS (COM HORAS)
    # ==========================================
    
    daily_avg_real = []
    dates_for_chart = []
    
    for i, record in enumerate(all_records):
        if i == 0:
            # Primeiro registro: ignoramos (não temos referência anterior)
            continue
        else:
            date_obj = record.recorded_at
            total_puffs = record.puff_count
            
            # Calcular gap REAL em dias (com horas!)
            prev_record = all_records[i-1]
            time_diff = (date_obj - prev_record.recorded_at).total_seconds()
            days_diff = time_diff / (24 * 3600)
            
            if days_diff < 0.0001:
                days_diff = 0.0001
            
            daily_avg = total_puffs / days_diff
            daily_avg_real.append(round(daily_avg, 2))
            dates_for_chart.append(date_obj.strftime('%Y-%m-%d %H:%M'))
            
            logger.info(f"📅 {date_obj.strftime('%Y-%m-%d %H:%M')}: {total_puffs} puffs em {days_diff:.4f} dias → média {daily_avg:.2f}/dia")
    # ==========================================
    # 3. MÉDIA ATUAL (APENAS ÚLTIMOS 30 DIAS)
    # ==========================================
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    records_30dias = RecordVape.query.filter_by(user_id=user_id)\
        .filter(RecordVape.recorded_at >= thirty_days_ago).all()
    
    if records_30dias:
        total_puffs_30dias = sum(r.puff_count for r in records_30dias)
        current_avg = round(total_puffs_30dias / 30, 2)
        logger.info(f"📊 Média atual (30 dias): {total_puffs_30dias} / 30 = {current_avg:.2f}/dia")
    else:
        # Fallback: usar o último valor do histórico
        current_avg = daily_avg_real[-1] if daily_avg_real else 0
        logger.info(f"📊 Média atual (fallback): {current_avg}")
    
    # ==========================================
    # 4. PREVISÕES COM ML (USANDO DATAS REAIS)
    # ==========================================
    forecast_results = {}
    forecast_dates = {}
    
    logger.info("🧮 Treinando modelo de regressão linear com datas reais...")
    
    # ==========================================
    # 4. PREVISÕES COM ML (USANDO DATAS REAIS + SUAVIZAÇÃO)
    # ==========================================
    forecast_results = {}
    forecast_dates = {}
    
    logger.info("🧮 Treinando modelo de regressão linear com datas reais...")
    
    # Pegar o primeiro registro como referência (timestamp 0)
    first_record = all_records[0]
    first_date = first_record.recorded_at
    
    # Construir X e Y brutos
    X = []
    y_raw = []
    
    for i, record in enumerate(all_records):
        if i == 0:
            continue
        else:
            # X = data real em dias desde o primeiro registro
            time_diff = (record.recorded_at - first_date).total_seconds()
            days_from_start = time_diff / (24 * 3600)
            X.append(round(days_from_start, 4))
            
            # Y = média real (consumo / gap)
            prev_record = all_records[i-1]
            gap = (record.recorded_at - prev_record.recorded_at).total_seconds() / (24 * 3600)
            if gap < 0.0001:
                gap = 0.0001
            daily_avg = record.puff_count / gap
            y_raw.append(round(daily_avg, 2))
    
    logger.info(f"📊 Calculados {len(y_raw)} pontos")
    
    # ==========================================
    # SUAVIZAÇÃO: se y > 2000, substituir pela média dos vizinhos
    # ==========================================
    y_suavizado = y_raw.copy()
    
    for i in range(len(y_suavizado)):
        if y_suavizado[i] > 2000:
            # Calcular média com vizinhos (se existirem)
            vizinhos = []
            if i > 0:
                vizinhos.append(y_raw[i-1])
            if i < len(y_raw) - 1:
                vizinhos.append(y_raw[i+1])
            
            if vizinhos:
                media_vizinhos = sum(vizinhos) / len(vizinhos)
                y_suavizado[i] = round(media_vizinhos, 2)
                logger.info(f"🔄 Suavizando ponto {i}: {y_raw[i]:.2f} → {y_suavizado[i]:.2f} (média dos vizinhos)")
            else:
                # Se não tiver vizinhos, mantém o valor
                y_suavizado[i] = y_raw[i]
    
    logger.info(f"📊 Usando {len(X)} pontos com datas reais")
    logger.info(f"📅 Primeira data (X): {X[0]:.4f} dias")
    logger.info(f"📅 Última data (X): {X[-1]:.4f} dias")
    
    # Treinar o modelo com datas reais
    X_array = np.array(X).reshape(-1, 1)
    y_array = np.array(y_suavizado)
    
    model = LinearRegression()
    model.fit(X_array, y_array)
    
    slope = model.coef_[0]
    intercept = model.intercept_
    
    logger.info(f"📐 Inclinação: {slope:.4f} puffs/dia")
    logger.info(f"📐 Intercepto: {intercept:.4f}")
    
    # Última data registrada
    last_date_days = X[-1] if X else 0
    logger.info(f"⏰ Última data: {last_date_days:.4f} dias desde o início")
    
    forecast_days = [30, 90, 120]
    now = datetime.now()
    
    for days in forecast_days:
        # Data futura em dias desde o início
        future_days = last_date_days + days
        pred = model.predict([[future_days]])[0]
        forecast_results[days] = round(max(5.0, pred), 2)
        forecast_dates[days] = (now + timedelta(days=days)).strftime('%Y-%m-%d')
        
        logger.info(f"🔮 Previsão para {days} dias (data {future_days:.2f}): {forecast_results[days]:.2f} puffs/dia")
    # ==========================================
    # 5. RESPOSTA
    # ==========================================
    response = {
        'dates': dates_for_chart,
        'daily_avg': daily_avg_real,
        'current_avg': current_avg,
        'forecast': forecast_results,
        'forecast_dates': forecast_dates,
        'debug': {
            'total_records_historicos': len(all_records),
            'total_days_historicos': len(daily_avg_real),
            'records_30dias': len(records_30dias),
            'total_puffs_30dias': total_puffs_30dias if records_30dias else 0,
            'model_trained': True,
            'slope': round(slope, 4),
            'intercept': round(intercept, 4)
        }
    }
    
    return jsonify(response)
