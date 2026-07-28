import sys
import os

# Adiciona o diretório raiz ao path para garantir as importações corretas
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.modules.core.database import db
from app.database.models import Eu2016
from app.ml.predictor import FitMLService

def main():
    app = create_app()
    with app.app_context():
        # Busca registros que possuem alguma das colunas alvo nulas
        registros = Eu2016.query.filter(
            (Eu2016.musculo.is_(None)) | 
            (Eu2016.idade.is_(None)) | 
            (Eu2016.basal.is_(None))
        ).all()
        
        print(f"Total de registros encontrados com campos nulos: {len(registros)}")
        
        # Agrupa por usuário para instanciar o FitMLService isoladamente por usuário
        usuarios_processados = {}
        
        for reg in registros:
            user_id = reg.fk_user_id
            if user_id not in usuarios_processados:
                ml_service = FitMLService(user_id=user_id)
                ml_service.prepare_ml_data()
                ml_service.train_models()
                usuarios_processados[user_id] = ml_service
            
            ml_service = usuarios_processados[user_id]
            
            # Se houver modelos treinados, utiliza o método existente para prever e atualizar
            if ml_service.trained_models:
                sucesso = ml_service.predict_and_update_db_record(reg.id)
                if sucesso:
                    print(f"Registro ID {reg.id} processado e atualizado com sucesso.")
            else:
                print(f"Não foi possível treinar modelos para o usuário {user_id} (dados insuficientes).")

        print("Processo concluído.")

if __name__ == "__main__":
    main()
