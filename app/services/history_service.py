#app/services/history_service.py
from datetime import datetime
from app.database.models import Eu2016
from app.modules.core.database import db
from app.ml.predictor import FitMLService

def receber_e_processar_dados(user_id, peso, gordura, viceral, carimbo=None):
    if carimbo is None:
        carimbo = datetime.now()

    # 1. Cria o registro inicial com os dados fornecidos e os demais como None
    novo_registro = Eu2016(
        fk_user_id=user_id,
        peso=peso,
        gordura=gordura,
        viceral=viceral,
        carimbo=carimbo,
        musculo=None,
        idade=None,
        basal=None
    )
    
    db.session.add(novo_registro)
    db.session.commit()

    # 2. Aciona o serviço de ML para preencher os campos nulos utilizando a sua classe original
    ml_service = FitMLService(user_id=user_id)
    ml_service.predict_and_update_db_record(novo_registro.id)

    return novo_registro
