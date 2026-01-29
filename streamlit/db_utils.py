import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
import pandas as pd

def get_connection():
    """
    Conecta ao banco de dados usando secrets do Streamlit.
    Prioridade: st.secrets > variáveis de ambiente
    """
    try:
        # Tenta usar os secrets do Streamlit primeiro (para produção e dev local)
        db_config = st.secrets["db"]
        return psycopg2.connect(
            host=db_config["host"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            port=db_config.get("port", 5432),
            sslmode="require"
        )
    except (KeyError, FileNotFoundError):
        # Fallback para variáveis de ambiente (se secrets não estiver configurado)
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432),
            sslmode="require"
        )

def test_connection():
    """
    Testa se a conexão com o banco está funcionando.
    Retorna True se conectou, False caso contrário.
    """
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False

def run_query(query):
    """
    Executa uma query e retorna os resultados como DataFrame do pandas.
    Útil para queries que retornam múltiplas linhas.
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_metric_value(query):
    """
    Executa uma query e retorna um único valor (primeira linha, primeira coluna).
    Útil para queries de agregação (COUNT, SUM, AVG, etc.).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0]
