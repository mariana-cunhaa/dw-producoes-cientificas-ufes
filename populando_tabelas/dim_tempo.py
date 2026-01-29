import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor

def popular_dim_tempo():
    """
    Popula a tabela dw.dim_tempo com todos os anos das tabelas de produções.
    
    Tabelas de origem (staging):
    - stg.artigos (ano)
    - stg.livros (ano)
    - stg.capitulos_livros (ano)
    - stg.textos_jornais (ano, data_publicacao)
    - stg.trabalhos_eventos (ano, ano_realizacao)
    - stg.apresentacoes_trabalho (ano)
    - stg.outras_producoes (ano)
    - stg.projetos_pesquisa (ano_inicio, ano_fim)
    
    Estratégia:
    - Extrai TODOS os anos de todas as tabelas de produções científicas
    - Remove duplicatas com DISTINCT
    - Filtra anos inválidos (< 1900 ou > 2025)
    """
    
    try:
        query = """
        INSERT INTO dw.dim_tempo (ano)
        
        -- ARTIGOS
        SELECT DISTINCT
            CAST(ano AS INT) AS ano
        FROM stg.artigos
        WHERE ano IS NOT NULL
          AND ano ~ '^[0-9]+$'
          AND CAST(ano AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- LIVROS
        SELECT DISTINCT
            CAST(ano AS INT)
        FROM stg.livros
        WHERE ano IS NOT NULL
          AND ano ~ '^[0-9]+$'
          AND CAST(ano AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- CAPÍTULOS DE LIVROS
        SELECT DISTINCT
            CAST(ano AS INT)
        FROM stg.capitulos_livros
        WHERE ano IS NOT NULL
          AND ano ~ '^[0-9]+$'
          AND CAST(ano AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- TEXTOS EM JORNAIS (do campo ano)
        SELECT DISTINCT
            CAST(ano AS INT)
        FROM stg.textos_jornais
        WHERE ano IS NOT NULL
          AND ano ~ '^[0-9]+$'
          AND CAST(ano AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- TEXTOS EM JORNAIS (extraído de data_publicacao)
        SELECT DISTINCT
            EXTRACT(YEAR FROM TO_DATE(data_publicacao, 'DD/MM/YYYY'))::INT
        FROM stg.textos_jornais
        WHERE data_publicacao IS NOT NULL
          AND data_publicacao ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
          AND EXTRACT(YEAR FROM TO_DATE(data_publicacao, 'DD/MM/YYYY'))::INT BETWEEN 1900 AND 2025
        
        UNION
        
        -- TRABALHOS EM EVENTOS
        SELECT DISTINCT
            CAST(ano AS INT)
        FROM stg.trabalhos_eventos
        WHERE ano IS NOT NULL
          AND ano ~ '^[0-9]+$'
          AND CAST(ano AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- TRABALHOS EM EVENTOS (ano de realização)
        SELECT DISTINCT
            CAST(ano_realizacao AS INT)
        FROM stg.trabalhos_eventos
        WHERE ano_realizacao IS NOT NULL
          AND ano_realizacao ~ '^[0-9]+$'
          AND CAST(ano_realizacao AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- APRESENTAÇÕES DE TRABALHO
        SELECT DISTINCT
            CAST(ano AS INT)
        FROM stg.apresentacoes_trabalho
        WHERE ano IS NOT NULL
          AND ano ~ '^[0-9]+$'
          AND CAST(ano AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- OUTRAS PRODUÇÕES
        SELECT DISTINCT
            CAST(ano AS INT)
        FROM stg.outras_producoes
        WHERE ano IS NOT NULL
          AND ano ~ '^[0-9]+$'
          AND CAST(ano AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- PROJETOS (ano início)
        SELECT DISTINCT
            CAST(ano_inicio AS INT)
        FROM stg.projetos_pesquisa
        WHERE ano_inicio IS NOT NULL
          AND ano_inicio ~ '^[0-9]+$'
          AND CAST(ano_inicio AS INT) BETWEEN 1900 AND 2025
        
        UNION
        
        -- PROJETOS (ano fim)
        SELECT DISTINCT
            CAST(ano_fim AS INT)
        FROM stg.projetos_pesquisa
        WHERE ano_fim IS NOT NULL
          AND ano_fim ~ '^[0-9]+$'
          AND CAST(ano_fim AS INT) BETWEEN 1900 AND 2025;
        """
        
        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount
            
            print(f"Tabela dw.dim_tempo populada com sucesso!")
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    MIN(ano) as ano_min,
                    MAX(ano) as ano_max
                FROM dw.dim_tempo;
            """)
            
            stats = cursor.fetchone()
            print("\nEstatísticas da dim_tempo:")
            print(f"   Total de anos únicos: {stats[0]}")
            print(f"   Período: {stats[1]} a {stats[2]}")
            
            cursor.execute("""
                SELECT 
                    FLOOR(ano / 10) * 10 || 's' as decada,
                    COUNT(*) as quantidade
                FROM dw.dim_tempo
                GROUP BY FLOOR(ano / 10)
                ORDER BY FLOOR(ano / 10);
            """)
            
            decadas = cursor.fetchall()
            if decadas:
                print("\nDistribuição por década:")
                for decada, qtd in decadas:
                    print(f"   {decada}: {qtd} anos")
            
            cursor.execute("""
                SELECT ano
                FROM dw.dim_tempo
                ORDER BY ano;
            """)
            
            anos = [row[0] for row in cursor.fetchall()]
            if len(anos) <= 50:
                print(f"\nAnos cadastrados: {', '.join(map(str, anos))}")
            else:
                print(f"\nAmostra dos primeiros/últimos anos: {', '.join(map(str, anos[:5]))} ... {', '.join(map(str, anos[-5:]))}")
        
    except Exception as e:
        print(f"Erro ao popular dim_tempo: {e}")
        raise


if __name__ == "__main__":
    popular_dim_tempo()