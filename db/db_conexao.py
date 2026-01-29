import psycopg2
from contextlib import contextmanager

DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'marianacunha',
    'password': '',  
    'host': 'localhost',
    'port': '5432'
}

def obter_conexao():
    """
    Cria e retorna uma conexão com o banco de dados PostgreSQL.
    
    Returns:
        psycopg2.connection: Objeto de conexão com o banco de dados
        
    Raises:
        psycopg2.Error: Se houver erro ao conectar com o banco
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise


@contextmanager
def obter_cursor():
    """
    Context manager para gerenciar conexão e cursor automaticamente.
    Faz commit automaticamente em caso de sucesso e rollback em caso de erro.
    
    Uso:
        with obter_cursor() as cursor:
            cursor.execute("SELECT * FROM tabela")
            resultados = cursor.fetchall()
    
    Yields:
        psycopg2.cursor: Cursor para executar queries
    """
    conn = None
    cursor = None
    
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro na execução: {e}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def executar_query(query, params=None, fetch=False):
    """
    Executa uma query no banco de dados.
    
    Args:
        query (str): Query SQL a ser executada
        params (tuple, optional): Parâmetros para a query (previne SQL injection)
        fetch (bool): Se True, retorna os resultados. Se False, apenas executa.
        
    Returns:
        list ou int: Lista de resultados se fetch=True, ou número de linhas afetadas
        
    Raises:
        psycopg2.Error: Se houver erro na execução da query
    """
    try:
        with obter_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                return cursor.fetchall()
            else:
                return cursor.rowcount
                
    except psycopg2.Error as e:
        print(f"Erro ao executar query: {e}")
        raise


def testar_conexao():
    """
    Testa a conexão com o banco de dados.
    
    Returns:
        bool: True se a conexão foi bem-sucedida, False caso contrário
    """
    try:
        with obter_cursor() as cursor:
            cursor.execute("SELECT version();")
            versao = cursor.fetchone()
            print(f"Conexão bem-sucedida!")
            print(f"Versão do PostgreSQL: {versao[0]}")
            return True
            
    except psycopg2.Error as e:
        print(f"Falha ao conectar: {e}")
        return False

def contar_registros(tabela, schema='tcc'):
    """
    Conta o número de registros em uma tabela.
    
    Args:
        tabela (str): Nome da tabela
        schema (str): Schema da tabela (padrão: 'tcc')
        
    Returns:
        int: Número de registros na tabela
    """
    query = f"SELECT COUNT(*) FROM {schema}.{tabela};"
    resultado = executar_query(query, fetch=True)
    return resultado[0][0] if resultado else 0


def limpar_tabela(tabela, schema='tcc'):
    """
    Remove todos os registros de uma tabela (TRUNCATE).
    CUIDADO: Esta operação não pode ser desfeita!
    
    Args:
        tabela (str): Nome da tabela
        schema (str): Schema da tabela (padrão: 'tcc')
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        query = f"TRUNCATE TABLE {schema}.{tabela} RESTART IDENTITY CASCADE;"
        executar_query(query)
        print(f"Tabela {schema}.{tabela} limpa com sucesso!")
        return True
    except psycopg2.Error:
        return False


if __name__ == "__main__":
    testar_conexao()

