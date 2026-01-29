import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor

def popular_dim_pesquisador():
    """
    Popula a tabela dw.dim_pesquisador com dados da tabela stg.pesquisador.
    Extrai informações básicas dos pesquisadores (id_lattes, nome, atuação profissional).
    """
    
    try:
        query = """
        INSERT INTO dw.dim_pesquisador (
            id_lattes,
            nome,
            atuacao_profissional
        )
        SELECT DISTINCT
            id_lattes,
            CASE 
                WHEN nome IS NULL THEN 'Não se aplica.'
                WHEN TRIM(nome) = '' THEN 'Não se aplica.'
                WHEN TRIM(nome) = '.' THEN 'Não se aplica.'
                WHEN TRIM(nome) = '...' THEN 'Não se aplica.'
                ELSE TRIM(nome)
            END as nome,
            CASE 
                -- Padronização: Universidade Federal do Espírito Santo
                WHEN (atuacao_profissional ~* 'federal do esp[ií]rito santo'
                      OR atuacao_profissional ~* 'ufes')
                     AND atuacao_profissional !~* 'instituto'
                     AND atuacao_profissional !~* 'regional'
                     AND atuacao_profissional !~* 'justiça'
                     AND atuacao_profissional !~* 'associa[cç][aã]o' 
                THEN 'Universidade Federal do Espírito Santo'
                -- Valores nulos ou inválidos
                WHEN atuacao_profissional IS NULL THEN 'Não se aplica.'
                WHEN TRIM(atuacao_profissional) = '' THEN 'Não se aplica.'
                WHEN TRIM(atuacao_profissional) = '.' THEN 'Não se aplica.'
                WHEN TRIM(atuacao_profissional) = '...' THEN 'Não se aplica.'
                -- Mantém valor original
                ELSE TRIM(atuacao_profissional)
            END as atuacao_profissional
        FROM stg.pesquisador
        WHERE id_lattes IS NOT NULL;
        """
        
        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(id_lattes) as com_id_lattes,
                    COUNT(nome) as com_nome,
                    COUNT(CASE WHEN atuacao_profissional != 'Não se aplica.' THEN 1 END) as com_atuacao_real,
                    COUNT(CASE WHEN atuacao_profissional = 'Não se aplica.' THEN 1 END) as sem_atuacao
                FROM dw.dim_pesquisador;
            """)
            
            stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT id_lattes, nome, 
                       CASE 
                           WHEN LENGTH(atuacao_profissional) > 60 
                           THEN LEFT(atuacao_profissional, 60) || '...'
                           ELSE atuacao_profissional
                       END as atuacao_resumida
                FROM dw.dim_pesquisador
                ORDER BY nome
                LIMIT 10;
            """)
            
        
    except Exception as e:
        print(f"Erro ao popular dim_pesquisador: {e}")
        raise


if __name__ == "__main__":
    popular_dim_pesquisador()