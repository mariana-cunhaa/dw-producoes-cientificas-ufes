import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_cursor

def popular_dim_area():
    """
    Popula a tabela dw.dim_area com dados da tabela stg.areas_atuacao.
    Extrai áreas de conhecimento únicas dos pesquisadores.
    """
    
    try:
        query = """
        INSERT INTO dw.dim_area (
            grande_area,
            area
        )
        SELECT DISTINCT
            nome_grande_area AS grande_area,
            nome_area        AS area
        FROM stg.areas_atuacao
        WHERE nome_area IS NOT NULL;
        """
        
        with obter_cursor() as cursor:
            cursor.execute(query)
            registros_inseridos = cursor.rowcount
            
            print(f"Tabela dw.dim_area populada com sucesso!")
            print(f"Total de registros inseridos: {registros_inseridos}")
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(grande_area) as com_grande_area,
                    COUNT(area) as com_area
                FROM dw.dim_area;
            """)
            
            cursor.execute("""
                SELECT grande_area, area
                FROM dw.dim_area
                LIMIT 5;
            """)
            
            amostra = cursor.fetchall()
            if amostra:
                for i, (ga, a) in enumerate(amostra, 1):
                    print(f"   {i}. Grande Área: {ga or 'N/A'}")
                    print(f"      Área: {a or 'N/A'}")
                    print()
        
    except Exception as e:
        print(f"Erro ao popular dim_area: {e}")
        raise


if __name__ == "__main__":
    popular_dim_area()

