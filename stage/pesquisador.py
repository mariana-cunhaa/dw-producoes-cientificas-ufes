import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_curriculos_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    curriculos = []

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

                dados_gerais = curriculo_vitae.get("DADOS-GERAIS", {})
                
                # Nome 
                nome = dados_gerais.get("@NOME-COMPLETO", "")

                # Id Lattes
                id_lattes = curriculo_vitae.get("@NUMERO-IDENTIFICADOR", "")

                if not id_lattes:
                    id_lattes_ajustado = nome.replace(" ", "")
                else:
                    id_lattes_ajustado = id_lattes

                # Atuação profissional
                atuacao_profissional = ""
                dados_gerais = curriculo_vitae.get("DADOS-GERAIS", {})
                endereco = dados_gerais.get("ENDERECO", {})
                if isinstance(endereco, dict):
                    end_prof = endereco.get("ENDERECO-PROFISSIONAL", {})
                    if isinstance(end_prof, dict):
                        atuacao_profissional = end_prof.get("@NOME-INSTITUICAO-EMPRESA", "")

                curriculos.append({
                    "id_lattes": id_lattes_ajustado,
                    "nome": nome,
                    "atuacao_profissional": atuacao_profissional
                })
    
    return curriculos

def salvar_no_banco(curriculos):
    """Salva os dados dos pesquisadores no banco de dados"""
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        contador_inseridos = 0
        contador_erros = 0
        
        for curriculo in curriculos:
            try:
                id_lattes = curriculo['id_lattes']
                nome = curriculo['nome'][:100] if curriculo['nome'] else None
                atuacao = curriculo['atuacao_profissional'] or None

                if not id_lattes:
                    id_lattes = (nome or "").replace(" ", "")
                    print(f"id_lattes ausente, usando nome formatado sem espaços como id_lattes: {id_lattes}")

                if id_lattes and nome:
                    cursor.execute("""
                        INSERT INTO stg.pesquisador (id_lattes, nome, atuacao_profissional)
                        VALUES (%s, %s, %s)
                    """, (id_lattes, nome, atuacao))
                    contador_inseridos += 1
                else:
                    print(f"Ignorado: pesquisador sem nome ou ID (Nome: {nome}, ID: {id_lattes})")
                    contador_erros += 1
                    
            except Exception as e:
                print(f"Erro ao inserir {curriculo['nome']}: {e}")
                contador_erros += 1
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de pesquisadores inseridos: {contador_inseridos}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração dos currículos...")
    curriculos = parse_curriculos_json()
    
    print(f"\nTotal de currículos encontrados: {len(curriculos)}")
    
    if curriculos:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(curriculos)
    else:
        print("Nenhum currículo encontrado para salvar.")

if __name__ == "__main__":
    main()