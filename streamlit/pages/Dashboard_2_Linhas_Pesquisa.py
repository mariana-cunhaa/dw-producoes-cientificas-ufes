"""
Dashboard 2: Linhas de Pesquisa
Análises consolidadas sobre linhas de pesquisa e diversidade temática
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from PIL import Image

# Adicionar diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))
from db_utils import run_query, get_metric_value
from ufes_theme import (
    load_css, 
    render_footer,
    apply_plotly_theme,
    get_plotly_config,
    limpar_capitalizacao,
    CHART_COLORS,
    UFES_COLORS
)

# ========================================
# CONFIGURAÇÃO DA PÁGINA
# ========================================
st.set_page_config(
    page_title="Linhas de Pesquisa - UFES",
    page_icon="🔬",
    layout="wide"
)

# ========================================
# CARREGAR TEMA UFES
# ========================================
load_css()

# ========================================
# LOGO E HEADER
# ========================================
try:
    logo_path = Path(__file__).parent.parent / "logo_ufes.png"
    logo = Image.open(logo_path)
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image(logo, width=120)
    with col_title:
        st.title("Linhas de Pesquisa")
        st.markdown("**Análises sobre linhas de pesquisa e diversidade temática**")
except Exception as e:
    st.title("Linhas de Pesquisa")
    st.markdown("**Análises sobre linhas de pesquisa e diversidade temática**")

st.markdown("---")

# ========================================
# PERGUNTA 6: Distribuição por Linha de Pesquisa
# ========================================
st.header("6. Distribuição de Pesquisadores por Linha de Pesquisa")
st.markdown("*Análise da distribuição de pesquisadores entre as linhas de pesquisa*")

# Aviso sobre cobertura dos dados
query_total_base = "SELECT COUNT(*) FROM dw.dim_pesquisador;"
query_com_linha = "SELECT COUNT(DISTINCT id_pesquisador) FROM dw.fato_pesquisador_linha_pesquisa;"
total_pesq_base = get_metric_value(query_total_base)
total_pesq_com_linha = get_metric_value(query_com_linha)
cobertura_pct = (total_pesq_com_linha / total_pesq_base * 100) if total_pesq_base > 0 else 0

st.info(f"""
📊 **Cobertura dos dados**: {total_pesq_com_linha:,} de {total_pesq_base:,} pesquisadores ({cobertura_pct:.1f}%) 
possuem **linha de pesquisa cadastrada** no currículo Lattes. Os demais não preencheram esta informação.
""")

query_linhas = """
SELECT
  dlp.linha_pesquisa,
  COUNT(DISTINCT fpl.id_pesquisador) AS pesquisadores_distintos
