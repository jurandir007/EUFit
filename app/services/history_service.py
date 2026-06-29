# app/services/history_service.py
from app.database.models import Eu2016


def get_formatted_history():
    records = Eu2016.query.all()

    return [{
        "date": r.carimbo.strftime("%Y-%m-%d %H:%M:%S") if r.carimbo else None,
        "weight": r.peso,
        "fat": r.gordura,
        "muscle": r.musculo,
        "basal": r.basal,
        "age": r.idade,
        "visceral": r.viceral
    } for r in records]