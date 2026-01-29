"""
Dashboard 1: Áreas de Atuação
Análises consolidadas sobre grandes áreas de conhecimento e distribuição de pesquisadores
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from PIL import Image

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

# CONFIGURAÇÃO DA PÁGINA

st.set_page_config(
    page_title="Áreas de Atuação - UFES",
    page_icon="📊",
    layout="wide"
)

load_css()

try:
    logo_path = Path(__file__).parent.parent / "logo_ufes.png"
    logo = Image.open(logo_path)
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image(logo, width=120)
    with col_title:
        st.title("Áreas de Atuação")
        st.markdown("**Análises sobre grandes áreas de conhecimento e distribuição de pesquisadores**")
except Exception as e:
    st.title("Áreas de Atuação")
    st.markdown("**Análises sobre grandes áreas de conhecimento e distribuição de pesquisadores**")

st.markdown("---")


# PERGUNTA 1: Pesquisadores por Grande Área

st.header("1. Pesquisadores por Grande Área")
st.markdown("*Quantos pesquisadores distintos atuam em cada grande área?*")

query_pesq_por_area = """
SELECT
  da.grande_area,
  COUNT(DISTINCT fpa.id_pesquisador) AS pesquisadores_distintos
FROM dw.fato_pesquisador_area_atuacao fpa
JOIN dw.dim_area da ON da.id_area = fpa.id_area
GROUP BY da.grande_area
ORDER BY pesquisadores_distintos DESC;
"""

try:
    df_pesq_area = run_query(query_pesq_por_area)
    
   
    df_pesq_area['grande_area'] = df_pesq_area['grande_area'].apply(limpar_capitalizacao)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        total_pesquisadores = df_pesq_area['pesquisadores_distintos'].sum()
        st.metric("👥 Total de Pesquisadores", f"{total_pesquisadores:,}")
    with col2:
        total_areas = len(df_pesq_area)
        st.metric("📚 Total de Grandes Áreas", f"{total_areas}")
    
    st.markdown("")
    
    fig = px.bar(
        df_pesq_area,
        y='grande_area',
        x='pesquisadores_distintos',
        orientation='h',
        title='Distribuição de Pesquisadores por Grande Área',
        labels={
            'pesquisadores_distintos': 'Quantidade de Pesquisadores',
            'grande_area': 'Grande Área'
        },
        color='pesquisadores_distintos',
        color_continuous_scale=[
            [0, UFES_COLORS['light_blue']],
            [0.5, UFES_COLORS['secondary_blue']],
            [1, UFES_COLORS['primary_blue']]
        ],
        text='pesquisadores_distintos'
    )
    
    fig = apply_plotly_theme(fig)
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(
        showlegend=False,
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())
    
    with st.expander("📋 Ver dados detalhados"):
        df_pesq_area['percentual'] = (df_pesq_area['pesquisadores_distintos'] / total_pesquisadores * 100).round(2)
        st.dataframe(
            df_pesq_area.style.format({
                'pesquisadores_distintos': '{:,.0f}',
                'percentual': '{:.2f}%'
            }),
            use_container_width=True,
            height=400
        )
        
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")


# PERGUNTA 2: Pesquisadores Multi-área
st.header("2. Pesquisadores Multi-área")
st.markdown("*Quantos pesquisadores atuam em mais de uma grande área?*")

query_multi_area = """
SELECT COUNT(*) AS pesquisadores_multi_grande_area
FROM (
  SELECT
    fpa.id_pesquisador
  FROM dw.fato_pesquisador_area_atuacao fpa
  JOIN dw.dim_area da ON da.id_area = fpa.id_area
  GROUP BY fpa.id_pesquisador
  HAVING COUNT(DISTINCT da.grande_area) > 1
) x;
"""

try:
    df_multi_area = run_query(query_multi_area)
    total_multi_area = int(df_multi_area['pesquisadores_multi_grande_area'].iloc[0])
    
    query_total_pesq = """
    SELECT COUNT(DISTINCT id_pesquisador) 
    FROM dw.fato_pesquisador_area_atuacao;
    """
    total_geral = get_metric_value(query_total_pesq)
    mono_area = total_geral - total_multi_area
    percentual = (total_multi_area / total_geral * 100) if total_geral > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Pesquisadores Multi-área",
            value=f"{total_multi_area:,}",
            help="Pesquisadores que atuam em 2 ou mais grandes áreas"
        )
    
    with col2:
        st.metric(
            label="Percentual do Total",
            value=f"{percentual:.1f}%",
            help=f"De {total_geral:,} pesquisadores no total"
        )
    
    with col3:
        st.metric(
            label="Pesquisadores Mono-área",
            value=f"{mono_area:,}",
            help="Pesquisadores que atuam em apenas 1 grande área"
        )
    
    df_comparacao = pd.DataFrame({
        'Tipo': ['Multi-área', 'Mono-área'],
        'Quantidade': [total_multi_area, mono_area]
    })
    
    fig2 = px.pie(
        df_comparacao,
        values='Quantidade',
        names='Tipo',
        title='Distribuição: Mono-área vs Multi-área',
        color='Tipo',
        color_discrete_map={'Multi-área': UFES_COLORS['primary_blue'], 'Mono-área': UFES_COLORS['light_blue']},
        hole=0.4
    )
    
    fig2 = apply_plotly_theme(fig2)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig2, use_container_width=True, config=get_plotly_config())
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")


# PERGUNTA 3: Percentual por Grande Área
st.header("3. Percentual de Pesquisadores por Grande Área")
st.markdown("*Qual o percentual de pesquisadores em cada grande área?*")

query_percentual = """
WITH base AS (
  SELECT
    da.grande_area,
    COUNT(DISTINCT fpa.id_pesquisador) AS pesquisadores
  FROM dw.fato_pesquisador_area_atuacao fpa
  JOIN dw.dim_area da ON da.id_area = fpa.id_area
  GROUP BY da.grande_area
),
total AS (
  SELECT SUM(pesquisadores) AS total_pesquisadores FROM base
)
SELECT
  b.grande_area,
  b.pesquisadores,
  ROUND(100.0 * b.pesquisadores / t.total_pesquisadores, 2) AS pct_pesquisadores
