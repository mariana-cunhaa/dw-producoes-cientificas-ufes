import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db_conexao import obter_conexao

def parse_projetos_pesquisa_json():
    pasta_json = os.path.join(os.path.dirname(__file__), "lattes_tcc", "arquivos_json")
    pasta_json = os.path.abspath(pasta_json)
    projetos_pesquisa = []
    
    total_arquivos = 0
    arquivos_com_projetos = 0

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

                projetos_encontrados_neste_arquivo = 0
                
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
                    
                    atividades_projeto = atuacao.get("ATIVIDADES-DE-PARTICIPACAO-EM-PROJETO", {})
                    
                    if not atividades_projeto:
                        continue
                    
                    participacao_projeto_list = atividades_projeto.get("PARTICIPACAO-EM-PROJETO", [])
                    
                    if isinstance(participacao_projeto_list, dict):
                        participacao_projeto_list = [participacao_projeto_list]
                    
                    for participacao in participacao_projeto_list:
                        if not isinstance(participacao, dict):
                            continue
                        
                        projeto = participacao.get("PROJETO-DE-PESQUISA", {})
                        
                        if not isinstance(projeto, dict):
                            continue
                        
                        ano_inicio = projeto.get("@ANO-INICIO", "")
                        ano_fim = projeto.get("@ANO-FIM", "")
                        nome_projeto = projeto.get("@NOME-DO-PROJETO", "")
                        descricao_projeto = projeto.get("@DESCRICAO-DO-PROJETO", "")
                        situacao = projeto.get("@SITUACAO", "")
                        natureza = projeto.get("@NATUREZA", "")
                        
                        if id_lattes and nome_projeto:
                            projetos_pesquisa.append({
                                "id_lattes": id_lattes,
                                "ano_inicio": ano_inicio,
                                "ano_fim": ano_fim,
                                "nome_projeto": nome_projeto,
                                "descricao_projeto": descricao_projeto,
                                "situacao": situacao,
                                "natureza": natureza
                            })
                            projetos_encontrados_neste_arquivo += 1
                
                if projetos_encontrados_neste_arquivo > 0:
                    arquivos_com_projetos += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de arquivos JSON processados: {total_arquivos}")
    print(f"   - Arquivos com projetos de pesquisa: {arquivos_com_projetos}")
    print(f"   - Arquivos sem projetos de pesquisa: {total_arquivos - arquivos_com_projetos}")
    
    return projetos_pesquisa

def salvar_no_banco(projetos_pesquisa):
    """Salva os projetos de pesquisa no banco de dados"""
    try:
        conn = obter_conexao()
        conn.autocommit = True  
        cursor = conn.cursor()
        
        contador_inseridos = 0
        contador_erros = 0
        
        for projeto in projetos_pesquisa:
            try:
                id_lattes = projeto['id_lattes']
                ano_inicio = projeto['ano_inicio'] or None
                ano_fim = projeto['ano_fim'] or None
                nome_projeto = projeto['nome_projeto'][:500] if projeto['nome_projeto'] else None
                descricao_projeto = projeto['descricao_projeto'][:5000] if projeto['descricao_projeto'] else None
                situacao = projeto['situacao'][:100] if projeto['situacao'] else None
                natureza = projeto['natureza'][:100] if projeto['natureza'] else None
                
                if id_lattes and nome_projeto:
                    cursor.execute("""
                        INSERT INTO stg.projetos_pesquisa (
                            id_lattes, 
                            ano_inicio, 
                            ano_fim, 
                            nome_projeto, 
                            descricao_projeto,
                            situacao,
                            natureza
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (id_lattes, ano_inicio, ano_fim, nome_projeto, descricao_projeto, situacao, natureza))
                    contador_inseridos += 1
                    
                    if contador_inseridos % 1000 == 0:
                        print(f"   Progresso: {contador_inseridos} projetos inseridos...")
                else:
                    contador_erros += 1
                    
            except Exception as e:
                contador_erros += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Total de projetos de pesquisa inseridos: {contador_inseridos}")
        if contador_erros > 0:
            print(f"✗ Total de erros: {contador_erros}")
            
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")

def main():
    print("Iniciando extração dos projetos de pesquisa dos currículos...")
    projetos_pesquisa = parse_projetos_pesquisa_json()
    
    print(f"\nTotal de projetos de pesquisa encontrados: {len(projetos_pesquisa)}")
    
    if projetos_pesquisa:
        print("\nSalvando no banco de dados...")
        salvar_no_banco(projetos_pesquisa)
    else:
        print("Nenhum projeto de pesquisa encontrado para salvar.")

if __name__ == "__main__":
    main()

