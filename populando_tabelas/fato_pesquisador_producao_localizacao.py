import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor


def popular_fato_pesquisador_producao_localizacao():

    try:
        query = """
        INSERT INTO dw.fato_pesquisador_producao_localizacao (
            id_pesquisador,
            id_tempo,
            id_tipo_producao,
            id_localizacao_trabalhos,
            qtd_producoes
        )

        -- 1) TRABALHOS EM EVENTOS (localização: país do evento; instituição = NULL)
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            dlt.id_localizacao_trabalhos,
            COUNT(*) AS qtd_producoes
        FROM stg.trabalhos_eventos te
        JOIN dw.dim_pesquisador dp
            ON dp.id_lattes = te.id_lattes
        JOIN dw.dim_tempo dt
            ON te.ano ~ '^[0-9]{4}$'
           AND te.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Trabalho em Evento'
        JOIN dw.dim_localizacao_trabalhos dlt
            ON dlt.id_lattes = te.id_lattes
           AND dlt.pais IS NOT DISTINCT FROM te.pais_evento
           AND dlt.instituicao IS NULL
        WHERE dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            dlt.id_localizacao_trabalhos

        UNION ALL

        -- 2) APRESENTAÇÕES DE TRABALHO (localização: país + instituição promotora)
        SELECT
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            dlt.id_localizacao_trabalhos,
            COUNT(*) AS qtd_producoes
        FROM stg.apresentacoes_trabalho at
        JOIN dw.dim_pesquisador dp
            ON dp.id_lattes = at.id_lattes
        JOIN dw.dim_tempo dt
            ON at.ano ~ '^[0-9]{4}$'
           AND at.ano::INT = dt.ano
        JOIN dw.dim_tipo_producao dtp
            ON dtp.tipo_producao = 'Apresentação de Trabalho'
        JOIN dw.dim_localizacao_trabalhos dlt
            ON dlt.id_lattes = at.id_lattes
           AND dlt.pais IS NOT DISTINCT FROM at.pais
           AND dlt.instituicao IS NOT DISTINCT FROM at.instituicao_promotora
        WHERE dt.ano < 2026
        GROUP BY
            dp.id_pesquisador,
            dt.id_tempo,
            dtp.id_tipo_producao,
            dlt.id_localizacao_trabalhos

        ON CONFLICT (
            id_pesquisador,
            id_tempo,
            id_tipo_producao,
            id_localizacao_trabalhos
        ) DO NOTHING;
        """

        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount

            print("Tabela dw.fato_pesquisador_producao_localizacao populada com sucesso!")
            print(f"Total de registros inseridos: {registros_inseridos}")

            cursor.execute("""
                SELECT
                    COUNT(*) AS total_registros,
                    SUM(qtd_producoes) AS total_producoes
                FROM dw.fato_pesquisador_producao_localizacao;
            """)
            total_reg, total_prod = cursor.fetchone()

            print("\nEstatísticas da fato_pesquisador_producao_localizacao:")
            print(f"   Total de registros: {total_reg}")
            print(f"   Total de produções: {total_prod}")

    except Exception as e:
        print(f"Erro ao popular fato_pesquisador_producao_localizacao: {e}")
        raise


if __name__ == "__main__":
    popular_fato_pesquisador_producao_localizacao()