FROM dw.fato_pesquisador_linha_pesquisa fpl
JOIN dw.dim_linha_pesquisa dlp ON dlp.id_linha_pesquisa = fpl.id_linha_pesquisa
GROUP BY dlp.linha_pesquisa
ORDER BY pesquisadores_distintos DESC;
"""

try:
    df_linhas = run_query(query_linhas)
    
    df_linhas['linha_pesquisa'] = df_linhas['linha_pesquisa'].apply(limpar_capitalizacao)
    
    total_linhas = len(df_linhas)
    
    total_pesquisadores = total_pesq_com_linha  
    
    total_relacoes = df_linhas['pesquisadores_distintos'].sum()
    
    media_pesq_por_linha = df_linhas['pesquisadores_distintos'].mean()
    media_linhas_por_pesq = total_relacoes / total_pesquisadores if total_pesquisadores > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Linhas de Pesquisa", f"{total_linhas:,}")
    with col2:
        st.metric(
            "Total de Pesquisadores", 
            f"{total_pesquisadores:,}",
            help=f"Pesquisadores únicos com linha cadastrada. Total de relações: {total_relacoes:,}"
        )
    with col3:
        st.metric(
            "Média de Linhas/Pesquisador", 
            f"{media_linhas_por_pesq:.1f}",
            help=f"Cada pesquisador atua em média em {media_linhas_por_pesq:.1f} linhas"
        )
    
    st.markdown("---")
    
    # Top 20 Linhas de Pesquisa
    st.subheader("Top 20 Linhas com Mais Pesquisadores")
    
    df_top20 = df_linhas.head(20)
    
    fig1 = px.bar(
        df_top20,
        x='pesquisadores_distintos',
        y='linha_pesquisa',
        orientation='h',
        title='Top 20 Linhas de Pesquisa',
        labels={
            'pesquisadores_distintos': 'Quantidade de Pesquisadores',
            'linha_pesquisa': 'Linha de Pesquisa'
        },
        color='pesquisadores_distintos',
        color_continuous_scale='Greens'
    )
    
    fig1 = apply_plotly_theme(fig1)
    fig1.update_layout(
        showlegend=False,
        height=600,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig1, use_container_width=True, config=get_plotly_config())
    
    st.markdown("---")
    
    # Busca por linha específica
    st.subheader("Buscar Linha de Pesquisa Específica")
    
    busca = st.text_input(
        "Digite parte do nome da linha de pesquisa:",
        placeholder="Ex: inteligência artificial, saúde pública..."
    )
    
    if busca:
        df_filtrado = df_linhas[
            df_linhas['linha_pesquisa'].str.contains(busca, case=False, na=False)
        ]
        
        if len(df_filtrado) > 0:
            st.success(f" Encontradas {len(df_filtrado)} linhas correspondentes")
            
            # Tabela
            df_busca_display = df_filtrado.copy()
            df_busca_display.index = range(1, len(df_busca_display) + 1)
            df_busca_display.columns = ['Linha de Pesquisa', 'Pesquisadores']
            st.dataframe(df_busca_display, use_container_width=True)
        else:
            st.warning("⚠️ Nenhuma linha encontrada com esse termo")
    
    with st.expander(f"📋 Ver todas as {total_linhas:,} linhas de pesquisa"):
        st.info("💡 Dica: Use Ctrl+F (Cmd+F no Mac) para buscar na tabela")
        
        df_display = df_linhas.copy()
        df_display.index = range(1, len(df_display) + 1)
        df_display.columns = ['Linha de Pesquisa', 'Pesquisadores']
        
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400
        )
    
except Exception as e:
    st.error(f" Erro ao carregar dados: {e}")

st.markdown("---")

# ========================================
# PERGUNTA 7: Pesquisadores Multi-linha
# ========================================
st.header("7. Pesquisadores Multi-linha")
st.markdown("*Quantos pesquisadores têm mais de 1 linha de pesquisa?*")

query_multi_linha = """
SELECT COUNT(*) AS pesquisadores_multilinha
FROM (
  SELECT
    id_pesquisador
  FROM dw.fato_pesquisador_linha_pesquisa
  GROUP BY id_pesquisador
  HAVING COUNT(DISTINCT id_linha_pesquisa) > 1
) x;
"""

try:
    df_multi_linha = run_query(query_multi_linha)
    total_multi_linha = int(df_multi_linha['pesquisadores_multilinha'].iloc[0])
    
    query_total = """
    SELECT COUNT(DISTINCT id_pesquisador) 
    FROM dw.fato_pesquisador_linha_pesquisa;
    """
    total_geral = get_metric_value(query_total)
    mono_linha = total_geral - total_multi_linha
    percentual = (total_multi_linha / total_geral * 100) if total_geral > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Pesquisadores Multi-linha",
            value=f"{total_multi_linha:,}",
            help="Pesquisadores que atuam em 2 ou mais linhas de pesquisa"
        )
    
    with col2:
        st.metric(
            label="Percentual do Total",
            value=f"{percentual:.1f}%",
            help=f"De {total_geral:,} pesquisadores no total"
        )
    
    with col3:
        st.metric(
            label="Pesquisadores Mono-linha",
            value=f"{mono_linha:,}",
            help="Pesquisadores que atuam em apenas 1 linha de pesquisa"
        )
    
    df_comparacao = pd.DataFrame({
        'Tipo': ['Multi-linha', 'Mono-linha'],
        'Quantidade': [total_multi_linha, mono_linha]
    })
    
    fig2 = px.pie(
        df_comparacao,
        values='Quantidade',
        names='Tipo',
        title='Distribuição: Mono-linha vs Multi-linha',
        color='Tipo',
        color_discrete_map={
            'Multi-linha': UFES_COLORS['primary_blue'], 
            'Mono-linha': UFES_COLORS['light_blue']
        },
        hole=0.4
    )
    
    fig2 = apply_plotly_theme(fig2)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig2, use_container_width=True, config=get_plotly_config())
    
    with st.expander("ℹ️ Entenda os dados"):
        # Verificar total de pesquisadores na base
        query_total_base = "SELECT COUNT(*) FROM dw.dim_pesquisador;"
        total_base = get_metric_value(query_total_base)
        pesq_sem_linha = total_base - total_geral
        
        st.markdown(f"""
        **Interpretação:**
        - **{total_multi_linha:,}** pesquisadores atuam em **2 ou mais** linhas de pesquisa ({percentual:.1f}% dos que têm linha)
        - **{mono_linha:,}** pesquisadores atuam em **apenas 1** linha de pesquisa ({100-percentual:.1f}% dos que têm linha)
        - Total de pesquisadores **com linha de pesquisa**: **{total_geral:,}**
        - Total de pesquisadores **na base**: **{total_base:,}**
        - Pesquisadores **sem linha de pesquisa cadastrada**: **{pesq_sem_linha:,}** ({pesq_sem_linha/total_base*100:.1f}%)
        
        **O que isso significa?**
        - **Multi-linha** indica pesquisadores com **diversidade temática** dentro de sua área
        - **Mono-linha** sugere **especialização** em um tema específico
        - Nem todos os pesquisadores da base têm linha de pesquisa cadastrada no currículo Lattes
        """)
    
except Exception as e:
    st.error(f" Erro ao carregar dados: {e}")

st.markdown("---")

# ========================================
# PERGUNTA 8: Média de Linhas por Grande Área
# ========================================
st.header("8. Média de Linhas de Pesquisa por Grande Área")
st.markdown("*Quais grandes áreas concentram pesquisadores com maior diversidade de linhas?*")

query_media_linhas = """
WITH linhas_por_pesq AS (
  SELECT
    id_pesquisador,
    COUNT(DISTINCT id_linha_pesquisa) AS qtd_linhas
  FROM dw.fato_pesquisador_linha_pesquisa
  GROUP BY id_pesquisador
)
SELECT
  da.grande_area,
  ROUND(AVG(lpp.qtd_linhas)::numeric, 2) AS media_linhas_por_pesquisador,
  COUNT(DISTINCT fpa.id_pesquisador) AS pesquisadores_na_grande_area
