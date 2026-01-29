import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_trabalhos_eventos_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    trabalhos = []
    
    total_arquivos = 0
    arquivos_com_trabalhos = 0

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

                trabalhos_encontrados_neste_arquivo = 0
                
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
                trabalhos_eventos = producao_bibliografica.get("TRABALHOS-EM-EVENTOS")
                
                if not trabalhos_eventos:
                    continue
                
                trabalho_evento_list = trabalhos_eventos.get("TRABALHO-EM-EVENTOS", [])
                
                if isinstance(trabalho_evento_list, dict):
                    trabalho_evento_list = [trabalho_evento_list]
                
                for trabalho in trabalho_evento_list:
                    if not isinstance(trabalho, dict):
                        continue
                    
                    dados_basicos = trabalho.get("DADOS-BASICOS-DO-TRABALHO", {})
                    
                    if not isinstance(dados_basicos, dict):
                        continue
                    
                    titulo = dados_basicos.get("@TITULO-DO-TRABALHO", "")
                    ano = dados_basicos.get("@ANO-DO-TRABALHO", "")
                    doi = dados_basicos.get("@DOI", "")
                    idioma = dados_basicos.get("@IDIOMA", "")
                    natureza = dados_basicos.get("@NATUREZA", "")
                    meio_divulgacao = dados_basicos.get("@MEIO-DE-DIVULGACAO", "")
                    pais_evento = dados_basicos.get("@PAIS-DO-EVENTO", "")
                    
                    detalhamento = trabalho.get("DETALHAMENTO-DO-TRABALHO", {})
                    
                    if isinstance(detalhamento, dict):
                        nome_evento = detalhamento.get("@NOME-DO-EVENTO", "")
                        titulo_anais = detalhamento.get("@TITULO-DOS-ANAIS-OU-PROCEEDINGS", "")
                        ano_realizacao = detalhamento.get("@ANO-DE-REALIZACAO", "")
                        cidade_evento = detalhamento.get("@CIDADE-DO-EVENTO", "")
                        classificacao_evento = detalhamento.get("@CLASSIFICACAO-DO-EVENTO", "")
                        nome_editora = detalhamento.get("@NOME-DA-EDITORA", "")
                        cidade_editora = detalhamento.get("@CIDADE-DA-EDITORA", "")
                        isbn = detalhamento.get("@ISBN", "")
                        volume = detalhamento.get("@VOLUME", "")
                        pagina_inicial = detalhamento.get("@PAGINA-INICIAL", "")
                        pagina_final = detalhamento.get("@PAGINA-FINAL", "")
                    else:
                        nome_evento = titulo_anais = ano_realizacao = cidade_evento = ""
                        classificacao_evento = nome_editora = cidade_editora = isbn = ""
                        volume = pagina_inicial = pagina_final = ""
                    
                    if id_lattes and titulo:
                        autores = trabalho.get("AUTORES", [])
                        
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
                        
                        trabalhos.append({
                            "id_lattes": id_lattes,
                            "ano": ano,
                            "titulo": titulo,
                            "nome_evento": nome_evento,
                            "titulo_anais": titulo_anais,
                            "doi": doi,
                            "idioma": idioma,
                            "natureza": natureza,
                            "meio_divulgacao": meio_divulgacao,
                            "pais_evento": pais_evento,
                            "ano_realizacao": ano_realizacao,
                            "cidade_evento": cidade_evento,
                            "classificacao_evento": classificacao_evento,
                            "nome_editora": nome_editora,
                            "cidade_editora": cidade_editora,
                            "isbn": isbn,
                            "volume": volume,
                            "pagina_inicial": pagina_inicial,
                            "pagina_final": pagina_final,
                            "autores": autores_concatenados
                        })
                        trabalhos_encontrados_neste_arquivo += 1
                
                if trabalhos_encontrados_neste_arquivo > 0:
                    arquivos_com_trabalhos += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com trabalhos em eventos: {arquivos_com_trabalhos}")
    print(f"   - Arquivos sem trabalhos em eventos: {total_arquivos - arquivos_com_trabalhos}")
    
    return trabalhos

def salvar_no_banco(trabalhos):
    """Salva os trabalhos em eventos no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True
        cursor = conn.cursor()
        
        contador_trabalhos = 0
        contador_erros = 0
        
        print("\nInserindo trabalhos em eventos...")
        for trabalho in trabalhos:
            try:
                id_lattes = trabalho['id_lattes']
                ano = trabalho['ano'][:10] if trabalho['ano'] else None
                titulo = trabalho['titulo'][:1000] if trabalho['titulo'] else None
                nome_evento = trabalho['nome_evento'][:500] if trabalho['nome_evento'] else None
                titulo_anais = trabalho['titulo_anais'][:500] if trabalho['titulo_anais'] else None
                doi = trabalho['doi'][:255] if trabalho['doi'] else None
                idioma = trabalho['idioma'][:50] if trabalho['idioma'] else None
                natureza = trabalho['natureza'][:50] if trabalho['natureza'] else None
                meio_divulgacao = trabalho['meio_divulgacao'][:50] if trabalho['meio_divulgacao'] else None
                pais_evento = trabalho['pais_evento'][:100] if trabalho['pais_evento'] else None
                ano_realizacao = trabalho['ano_realizacao'][:10] if trabalho['ano_realizacao'] else None
                cidade_evento = trabalho['cidade_evento'][:255] if trabalho['cidade_evento'] else None
                classificacao_evento = trabalho['classificacao_evento'][:50] if trabalho['classificacao_evento'] else None
                nome_editora = trabalho['nome_editora'][:255] if trabalho['nome_editora'] else None
                cidade_editora = trabalho['cidade_editora'][:255] if trabalho['cidade_editora'] else None
                isbn = trabalho['isbn'][:50] if trabalho['isbn'] else None
                volume = trabalho['volume'][:20] if trabalho['volume'] else None
                pagina_inicial = trabalho['pagina_inicial'][:10] if trabalho['pagina_inicial'] else None
                pagina_final = trabalho['pagina_final'][:10] if trabalho['pagina_final'] else None
                autores = trabalho['autores'] or None
                
                if id_lattes and titulo:
                    cursor.execute("""
                        INSERT INTO stg.trabalhos_eventos (
                            id_lattes, ano, titulo, nome_evento, titulo_anais, doi, idioma,
                            natureza, meio_divulgacao, pais_evento, ano_realizacao, cidade_evento,
                            classificacao_evento, nome_editora, cidade_editora, isbn, volume,
                            pagina_inicial, pagina_final, autores
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id_lattes, ano, titulo, nome_evento, titulo_anais, doi, idioma, natureza,
                          meio_divulgacao, pais_evento, ano_realizacao, cidade_evento, classificacao_evento,
                          nome_editora, cidade_editora, isbn, volume, pagina_inicial, pagina_final, autores))
                    
                    contador_trabalhos += 1
                    
                    if contador_trabalhos % 1000 == 0:
                        print(f"   Progresso: {contador_trabalhos} trabalhos inseridos...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de trabalhos em eventos inseridos: {contador_trabalhos}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração dos trabalhos em eventos dos currículos...")
    trabalhos = parse_trabalhos_eventos_json()
    
    print(f"\nTotal de trabalhos em eventos encontrados: {len(trabalhos)}")
    
    if trabalhos:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(trabalhos)
    else:
        print("Nenhum trabalho em evento encontrado para salvar.")

if __name__ == "__main__":
    main()

