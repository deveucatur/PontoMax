import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def conexaoBD():
    conexao = mysql.connector.connect(
        passwd=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        host=os.getenv("DB_HOST"),
        database='gestao_escala'
    )

    return conexao