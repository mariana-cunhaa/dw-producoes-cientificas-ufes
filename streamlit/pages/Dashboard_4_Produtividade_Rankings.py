"""
Dashboard 4: Produtividade e Rankings
Análises consolidadas sobre pesquisadores mais produtivos e pesquisadores ativos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from PIL import Image

sys.path.append(str(Path(__file__).parent.parent))
from db_utils import run_query
from ufes_theme import (
    load_css, 
    render_footer,
    apply_plotly_theme,
    get_plotly_config,
    CHART_COLORS,
    UFES_COLORS
)

st.set_page_config(
    page_title="Produtividade e Rankings - UFES",
    page_icon="🏆",
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
        st.title("Produtividade e Rankings")
        st.markdown("**Análises sobre pesquisadores mais produtivos e pesquisadores ativos**")
except Exception as e:
    st.title("Produtividade e Rankings")
    st.markdown("**Análises sobre pesquisadores mais produtivos e pesquisadores ativos**")

st.markdown("---")

# PERGUNTA 12: Top 20 Pesquisadores
st.header("12. Top 20 Pesquisadores Mais Produtivos")
st.markdown("*Ranking dos pesquisadores com maior número total de produções científicas*")

query_top_pesquisadores = """
SELECT
  dp.id_pesquisador,
  dp.id_lattes,
  dp.nome,
  SUM(f.qtd_producoes) AS total_producoes
FROM dw.fato_pesquisador_producoes f
JOIN dw.dim_pesquisador dp
  ON f.id_pesquisador = dp.id_pesquisador
GROUP BY
  dp.id_pesquisador,
  dp.id_lattes,
  dp.nome
ORDER BY
  total_producoes DESC
LIMIT 20;
"""

try:
    df_top20 = run_query(query_top_pesquisadores)
    
    total_top20 = df_top20['total_producoes'].sum()
    media_top20 = df_top20['total_producoes'].mean()
    primeiro_lugar = df_top20.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Produções (Top 20)", f"{total_top20:,}")
    with col2:
        st.metric("Média do Top 20", f"{media_top20:,.0f}")
    with col3:
        st.metric("1º Lugar", f"{primeiro_lugar['total_producoes']:,} produções")
    
    st.markdown("---")
    
    st.subheader("Ranking dos Top 20")
    
    fig1 = px.bar(
        df_top20,
        x='total_producoes',
        y='nome',
        orientation='h',
        title='Top 20 Pesquisadores Mais Produtivos',
        labels={
            'total_producoes': 'Total de Produções',
            'nome': 'Pesquisador'
        },
        color='total_producoes',
        color_continuous_scale='Oranges',
        text='total_producoes'
    )
    
    fig1 = apply_plotly_theme(fig1)
    fig1.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig1.update_layout(
        showlegend=False,
        height=600,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig1, use_container_width=True, config=get_plotly_config())
    
    with st.expander("📋 Ver ranking detalhado com ID Lattes"):
        df_display = df_top20[['nome', 'id_lattes', 'total_producoes']].copy()
        df_display.insert(0, 'Posição', range(1, 21))
        df_display.columns = ['Posição', 'Pesquisador', 'ID Lattes', 'Total de Produções']
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
    
    with st.expander("💡 Insights"):
        top_3 = df_top20.head(3)
        ultimo_lugar = df_top20.iloc[19]
        diferenca_1_20 = primeiro_lugar['total_producoes'] - ultimo_lugar['total_producoes']
        
        st.markdown(f"""
        **Pódio (Top 3):**
        """)
        
        for i, (idx, row) in enumerate(top_3.iterrows(), 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.markdown(f"{emoji} **{row['nome']}** - {row['total_producoes']:,} produções")
        
        st.markdown(f"""
        
        **Análise do Ranking:**
        - 📊 **Total do Top 20:** {total_top20:,} produções
        - 📈 **Média:** {media_top20:,.0f} produções por pesquisador
        - 🔝 **1º lugar:** {primeiro_lugar['nome']} ({primeiro_lugar['total_producoes']:,} produções)
        - 🔹 **20º lugar:** {ultimo_lugar['nome']} ({ultimo_lugar['total_producoes']:,} produções)
        - 📊 **Diferença 1º → 20º:** {diferenca_1_20:,} produções ({(diferenca_1_20/primeiro_lugar['total_producoes']*100):.1f}%)
        """)
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# PERGUNTA 13: Pesquisadores Ativos por Ano
st.header("13. Pesquisadores Ativos por Ano")
st.markdown("*Quantos pesquisadores publicaram em cada ano?*")

query_pesq_por_ano = """
SELECT
  dt.ano,
  COUNT(DISTINCT f.id_pesquisador) AS qtd_pesquisadores
