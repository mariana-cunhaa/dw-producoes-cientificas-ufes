import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor

def investigar_anos_invalidos():
    """
    Investiga de quais tabelas vêm os anos suspeitos/inválidos.
    """
    
    ano_atual = 2026
    
    try:
        with obter_cursor() as cursor:
            
            # ARTIGOS
            cursor.execute(f"""
                SELECT 'artigos' as tabela, CAST(ano AS INT) as ano, COUNT(*) as quantidade
                FROM stg.artigos
                WHERE ano IS NOT NULL 
                  AND ano ~ '^[0-9]+$'
                  AND CAST(ano AS INT) > {ano_atual}
                GROUP BY ano
                ORDER BY ano;
            """)
            artigos = cursor.fetchall()
            
            # LIVROS
            cursor.execute(f"""
                SELECT 'livros' as tabela, CAST(ano AS INT) as ano, COUNT(*) as quantidade
                FROM stg.livros
                WHERE ano IS NOT NULL 
                  AND ano ~ '^[0-9]+$'
                  AND CAST(ano AS INT) > {ano_atual}
                GROUP BY ano
                ORDER BY ano;
            """)
            livros = cursor.fetchall()
            
            # CAPÍTULOS DE LIVROS
            cursor.execute(f"""
                SELECT 'capitulos_livros' as tabela, CAST(ano AS INT) as ano, COUNT(*) as quantidade
                FROM stg.capitulos_livros
                WHERE ano IS NOT NULL 
                  AND ano ~ '^[0-9]+$'
                  AND CAST(ano AS INT) > {ano_atual}
                GROUP BY ano
                ORDER BY ano;
            """)
            capitulos = cursor.fetchall()
            
            # TEXTOS EM JORNAIS (campo ano)
            cursor.execute(f"""
                SELECT 'textos_jornais' as tabela, CAST(ano AS INT) as ano, COUNT(*) as quantidade
                FROM stg.textos_jornais
                WHERE ano IS NOT NULL 
                  AND ano ~ '^[0-9]+$'
                  AND CAST(ano AS INT) > {ano_atual}
                GROUP BY ano
                ORDER BY ano;
            """)
            textos = cursor.fetchall()
            
            # TRABALHOS EM EVENTOS
            cursor.execute(f"""
                SELECT 'trabalhos_eventos (ano)' as tabela, CAST(ano AS INT) as ano, COUNT(*) as quantidade
                FROM stg.trabalhos_eventos
                WHERE ano IS NOT NULL 
                  AND ano ~ '^[0-9]+$'
                  AND CAST(ano AS INT) > {ano_atual}
                GROUP BY ano
                ORDER BY ano;
            """)
            eventos_ano = cursor.fetchall()
            
            # TRABALHOS EM EVENTOS (ano_realizacao)
            cursor.execute(f"""
                SELECT 'trabalhos_eventos (ano_realizacao)' as tabela, CAST(ano_realizacao AS INT) as ano, COUNT(*) as quantidade
                FROM stg.trabalhos_eventos
                WHERE ano_realizacao IS NOT NULL 
                  AND ano_realizacao ~ '^[0-9]+$'
                  AND CAST(ano_realizacao AS INT) > {ano_atual}
                GROUP BY ano_realizacao
                ORDER BY ano_realizacao;
            """)
            eventos_realizacao = cursor.fetchall()
            
            # APRESENTAÇÕES DE TRABALHO
            cursor.execute(f"""
                SELECT 'apresentacoes_trabalho' as tabela, CAST(ano AS INT) as ano, COUNT(*) as quantidade
                FROM stg.apresentacoes_trabalho
                WHERE ano IS NOT NULL 
                  AND ano ~ '^[0-9]+$'
                  AND CAST(ano AS INT) > {ano_atual}
                GROUP BY ano
                ORDER BY ano;
            """)
            apresentacoes = cursor.fetchall()
            
            # OUTRAS PRODUÇÕES
            cursor.execute(f"""
                SELECT 'outras_producoes' as tabela, CAST(ano AS INT) as ano, COUNT(*) as quantidade
                FROM stg.outras_producoes
                WHERE ano IS NOT NULL 
                  AND ano ~ '^[0-9]+$'
                  AND CAST(ano AS INT) > {ano_atual}
                GROUP BY ano
                ORDER BY ano;
            """)
            outras = cursor.fetchall()
            
            # PROJETOS (ano_inicio)
            cursor.execute(f"""
                SELECT 'projetos_pesquisa (ano_inicio)' as tabela, CAST(ano_inicio AS INT) as ano, COUNT(*) as quantidade
                FROM stg.projetos_pesquisa
                WHERE ano_inicio IS NOT NULL 
                  AND ano_inicio ~ '^[0-9]+$'
                  AND CAST(ano_inicio AS INT) > {ano_atual}
                GROUP BY ano_inicio
                ORDER BY ano_inicio;
            """)
            projetos_inicio = cursor.fetchall()
            
            # PROJETOS (ano_fim)
            cursor.execute(f"""
                SELECT 'projetos_pesquisa (ano_fim)' as tabela, CAST(ano_fim AS INT) as ano, COUNT(*) as quantidade
                FROM stg.projetos_pesquisa
                WHERE ano_fim IS NOT NULL 
                  AND ano_fim ~ '^[0-9]+$'
                  AND CAST(ano_fim AS INT) > {ano_atual}
                GROUP BY ano_fim
                ORDER BY ano_fim;
            """)
            projetos_fim = cursor.fetchall()
            
            todos_resultados = (artigos + livros + capitulos + textos + 
                              eventos_ano + eventos_realizacao + apresentacoes + 
                              outras + projetos_inicio + projetos_fim)
            
            if todos_resultados:
                print("ANOS INVÁLIDOS ENCONTRADOS (> 2026):\n")
                print(f"{'Tabela':<40} {'Ano':<10} {'Quantidade':<10}")
                print("-" * 60)
                
                for tabela, ano, qtd in todos_resultados:
                    print(f"{tabela:<40} {ano:<10} {qtd:<10}")
                
                print("\n" + "=" * 60)
                print(f"Total de registros com anos inválidos: {sum(r[2] for r in todos_resultados)}")
            else:
                print("Nenhum ano inválido encontrado (> 2026)!")
            
            print("\n\nVerificando anos muito antigos (< 1900)...\n")
            
            cursor.execute("""
                SELECT 'artigos' as tabela, CAST(ano AS INT) as ano, COUNT(*) as quantidade
                FROM stg.artigos
                WHERE ano IS NOT NULL 
                  AND ano ~ '^[0-9]+$'
                  AND CAST(ano AS INT) < 1900
                GROUP BY ano
                
                UNION ALL
                
                SELECT 'livros', CAST(ano AS INT), COUNT(*)
                FROM stg.livros
                WHERE ano IS NOT NULL AND ano ~ '^[0-9]+$' AND CAST(ano AS INT) < 1900
                GROUP BY ano
                
                UNION ALL
                
                SELECT 'capitulos_livros', CAST(ano AS INT), COUNT(*)
                FROM stg.capitulos_livros
                WHERE ano IS NOT NULL AND ano ~ '^[0-9]+$' AND CAST(ano AS INT) < 1900
                GROUP BY ano
                
                UNION ALL
                
                SELECT 'trabalhos_eventos', CAST(ano AS INT), COUNT(*)
                FROM stg.trabalhos_eventos
                WHERE ano IS NOT NULL AND ano ~ '^[0-9]+$' AND CAST(ano AS INT) < 1900
                GROUP BY ano
                
                UNION ALL
                
                SELECT 'apresentacoes_trabalho', CAST(ano AS INT), COUNT(*)
                FROM stg.apresentacoes_trabalho
                WHERE ano IS NOT NULL AND ano ~ '^[0-9]+$' AND CAST(ano AS INT) < 1900
                GROUP BY ano
                
                UNION ALL
                
                SELECT 'outras_producoes', CAST(ano AS INT), COUNT(*)
                FROM stg.outras_producoes
                WHERE ano IS NOT NULL AND ano ~ '^[0-9]+$' AND CAST(ano AS INT) < 1900
                GROUP BY ano
                
                ORDER BY ano;
            """)
            
            anos_antigos = cursor.fetchall()
            
            if anos_antigos:
                print(f"{'Tabela':<40} {'Ano':<10} {'Quantidade':<10}")
                print("-" * 60)
                for tabela, ano, qtd in anos_antigos:
                    print(f"{tabela:<40} {ano:<10} {qtd:<10}")
            else:
                print("Nenhum ano muito antigo encontrado (< 1900)!")
                
    except Exception as e:
        print(f"Erro: {e}")
        raise


if __name__ == "__main__":
    investigar_anos_invalidos()

