from app import create_app
from app.ml.predictor import FitMLService

app = create_app()

with app.app_context():
    # Substitua pelo ID real de um usuário que possui dados no banco
    test_user_id = 3 
    
    print(f"Iniciando teste do serviço ML para o usuário ID: {test_user_id}")
    
    ml_service = FitMLService(user_id=test_user_id)
    
    # 1. Testa o carregamento dos dados
    ml_service.prepare_ml_data()
    if ml_service.df_ml_data is not None:
        print(f"-> Dados carregados com sucesso! Total de registros: {len(ml_service.df_ml_data)}")
    else:
        print("-> Erro: DataFrame veio vazio.")
        exit()
        
    # 2. Testa o treinamento dos modelos
    success_train = ml_service.train_models()
    if success_train:
        print("-> Modelos de Regressão Linear treinados com sucesso!")
        print(f"-> Modelos gerados: {list(ml_service.trained_models.keys())}")
    else:
        print("-> Erro ao treinar os modelos (verifique se há dados suficientes sem valores nulos).")
        exit()
        
    print("Fase 1 e Fase 2 validadas com sucesso no banco de dados!")
