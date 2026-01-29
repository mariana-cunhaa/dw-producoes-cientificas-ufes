import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_linhas_pesquisa_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    linhas_pesquisa = []

    for filename in os.listdir(pasta_json):
        if filename.endswith(".json"):
            caminho_arquivo = os.path.join(pasta_json, filename)
            with open(caminho_arquivo, 'r', encoding='utf-8') as file:
                try:
                    dados = json.load(file)
                except Exception as e:
                    print(f"Erro ao ler {caminho_arquivo}: {e}")
                    continue

                curriculo_vitae = dados.get("CURRICULO-VITAE", {})
                
                # Id Lattes
                id_lattes = curriculo_vitae.get("@NUMERO-IDENTIFICADOR", "")
                
                # Nome (caso não tenha id_lattes)
                dados_gerais = curriculo_vitae.get("DADOS-GERAIS", {})
                nome = dados_gerais.get("@NOME-COMPLETO", "")
                
                if not id_lattes:
                    id_lattes = nome.replace(" ", "")
                
                atuacoes_profissionais = dados_gerais.get("ATUACOES-PROFISSIONAIS")
                
                if not atuacoes_profissionais:
                    continue
                
                atuacao_profissional_list = atuacoes_profissionais.get("ATUACAO-PROFISSIONAL", [])
                
                if isinstance(atuacao_profissional_list, dict):
                    atuacao_profissional_list = [atuacao_profissional_list]
                
                for atuacao in atuacao_profissional_list:
                    if not isinstance(atuacao, dict):
                        continue
                    
                    atividades_pesquisa = atuacao.get("ATIVIDADES-DE-PESQUISA-E-DESENVOLVIMENTO", {})
                    
                    pesquisa_desenvolvimento_list = atividades_pesquisa.get("PESQUISA-E-DESENVOLVIMENTO", [])
                    
                    if isinstance(pesquisa_desenvolvimento_list, dict):
                        pesquisa_desenvolvimento_list = [pesquisa_desenvolvimento_list]
                    
                    for pesquisa in pesquisa_desenvolvimento_list:
                        if not isinstance(pesquisa, dict):
                            continue
                        
                        linha_pesquisa_list = pesquisa.get("LINHA-DE-PESQUISA", [])
                        
                        if isinstance(linha_pesquisa_list, dict):
                            linha_pesquisa_list = [linha_pesquisa_list]
                        
                        for linha in linha_pesquisa_list:
                            if not isinstance(linha, dict):
                                continue
                            
                            titulo_linha = linha.get("@TITULO-DA-LINHA-DE-PESQUISA", "")
                            
                            if titulo_linha and id_lattes:
                                linhas_pesquisa.append({
                                    "id_lattes": id_lattes,
                                    "linha_pesquisa": titulo_linha
                                })
    
    return linhas_pesquisa

def salvar_no_banco(linhas_pesquisa):
    """Salva as linhas de pesquisa no banco de dados"""
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        contador_inseridos = 0
        contador_erros = 0
        
        for linha in linhas_pesquisa:
            try:
                id_lattes = linha['id_lattes']
                linha_pesquisa = linha['linha_pesquisa'][:500] if linha['linha_pesquisa'] else None
                
                if id_lattes and linha_pesquisa:
                    cursor.execute("""
                        INSERT INTO stg.linha_pesquisa (id_lattes, linha_pesquisa)
                        VALUES (%s, %s)
                    """, (id_lattes, linha_pesquisa))
                    contador_inseridos += 1
                else:
                    print(f"Ignorado: linha sem ID ou título (ID: {id_lattes}, Linha: {linha_pesquisa})")
                    contador_erros += 1
                    
            except Exception as e:
                print(f"Erro ao inserir linha '{linha['linha_pesquisa']}': {e}")
                contador_erros += 1
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de linhas de pesquisa inseridas: {contador_inseridos}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração das linhas de pesquisa dos currículos...")
    linhas_pesquisa = parse_linhas_pesquisa_json()
    
    print(f"\nTotal de linhas de pesquisa encontradas: {len(linhas_pesquisa)}")
    
    if linhas_pesquisa:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(linhas_pesquisa)
    else:
        print("Nenhuma linha de pesquisa encontrada para salvar.")

if __name__ == "__main__":
    main()

