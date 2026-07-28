from app import create_app
from app.database.models import Eu2016
from app.modules.core.database import db

def calcular_str_comb(gordura, musculo, basal, idade, viceral):
    """
    Calcula a string combinada com base nos campos nulos/ausentes.
    Ordem: Gordura (f), Musculo (m), basal (b), Idade (a), viceral (v).
    Se todos preenchidos, retorna '0'.
    """
    if gordura is not None and musculo is not None and basal is not None and idade is not None and viceral is not None:
        return '0'
    
    resultado = ""
    resultado += 'f' if gordura is None else ''
    resultado += 'm' if musculo is None else ''
    resultado += 'b' if basal is None else ''
    resultado += 'a' if idade is None else ''
    resultado += 'v' if viceral is None else ''
    
    return resultado

def executar():
    app = create_app()
    with app.app_context():
        # Busca todos os registros do banco de dados
        registros = db.session.query(Eu2016).all()
        print(f"Total de registros encontrados: {len(registros)}")
        
        atualizados = 0
        for reg in registros:
            # Note que estou usando os nomes exatos mapeados no models.py
            novo_valor = calcular_str_comb(
                gordura=reg.gordura,
                musculo=reg.musculo,
                basal=reg.basal,
                idade=reg.idade,
                viceral=reg.viceral
            )
            reg.str_comb = novo_valor
            atualizados += 1
            
        # Salva tudo no banco
        db.session.commit()
        print(f"Sucesso! {atualizados} registros atualizados com a str_comb.")

if __name__ == "__main__":
    executar()
