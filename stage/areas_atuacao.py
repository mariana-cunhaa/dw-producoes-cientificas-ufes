import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_areas_atuacao_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    areas_atuacao = []
    
    total_arquivos = 0
    arquivos_com_areas = 0

    for filename in os.listdir(pasta_json):
        if filename.endswith(".json"):
            total_arquivos += 1
            caminho_arquivo = os.path.join(pasta_json, filename)
            with open(caminho_arquivo, 'r', encoding='utf-8') as file:
                try:
                    dados = json.load(file)
                except Exception as e:
                    print(f"Erro ao ler {caminho_arquivo}: {e}")
                    continue

                areas_encontradas_neste_arquivo = 0
                
                curriculo_vitae = dados.get("CURRICULO-VITAE", {})
                
                # Id Lattes
                id_lattes = curriculo_vitae.get("@NUMERO-IDENTIFICADOR", "")
                
                # Nome (caso não tenha id_lattes)
                dados_gerais = curriculo_vitae.get("DADOS-GERAIS", {})
                nome = dados_gerais.get("@NOME-COMPLETO", "")
                
                if not id_lattes:
                    id_lattes = nome.replace(" ", "")
                
                # Navegar até AREAS-DE-ATUACAO
                areas_de_atuacao_obj = dados_gerais.get("AREAS-DE-ATUACAO")
                
                # Se não houver áreas de atuação, pular este currículo
                if not areas_de_atuacao_obj:
                    continue
                
                area_de_atuacao_list = areas_de_atuacao_obj.get("AREA-DE-ATUACAO", [])
                
                if isinstance(area_de_atuacao_list, dict):
                    area_de_atuacao_list = [area_de_atuacao_list]
                
                for area in area_de_atuacao_list:
                    if not isinstance(area, dict):
                        continue
                    
                    nome_grande_area = area.get("@NOME-GRANDE-AREA-DO-CONHECIMENTO", "")
                    nome_area = area.get("@NOME-DA-AREA-DO-CONHECIMENTO", "")
                    nome_sub_area = area.get("@NOME-DA-SUB-AREA-DO-CONHECIMENTO", "")
                    nome_especialidade = area.get("@NOME-DA-ESPECIALIDADE", "")
                    
                    # Inserir apenas se houver pelo menos o nome da área
                    if id_lattes and nome_area:
                        areas_atuacao.append({
                            "id_lattes": id_lattes,
                            "nome_grande_area": nome_grande_area,
                            "nome_area": nome_area,
                            "nome_sub_area": nome_sub_area,
                            "nome_especialidade": nome_especialidade
                        })
                        areas_encontradas_neste_arquivo += 1
                
                if areas_encontradas_neste_arquivo > 0:
                    arquivos_com_areas += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com áreas de atuação: {arquivos_com_areas}")
    print(f"   - Arquivos sem áreas de atuação: {total_arquivos - arquivos_com_areas}")
    
    return areas_atuacao

def salvar_no_banco(areas_atuacao):
    """Salva as áreas de atuação no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True  
        cursor = conn.cursor()
        
        contador_inseridos = 0
        contador_erros = 0
        
        for area in areas_atuacao:
            try:
                id_lattes = area['id_lattes']
                nome_grande_area = area['nome_grande_area'][:255] if area['nome_grande_area'] else None
                nome_area = area['nome_area'][:255] if area['nome_area'] else None
                nome_sub_area = area['nome_sub_area'][:255] if area['nome_sub_area'] else None
                nome_especialidade = area['nome_especialidade'][:255] if area['nome_especialidade'] else None
                
                if id_lattes and nome_area:
                    cursor.execute("""
                        INSERT INTO stg.areas_atuacao (
                            id_lattes, 
                            nome_grande_area, 
                            nome_area, 
                            nome_sub_area, 
                            nome_especialidade
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (id_lattes, nome_grande_area, nome_area, nome_sub_area, nome_especialidade))
                    contador_inseridos += 1
                    
                    if contador_inseridos % 1000 == 0:
                        print(f"   Progresso: {contador_inseridos} áreas inseridas...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de áreas de atuação inseridas: {contador_inseridos}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração das áreas de atuação dos currículos...")
    areas_atuacao = parse_areas_atuacao_json()
    
    print(f"\nTotal de áreas de atuação encontradas: {len(areas_atuacao)}")
    
    if areas_atuacao:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(areas_atuacao)
    else:
        print("Nenhuma área de atuação encontrada para salvar.")

if __name__ == "__main__":
    main()

