import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

try:
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user;")
            banco, usuario = cursor.fetchone()

            print("Conexão realizada com sucesso.")
            print(f"Banco: {banco}")
            print(f"Usuário: {usuario}")

except psycopg.Error as erro:
    print("Não foi possível conectar ao PostgreSQL.")
    print(erro)