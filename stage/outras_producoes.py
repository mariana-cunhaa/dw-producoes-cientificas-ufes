import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_outras_producoes_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    outras_producoes = []
    
    total_arquivos = 0
    arquivos_com_outras = 0

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

                outras_encontradas_neste_arquivo = 0
                
                curriculo_vitae = dados.get("CURRICULO-VITAE", {})
                
                # Id Lattes
                id_lattes = curriculo_vitae.get("@NUMERO-IDENTIFICADOR", "")
                
                # Nome (caso não tenha id_lattes)
                dados_gerais = curriculo_vitae.get("DADOS-GERAIS", {})
                nome = dados_gerais.get("@NOME-COMPLETO", "")
                
                if not id_lattes:
                    id_lattes = nome.replace(" ", "")
                
                producao_bibliografica = curriculo_vitae.get("PRODUCAO-BIBLIOGRAFICA")
                
                if not producao_bibliografica:
                    continue
                
                demais_tipos = producao_bibliografica.get("DEMAIS-TIPOS-DE-PRODUCAO-BIBLIOGRAFICA")
                
                if not demais_tipos:
                    continue
                
                outra_producao_list = demais_tipos.get("OUTRA-PRODUCAO-BIBLIOGRAFICA", [])
                
                if isinstance(outra_producao_list, dict):
                    outra_producao_list = [outra_producao_list]
                
                for outra in outra_producao_list:
                    if not isinstance(outra, dict):
                        continue
                    
                    dados_basicos = outra.get("DADOS-BASICOS-DE-OUTRA-PRODUCAO", {})
                    
                    if not isinstance(dados_basicos, dict):
                        continue
                    
                    titulo = dados_basicos.get("@TITULO", "")
                    ano = dados_basicos.get("@ANO", "")
                    doi = dados_basicos.get("@DOI", "")
                    idioma = dados_basicos.get("@IDIOMA", "")
                    natureza = dados_basicos.get("@NATUREZA", "")
                    meio_divulgacao = dados_basicos.get("@MEIO-DE-DIVULGACAO", "")
                    pais_publicacao = dados_basicos.get("@PAIS-DE-PUBLICACAO", "")
                    
                    detalhamento = outra.get("DETALHAMENTO-DE-OUTRA-PRODUCAO", {})
                    
                    if isinstance(detalhamento, dict):
                        cidade_editora = detalhamento.get("@CIDADE-DA-EDITORA", "")
                        editora = detalhamento.get("@EDITORA", "")
                        issn_isbn = detalhamento.get("@ISSN-ISBN", "")
                        numero_paginas = detalhamento.get("@NUMERO-DE-PAGINAS", "")
                    else:
                        cidade_editora = editora = issn_isbn = numero_paginas = ""
                    
                    if id_lattes and titulo:
                        autores = outra.get("AUTORES", [])
                        
                        if isinstance(autores, dict):
                            autores = [autores]
                        
                        lista_autores = []
                        for autor in autores:
                            if isinstance(autor, dict):
                                nome_para_citacao = autor.get("@NOME-PARA-CITACAO", "")
                                ordem_autoria = autor.get("@ORDEM-DE-AUTORIA", "")
                                
                                if nome_para_citacao:
                                    lista_autores.append(f"{ordem_autoria}|{nome_para_citacao}")
                        
                        autores_concatenados = "; ".join(lista_autores) if lista_autores else ""
                        
                        outras_producoes.append({
                            "id_lattes": id_lattes,
                            "ano": ano,
                            "titulo": titulo,
                            "doi": doi,
                            "idioma": idioma,
                            "natureza": natureza,
                            "meio_divulgacao": meio_divulgacao,
                            "pais_publicacao": pais_publicacao,
                            "cidade_editora": cidade_editora,
                            "editora": editora,
                            "issn_isbn": issn_isbn,
                            "numero_paginas": numero_paginas,
                            "autores": autores_concatenados
                        })
                        outras_encontradas_neste_arquivo += 1
                
                if outras_encontradas_neste_arquivo > 0:
                    arquivos_com_outras += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com outras produções bibliográficas: {arquivos_com_outras}")
    print(f"   - Arquivos sem outras produções bibliográficas: {total_arquivos - arquivos_com_outras}")
    
    return outras_producoes

def salvar_no_banco(outras_producoes):
    """Salva as outras produções bibliográficas no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True
        cursor = conn.cursor()
        
        contador_outras = 0
        contador_erros = 0
        
        print("\nInserindo outras produções bibliográficas...")
        for outra in outras_producoes:
            try:
                id_lattes = outra['id_lattes']
                ano = outra['ano'][:10] if outra['ano'] else None
                titulo = outra['titulo'][:1000] if outra['titulo'] else None
                doi = outra['doi'][:255] if outra['doi'] else None
                idioma = outra['idioma'][:50] if outra['idioma'] else None
                natureza = outra['natureza'][:200] if outra['natureza'] else None
                meio_divulgacao = outra['meio_divulgacao'][:50] if outra['meio_divulgacao'] else None
                pais_publicacao = outra['pais_publicacao'][:100] if outra['pais_publicacao'] else None
                cidade_editora = outra['cidade_editora'][:255] if outra['cidade_editora'] else None
                editora = outra['editora'][:500] if outra['editora'] else None
                issn_isbn = outra['issn_isbn'][:50] if outra['issn_isbn'] else None
                numero_paginas = outra['numero_paginas'][:20] if outra['numero_paginas'] else None
                autores = outra['autores'] or None
                
                if id_lattes and titulo:
                    cursor.execute("""
                        INSERT INTO stg.outras_producoes (
                            id_lattes, ano, titulo, doi, idioma, natureza,
                            meio_divulgacao, pais_publicacao, cidade_editora, editora,
                            issn_isbn, numero_paginas, autores
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id_lattes, ano, titulo, doi, idioma, natureza, meio_divulgacao,
                          pais_publicacao, cidade_editora, editora, issn_isbn, numero_paginas, autores))
                    
                    contador_outras += 1
                    
                    if contador_outras % 1000 == 0:
                        print(f"   Progresso: {contador_outras} produções inseridas...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de outras produções bibliográficas inseridas: {contador_outras}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração das outras produções bibliográficas dos currículos...")
    outras_producoes = parse_outras_producoes_json()
    
    print(f"\nTotal de outras produções bibliográficas encontradas: {len(outras_producoes)}")
    
    if outras_producoes:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(outras_producoes)
    else:
        print("Nenhuma outra produção bibliográfica encontrada para salvar.")

if __name__ == "__main__":
    main()

