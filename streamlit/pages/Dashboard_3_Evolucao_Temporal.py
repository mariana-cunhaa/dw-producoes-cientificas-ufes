"""
Dashboard 3: Evolução Temporal e Tipos de Produção
Análises consolidadas sobre evolução temporal, tipos de produção e produtividade
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

# CONFIGURAÇÃO DA PÁGINA

st.set_page_config(
    page_title="Evolução Temporal - UFES",
    page_icon="📈",
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
        st.title("Evolução Temporal e Tipos de Produção")
        st.markdown("**Análises sobre evolução temporal, tipos de produção e produtividade**")
except Exception as e:
    st.title("Evolução Temporal e Tipos de Produção")
    st.markdown("**Análises sobre evolução temporal, tipos de produção e produtividade**")

st.markdown("---")

# PERGUNTA 9: Evolução Temporal
st.header("9. Evolução Temporal das Produções Científicas")
st.markdown("*Como evoluiu a produção científica ao longo do tempo?*")

query_evolucao = """
SELECT
  dt.ano,
  SUM(f.qtd_producoes) AS total_producoes
FROM dw.fato_pesquisador_producoes f
JOIN dw.dim_tempo dt
  ON f.id_tempo = dt.id_tempo
GROUP BY dt.ano
ORDER BY dt.ano;
"""

try:
    df_evolucao = run_query(query_evolucao)
    
    total_geral = df_evolucao['total_producoes'].sum()
    ano_inicial = df_evolucao['ano'].min()
    ano_final = df_evolucao['ano'].max()
    media_anual = df_evolucao['total_producoes'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Produções", f"{total_geral:,}")
    with col2:
        st.metric("Período", f"{ano_inicial} - {ano_final}")
    with col3:
        st.metric("Anos Analisados", len(df_evolucao))
    with col4:
        st.metric("Média Anual", f"{media_anual:,.0f}")
    
    st.markdown("---")
    
    fig1 = px.line(
        df_evolucao,
        x='ano',
        y='total_producoes',
        title='Evolução Anual da Produção Científica',
        labels={
            'ano': 'Ano',
            'total_producoes': 'Total de Produções'
        },
        markers=True
    )
    
    fig1 = apply_plotly_theme(fig1)
    fig1.update_traces(line=dict(width=3, color=UFES_COLORS['primary_blue']), marker=dict(size=8))
    fig1.update_layout(height=450)
    
    st.plotly_chart(fig1, use_container_width=True, config=get_plotly_config())
    
    st.markdown("---")
    
    st.subheader("Crescimento Ano a Ano")
    
    df_crescimento = df_evolucao.copy()
    df_crescimento['variacao_pct'] = df_crescimento['total_producoes'].pct_change() * 100
    df_crescimento = df_crescimento.dropna()
    
    fig2 = px.bar(
        df_crescimento,
        x='ano',
        y='variacao_pct',
        title='Variação Percentual Ano a Ano',
        labels={
            'ano': 'Ano',
            'variacao_pct': 'Variação (%)'
        },
        color='variacao_pct',
        color_continuous_scale=['red', 'yellow', 'green'],
        color_continuous_midpoint=0
    )
    
    fig2 = apply_plotly_theme(fig2)
    fig2.update_layout(height=350)
    
    st.plotly_chart(fig2, use_container_width=True, config=get_plotly_config())
    
    with st.expander("💡 Insights"):
        ano_max = df_evolucao.loc[df_evolucao['total_producoes'].idxmax()]
        ano_min = df_evolucao.loc[df_evolucao['total_producoes'].idxmin()]
        
        # Crescimento total do período
        producao_inicial = df_evolucao.iloc[0]['total_producoes']
        producao_final = df_evolucao.iloc[-1]['total_producoes']
        crescimento_total = ((producao_final - producao_inicial) / producao_inicial * 100) if producao_inicial > 0 else 0
        
        st.markdown(f"""
        **Análise Temporal:**
        - 📅 **Período analisado:** {ano_inicial} a {ano_final} ({len(df_evolucao)} anos)
        - 📊 **Total de produções:** {total_geral:,}
        - 📈 **Média anual:** {media_anual:,.0f} produções
        
        **Extremos:**
        - 🔝 **Ano com mais produções:** {int(ano_max['ano'])} ({ano_max['total_producoes']:,} produções)
        - 🔻 **Ano com menos produções:** {int(ano_min['ano'])} ({ano_min['total_producoes']:,} produções)
        
        **Crescimento:**
        - {ano_inicial}: {producao_inicial:,} produções
        - {ano_final}: {producao_final:,} produções
        - **Variação total:** {crescimento_total:+.1f}%
        """)
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# PERGUNTA 10: Distribuição por Tipo
st.header("10. Distribuição por Tipo de Produção")
st.markdown("*Qual é a distribuição da produção científica por tipo?*")

query_por_tipo = """
SELECT
  dtp.tipo_producao,
  SUM(f.qtd_producoes) AS total_producoes
