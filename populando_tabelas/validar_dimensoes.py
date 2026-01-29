import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor

def validar_dimensoes():
    """
    Valida todas as tabelas dimensão criadas.
    """
    
    try:
        with obter_cursor() as cursor:
            
            cursor.execute("SELECT COUNT(*) FROM dw.dim_pesquisador;")
            total = cursor.fetchone()[0]
            print(f"   Total de pesquisadores: {total}")
            
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT id_lattes) as unicos,
                    COUNT(*) as total
                FROM dw.dim_pesquisador;
            """)
            unicos, total_reg = cursor.fetchone()
            print(f"   ID Lattes únicos: {unicos}")
            if unicos != total_reg:
                print(f"ATENÇÃO: Há {total_reg - unicos} registros duplicados!")
            else:
                print(f"Sem duplicatas")
            
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN nome IS NULL OR nome = '' THEN 1 END) as sem_nome,
                    COUNT(CASE WHEN atuacao_profissional IS NULL OR atuacao_profissional = '' THEN 1 END) as sem_atuacao
                FROM dw.dim_pesquisador;
            """)
            sem_nome, sem_atuacao = cursor.fetchone()
            print(f"   Sem nome: {sem_nome}")
            print(f"   Sem atuação: {sem_atuacao}")
            
            cursor.execute("SELECT COUNT(*) FROM dw.dim_area;")
            total = cursor.fetchone()[0]
            print(f"   Total de áreas: {total}")
            
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT grande_area) as grandes_areas,
                    COUNT(DISTINCT area) as areas,
                    COUNT(DISTINCT sub_area) as sub_areas,
                    COUNT(DISTINCT especialidade) as especialidades
                FROM dw.dim_area;
            """)
            ga, a, sa, e = cursor.fetchone()
            print(f"   Grandes áreas únicas: {ga}")
            print(f"   Áreas únicas: {a}")
            print(f"   Sub-áreas únicas: {sa}")
            print(f"   Especialidades únicas: {e}")
            
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT grande_area, area, sub_area, especialidade, COUNT(*) as qtd
                    FROM dw.dim_area
                    GROUP BY grande_area, area, sub_area, especialidade
                    HAVING COUNT(*) > 1
                ) duplicatas;
            """)
            duplicatas = cursor.fetchone()[0]
            if duplicatas > 0:
                print(f"ATENÇÃO: {duplicatas} combinações duplicadas!")
            else:
                print(f"Sem duplicatas")
            
            cursor.execute("SELECT COUNT(*) FROM dw.dim_tempo;")
            total = cursor.fetchone()[0]
            print(f"   Total de anos: {total}")
            
            cursor.execute("""
                SELECT 
                    MIN(ano) as ano_min,
                    MAX(ano) as ano_max
                FROM dw.dim_tempo;
            """)
            ano_min, ano_max = cursor.fetchone()
            print(f"   Período: {ano_min} a {ano_max}")
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM dw.dim_tempo
                WHERE ano < 1900 OR ano > 2026;
            """)
            invalidos = cursor.fetchone()[0]
            if invalidos > 0:
                print(f"ATENÇÃO: {invalidos} anos fora do intervalo válido (1900-2026)!")
            else:
                print(f"Todos os anos estão no intervalo válido")
            
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT ano, COUNT(*) as qtd
                    FROM dw.dim_tempo
                    GROUP BY ano
                    HAVING COUNT(*) > 1
                ) duplicatas;
            """)
            duplicatas = cursor.fetchone()[0]
            if duplicatas > 0:
                print(f"ATENÇÃO: {duplicatas} anos duplicados!")
            else:
                print(f"Sem duplicatas")
            
            cursor.execute("SELECT COUNT(*) FROM dw.dim_localizacao;")
            total = cursor.fetchone()[0]
            print(f"   Total de localizações: {total}")
            
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN pais IS NOT NULL AND pais != '' THEN 1 END) as com_pais,
                    COUNT(CASE WHEN cidade IS NOT NULL AND cidade != '' THEN 1 END) as com_cidade,
                    COUNT(CASE WHEN local_especifico IS NOT NULL AND local_especifico != '' THEN 1 END) as com_local,
                    COUNT(CASE WHEN instituicao IS NOT NULL AND instituicao != '' THEN 1 END) as com_instituicao
                FROM dw.dim_localizacao;
            """)
            pais, cidade, local, inst = cursor.fetchone()
            print(f"   Com país: {pais}")
            print(f"   Com cidade: {cidade}")
            print(f"   Com local específico: {local}")
            print(f"   Com instituição: {inst}")
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM dw.dim_localizacao
                WHERE (pais IS NULL OR pais = '')
                  AND (cidade IS NULL OR cidade = '')
                  AND (local_especifico IS NULL OR local_especifico = '')
                  AND (instituicao IS NULL OR instituicao = '');
            """)
            vazios = cursor.fetchone()[0]
            if vazios > 0:
                print(f"ATENÇÃO: {vazios} registros completamente vazios!")
            else:
                print(f"Nenhum registro vazio")
            
            cursor.execute("SELECT COUNT(*) FROM dw.dim_tipo_producao;")
            total = cursor.fetchone()[0]
            print(f"   Total de tipos de produção: {total}")
            
            cursor.execute("""
                SELECT 
                    tipo_producao,
                    COUNT(*) as variações
                FROM dw.dim_tipo_producao
                GROUP BY tipo_producao
                ORDER BY tipo_producao;
            """)
            tipos = cursor.fetchall()
            print(f"Distribuição por tipo:")
            for tipo, variações in tipos:
                print(f"      • {tipo}: {variações} variação(ões)")
            
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN natureza IS NOT NULL AND natureza != '' THEN 1 END) as com_natureza,
                    COUNT(CASE WHEN meio_divulgacao IS NOT NULL AND meio_divulgacao != '' THEN 1 END) as com_meio
                FROM dw.dim_tipo_producao;
            """)
            nat, meio = cursor.fetchone()
            print(f"Com natureza preenchida: {nat}")
            print(f"   Com meio de divulgação preenchido: {meio}")
            
            cursor.execute("""
                SELECT 
                    'dim_pesquisador' as tabela,
                    COUNT(*) as registros
                FROM dw.dim_pesquisador
                UNION ALL
                SELECT 'dim_area', COUNT(*) FROM dw.dim_area
                UNION ALL
                SELECT 'dim_tempo', COUNT(*) FROM dw.dim_tempo
                UNION ALL
                SELECT 'dim_localizacao', COUNT(*) FROM dw.dim_localizacao
                UNION ALL
                SELECT 'dim_tipo_producao', COUNT(*) FROM dw.dim_tipo_producao;
            """)
            
            resumo = cursor.fetchall()
            print(f"\n{'Tabela':<25} {'Registros':>15}")
            print("-" * 40)
            total_geral = 0
            for tabela, qtd in resumo:
                print(f"{tabela:<25} {qtd:>15,}")
                total_geral += qtd
            print("-" * 40)
            print(f"{'TOTAL':<25} {total_geral:>15,}")
            
            
    except Exception as e:
        print(f"Erro durante validação: {e}")
        raise


if __name__ == "__main__":
    validar_dimensoes()

