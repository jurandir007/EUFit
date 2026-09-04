#app/ml/predictor.py
#https://chat.deepseek.com/share/r29l7jxzywmikc4sp2

import pandas as pd
from sklearn.linear_model import LinearRegression
from app.modules.core.database import db
from app.database.models import Eu2016

class FitMLService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.df_ml_data = None
        self.trained_models = {}

    def prepare_ml_data(self):
        # Loads data from the database specifically for the active user,
        # ensuring strict data isolation based on fk_user_id.
        # Stores the prepared DataFrame in self.df_ml_data.
        records = Eu2016.query.filter_by(fk_user_id=self.user_id).all()
        if records:
            data = []
            for r in records:
                data.append({
                    'peso': getattr(r, 'peso', None),
                    'gordura': getattr(r, 'gordura', None),
                    'viceral': getattr(r, 'viceral', None),
                    'musculo': getattr(r, 'musculo', None),
                    'idade': getattr(r, 'idade', None),
                    'basal': getattr(r, 'basal', None)
                })
            self.df_ml_data = pd.DataFrame(data)
        else:
            self.df_ml_data = pd.DataFrame()

    def train_models(self):
        if self.df_ml_data is None or self.df_ml_data.empty:
            self.prepare_ml_data()
            if self.df_ml_data.empty:
                return False

        X_cols = ['peso', 'gordura', 'viceral']
        y_cols = ['musculo', 'idade', 'basal']

        training_df = self.df_ml_data[X_cols + y_cols].dropna()
        if training_df.empty:
            return False

        X = training_df[X_cols]
        for target in y_cols:
            y = training_df[target]
            model = LinearRegression()
            model.fit(X, y)
            self.trained_models[target] = model
        return True

    def predict_and_update_db_record(self, record_id):
        record = Eu2016.query.get(record_id)
        if not record or record.fk_user_id != self.user_id:
            return False

        if record.musculo is not None:
            return False

        if not self.trained_models:
            success = self.train_models()
            if not success:
                return False

        input_data = pd.DataFrame([[record.peso, record.gordura, record.viceral]], 
                                    columns=['peso', 'gordura', 'viceral'])

        predictions = {}
        for target, model in self.trained_models.items():
            pred = model.predict(input_data)[0]
            predictions[target] = round(float(pred), 2)

        record.musculo = predictions['musculo']
        record.idade = predictions['idade']
        record.basal = predictions['basal']
        
        db.session.commit()
        return True
    
    def predict_on_the_fly(self, peso, gordura, viceral):
        """
        Treina o modelo com o histórico do usuário e prevê os valores 
        de músculo, idade e basal em memória, sem tocar no banco.
        """
        if self.df_ml_data is None or self.df_ml_data.empty:
            self.prepare_ml_data()
            
        # Trava de Segurança (Cold Start): Exige ao menos 5 registros para prever
        if self.df_ml_data.empty or len(self.df_ml_data) < 5:
            return None

        success = self.train_models()
        if not success:
            return None

        # Padroniza a entrada utilizando 'viceral' conforme exigido pelo modelo de treino
        input_data = pd.DataFrame([{
            'peso': float(peso), 
            'gordura': float(gordura), 
            'viceral': float(viceral)
        }], columns=['peso', 'gordura', 'viceral'])

        predictions = {}
        for target, model in self.trained_models.items():
            pred = model.predict(input_data)[0]
            # Trava biológica (clipping): impede valores negativos em métricas corporais
            safe_value = max(0.0, float(pred))
            predictions[target] = round(safe_value, 2)

        return {
            'musculo': predictions.get('musculo'),
            'idade': round(predictions.get('idade', 0)), # Idade arredondada para inteiro
            'basal': predictions.get('basal')
        }
