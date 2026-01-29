import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_livros_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    livros = []
    
    total_arquivos = 0
    arquivos_com_livros = 0

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

                livros_encontrados_neste_arquivo = 0
                
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
                
                livros_capitulos = producao_bibliografica.get("LIVROS-E-CAPITULOS")
                
                if not livros_capitulos:
                    continue
                
                livros_pub_org = livros_capitulos.get("LIVROS-PUBLICADOS-OU-ORGANIZADOS")
                
                if not livros_pub_org:
                    continue
                
                livro_publicado_list = livros_pub_org.get("LIVRO-PUBLICADO-OU-ORGANIZADO", [])
                
                if isinstance(livro_publicado_list, dict):
                    livro_publicado_list = [livro_publicado_list]
                
                for livro in livro_publicado_list:
                    if not isinstance(livro, dict):
                        continue
                    
                    dados_basicos = livro.get("DADOS-BASICOS-DO-LIVRO", {})
                    
                    if not isinstance(dados_basicos, dict):
                        continue
                    
                    titulo = dados_basicos.get("@TITULO-DO-LIVRO", "")
                    ano = dados_basicos.get("@ANO", "")
                    
                    detalhamento = livro.get("DETALHAMENTO-DO-LIVRO", {})
                    
                    if isinstance(detalhamento, dict):
                        numero_edicao = detalhamento.get("@NUMERO-DA-EDICAO-REVISAO", "")
                        cidade_editora = detalhamento.get("@CIDADE-DA-EDITORA", "")
                        nome_editora = detalhamento.get("@NOME-DA-EDITORA", "")
                        numero_volumes = detalhamento.get("@NUMERO-DE-VOLUMES", "")
                        numero_paginas = detalhamento.get("@NUMERO-DE-PAGINAS", "")
                    else:
                        numero_edicao = cidade_editora = nome_editora = numero_volumes = numero_paginas = ""
                    
                    if id_lattes and titulo:
                        autores = livro.get("AUTORES", [])
                        
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
                        
                        livros.append({
                            "id_lattes": id_lattes,
                            "ano": ano,
                            "titulo": titulo,
                            "numero_edicao": numero_edicao,
                            "cidade_editora": cidade_editora,
                            "nome_editora": nome_editora,
                            "numero_volumes": numero_volumes,
                            "numero_paginas": numero_paginas,
                            "autores": autores_concatenados
                        })
                        livros_encontrados_neste_arquivo += 1
                
                if livros_encontrados_neste_arquivo > 0:
                    arquivos_com_livros += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com livros: {arquivos_com_livros}")
    print(f"   - Arquivos sem livros: {total_arquivos - arquivos_com_livros}")
    
    return livros

def salvar_no_banco(livros):
    """Salva os livros no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True
        cursor = conn.cursor()
        
        contador_livros = 0
        contador_erros = 0
        
        print("\nInserindo livros...")
        for livro in livros:
            try:
                id_lattes = livro['id_lattes']
                ano = livro['ano'][:10] if livro['ano'] else None
                titulo = livro['titulo'][:1000] if livro['titulo'] else None
                numero_edicao = livro['numero_edicao'][:50] if livro['numero_edicao'] else None
                cidade_editora = livro['cidade_editora'][:255] if livro['cidade_editora'] else None
                nome_editora = livro['nome_editora'][:255] if livro['nome_editora'] else None
                numero_volumes = livro['numero_volumes'][:50] if livro['numero_volumes'] else None
                numero_paginas = livro['numero_paginas'][:50] if livro['numero_paginas'] else None
                autores = livro['autores'] or None
                
                if id_lattes and titulo:
                    cursor.execute("""
                        INSERT INTO stg.livros (
                            id_lattes, ano, titulo, numero_edicao, cidade_editora,
                            nome_editora, numero_volumes, numero_paginas, autores
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id_lattes, ano, titulo, numero_edicao, cidade_editora,
                          nome_editora, numero_volumes, numero_paginas, autores))
                    
                    contador_livros += 1
                    
                    if contador_livros % 1000 == 0:
                        print(f"   Progresso: {contador_livros} livros inseridos...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de livros inseridos: {contador_livros}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração dos livros dos currículos...")
    livros = parse_livros_json()
    
    print(f"\nTotal de livros encontrados: {len(livros)}")
    
    if livros:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(livros)
    else:
        print("Nenhum livro encontrado para salvar.")

if __name__ == "__main__":
    main()