FROM base b
CROSS JOIN total t
ORDER BY b.pesquisadores DESC;
"""

try:
    df_percentual = run_query(query_percentual)
    
    df_percentual['grande_area'] = df_percentual['grande_area'].apply(limpar_capitalizacao)
    
    fig3 = px.bar(
        df_percentual,
        x='pct_pesquisadores',
        y='grande_area',
        orientation='h',
        title='Percentual de Pesquisadores por Grande Área',
        labels={
            'pct_pesquisadores': 'Percentual (%)',
            'grande_area': 'Grande Área'
        },
        color='pct_pesquisadores',
        color_continuous_scale='Blues',
        text='pct_pesquisadores'
    )
    
    fig3 = apply_plotly_theme(fig3)
    fig3.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig3.update_layout(
        showlegend=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig3, use_container_width=True, config=get_plotly_config())
    
    with st.expander("💡 Insights"):
        maior_area = df_percentual.iloc[0]
        menor_area = df_percentual.iloc[-1]
        
        st.markdown(f"""
        **Destaques:**
        - 🥇 **Maior concentração:** {maior_area['grande_area']} com **{maior_area['pct_pesquisadores']:.2f}%** ({maior_area['pesquisadores']:,} pesquisadores)
        - 🥉 **Menor concentração:** {menor_area['grande_area']} com **{menor_area['pct_pesquisadores']:.2f}%** ({menor_area['pesquisadores']:,} pesquisadores)
        - 📊 **Diferença:** {maior_area['pct_pesquisadores'] - menor_area['pct_pesquisadores']:.2f} pontos percentuais
        """)
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")


# PERGUNTA 4: Distribuição Multi-área
st.header("4. Distribuição de Grandes Áreas por Pesquisador")
st.markdown("*Quantos pesquisadores têm 1, 2, 3... grandes áreas?*")

query_distribuicao = """
WITH por_pesq AS (
  SELECT
    fpa.id_pesquisador,
    COUNT(DISTINCT da.grande_area) AS qtd_grandes_areas
  FROM dw.fato_pesquisador_area_atuacao fpa
  JOIN dw.dim_area da ON da.id_area = fpa.id_area
  GROUP BY fpa.id_pesquisador
)
SELECT
  qtd_grandes_areas,
  COUNT(*) AS pesquisadores
