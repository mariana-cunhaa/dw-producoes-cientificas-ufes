import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor, executar_query

def popular_dim_localizacao_trabalhos():
    """
    Popula a dimensão dw.dim_localizacao_trabalhos com informações de localização 
    geográfica e institucional das apresentações de trabalho científico.
    
    TABELA DE ORIGEM:
    - stg.apresentacoes_trabalho (pais, instituicao_promotora)
    
    ESTRUTURA DA DIMENSÃO:
    - id_localizacao_trabalhos (PK) - Chave surrogate gerada automaticamente
    - id_lattes - ID do pesquisador no Lattes (natural key)
    - pais - País onde a apresentação foi realizada
    - instituicao - Instituição promotora/organizadora do evento
    
    MAPEAMENTO DE CAMPOS:
    - id_lattes → id_lattes (identificador do pesquisador)
    - pais → pais (país do evento)
    - instituicao_promotora → instituicao (instituição organizadora, com limpeza e padronização)
    
    TRANSFORMAÇÕES APLICADAS:
    
    País:
    - Valores NULL ou vazios → "Não se aplica."
    - Remove espaços em branco extras (TRIM)
    
    Instituição:
    - Padroniza "UFES", "federal do espírito santo", "ceunes/ufes" → "Universidade Federal do Espírito Santo"
    - Remove HTML entities (&#123;, &quot;, etc.)
    - Remove caracteres especiais no início (vírgula, ponto, ?, !, etc.)
    - Remove URLs (www., .br, .com, etc.)
    - Remove caracteres não-ASCII
    - Remove espaços duplicados
    - Valores NULL, vazios ou inválidos → "Não se aplica."
    
    REGRAS DE NEGÓCIO:
    - Remove duplicatas com SELECT DISTINCT
    - Filtra apenas registros com id_lattes válido (NOT NULL)
    - Mantém combinações únicas de (id_lattes, pais, instituicao)
    
    CASOS DE USO:
    Esta dimensão permite análises sobre:
    - Apresentações em eventos internacionais vs nacionais
    - Colaborações e parcerias com instituições específicas
    - Distribuição geográfica das apresentações científicas
    - Identificação de pesquisadores com maior atuação internacional
    """

    try:
        query = r"""
        INSERT INTO dw.dim_localizacao_trabalhos (id_lattes, pais, instituicao)
        
        -- APRESENTAÇÕES DE TRABALHO
        SELECT DISTINCT
            id_lattes AS id_lattes,
            COALESCE(NULLIF(TRIM(pais), ''), 'Não se aplica.') AS pais,
            CASE 
                -- Valores nulos ou inválidos (PRIMEIRO)
                WHEN instituicao_promotora IS NULL THEN 'Não se aplica.'
                WHEN TRIM(instituicao_promotora) = '' THEN 'Não se aplica.'
                WHEN TRIM(instituicao_promotora) ~* '^&quot' THEN 'Não se aplica.'
                WHEN instituicao_promotora ~* 'www\.' THEN 'Não se aplica.'
                WHEN instituicao_promotora ~* '\.br' THEN 'Não se aplica.'
                -- Padronização: Universidade Federal do Espírito Santo
                WHEN (instituicao_promotora ~* 'federal do esp[ií]rito santo'
                      OR instituicao_promotora ~* 'ufes'
                      OR instituicao_promotora ~* 'ceunes/ufes')
                     AND instituicao_promotora !~* 'instituto'
                     AND instituicao_promotora !~* 'regional'
                     AND instituicao_promotora !~* 'justiça'
                     AND instituicao_promotora !~* 'associa[cç][aã]o' 
                THEN 'Universidade Federal do Espírito Santo'
                -- Limpeza de caracteres especiais e HTML entities
                ELSE 
                    CASE 
                        WHEN TRIM(REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                                        REGEXP_REPLACE(instituicao_promotora, '&#\d+;', '', 'g'),
                                        '&[a-z]+;', '', 'gi'
                                    ),
                                    '^[,\.\?!;\-\s]+', '', 'g'
                                ),
                                '\s+', ' ', 'g'
                            ),
                            '[^\x20-\x7E]', '', 'g'
                        )) = '' THEN 'Não se aplica.'
                        ELSE TRIM(REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                                        REGEXP_REPLACE(instituicao_promotora, '&#\d+;', '', 'g'),
                                        '&[a-z]+;', '', 'gi'
                                    ),
                                    '^[,\.\?!;\-\s]+', '', 'g'
                                ),
                                '\s+', ' ', 'g'
                            ),
                            '[^\x20-\x7E]', '', 'g'
                        ))
                    END
            END AS instituicao
        FROM stg.apresentacoes_trabalho
        WHERE id_lattes IS NOT NULL;
        """
        
        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount
            
            print(f"Tabela dw.dim_localizacao_trabalhos populada com sucesso!")
            print(f"Total de registros inseridos: {registros_inseridos}")
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(pais) as com_pais,
                    COUNT(instituicao) as com_instituicao
                FROM dw.dim_localizacao_trabalhos;
            """)
            
            stats = cursor.fetchone()
            print("\nEstatísticas da dim_localizacao_trabalhos:")
            print(f"   Total de localizações: {stats[0]}")
            print(f"   Com país: {stats[1]}")
            print(f"   Com instituição: {stats[2]}")
            
            cursor.execute("""
                SELECT 
                    id_lattes,
                    pais,
                    instituicao
                FROM dw.dim_localizacao_trabalhos
                LIMIT 5;
            """)
            
            amostra = cursor.fetchall()
            if amostra:
                for i, (id_lattes, pais, instituicao) in enumerate(amostra, 1):
                    print(f"   {i}. ID Lattes: {id_lattes}")
                    print(f"      País: {pais or 'N/A'} | Instituição: {instituicao or 'N/A'}")
                    print()
        
    except Exception as e:
        print(f"Erro ao popular dim_localizacao_trabalhos: {e}")
        raise


if __name__ == "__main__":
    popular_dim_localizacao_trabalhos()
