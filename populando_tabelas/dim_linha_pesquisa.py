import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor


def _normalizar_linha_pesquisa_sql() -> str:
    """
    Retorna a expressão SQL para normalização de linhas de pesquisa.
    
    Transformações aplicadas:
    - Remove aspas duplas
    - Remove URLs completas (http://, https://)
    - Remove prefixos alfabéticos como "a)", "b)", "c)", "d)"
    - Remove números no início seguidos de espaço ou ponto (ex: "2. ", "3 ")
    - Remove caracteres especiais no início (ex: "?", "&", ":")
    - Remove pontos finais desnecessários
    - Normaliza para Title Case (primeira letra maiúscula)
    - Remove espaços duplicados
    
    Returns:
        str: Expressão SQL de normalização
    """
    return r"""
        TRIM(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                                        INITCAP(linha_pesquisa),
                                        '"',  -- Remove aspas duplas
                                        '', 
                                        'g'
                                    ),
                                    'https?://[^\s]+',  -- Remove URLs completas
                                    '', 
                                    'gi'
                                ),
                                '^[a-z]\)\s*',  -- Remove prefixos alfabéticos "a) ", "b) ", etc
                                '', 
                                'gi'
                            ),
                            '^\d+[\.\s]+',  -- Remove números no início seguidos de ponto ou espaço "1. ", "2 "
                            '', 
                            'g'
                        ),
                        '^[^a-zA-Z0-9]+',  -- Remove caracteres especiais no início
                        '', 
                        'g'
                    ),
                    '\.$',  -- Remove ponto final
                    '', 
                    'g'
                ),
                '\s+',  -- Remove espaços duplicados
                ' ', 
                'g'
            )
        )
    """


def _filtros_validacao_sql() -> str:
    """
    Retorna a cláusula WHERE para filtrar dados inválidos.
    
    Filtros aplicados:
    - Remove valores NULL
    - Remove strings vazias
    - Remove linhas que são apenas URLs
    - Remove linhas muito curtas (≤ 3 caracteres)
    
    Returns:
        str: Cláusula WHERE SQL
    """
    return r"""
        WHERE linha_pesquisa IS NOT NULL
          AND TRIM(linha_pesquisa) != ''
          AND linha_pesquisa !~ '^https?://'
          AND LENGTH(TRIM(linha_pesquisa)) > 3
    """


def inserir_linhas_normalizadas(cursor) -> int:
    """
    Insere linhas de pesquisa normalizadas na tabela dimensional.
    
    Args:
        cursor: Cursor do banco de dados
        
    Returns:
        int: Número de registros inseridos
    """
    normalizacao_sql = _normalizar_linha_pesquisa_sql()
    filtros_sql = _filtros_validacao_sql()
    
    query = f"""
        INSERT INTO dw.dim_linha_pesquisa (linha_pesquisa)
        SELECT DISTINCT
            {normalizacao_sql} AS linha_pesquisa_normalizada
        FROM stg.linha_pesquisa
        {filtros_sql};
    """
    
    cursor.execute(query)
    return cursor.rowcount


def obter_estatisticas_dimensao(cursor) -> dict:
    """
    Coleta estatísticas da tabela dimensional.
    
    Args:
        cursor: Cursor do banco de dados
        
    Returns:
        dict: Dicionário com estatísticas
    """
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            AVG(LENGTH(linha_pesquisa))::INT as tamanho_medio
        FROM dw.dim_linha_pesquisa;
    """)
    
    stats = cursor.fetchone()
    
    return {
        'total': stats[0],
        'tamanho_medio': stats[1]
    }


def obter_estatisticas_stage(cursor) -> dict:
    """
    Coleta estatísticas da tabela de staging.
    
    Args:
        cursor: Cursor do banco de dados
        
    Returns:
        dict: Dicionário com estatísticas da stage
    """
    cursor.execute("""
        SELECT COUNT(*) as total_origem
        FROM stg.linha_pesquisa
        WHERE linha_pesquisa IS NOT NULL
          AND TRIM(linha_pesquisa) != '';
    """)
    total_origem = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT id_lattes)
        FROM stg.linha_pesquisa;
    """)
    pesquisadores = cursor.fetchone()[0]
    
    return {
        'total_origem': total_origem,
        'pesquisadores': pesquisadores
    }


def obter_amostra_linhas(cursor, limite: int = 10) -> list:
    """
    Obtém amostra de linhas normalizadas.
    
    Args:
        cursor: Cursor do banco de dados
        limite: Número de registros a retornar
        
    Returns:
        list: Lista de tuplas (linha_pesquisa, tamanho
    """
    cursor.execute(f"""
        SELECT 
            linha_pesquisa,
            LENGTH(linha_pesquisa) as tamanho
        FROM dw.dim_linha_pesquisa
        ORDER BY linha_pesquisa
        LIMIT {limite};
    """)
    
    return cursor.fetchall()


def obter_dados_removidos(cursor, limite: int = 5) -> list:
    """
    Obtém exemplos de dados que foram filtrados/removidos.
    
    Args:
        cursor: Cursor do banco de dados
        limite: Número de registros a retornar
        
    Returns:
        list: Lista de linhas removidas
    """
    cursor.execute(f"""
        SELECT DISTINCT linha_pesquisa
        FROM stg.linha_pesquisa
        WHERE linha_pesquisa IS NOT NULL
          AND TRIM(linha_pesquisa) != ''
          AND (
            linha_pesquisa ~ '^https?://'
            OR LENGTH(TRIM(linha_pesquisa)) <= 2
          )
        LIMIT {limite};
    """)
    
    return cursor.fetchall()

def popular_dim_linha_pesquisa():
    """
    Função principal que orquestra o processo de população da dim_linha_pesquisa.
    
    Responsabilidades:
    1. Coordenar as chamadas das funções especializadas
    2. Gerenciar transações do banco de dados
    3. Tratar exceções
    """
    try:
        
        with obter_cursor() as cursor:
            registros_inseridos = inserir_linhas_normalizadas(cursor)
            
            stats_dim = obter_estatisticas_dimensao(cursor)
            stats_stage = obter_estatisticas_stage(cursor)
            
            amostra = obter_amostra_linhas(cursor, limite=10)
            removidos = obter_dados_removidos(cursor, limite=5)
            
        
        print("Processo finalizado com sucesso!\n")
        
    except Exception as e:
        print(f"Erro ao popular dim_linha_pesquisa: {e}")
        raise


if __name__ == "__main__":
    popular_dim_linha_pesquisa()