FROM por_pesq
GROUP BY qtd_grandes_areas
ORDER BY qtd_grandes_areas;
"""

try:
    df_distrib = run_query(query_distribuicao)
    
    total_pesquisadores = df_distrib['pesquisadores'].sum()
    max_areas = df_distrib['qtd_grandes_areas'].max()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Total de Pesquisadores", f"{total_pesquisadores:,}")
    with col2:
        st.metric("Máximo de Áreas", int(max_areas))
    
    fig4 = px.bar(
        df_distrib,
        x='qtd_grandes_areas',
        y='pesquisadores',
        title='Distribuição: Quantidade de Grandes Áreas por Pesquisador',
        labels={
            'qtd_grandes_areas': 'Quantidade de Grandes Áreas',
            'pesquisadores': 'Quantidade de Pesquisadores'
        },
        color='qtd_grandes_areas',
        color_continuous_scale='Viridis'
    )
    
    fig4 = apply_plotly_theme(fig4)
    fig4.update_layout(showlegend=False, height=400)
    
    st.plotly_chart(fig4, use_container_width=True, config=get_plotly_config())
    
    with st.expander("💡 Insights"):
        mono_area = df_distrib[df_distrib['qtd_grandes_areas'] == 1]['pesquisadores'].sum() if 1 in df_distrib['qtd_grandes_areas'].values else 0
        multi_area = df_distrib[df_distrib['qtd_grandes_areas'] > 1]['pesquisadores'].sum()
        pct_mono = (mono_area / total_pesquisadores * 100) if total_pesquisadores > 0 else 0
        pct_multi = (multi_area / total_pesquisadores * 100) if total_pesquisadores > 0 else 0
        
        st.markdown(f"""
        **Análise da Distribuição:**
        - 🔵 **Mono-área (1 área):** {mono_area:,} pesquisadores ({pct_mono:.1f}%)
        - 🟢 **Multi-área (2+ áreas):** {multi_area:,} pesquisadores ({pct_multi:.1f}%)
        - 📈 **Máximo observado:** {int(max_areas)} grandes áreas
        
        **Interpretação:**
        A maioria dos pesquisadores ({pct_mono:.1f}%) atua em **apenas 1 grande área**, 
        indicando especialização. Apenas {pct_multi:.1f}% têm atuação interdisciplinar.
        """)
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# ========================================
# PERGUNTA 5: Top Pesquisadores Multi-área
# ========================================
st.header("5. Top Pesquisadores Multi-área")
st.markdown("*Quais pesquisadores têm mais áreas de atuação?*")

query_top_pesquisadores = """
SELECT
  dp.nome,
  COUNT(DISTINCT da.area) AS qtd_areas,
  COUNT(DISTINCT da.grande_area) AS qtd_grandes_areas
FROM dw.fato_pesquisador_area_atuacao fpa
JOIN dw.dim_pesquisador dp ON dp.id_pesquisador = fpa.id_pesquisador
JOIN dw.dim_area da ON da.id_area = fpa.id_area
GROUP BY dp.nome
ORDER BY qtd_grandes_areas DESC, qtd_areas DESC
LIMIT 10;
"""

try:
    df_top = run_query(query_top_pesquisadores)
    
    max_grandes_areas = df_top['qtd_grandes_areas'].max()
    max_areas = df_top['qtd_areas'].max()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Máximo de Grandes Áreas", int(max_grandes_areas))
    with col2:
        st.metric("Máximo de Áreas (detalhe)", int(max_areas))
    
    fig5 = px.bar(
        df_top,
        x='qtd_grandes_areas',
        y='nome',
        orientation='h',
        title='Top 10 Pesquisadores por Grandes Áreas',
        labels={
            'qtd_grandes_areas': 'Quantidade de Grandes Áreas',
            'nome': 'Pesquisador'
        },
        color='qtd_grandes_areas',
        color_continuous_scale='Oranges'
    )
    
    fig5 = apply_plotly_theme(fig5)
    fig5.update_layout(
        showlegend=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig5, use_container_width=True, config=get_plotly_config())
    
    with st.expander("📋 Ver ranking completo"):
        df_display = df_top.copy()
        df_display.index = range(1, len(df_display) + 1)
        df_display.columns = ['Pesquisador', 'Qtd Áreas', 'Qtd Grandes Áreas']
        
        st.dataframe(
            df_display,
            use_container_width=True
        )
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# ========================================
# FOOTER UFES
# ========================================
render_footer()

