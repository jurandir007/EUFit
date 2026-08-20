import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do seu arquivo específico
load_dotenv('neon.env')

# Certifique-se de que o nome da variável dentro do neon.env seja DATABASE_URL
# Se for diferente (ex: NEON_DB_URL), altere a linha abaixo.
DATABASE_URL = os.getenv('DATABASE_URL_Neon')

def configurar_banco():
    if not DATABASE_URL:
        print("Erro: Variável de ambiente de conexão não encontrada no neon.env.")
        return

    try:
        print("Conectando ao banco de dados Neon...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. Adicionar a coluna deleted_at na tabela users (Soft Delete)
        print("Adicionando coluna 'deleted_at' na tabela 'users' (se não existir)...")
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;
        """)

        # 2. Criar a tabela record_vape (com Cascade)
        print("Criando a tabela 'record_vape'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS record_vape (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                puff_count INTEGER NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Confirma as alterações no banco de dados
        conn.commit()
        print("Sucesso! Banco de dados atualizado.")

    except psycopg2.Error as e:
        print(f"Erro no banco de dados: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        # Fecha o cursor e a conexão com segurança
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    configurar_banco()
