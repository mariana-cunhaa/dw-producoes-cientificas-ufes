import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_artigos_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    artigos = []
    
    total_arquivos = 0
    arquivos_com_artigos = 0

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

                artigos_encontrados_neste_arquivo = 0
                
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
                
                artigos_publicados = producao_bibliografica.get("ARTIGOS-PUBLICADOS")
                
                if not artigos_publicados:
                    os.CLD_CONTINUED
                artigo_publicado_list = artigos_publicados.get("ARTIGO-PUBLICADO", [])
                
                if isinstance(artigo_publicado_list, dict):
                    artigo_publicado_list = [artigo_publicado_list]
                
                for artigo in artigo_publicado_list:
                    if not isinstance(artigo, dict):
                        continue
                    
                    dados_basicos = artigo.get("DADOS-BASICOS-DO-ARTIGO", {})
                    
                    if not isinstance(dados_basicos, dict):
                        continue
                    
                    ano = dados_basicos.get("@ANO-DO-ARTIGO", "")
                    titulo = dados_basicos.get("@TITULO-DO-ARTIGO", "")
                    doi = dados_basicos.get("@DOI", "")
                    idioma = dados_basicos.get("@IDIOMA", "")
                    natureza = dados_basicos.get("@NATUREZA", "")
                    meio_divulgacao = dados_basicos.get("@MEIO-DE-DIVULGACAO", "")
                    
                    detalhamento = artigo.get("DETALHAMENTO-DO-ARTIGO", {})
                    
                    if isinstance(detalhamento, dict):
                        titulo_periodico = detalhamento.get("@TITULO-DO-PERIODICO-OU-REVISTA", "")
                        volume = detalhamento.get("@VOLUME", "")
                        pagina_inicial = detalhamento.get("@PAGINA-INICIAL", "")
                        pagina_final = detalhamento.get("@PAGINA-FINAL", "")
                        issn = detalhamento.get("@ISSN", "")
                        local_publicacao = detalhamento.get("@LOCAL-DE-PUBLICACAO", "")
                    else:
                        titulo_periodico = volume = pagina_inicial = pagina_final = issn = local_publicacao = ""
                    
                    if id_lattes and titulo:
                        autores = artigo.get("AUTORES", [])
                        
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
                        
                        artigos.append({
                            "id_lattes": id_lattes,
                            "ano": ano,
                            "titulo": titulo,
                            "doi": doi,
                            "idioma": idioma,
                            "natureza": natureza,
                            "meio_divulgacao": meio_divulgacao,
                            "titulo_periodico": titulo_periodico,
                            "volume": volume,
                            "pagina_inicial": pagina_inicial,
                            "pagina_final": pagina_final,
                            "issn": issn,
                            "local_publicacao": local_publicacao,
                            "autores": autores_concatenados
                        })
                        artigos_encontrados_neste_arquivo += 1
                
                if artigos_encontrados_neste_arquivo > 0:
                    arquivos_com_artigos += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com artigos: {arquivos_com_artigos}")
    print(f"   - Arquivos sem artigos: {total_arquivos - arquivos_com_artigos}")
    
    return artigos

def salvar_no_banco(artigos):
    """Salva os artigos no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True
        cursor = conn.cursor()
        
        contador_artigos = 0
        contador_erros = 0
        
        print("\nInserindo artigos...")
        for artigo in artigos:
            try:
                id_lattes = artigo['id_lattes']
                ano = artigo['ano'] or None
                titulo = artigo['titulo'][:1000] if artigo['titulo'] else None
                doi = artigo['doi'][:255] if artigo['doi'] else None
                idioma = artigo['idioma'][:50] if artigo['idioma'] else None
                natureza = artigo['natureza'][:50] if artigo['natureza'] else None
                meio_divulgacao = artigo['meio_divulgacao'][:50] if artigo['meio_divulgacao'] else None
                titulo_periodico = artigo['titulo_periodico'][:500] if artigo['titulo_periodico'] else None
                volume = artigo['volume'][:20] if artigo['volume'] else None
                pagina_inicial = artigo['pagina_inicial'][:10] if artigo['pagina_inicial'] else None
                pagina_final = artigo['pagina_final'][:10] if artigo['pagina_final'] else None
                issn = artigo['issn'][:20] if artigo['issn'] else None
                local_publicacao = artigo['local_publicacao'][:255] if artigo['local_publicacao'] else None
                autores = artigo['autores'] or None
                
                if id_lattes and titulo:
                    cursor.execute("""
                        INSERT INTO stg.artigos (
                            id_lattes, ano, titulo, doi, idioma, natureza, 
                            meio_divulgacao, titulo_periodico, volume, 
                            pagina_inicial, pagina_final, issn, local_publicacao, autores
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id_lattes, ano, titulo, doi, idioma, natureza, meio_divulgacao,
                          titulo_periodico, volume, pagina_inicial, pagina_final, issn, local_publicacao, autores))
                    
                    contador_artigos += 1
                    
                    if contador_artigos % 1000 == 0:
                        print(f"   Progresso: {contador_artigos} artigos inseridos...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de artigos inseridos: {contador_artigos}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração dos artigos dos currículos...")
    artigos = parse_artigos_json()
    
    print(f"\nTotal de artigos encontrados: {len(artigos)}")
    
    if artigos:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(artigos)
    else:
        print("Nenhum artigo encontrado para salvar.")

if __name__ == "__main__":
    main()

