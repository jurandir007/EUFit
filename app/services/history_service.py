# app/services/history_service.py
from datetime import datetime
from app.database.models import Eu2016
from app.modules.core.database import db
from app.ml.predictor import FitMLService

def receber_e_processar_dados(user_id, peso, gordura, viceral, musculo=None, idade=None, basal=None):
    # Lógica exata: acumula a letra apenas dos campos que estão ausentes (None)
    str_comb_valor = ""
    if gordura is None: str_comb_valor += "f"
    if musculo is None: str_comb_valor += "m"
    if basal is None: str_comb_valor += "b"
    if idade is None: str_comb_valor += "a"
    if viceral is None: str_comb_valor += "v"

    # Se todos os campos estiverem preenchidos, o valor gravado é '0'
    if str_comb_valor == "":
        str_comb_valor = "0"

    # Se algum dos campos opcionais estiver ausente, aciona a IA preditiva
    if musculo is None or idade is None or basal is None:
        try:
            ml_service = FitMLService(user_id)
            predicoes = ml_service.predict_on_the_fly(peso, gordura, viceral)
            
            if predicoes:
                musculo = musculo if musculo is not None else float(predicoes.get('musculo'))
                idade = idade if idade is not None else int(predicoes.get('idade'))
                basal = basal if basal is not None else float(predicoes.get('basal'))
        except Exception as e:
            print(f"Aviso: Falha na predição de IA, prosseguindo com dados parciais. Erro: {e}")

    # Persistência final unificada no banco de dados incluindo a str_comb correta
    novo_registro = Eu2016(
        fk_user_id=user_id,
        peso=float(peso),
        gordura=float(gordura),
        viceral=float(viceral),
        musculo=float(musculo) if musculo is not None else None,
        idade=float(idade) if idade is not None else None,
        basal=float(basal) if basal is not None else None,
        str_comb=str_comb_valor,
        carimbo=datetime.now()
    )
    db.session.add(novo_registro)
    db.session.commit()