FROM dw.fato_pesquisador_producoes f
JOIN dw.dim_tipo_producao dtp
  ON f.id_tipo_producao = dtp.id_tipo_producao
GROUP BY dtp.tipo_producao
ORDER BY total_producoes DESC;
"""

try:
    df_tipos = run_query(query_por_tipo)
    
    total_geral = df_tipos['total_producoes'].sum()
    df_tipos['percentual'] = (df_tipos['total_producoes'] / total_geral * 100).round(2)
    
    total_tipos = len(df_tipos)
    tipo_mais_comum = df_tipos.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Produções", f"{total_geral:,}")
    with col2:
        st.metric("Tipos de Produção", total_tipos)
    with col3:
        st.metric("Tipo Mais Comum", tipo_mais_comum['tipo_producao'])
    
    st.markdown("---")
    
    st.subheader("Total de Produções por Tipo")
    
    fig3 = px.bar(
        df_tipos,
        x='total_producoes',
        y='tipo_producao',
        orientation='h',
        title='Distribuição por Tipo de Produção',
        labels={
            'total_producoes': 'Total de Produções',
            'tipo_producao': 'Tipo de Produção'
        },
        color='total_producoes',
        color_continuous_scale='Blues',
        text='total_producoes'
    )
    
    fig3 = apply_plotly_theme(fig3)
    fig3.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig3.update_layout(
        showlegend=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig3, use_container_width=True, config=get_plotly_config())
    
    st.markdown("---")
    
    st.subheader("Distribuição Percentual por Tipo")
    
    fig4 = px.pie(
        df_tipos,
        values='total_producoes',
        names='tipo_producao',
        title='Percentual por Tipo de Produção',
        hole=0.3
    )
    
    fig4 = apply_plotly_theme(fig4)
    fig4.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig4, use_container_width=True, config=get_plotly_config())
    
    with st.expander("💡 Insights"):
        top_3 = df_tipos.head(3)
        top_3_total = top_3['total_producoes'].sum()
        top_3_pct = (top_3_total / total_geral * 100)
        
        st.markdown(f"""
        **Análise da Distribuição:**
        - 📊 **Total geral:** {total_geral:,} produções
        - 📚 **Tipos cadastrados:** {total_tipos}
        
        **Top 3 Tipos:**
        """)
        
        for i, (idx, row) in enumerate(top_3.iterrows(), 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.markdown(f"{emoji} **{row['tipo_producao']}:** {row['total_producoes']:,} produções ({row['percentual']:.2f}%)")
        
        st.markdown(f"""
        
        **Concentração:**
        - Os **Top 3** representam {top_3_pct:.1f}% do total
        - {'Alta concentração' if top_3_pct > 60 else 'Distribuição equilibrada'} entre os tipos
        """)
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# PERGUNTA 11: Média por Pesquisador
st.header("11. Média de Produções por Pesquisador ao Longo do Tempo")
st.markdown("*Qual é a média de produções por pesquisador ao longo do tempo?*")

query_media_temporal = """
SELECT
  dt.ano,
  ROUND(
    SUM(f.qtd_producoes) * 1.0
    / COUNT(DISTINCT f.id_pesquisador),
    2
  ) AS media_producoes_por_pesquisador
