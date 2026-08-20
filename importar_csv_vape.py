import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv('neon.env')

# Usando o nome correto da variável que você encontrou
DATABASE_URL = os.getenv('DATABASE_URL_Neon')

def importar_dados_csv(caminho_arquivo_csv):
    if not DATABASE_URL:
        print("Erro: Variável DATABASE_URL_Neon não encontrada no neon.env.")
        return

    try:
        print("Conectando ao banco de dados Neon para importação...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print(f"Lendo o arquivo '{caminho_arquivo_csv}' e enviando para o banco...")
        
        # O bloco with garante que o arquivo seja fechado corretamente após a leitura
        with open(caminho_arquivo_csv, 'r', encoding='utf-8') as f:
            # copy_expert usa o comando COPY nativo do PostgreSQL, que é a forma mais rápida e segura de importar CSV
            comando_sql = """
                COPY record_vape(user_id, puff_count, recorded_at) 
                FROM STDIN WITH CSV HEADER DELIMITER ','
            """
            cur.copy_expert(comando_sql, f)

        # Confirma a transação
        conn.commit()
        print("Sucesso absoluto! Todos os dados foram inseridos na tabela 'record_vape'.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo_csv}' não foi encontrado na pasta atual.")
    except psycopg2.Error as e:
        print(f"Erro no banco de dados: {e}")
        if 'conn' in locals():
            conn.rollback() # Desfaz a operação em caso de erro
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        # Fecha as conexões
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    # COLOQUE AQUI O NOME DO SEU ARQUIVO CSV
    nome_do_seu_csv = "puff.csv" 
    
    importar_dados_csv(nome_do_seu_csv)
