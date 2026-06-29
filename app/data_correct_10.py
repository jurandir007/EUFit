# data_correct_10.py
from app import create_app
from app.database.models import db, Eu2016


def corrigir_todos_dados():
    app = create_app()

    with app.app_context():
        print("--- Iniciando correção dos dados ---")
        registros = Eu2016.query.all()
        alteracoes = 0

        for r in registros:
            mudou = False

            # Correção Musculo (> 450)
            if r.musculo and r.musculo > 450:
                if 1000 <= r.musculo < 10000:
                    r.musculo /= 10
                elif r.musculo >= 10000:
                    r.musculo /= 100
                mudou = True

            # Correção Basal (Esperado 4 dígitos: 1000-9999)
            if r.basal and r.basal >= 10000:
                if 10000 <= r.basal < 100000:
                    r.basal /= 10
                elif r.basal >= 100000:
                    r.basal /= 100
                mudou = True

            # Correção Idade (Esperado 2 dígitos: 10-99)
            if r.idade and r.idade >= 100:
                if 100 <= r.idade < 1000:
                    r.idade /= 10
                elif r.idade >= 1000:
                    r.idade /= 100
                mudou = True

            if mudou:
                alteracoes += 1

        if alteracoes > 0:
            db.session.commit()
            print(f"Sucesso! {alteracoes} registros foram corrigidos no Neon.")
        else:
            print("Nenhum dado precisou de correção.")


if __name__ == '__main__':
    corrigir_todos_dados()