FROM dw.fato_pesquisador_producoes f
JOIN dw.dim_tempo dt
  ON f.id_tempo = dt.id_tempo
GROUP BY dt.ano
ORDER BY dt.ano;
"""

try:
    df_pesq_ano = run_query(query_pesq_por_ano)
    
    ano_inicial = df_pesq_ano['ano'].min()
    ano_final = df_pesq_ano['ano'].max()
    max_pesquisadores = df_pesq_ano['qtd_pesquisadores'].max()
    ano_max = df_pesq_ano.loc[df_pesq_ano['qtd_pesquisadores'].idxmax(), 'ano']
    media_pesq = df_pesq_ano['qtd_pesquisadores'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Período", f"{ano_inicial} - {ano_final}")
    with col2:
        st.metric("Média de Pesquisadores/Ano", f"{media_pesq:,.0f}")
    with col3:
        st.metric("Ano com Mais Pesquisadores", int(ano_max))
    with col4:
        st.metric("Máximo de Pesquisadores", f"{max_pesquisadores:,}")
    
    st.markdown("---")
    
    st.subheader("Evolução da Quantidade de Pesquisadores Ativos")
    
    fig2 = px.line(
        df_pesq_ano,
        x='ano',
        y='qtd_pesquisadores',
        title='Evolução Anual de Pesquisadores Ativos',
        labels={
            'ano': 'Ano',
            'qtd_pesquisadores': 'Quantidade de Pesquisadores'
        },
        markers=True
    )
    
    fig2 = apply_plotly_theme(fig2)
    fig2.update_traces(line=dict(width=3, color='#2ca02c'), marker=dict(size=8))
    fig2.update_layout(height=450)
    
    st.plotly_chart(fig2, use_container_width=True, config=get_plotly_config())
    
    st.markdown("---")
    
    st.subheader("Crescimento na Base de Pesquisadores")
    
    df_crescimento = df_pesq_ano.copy()
    df_crescimento['variacao'] = df_crescimento['qtd_pesquisadores'].diff()
    df_crescimento = df_crescimento.dropna()
    
    fig3 = px.bar(
        df_crescimento,
        x='ano',
        y='variacao',
        title='Variação Anual no Número de Pesquisadores',
        labels={
            'ano': 'Ano',
            'variacao': 'Variação (novos pesquisadores)'
        },
        color='variacao',
        color_continuous_scale=['red', 'yellow', 'green'],
        color_continuous_midpoint=0
    )
    
    fig3 = apply_plotly_theme(fig3)
    fig3.update_layout(height=350)
    
    st.plotly_chart(fig3, use_container_width=True, config=get_plotly_config())
    
    with st.expander("💡 Insights"):
        ano_min = df_pesq_ano.loc[df_pesq_ano['qtd_pesquisadores'].idxmin(), 'ano']
        min_pesquisadores = df_pesq_ano['qtd_pesquisadores'].min()
        
        pesq_inicial = df_pesq_ano.iloc[0]['qtd_pesquisadores']
        pesq_final = df_pesq_ano.iloc[-1]['qtd_pesquisadores']
        crescimento_total = pesq_final - pesq_inicial
        crescimento_pct = (crescimento_total / pesq_inicial * 100) if pesq_inicial > 0 else 0
        
        st.markdown(f"""
        **Análise da Base de Pesquisadores:**
        - 📅 **Período:** {ano_inicial} a {ano_final}
        - 👥 **Média anual:** {media_pesq:,.0f} pesquisadores ativos
        
        **Extremos:**
        - 🔝 **Ano com mais pesquisadores:** {int(ano_max)} ({max_pesquisadores:,} pesquisadores)
        - 🔻 **Ano com menos pesquisadores:** {int(ano_min)} ({min_pesquisadores:,} pesquisadores)
        - 📊 **Diferença:** {max_pesquisadores - min_pesquisadores:,} pesquisadores
        
        **Crescimento da Base:**
        - {ano_inicial}: {pesq_inicial:,} pesquisadores
        - {ano_final}: {pesq_final:,} pesquisadores
        - **Variação total:** {crescimento_total:+,} pesquisadores ({crescimento_pct:+.1f}%)
        
        **Interpretação:**
        {"📈 Expansão da base" if crescimento_total > 0 else "📉 Contração da base" if crescimento_total < 0 else "➡️ Base estável"} de pesquisadores ao longo do período.
        
        **Observação:**
        - Este número representa pesquisadores **ativos** (que publicaram) em cada ano
        - Um pesquisador pode aparecer em múltiplos anos
        """)
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# FOOTER UFES
render_footer()

