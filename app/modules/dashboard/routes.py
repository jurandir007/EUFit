from flask import Blueprint, render_template
from app.database.models import Eu2016
# ... (os teus outros imports)

# 1. Instância do Blueprint definida UMA única vez
dashboard_bp = Blueprint('dashboard', __name__)

# 2. Decorador apontando para o Blueprint correto
@dashboard_bp.route('/view', methods=['GET'])
def view_dashboard():
    records = Eu2016.query.order_by(Eu2016.carimbo.desc()).all()
    return render_template('dashboard.html', history=records)