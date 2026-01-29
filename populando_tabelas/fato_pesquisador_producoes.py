import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor


def popular_fato_pesquisador_producoes():
    """
    Popula a tabela dw.fato_pesquisador_producoes com dados agregados
    de todas as produções científicas dos pesquisadores.
    """
    
    try:
        query = """
        INSERT INTO dw.fato_pesquisador_producoes (
            id_pesquisador,
            id_tempo,
            id_tipo_producao,
            qtd_producoes
        )
        
        -- 1. LIVROS
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            COUNT(l.id) AS qt_producoes
        FROM dw.dim_pesquisador dp
        JOIN stg.livros l
            ON dp.id_lattes = l.id_lattes
        JOIN dw.dim_tempo dt
            ON l.ano ~ '^[0-9]{4}$'
           AND l.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Livro'
        WHERE
            dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao
        
        UNION ALL
        
        -- 2. ARTIGOS
        SELECT
            dp.id_pesquisador,
            dtp.id_tipo_producao,
            COUNT(a.id) AS qt_producoes
        FROM dw.dim_pesquisador dp
        JOIN stg.artigos a
            ON dp.id_lattes = a.id_lattes
        JOIN dw.dim_tempo dt
            ON a.ano ~ '^[0-9]{4}$'
           AND a.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Artigo'
        WHERE
            dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dtp.id_tipo_producao
        
        UNION ALL
        
        -- 3. APRESENTAÇÃO DE TRABALHO
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            COUNT(at.id) AS qt_producoes
        FROM dw.dim_pesquisador dp
        JOIN stg.apresentacoes_trabalho at
            ON dp.id_lattes = at.id_lattes
        JOIN dw.dim_tempo dt
            ON at.ano ~ '^[0-9]{4}$'
           AND at.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Apresentação de Trabalho'
        WHERE
            dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao
        
        UNION ALL
        
        -- 4. PROJETOS PESQUISA
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            COUNT(pp.id) AS qt_producoes
        FROM dw.dim_pesquisador dp
        JOIN stg.projetos_pesquisa pp
            ON dp.id_lattes = pp.id_lattes
        JOIN dw.dim_tempo dt
            ON pp.ano_inicio ~ '^[0-9]{4}$'
           AND pp.ano_inicio::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'projetos pesquisa'
        WHERE
            dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao
        
        UNION ALL
        
        -- 5. TEXTO EM JORNAL
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            COUNT(tj.id) AS qt_producoes
        FROM dw.dim_pesquisador dp
        JOIN stg.textos_jornais tj
            ON dp.id_lattes = tj.id_lattes
        JOIN dw.dim_tempo dt
            ON tj.ano ~ '^[0-9]{4}$'
           AND tj.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Texto em Jornal'
        WHERE
            dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao
        
        UNION ALL
        
        -- 6. OUTRAS PRODUÇÕES
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            COUNT(op.id) AS qt_producoes
        FROM dw.dim_pesquisador dp
        JOIN stg.outras_producoes op
            ON dp.id_lattes = op.id_lattes
        JOIN dw.dim_tempo dt
            ON op.ano ~ '^[0-9]{4}$'
           AND op.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Outras Produções'
        WHERE
            dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao
        
        UNION ALL
        
        -- 7. CAPÍTULO DE LIVRO
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            COUNT(cl.id) AS qt_producoes
        FROM dw.dim_pesquisador dp
        JOIN stg.capitulos_livros cl
            ON dp.id_lattes = cl.id_lattes
        JOIN dw.dim_tempo dt
            ON cl.ano ~ '^[0-9]{4}$'
           AND cl.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Capítulo de Livro'
        WHERE
            dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao
        
        UNION ALL
        
        -- 8. TRABALHO EM EVENTO
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            COUNT(te.id) AS qt_producoes
        FROM dw.dim_pesquisador dp
        JOIN stg.trabalhos_eventos te
            ON dp.id_lattes = te.id_lattes
        JOIN dw.dim_tempo dt
            ON te.ano ~ '^[0-9]{4}$'
           AND te.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Trabalho em Evento'
        WHERE
            dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao;
        """
        
        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount
            
            print(f"Tabela dw.fato_pesquisador_producoes populada com sucesso!")
            print(f"Total de registros inseridos: {registros_inseridos}")
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_registros,
                    SUM(qtd_producoes) as total_producoes
                FROM dw.fato_pesquisador_producoes;
            """)
            
            stats = cursor.fetchone()
            print("\nEstatísticas da fato_pesquisador_producoes:")
            print(f"   Total de registros: {stats[0]}")
            print(f"   Total de produções: {stats[1]}")
            
            cursor.execute("""
                SELECT 
                    dtp.tipo_producao,
                    COUNT(*) as num_registros,
                    SUM(fpp.qtd_producoes) as total_producoes
                FROM dw.fato_pesquisador_producoes fpp
                JOIN dw.dim_tipo_producao dtp
                    ON fpp.id_tipo_producao = dtp.id_tipo_producao
                GROUP BY dtp.tipo_producao
                ORDER BY total_producoes DESC;
            """)
            
            stats_tipo = cursor.fetchall()
            if stats_tipo:
                print("\nProduções por tipo:")
                for tipo, num_reg, total_prod in stats_tipo:
                    print(f"   • {tipo}: {total_prod} produções em {num_reg} registros")
            
            cursor.execute("""
                SELECT 
                    dp.nome,
                    dtp.tipo_producao,
                    dt.ano,
                    fpp.qtd_producoes
                FROM dw.fato_pesquisador_producoes fpp
                JOIN dw.dim_pesquisador dp
                    ON fpp.id_pesquisador = dp.id_pesquisador
                JOIN dw.dim_tipo_producao dtp
                    ON fpp.id_tipo_producao = dtp.id_tipo_producao
                JOIN dw.dim_tempo dt
                    ON fpp.id_tempo = dt.id_tempo
                ORDER BY fpp.qtd_producoes DESC
                LIMIT 5;
            """)
            
            top_producoes = cursor.fetchall()
            if top_producoes:
                print("\nTop 5 registros com mais produções:")
                for i, (nome, tipo, ano, qtd) in enumerate(top_producoes, 1):
                    print(f"   {i}. {nome}")
                    print(f"      Tipo: {tipo} | Ano: {ano} | Quantidade: {qtd}")
                    print()
        
    except Exception as e:
        print(f"Erro ao popular fato_pesquisador_producoes: {e}")
        raise


if __name__ == "__main__":
    popular_fato_pesquisador_producoes()