FROM dw.fato_pesquisador_producoes f
JOIN dw.dim_tempo dt
  ON f.id_tempo = dt.id_tempo
GROUP BY dt.ano
ORDER BY dt.ano;
"""

try:
    df_media = run_query(query_media_temporal)
    
    media_geral = df_media['media_producoes_por_pesquisador'].mean()
    ano_inicial = df_media['ano'].min()
    ano_final = df_media['ano'].max()
    max_media = df_media['media_producoes_por_pesquisador'].max()
    ano_max_media = df_media.loc[df_media['media_producoes_por_pesquisador'].idxmax(), 'ano']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Média Geral", f"{media_geral:.2f}")
    with col2:
        st.metric("Período", f"{ano_inicial} - {ano_final}")
    with col3:
        st.metric("Maior Média", f"{max_media:.2f}")
    with col4:
        st.metric("Ano (Maior Média)", int(ano_max_media))
    
    st.markdown("---")
    
    st.subheader("Evolução da Média de Produções por Pesquisador")
    
    fig5 = px.line(
        df_media,
        x='ano',
        y='media_producoes_por_pesquisador',
        title='Média de Produções por Pesquisador ao Longo do Tempo',
        labels={
            'ano': 'Ano',
            'media_producoes_por_pesquisador': 'Média de Produções por Pesquisador'
        },
        markers=True
    )
    
    fig5 = apply_plotly_theme(fig5)
    fig5.update_traces(line=dict(width=3, color='#ff7f0e'), marker=dict(size=8))
    fig5.update_layout(height=450)
    
    st.plotly_chart(fig5, use_container_width=True, config=get_plotly_config())
    
    st.markdown("---")
    
    st.subheader("Variação da Média Ano a Ano")
    
    df_variacao = df_media.copy()
    df_variacao['variacao'] = df_variacao['media_producoes_por_pesquisador'].diff()
    df_variacao = df_variacao.dropna()
    
    fig6 = px.bar(
        df_variacao,
        x='ano',
        y='variacao',
        title='Variação da Média Ano a Ano',
        labels={
            'ano': 'Ano',
            'variacao': 'Variação da Média'
        },
        color='variacao',
        color_continuous_scale=['red', 'yellow', 'green'],
        color_continuous_midpoint=0
    )
    
    fig6 = apply_plotly_theme(fig6)
    fig6.update_layout(height=350)
    
    st.plotly_chart(fig6, use_container_width=True, config=get_plotly_config())
    
    with st.expander("💡 Insights"):
        ano_min_media = df_media.loc[df_media['media_producoes_por_pesquisador'].idxmin(), 'ano']
        min_media = df_media['media_producoes_por_pesquisador'].min()
        
        media_primeira_metade = df_media.head(len(df_media)//2)['media_producoes_por_pesquisador'].mean()
        media_segunda_metade = df_media.tail(len(df_media)//2)['media_producoes_por_pesquisador'].mean()
        tendencia_pct = ((media_segunda_metade - media_primeira_metade) / media_primeira_metade * 100) if media_primeira_metade > 0 else 0
        
        st.markdown(f"""
        **Análise da Produtividade:**
        - 📊 **Média geral do período:** {media_geral:.2f} produções/pesquisador/ano
        - 📅 **Período analisado:** {ano_inicial} a {ano_final}
        
        **Extremos:**
        - 🔝 **Ano mais produtivo:** {int(ano_max_media)} (média de {max_media:.2f})
        - 🔻 **Ano menos produtivo:** {int(ano_min_media)} (média de {min_media:.2f})
        - 📊 **Diferença:** {max_media - min_media:.2f} produções/pesquisador
        
        **Tendência:**
        - 1ª metade: média de {media_primeira_metade:.2f}
        - 2ª metade: média de {media_segunda_metade:.2f}
        - **Variação:** {tendencia_pct:+.1f}%
        
        **Interpretação:**
        {"📈 Aumento da produtividade" if tendencia_pct > 0 else "📉 Queda da produtividade" if tendencia_pct < 0 else "➡️ Produtividade estável"} ao longo do período.
        """)
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# FOOTER UFES
render_footer()

