# test_dados.py
from app import create_app
from app.services.history_service import get_formatted_history
from app.database.models import Eu2016  # Importado do arquivo models.py
from datetime import datetime


def test_ultimos_10():
    app = create_app()

    with app.app_context():
        print("--- Buscando os 10 últimos registros ---")
        try:
            # Consulta os registros ordenando pelo carimbo de forma decrescente
            registros = Eu2016.query.order_by(Eu2016.__table__.c['Carimbo de data/hora'].desc()).limit(10).all()

            # Formata conforme a lógica original definida em history_service.py
            dados = []
            for r in registros:
                carimbo = getattr(r, 'Carimbo de data/hora', None)
                if carimbo is None:
                    carimbo = datetime.now()
                    setattr(r, 'Carimbo de data/hora', carimbo)
                    db.session.commit()

                dados.append({
                    "date": carimbo.strftime("%Y-%m-%d %H:%M:%S") if carimbo else None,
                    "weight": r.Peso,
                    "fat": r.Gordura,
                    "muscle": r.Musculo,
                    "basal": r.basal,
                    "age": r.Idade,
                    "visceral": r.viceral
                })

            for i, item in enumerate(dados, 1):
                print(f"{i}: {item}")

        except Exception as e:
            print(f"Erro ao processar dados: {e}")


if __name__ == '__main__':
    test_ultimos_10()
