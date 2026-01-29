import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_capitulos_livros_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    capitulos = []
    
    total_arquivos = 0
    arquivos_com_capitulos = 0

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

                capitulos_encontrados_neste_arquivo = 0
                
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
                
                capitulos_livros_pub = livros_capitulos.get("CAPITULOS-DE-LIVROS-PUBLICADOS")
                
                if not capitulos_livros_pub:
                    continue
                
                capitulo_livro_list = capitulos_livros_pub.get("CAPITULO-DE-LIVRO-PUBLICADO", [])
                
                if isinstance(capitulo_livro_list, dict):
                    capitulo_livro_list = [capitulo_livro_list]
                
                for capitulo in capitulo_livro_list:
                    if not isinstance(capitulo, dict):
                        continue
                    
                    dados_basicos = capitulo.get("DADOS-BASICOS-DO-CAPITULO", {})
                    
                    if not isinstance(dados_basicos, dict):
                        continue
                    
                    titulo_capitulo = dados_basicos.get("@TITULO-DO-CAPITULO-DO-LIVRO", "")
                    ano = dados_basicos.get("@ANO", "")
                    doi = dados_basicos.get("@DOI", "")
                    idioma = dados_basicos.get("@IDIOMA", "")
                    meio_divulgacao = dados_basicos.get("@MEIO-DE-DIVULGACAO", "")
                    
                    detalhamento = capitulo.get("DETALHAMENTO-DO-CAPITULO", {})
                    
                    if isinstance(detalhamento, dict):
                        titulo_livro = detalhamento.get("@TITULO-DO-LIVRO", "")
                        numero_edicao = detalhamento.get("@NUMERO-DA-EDICAO-REVISAO", "")
                        cidade_editora = detalhamento.get("@CIDADE-DA-EDITORA", "")
                        nome_editora = detalhamento.get("@NOME-DA-EDITORA", "")
                        isbn = detalhamento.get("@ISBN", "")
                        pagina_inicial = detalhamento.get("@PAGINA-INICIAL", "")
                        pagina_final = detalhamento.get("@PAGINA-FINAL", "")
                        organizadores = detalhamento.get("@ORGANIZADORES", "")
                    else:
                        titulo_livro = numero_edicao = cidade_editora = nome_editora = ""
                        isbn = pagina_inicial = pagina_final = organizadores = ""
                    
                    if id_lattes and titulo_capitulo:
                        autores = capitulo.get("AUTORES", [])
                        
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
                        
                        capitulos.append({
                            "id_lattes": id_lattes,
                            "ano": ano,
                            "titulo_capitulo": titulo_capitulo,
                            "titulo_livro": titulo_livro,
                            "doi": doi,
                            "idioma": idioma,
                            "meio_divulgacao": meio_divulgacao,
                            "numero_edicao": numero_edicao,
                            "cidade_editora": cidade_editora,
                            "nome_editora": nome_editora,
                            "isbn": isbn,
                            "pagina_inicial": pagina_inicial,
                            "pagina_final": pagina_final,
                            "organizadores": organizadores,
                            "autores": autores_concatenados
                        })
                        capitulos_encontrados_neste_arquivo += 1
                
                if capitulos_encontrados_neste_arquivo > 0:
                    arquivos_com_capitulos += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com capítulos de livros: {arquivos_com_capitulos}")
    print(f"   - Arquivos sem capítulos de livros: {total_arquivos - arquivos_com_capitulos}")
    
    return capitulos

def salvar_no_banco(capitulos):
    """Salva os capítulos de livros no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True
        cursor = conn.cursor()
        
        contador_capitulos = 0
        contador_erros = 0
        
        print("\nInserindo capítulos de livros...")
        for capitulo in capitulos:
            try:
                id_lattes = capitulo['id_lattes']
                ano = capitulo['ano'][:10] if capitulo['ano'] else None
                titulo_capitulo = capitulo['titulo_capitulo'][:1000] if capitulo['titulo_capitulo'] else None
                titulo_livro = capitulo['titulo_livro'][:1000] if capitulo['titulo_livro'] else None
                doi = capitulo['doi'][:255] if capitulo['doi'] else None
                idioma = capitulo['idioma'][:50] if capitulo['idioma'] else None
                meio_divulgacao = capitulo['meio_divulgacao'][:50] if capitulo['meio_divulgacao'] else None
                numero_edicao = capitulo['numero_edicao'][:50] if capitulo['numero_edicao'] else None
                cidade_editora = capitulo['cidade_editora'][:255] if capitulo['cidade_editora'] else None
                nome_editora = capitulo['nome_editora'][:255] if capitulo['nome_editora'] else None
                isbn = capitulo['isbn'][:50] if capitulo['isbn'] else None
                pagina_inicial = capitulo['pagina_inicial'][:10] if capitulo['pagina_inicial'] else None
                pagina_final = capitulo['pagina_final'][:10] if capitulo['pagina_final'] else None
                organizadores = capitulo['organizadores'][:1000] if capitulo['organizadores'] else None
                autores = capitulo['autores'] or None
                
                if id_lattes and titulo_capitulo:
                    cursor.execute("""
                        INSERT INTO stg.capitulos_livros (
                            id_lattes, ano, titulo_capitulo, titulo_livro, doi, idioma,
                            meio_divulgacao, numero_edicao, cidade_editora, nome_editora,
                            isbn, pagina_inicial, pagina_final, organizadores, autores
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id_lattes, ano, titulo_capitulo, titulo_livro, doi, idioma, meio_divulgacao,
                          numero_edicao, cidade_editora, nome_editora, isbn, pagina_inicial,
                          pagina_final, organizadores, autores))
                    
                    contador_capitulos += 1
                    
                    if contador_capitulos % 1000 == 0:
                        print(f"   Progresso: {contador_capitulos} capítulos inseridos...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de capítulos de livros inseridos: {contador_capitulos}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração dos capítulos de livros dos currículos...")
    capitulos = parse_capitulos_livros_json()
    
    print(f"\nTotal de capítulos de livros encontrados: {len(capitulos)}")
    
    if capitulos:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(capitulos)
    else:
        print("Nenhum capítulo de livro encontrado para salvar.")

if __name__ == "__main__":
    main()

