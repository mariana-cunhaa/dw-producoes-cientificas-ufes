import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor

def popular_dim_tipo_producao():
    """
    Popula a tabela dw.dim_tipo_producao com tipos de produções científicas.
    
    Tabelas de origem (staging):
    - stg.artigos - 'Artigo'
    - stg.trabalhos_eventos - 'Trabalho em Evento'
    - stg.textos_jornais - 'Texto em Jornal'
    - stg.apresentacoes_trabalho - 'Apresentação de Trabalho'
    - stg.outras_producoes - 'Outras Produções'
    - stg.capitulos_livros - 'Capítulo de Livro'
    - stg.livros - 'Livro'
    - stg.projetos_pesquisa - 'projetos pesquisa'
    
    Estratégia:
    - Classifica cada registro pelo tipo da tabela de origem
    - Gera tipos padronizados de produção científica
    - Remove duplicatas com DISTINCT
    - Usa EXISTS para tabelas sem necessidade de filtros adicionais
    """
    
    try:
        query = """
        INSERT INTO dw.dim_tipo_producao (tipo_producao)
        
        SELECT DISTINCT
            'Artigo' AS tipo_producao
        FROM stg.artigos
        
        UNION
        
        -- TRABALHOS EM EVENTOS
        SELECT DISTINCT
            'Trabalho em Evento' AS tipo_producao
        FROM stg.trabalhos_eventos
        
        UNION
        
        -- TEXTOS EM JORNAIS
        SELECT DISTINCT
            'Texto em Jornal' AS tipo_producao
        FROM stg.textos_jornais
        
        UNION
        
        -- APRESENTAÇÕES DE TRABALHO
        SELECT DISTINCT
            'Apresentação de Trabalho' AS tipo_producao
        FROM stg.apresentacoes_trabalho
        
        UNION
        
        -- OUTRAS PRODUÇÕES
        SELECT DISTINCT
            'Outras Produções' AS tipo_producao
        FROM stg.outras_producoes
        
        UNION
        
        -- CAPÍTULOS DE LIVROS
        SELECT DISTINCT
            'Capítulo de Livro' AS tipo_producao
        FROM stg.capitulos_livros
        
        UNION
        
        -- LIVROS
        SELECT 
            'Livro' AS tipo_producao
        WHERE EXISTS (SELECT 1 FROM stg.livros)
        
        UNION
        
        -- PROJETOS DE PESQUISA
        SELECT 
            'projetos pesquisa' AS tipo_producao
        WHERE EXISTS (SELECT 1 FROM stg.projetos_pesquisa);
        """
        
        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT tipo_producao) as tipos_unicos
                FROM dw.dim_tipo_producao;
            """)
            
            stats = cursor.fetchone()
            print("\nEstatísticas da dim_tipo_producao:")
            print(f"   Total de combinações: {stats[0]}")
            print(f"   Tipos únicos de produção: {stats[1]}")
            
            cursor.execute("""
                SELECT 
                    tipo_producao,
                    COUNT(*) as quantidade
                FROM dw.dim_tipo_producao
                GROUP BY tipo_producao
                ORDER BY quantidade DESC;
            """)
            
            tipos = cursor.fetchall()
            if tipos:
                print("\nDistribuição por tipo de produção:")
                for tipo, quantidade in tipos:
                    print(f"   • {tipo}: {quantidade} quantidade(s)")
            
            cursor.execute("""
                SELECT tipo_producao
                FROM dw.dim_tipo_producao
                ORDER BY tipo_producao
                LIMIT 15;
            """)
            
            amostra = cursor.fetchall()
            if amostra:
                print("\nAmostra de tipos de produção cadastrados:")
                for tipo in amostra:
                    print(f"   • {tipo}")
        
    except Exception as e:
        print(f"Erro ao popular dim_tipo_producao: {e}")
        raise


if __name__ == "__main__":
    popular_dim_tipo_producao()

