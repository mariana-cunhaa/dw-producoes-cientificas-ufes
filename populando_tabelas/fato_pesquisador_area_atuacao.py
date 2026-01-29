import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor

def popular_fato_pesquisador_area_atuacao():
    """
    Popula a tabela dw.fato_pesquisador_area_atuacao a partir de:
    - stg.areas_atuacao (fonte)
    - dw.dim_pesquisador (mapeia id_lattes -> id_pesquisador)
    - dw.dim_area (mapeia grande_area/area -> id_area)
    """

    try:
        query = """
        INSERT INTO dw.fato_pesquisador_area_atuacao (
            id_pesquisador,
            id_area,
            presenca
        )
        SELECT DISTINCT
            dp.id_pesquisador,
            da.id_area,
            1 as presenca
        FROM stg.areas_atuacao aa
        JOIN dw.dim_pesquisador dp
            ON dp.id_lattes = aa.id_lattes
        JOIN dw.dim_area da
            ON TRIM(COALESCE(da.grande_area, '')) = TRIM(COALESCE(aa.nome_grande_area, ''))
           AND TRIM(da.area) = TRIM(aa.nome_area)
        WHERE aa.nome_area IS NOT NULL
          AND TRIM(aa.nome_area) != ''
        ON CONFLICT (id_pesquisador, id_area) DO NOTHING;
        """

        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount

            print("Tabela dw.fato_pesquisador_area_atuacao populada com sucesso!")
            print(f"Total de registros inseridos: {registros_inseridos}")

            cursor.execute("""
                SELECT
                    COUNT(*) as total_relacoes,
                    COUNT(DISTINCT id_pesquisador) as pesquisadores_distintos,
                    COUNT(DISTINCT id_area) as areas_distintas
                FROM dw.fato_pesquisador_area_atuacao;
            """)
            total_rel, pesq_dist, area_dist = cursor.fetchone()

            print("\nEstatísticas da fato_pesquisador_area_atuacao:")
            print(f"   Total de relações: {total_rel}")
            print(f"   Pesquisadores distintos: {pesq_dist}")
            print(f"   Áreas distintas: {area_dist}")

            cursor.execute("""
                SELECT
                    da.grande_area,
                    COUNT(DISTINCT fpa.id_pesquisador) as pesquisadores
                FROM dw.fato_pesquisador_area_atuacao fpa
                JOIN dw.dim_area da
                    ON fpa.id_area = da.id_area
                GROUP BY da.grande_area
                ORDER BY pesquisadores DESC
                LIMIT 10;
            """)
            top = cursor.fetchall()
            if top:
                print("\nTop 10 grandes áreas por pesquisadores distintos:")
                for grande_area, qtd in top:
                    print(f"   • {grande_area or 'N/A'}: {qtd}")

    except Exception as e:
        print(f"Erro ao popular fato_pesquisador_area_atuacao: {e}")
        raise


if __name__ == "__main__":
    popular_fato_pesquisador_area_atuacao()