FROM dw.fato_pesquisador_area_atuacao fpa
JOIN dw.dim_area da ON da.id_area = fpa.id_area
JOIN linhas_por_pesq lpp ON lpp.id_pesquisador = fpa.id_pesquisador
GROUP BY da.grande_area
ORDER BY media_linhas_por_pesquisador DESC;
"""

try:
    df_media = run_query(query_media_linhas)
    
    # Limpar capitalização incorreta
    df_media['grande_area'] = df_media['grande_area'].apply(limpar_capitalizacao)
    
    # Métricas gerais
    media_geral = df_media['media_linhas_por_pesquisador'].mean()
    max_media = df_media['media_linhas_por_pesquisador'].max()
    area_max = df_media.loc[df_media['media_linhas_por_pesquisador'].idxmax(), 'grande_area']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Média Geral", f"{media_geral:.2f} linhas/pesq")
    with col2:
        st.metric("Maior Média", f"{max_media:.2f}")
    with col3:
        st.metric("Grande Área Líder", area_max)
    
    st.markdown("---")
    
    fig3 = px.bar(
        df_media,
        x='media_linhas_por_pesquisador',
        y='grande_area',
        orientation='h',
        title='Média de Linhas por Pesquisador em Cada Grande Área',
        labels={
            'media_linhas_por_pesquisador': 'Média de Linhas por Pesquisador',
            'grande_area': 'Grande Área'
        },
        color='media_linhas_por_pesquisador',
        color_continuous_scale='Viridis',
        text='media_linhas_por_pesquisador'
    )
    
    fig3 = apply_plotly_theme(fig3)
    fig3.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig3.update_layout(
        showlegend=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig3, use_container_width=True, config=get_plotly_config())
    
    st.markdown("---")
    
    # Gráfico de dispersão: Média vs Quantidade de Pesquisadores
    st.subheader("Dispersão: Média de Linhas vs Quantidade de Pesquisadores")
    
    fig4 = px.scatter(
        df_media,
        x='pesquisadores_na_grande_area',
        y='media_linhas_por_pesquisador',
        size='pesquisadores_na_grande_area',
        color='grande_area',
        title='Relação entre Média de Linhas e Quantidade de Pesquisadores',
        labels={
            'pesquisadores_na_grande_area': 'Quantidade de Pesquisadores',
            'media_linhas_por_pesquisador': 'Média de Linhas por Pesquisador',
            'grande_area': 'Grande Área'
        },
        hover_data=['grande_area', 'media_linhas_por_pesquisador', 'pesquisadores_na_grande_area']
    )
    
    fig4 = apply_plotly_theme(fig4)
    fig4.update_xaxes(type="log")
    fig4.update_layout(height=500)
    
    st.plotly_chart(fig4, use_container_width=True, config=get_plotly_config())
    
    st.info("💡 Escala logarítmica no eixo X para melhor visualização da dispersão")
    
    with st.expander("💡 Insights"):
        top_1 = df_media.iloc[0]
        bottom_1 = df_media.iloc[-1]
        diferenca = top_1['media_linhas_por_pesquisador'] - bottom_1['media_linhas_por_pesquisador']
        
        st.markdown(f"""
        **Análise Comparativa:**
        - 🥇 **Maior diversidade:** {top_1['grande_area']}
          - Média: **{top_1['media_linhas_por_pesquisador']:.2f}** linhas por pesquisador
          - {top_1['pesquisadores_na_grande_area']:,} pesquisadores
        
        - 🔵 **Menor diversidade:** {bottom_1['grande_area']}
          - Média: **{bottom_1['media_linhas_por_pesquisador']:.2f}** linhas por pesquisador
          - {bottom_1['pesquisadores_na_grande_area']:,} pesquisadores
        
        - 📊 **Diferença:** {diferenca:.2f} linhas/pesquisador
        - 📈 **Média geral:** {media_geral:.2f} linhas/pesquisador
        
        **Interpretação:**
        - Áreas com **maior média** têm pesquisadores mais **versáteis** (atuam em múltiplas linhas)
        - Áreas com **menor média** tendem à **especialização** em poucas linhas
        """)
    
except Exception as e:
    st.error(f" Erro ao carregar dados: {e}")

st.markdown("---")

# ========================================
# FOOTER UFES
# ========================================
render_footer()

