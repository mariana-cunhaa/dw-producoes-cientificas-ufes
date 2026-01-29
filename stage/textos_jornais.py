import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_textos_jornais_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    textos = []
    
    total_arquivos = 0
    arquivos_com_textos = 0

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

                textos_encontrados_neste_arquivo = 0
                
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
                
                textos_jornais = producao_bibliografica.get("TEXTOS-EM-JORNAIS-OU-REVISTAS")
                
                if not textos_jornais:
                    continue
                
                texto_jornal_list = textos_jornais.get("TEXTO-EM-JORNAL-OU-REVISTA", [])
                
                if isinstance(texto_jornal_list, dict):
                    texto_jornal_list = [texto_jornal_list]
                
                for texto in texto_jornal_list:
                    if not isinstance(texto, dict):
                        continue
                    
                    dados_basicos = texto.get("DADOS-BASICOS-DO-TEXTO", {})
                    
                    if not isinstance(dados_basicos, dict):
                        continue
                    
                    titulo = dados_basicos.get("@TITULO-DO-TEXTO", "")
                    ano = dados_basicos.get("@ANO-DO-TEXTO", "")
                    doi = dados_basicos.get("@DOI", "")
                    idioma = dados_basicos.get("@IDIOMA", "")
                    natureza = dados_basicos.get("@NATUREZA", "")
                    meio_divulgacao = dados_basicos.get("@MEIO-DE-DIVULGACAO", "")
                    
                    detalhamento = texto.get("DETALHAMENTO-DO-TEXTO", {})
                    
                    if isinstance(detalhamento, dict):
                        titulo_jornal = detalhamento.get("@TITULO-DO-JORNAL-OU-REVISTA", "")
                        data_publicacao = detalhamento.get("@DATA-DE-PUBLICACAO", "")
                        local_publicacao = detalhamento.get("@LOCAL-DE-PUBLICACAO", "")
                        pagina_inicial = detalhamento.get("@PAGINA-INICIAL", "")
                        pagina_final = detalhamento.get("@PAGINA-FINAL", "")
                        volume = detalhamento.get("@VOLUME", "")
                        issn = detalhamento.get("@ISSN", "")
                    else:
                        titulo_jornal = data_publicacao = local_publicacao = ""
                        pagina_inicial = pagina_final = volume = issn = ""
                    
                    if id_lattes and titulo:
                        autores = texto.get("AUTORES", [])
                        
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
                        
                        textos.append({
                            "id_lattes": id_lattes,
                            "ano": ano,
                            "titulo": titulo,
                            "titulo_jornal": titulo_jornal,
                            "doi": doi,
                            "idioma": idioma,
                            "natureza": natureza,
                            "meio_divulgacao": meio_divulgacao,
                            "data_publicacao": data_publicacao,
                            "local_publicacao": local_publicacao,
                            "pagina_inicial": pagina_inicial,
                            "pagina_final": pagina_final,
                            "volume": volume,
                            "issn": issn,
                            "autores": autores_concatenados
                        })
                        textos_encontrados_neste_arquivo += 1
                
                if textos_encontrados_neste_arquivo > 0:
                    arquivos_com_textos += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com textos em jornais/revistas: {arquivos_com_textos}")
    print(f"   - Arquivos sem textos em jornais/revistas: {total_arquivos - arquivos_com_textos}")
    
    return textos

def salvar_no_banco(textos):
    """Salva os textos em jornais/revistas no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True
        cursor = conn.cursor()
        
        contador_textos = 0
        contador_erros = 0
        
        print("\nInserindo textos em jornais/revistas...")
        for texto in textos:
            try:
                id_lattes = texto['id_lattes']
                ano = texto['ano'][:10] if texto['ano'] else None
                titulo = texto['titulo'][:1000] if texto['titulo'] else None
                titulo_jornal = texto['titulo_jornal'][:500] if texto['titulo_jornal'] else None
                doi = texto['doi'][:255] if texto['doi'] else None
                idioma = texto['idioma'][:50] if texto['idioma'] else None
                natureza = texto['natureza'][:100] if texto['natureza'] else None
                meio_divulgacao = texto['meio_divulgacao'][:50] if texto['meio_divulgacao'] else None
                data_publicacao = texto['data_publicacao'][:20] if texto['data_publicacao'] else None
                local_publicacao = texto['local_publicacao'][:255] if texto['local_publicacao'] else None
                pagina_inicial = texto['pagina_inicial'][:10] if texto['pagina_inicial'] else None
                pagina_final = texto['pagina_final'][:10] if texto['pagina_final'] else None
                volume = texto['volume'][:20] if texto['volume'] else None
                issn = texto['issn'][:20] if texto['issn'] else None
                autores = texto['autores'] or None
                
                if id_lattes and titulo:
                    cursor.execute("""
                        INSERT INTO stg.textos_jornais (
                            id_lattes, ano, titulo, titulo_jornal, doi, idioma,
                            natureza, meio_divulgacao, data_publicacao, local_publicacao,
                            pagina_inicial, pagina_final, volume, issn, autores
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id_lattes, ano, titulo, titulo_jornal, doi, idioma, natureza,
                          meio_divulgacao, data_publicacao, local_publicacao, pagina_inicial,
                          pagina_final, volume, issn, autores))
                    
                    contador_textos += 1
                    
                    if contador_textos % 1000 == 0:
                        print(f"   Progresso: {contador_textos} textos inseridos...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de textos em jornais/revistas inseridos: {contador_textos}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração dos textos em jornais/revistas dos currículos...")
    textos = parse_textos_jornais_json()
    
    print(f"\nTotal de textos em jornais/revistas encontrados: {len(textos)}")
    
    if textos:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(textos)
    else:
        print("Nenhum texto em jornal/revista encontrado para salvar.")

if __name__ == "__main__":
    main()

