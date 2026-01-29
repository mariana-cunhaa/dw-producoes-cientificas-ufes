import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_apresentacoes_trabalho_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    apresentacoes = []
    
    total_arquivos = 0
    arquivos_com_apresentacoes = 0

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

                apresentacoes_encontradas_neste_arquivo = 0
                
                curriculo_vitae = dados.get("CURRICULO-VITAE", {})
                
                # Id Lattes
                id_lattes = curriculo_vitae.get("@NUMERO-IDENTIFICADOR", "")
                
                # Nome (caso não tenha id_lattes)
                dados_gerais = curriculo_vitae.get("DADOS-GERAIS", {})
                nome = dados_gerais.get("@NOME-COMPLETO", "")
                
                if not id_lattes:
                    id_lattes = nome.replace(" ", "")
                
                producao_tecnica = curriculo_vitae.get("PRODUCAO-TECNICA")
                
                if not producao_tecnica:
                    continue
                
                demais_tipos = producao_tecnica.get("DEMAIS-TIPOS-DE-PRODUCAO-TECNICA")
                
                if not demais_tipos:
                    continue
                
                apresentacao_list = demais_tipos.get("APRESENTACAO-DE-TRABALHO", [])
                
                if isinstance(apresentacao_list, dict):
                    apresentacao_list = [apresentacao_list]
                
                for apresentacao in apresentacao_list:
                    if not isinstance(apresentacao, dict):
                        continue
                    
                    dados_basicos = apresentacao.get("DADOS-BASICOS-DA-APRESENTACAO-DE-TRABALHO", {})
                    
                    if not isinstance(dados_basicos, dict):
                        continue
                    
                    titulo = dados_basicos.get("@TITULO", "")
                    ano = dados_basicos.get("@ANO", "")
                    doi = dados_basicos.get("@DOI", "")
                    idioma = dados_basicos.get("@IDIOMA", "")
                    natureza = dados_basicos.get("@NATUREZA", "")
                    pais = dados_basicos.get("@PAIS", "")
                    
                    detalhamento = apresentacao.get("DETALHAMENTO-DA-APRESENTACAO-DE-TRABALHO", {})
                    
                    if isinstance(detalhamento, dict):
                        nome_evento = detalhamento.get("@NOME-DO-EVENTO", "")
                        cidade_apresentacao = detalhamento.get("@CIDADE-DA-APRESENTACAO", "")
                        local_apresentacao = detalhamento.get("@LOCAL-DA-APRESENTACAO", "")
                        instituicao_promotora = detalhamento.get("@INSTITUICAO-PROMOTORA", "")
                    else:
                        nome_evento = cidade_apresentacao = local_apresentacao = instituicao_promotora = ""
                    
                    if id_lattes and titulo:
                        autores = apresentacao.get("AUTORES", [])
                        
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
                        
                        apresentacoes.append({
                            "id_lattes": id_lattes,
                            "ano": ano,
                            "titulo": titulo,
                            "doi": doi,
                            "idioma": idioma,
                            "natureza": natureza,
                            "pais": pais,
                            "nome_evento": nome_evento,
                            "cidade_apresentacao": cidade_apresentacao,
                            "local_apresentacao": local_apresentacao,
                            "instituicao_promotora": instituicao_promotora,
                            "autores": autores_concatenados
                        })
                        apresentacoes_encontradas_neste_arquivo += 1
                
                if apresentacoes_encontradas_neste_arquivo > 0:
                    arquivos_com_apresentacoes += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com apresentações de trabalho: {arquivos_com_apresentacoes}")
    print(f"   - Arquivos sem apresentações de trabalho: {total_arquivos - arquivos_com_apresentacoes}")
    
    return apresentacoes

def salvar_no_banco(apresentacoes):
    """Salva as apresentações de trabalho no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True
        cursor = conn.cursor()
        
        contador_apresentacoes = 0
        contador_erros = 0
        
        print("\nInserindo apresentações de trabalho...")
        for apresentacao in apresentacoes:
            try:
                id_lattes = apresentacao['id_lattes']
                ano = apresentacao['ano'][:10] if apresentacao['ano'] else None
                titulo = apresentacao['titulo'][:1000] if apresentacao['titulo'] else None
                doi = apresentacao['doi'][:255] if apresentacao['doi'] else None
                idioma = apresentacao['idioma'][:50] if apresentacao['idioma'] else None
                natureza = apresentacao['natureza'][:100] if apresentacao['natureza'] else None
                pais = apresentacao['pais'][:100] if apresentacao['pais'] else None
                nome_evento = apresentacao['nome_evento'][:500] if apresentacao['nome_evento'] else None
                cidade_apresentacao = apresentacao['cidade_apresentacao'][:255] if apresentacao['cidade_apresentacao'] else None
                local_apresentacao = apresentacao['local_apresentacao'][:255] if apresentacao['local_apresentacao'] else None
                instituicao_promotora = apresentacao['instituicao_promotora'][:500] if apresentacao['instituicao_promotora'] else None
                autores = apresentacao['autores'] or None
                
                if id_lattes and titulo:
                    cursor.execute("""
                        INSERT INTO stg.apresentacoes_trabalho (
                            id_lattes, ano, titulo, doi, idioma, natureza, pais,
                            nome_evento, cidade_apresentacao, local_apresentacao,
                            instituicao_promotora, autores
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (id_lattes, ano, titulo, doi, idioma, natureza, pais,
                          nome_evento, cidade_apresentacao, local_apresentacao,
                          instituicao_promotora, autores))
                    
                    contador_apresentacoes += 1
                    
                    if contador_apresentacoes % 1000 == 0:
                        print(f"   Progresso: {contador_apresentacoes} apresentações inseridas...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de apresentações de trabalho inseridas: {contador_apresentacoes}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração das apresentações de trabalho dos currículos...")
    apresentacoes = parse_apresentacoes_trabalho_json()
    
    print(f"\nTotal de apresentações de trabalho encontradas: {len(apresentacoes)}")
    
    if apresentacoes:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(apresentacoes)
    else:
        print("Nenhuma apresentação de trabalho encontrada para salvar.")

if __name__ == "__main__":
    main()

