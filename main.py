from sqlalchemy import create_engine, text

import gspread
from google.oauth2.service_account import Credentials


# 1. Definir os escopos de permissão necessários
escopos = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 2. Carregar o arquivo JSON com suas credenciais
credenciais = Credentials.from_service_account_file(
    "credentials.json",
    scopes=escopos
)

# 3. Autenticar no Google
gc = gspread.authorize(credenciais)

# 4. Abrir a planilha (use o nome exato da planilha que você compartilhou)
# Alternativamente, você pode usar gc.open_by_key("ID_DA_PLANILHA")
planilha = gc.open("EU 2016 (respostas)").sheet1

# 5. Ler todos os dados e imprimir
dados = planilha.get_all_records()
#print(dados)

from sqlalchemy import create_engine, text
from datetime import datetime

# String de conexão do Neon (copie do painel do seu projeto)
# Formato: postgresql://USER:PASSWORD@HOST/DATABASE_NAME?sslmode=require
DATABASE_URL = "postgresql://neondb_owner:npg_p0XIuzidoE8G@ep-divine-waterfall-ab3wca54-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Criar a engine de conexão
engine = create_engine(DATABASE_URL)



# Dentro da sua função, onde você prepara os dados para o 'conn.execute':
def inserir_dados_no_neon(lista_de_dados):
    if not lista_de_dados:
        print("Nenhum dado para inserir.")
        return

    try:
        with engine.connect() as conn:
            for item in lista_de_dados:  # A variável 'item' nasce aqui

                # A conversão precisa acontecer AQUI, dentro do loop
                data_original = item.get('Carimbo de data/hora')
                data_formatada = datetime.strptime(data_original, "%d/%m/%Y %H:%M:%S")

                sql = text("""
                           INSERT INTO "Eu_2016"
                           ("Carimbo de data/hora", "Peso", "Gordura", "Musculo", "basal", "Idade", "viceral")
                           VALUES (:carimbo, :peso, :gordura, :musculo, :basal, :idade, :viceral)
                           """)

                conn.execute(sql, {
                    "carimbo": data_formatada,
                    "peso": item.get('Peso'),
                    "gordura": item.get('Gordura'),
                    "musculo": item.get('Musculo'),
                    "basal": item.get('basal'),
                    "idade": item.get('Idade'),
                    "viceral": item.get('viceral')
                })
            conn.commit()
            print(f"Sucesso! {len(lista_de_dados)} registros inseridos.")

    except Exception as e:
        print(f"Erro ao inserir dados: {e}")
# Exemplo de uso:
# dados = [{'Carimbo de data/hora': '...', 'Peso': 913, ...}, {...}]

#inserir_dados_no_neon(dados)


def remover_duplicados_sem_id():
    """
    Remove registros duplicados na tabela 'Eu_2016' usando o 'ctid'
    (identificador físico do Postgres) já que não existe chave primária.
    """
    sql_limpeza = text("""
        DELETE FROM "Eu_2016" a
        USING "Eu_2016" b
        WHERE a.ctid < b.ctid 
        AND a."Carimbo de data/hora" = b."Carimbo de data/hora";
    """)

    try:
        with engine.connect() as conn:
            resultado = conn.execute(sql_limpeza)
            conn.commit()
            print(f"Limpeza concluída! {resultado.rowcount} linhas duplicadas foram removidas.")
    except Exception as e:
        print(f"Erro ao remover: {e}")

remover_duplicados_sem_id()