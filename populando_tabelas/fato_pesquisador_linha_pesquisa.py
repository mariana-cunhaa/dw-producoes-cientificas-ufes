import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor


def popular_fato_pesquisador_linha_pesquisa():
    """
    Popula a tabela dw.fato_pesquisador_linha_pesquisa a partir de:
    - stg.linha_pesquisa (fonte)
    - dw.dim_pesquisador (mapeia id_lattes -> id_pesquisador)
    - dw.dim_linha_pesquisa (mapeia texto da linha -> id_linha_pesquisa)
    """

    try:
        query = """
        INSERT INTO dw.fato_pesquisador_linha_pesquisa (
            id_pesquisador,
            id_linha_pesquisa,
            presenca
        )
        SELECT DISTINCT
            dp.id_pesquisador,
            dlp.id_linha_pesquisa,
            1 as presenca
        FROM stg.linha_pesquisa lp
        JOIN dw.dim_pesquisador dp
            ON dp.id_lattes = lp.id_lattes
        JOIN dw.dim_linha_pesquisa dlp
            ON dlp.linha_pesquisa = TRIM(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                                        REGEXP_REPLACE(
                                            INITCAP(lp.linha_pesquisa),
                                            '"',
                                            '', 
                                            'g'
                                        ),
                                        'https?://[^\s]+',
                                        '', 
                                        'gi'
                                    ),
                                    '^[a-z]\)\s*',
                                    '', 
                                    'gi'
                                ),
                                '^\d+[\.\s]+',
                                '', 
                                'g'
                            ),
                            '^[^a-zA-Z0-9]+',
                            '', 
                            'g'
                        ),
                        '\.$',
                        '', 
                        'g'
                    ),
                    '\s+',
                    ' ', 
                    'g'
                )
            )
        WHERE lp.linha_pesquisa IS NOT NULL
          AND TRIM(lp.linha_pesquisa) != ''
        ON CONFLICT (id_pesquisador, id_linha_pesquisa) DO NOTHING;
        """

        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount

            print("Tabela dw.fato_pesquisador_linha_pesquisa populada com sucesso!")
            print(f"Total de registros inseridos: {registros_inseridos}")

            cursor.execute("""
                SELECT
                    COUNT(*) as total_relacoes,
                    COUNT(DISTINCT id_pesquisador) as pesquisadores_distintos,
                    COUNT(DISTINCT id_linha_pesquisa) as linhas_distintas
                FROM dw.fato_pesquisador_linha_pesquisa;
            """)
            total_rel, pesq_dist, linhas_dist = cursor.fetchone()

            print("\nEstatísticas da fato_pesquisador_linha_pesquisa:")
            print(f"   Total de relações: {total_rel}")
            print(f"   Pesquisadores distintos: {pesq_dist}")
            print(f"   Linhas de pesquisa distintas: {linhas_dist}")

            cursor.execute("""
                SELECT
                    dlp.linha_pesquisa,
                    COUNT(DISTINCT fpl.id_pesquisador) as pesquisadores
                FROM dw.fato_pesquisador_linha_pesquisa fpl
                JOIN dw.dim_linha_pesquisa dlp
                    ON fpl.id_linha_pesquisa = dlp.id_linha_pesquisa
                GROUP BY dlp.linha_pesquisa
                ORDER BY pesquisadores DESC
                LIMIT 10;
            """)
            top = cursor.fetchall()
            if top:
                print("\nTop 10 linhas de pesquisa por pesquisadores distintos:")
                for linha, qtd in top:
                    linha_disp = linha if len(linha) <= 90 else linha[:87] + "..."
                    print(f"   • {linha_disp}: {qtd}")

    except Exception as e:
        print(f"Erro ao popular fato_pesquisador_linha_pesquisa: {e}")
        raise


if __name__ == "__main__":
    popular_fato_pesquisador_linha_pesquisa()