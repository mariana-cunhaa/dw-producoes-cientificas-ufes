"""
Script para atualizar todas as páginas do Streamlit com o tema UFES
Aplica automaticamente os imports e configurações do tema em todos os arquivos de páginas
"""

import os
import re
from pathlib import Path

# Diretório das páginas
PAGES_DIR = Path("/Users/marianacunha/Documents/TCC/stage/BI_PRODUCOES_CIENTIFICAS/streamlit/pages")

# Template de imports para adicionar
UFES_IMPORTS = """
# Importar tema UFES
sys.path.append(str(Path(__file__).parent.parent))
from ufes_theme import (
    load_css,
    render_header,
    render_footer,
    apply_plotly_theme,
    get_plotly_config,
    CHART_COLORS,
    UFES_COLORS
)
"""

# Template para substituir imports de visualização
PLOTLY_IMPORTS = """import plotly.express as px
import plotly.graph_objects as go"""

# Código para carregar CSS (após set_page_config)
LOAD_CSS_CODE = """
# ========================================
# CARREGAR TEMA UFES
# ========================================
load_css()
"""

# Template de footer
FOOTER_CODE = """
st.markdown("---")

# ========================================
# FOOTER UFES
# ========================================
render_footer()
"""


def update_page_file(file_path):
    """
    Atualiza um arquivo de página com o tema UFES
    
    Args:
        file_path: Caminho do arquivo
    
    Returns:
        bool: True se atualizado com sucesso
    """
    print(f"📝 Processando: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # 1. Adicionar imports necessários se não existirem
        if 'sys' not in content or 'Path' not in content:
            if 'import streamlit as st' in content:
                content = content.replace(
                    'import streamlit as st',
                    'import streamlit as st\nimport sys\nfrom pathlib import Path'
                )
                modified = True
        
        # 2. Substituir altair por plotly se necessário
        if 'import altair as alt' in content:
            content = content.replace('import altair as alt', PLOTLY_IMPORTS)
            modified = True
            print("  ↳ Substituindo Altair por Plotly")
        
        # 3. Adicionar imports do tema UFES se não existirem
        if 'from ufes_theme import' not in content:
            # Procurar onde adicionar (após outros imports)
            import_pattern = r'(from db_utils import.*?\n)'
            if re.search(import_pattern, content):
                content = re.sub(
                    import_pattern,
                    r'\1' + UFES_IMPORTS + '\n',
                    content
                )
                modified = True
                print("  ↳ Adicionando imports do tema UFES")
        
        # 4. Atualizar page_title para incluir UFES
        if 'page_title=' in content and 'UFES' not in content:
            content = re.sub(
                r'page_title="([^"]+)"',
                r'page_title="\1 - UFES"',
                content
            )
            modified = True
        
        # 5. Adicionar load_css() após st.set_page_config
        if 'load_css()' not in content and 'st.set_page_config' in content:
            content = re.sub(
                r'(\)\n)\n+(st\.title|# ====)',
                r'\1' + LOAD_CSS_CODE + r'\n\2',
                content
            )
            modified = True
            print("  ↳ Adicionando load_css()")
        
        # 6. Substituir st.title por render_header (se ainda não foi feito)
        title_pattern = r'st\.title\("([^"]+)"\)\n(?:st\.markdown\("([^"]+)"\)\n)?'
        title_match = re.search(title_pattern, content)
        
        if title_match and 'render_header' not in content:
            title = title_match.group(1)
            subtitle = title_match.group(2) if title_match.group(2) else None
            
            if subtitle:
                replacement = f'''render_header(
    title="{title}",
    subtitle="{subtitle}"
)
'''
            else:
                replacement = f'render_header(title="{title}")\n'
            
            content = re.sub(title_pattern, replacement, content)
            modified = True
            print("  ↳ Substituindo título por render_header()")
        
        # 7. Adicionar footer no final se não existir
        if 'render_footer()' not in content:
            # Remover footer antigo se existir
            old_footer_pattern = r'# ====.*?FOOTER.*?====.*?st\.markdown\(""".*?""", unsafe_allow_html=True\)'
            content = re.sub(old_footer_pattern, '', content, flags=re.DOTALL)
            
            # Adicionar novo footer
            if not content.rstrip().endswith('render_footer()'):
                content = content.rstrip() + '\n' + FOOTER_CODE
                modified = True
                print("  ↳ Adicionando footer UFES")
        
        # 8. Atualizar gráficos Altair para Plotly (básico - pode precisar ajuste manual)
        if 'alt.Chart' in content:
            print("  ⚠️  ATENÇÃO: Arquivo usa Altair. Requer conversão manual para Plotly")
            modified = True
        
        # Salvar se houve modificações
        if modified and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Arquivo atualizado!\n")
            return True
        else:
            print(f"  ⏭️  Arquivo já está atualizado ou não requer mudanças\n")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao processar arquivo: {e}\n")
        return False


def main():
    """Função principal para atualizar todas as páginas"""
    print("=" * 60)
    print("🎓 APLICANDO TEMA UFES EM TODAS AS PÁGINAS")
    print("=" * 60)
    print()
    
    # Listar todos os arquivos .py no diretório pages
    page_files = sorted(PAGES_DIR.glob("Q*.py"))
    
    if not page_files:
        print("❌ Nenhum arquivo de página encontrado!")
        return
    
    print(f"📂 Encontrados {len(page_files)} arquivos de página\n")
    
    # Processar cada arquivo
    updated_count = 0
    for page_file in page_files:
        if update_page_file(page_file):
            updated_count += 1
    
    print("=" * 60)
    print(f"✅ CONCLUÍDO!")
    print(f"   - Total de arquivos: {len(page_files)}")
    print(f"   - Arquivos atualizados: {updated_count}")
    print(f"   - Arquivos sem mudanças: {len(page_files) - updated_count}")
    print("=" * 60)
    print()
    print("⚠️  ATENÇÃO:")
    print("   - Arquivos com Altair precisam ser convertidos manualmente para Plotly")
    print("   - Revise os arquivos atualizados para garantir que estão corretos")
    print("   - Execute: streamlit run app.py para testar")
    print()


if __name__ == "__main__":
    main()

