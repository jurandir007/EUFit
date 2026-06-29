# test_dados.py
from app import create_app
from app.services.history_service import get_formatted_history
from app.database.models import Eu2016  # Importado do arquivo models.py


def test_ultimos_10():
    app = create_app()

    with app.app_context():
        print("--- Buscando os 10 últimos registros ---")
        try:
            # Consulta os registros ordenando pelo carimbo de forma decrescente
            registros = Eu2016.query.order_by(Eu2016.carimbo.desc()).limit(10).all()

            # Formata conforme a lógica original definida em history_service.py
            dados = [{
                "date": r.carimbo.strftime("%Y-%m-%d %H:%M:%S") if r.carimbo else None,
                "weight": r.peso,
                "fat": r.gordura,
                "muscle": r.musculo,
                "basal": r.basal,
                "age": r.idade,
                "visceral": r.viceral
            } for r in registros]

            for i, item in enumerate(dados, 1):
                print(f"{i}: {item}")

        except Exception as e:
            print(f"Erro ao processar dados: {e}")


if __name__ == '__main__':
    test_ultimos_10()