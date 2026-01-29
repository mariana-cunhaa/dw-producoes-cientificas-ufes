"""
Exemplos Práticos de Uso do Tema UFES
Exemplos de código para diferentes tipos de visualizações
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Importar tema UFES
sys.path.append(str(Path(__file__).parent))
from ufes_theme import (
    load_css,
    render_header,
    render_logo,
    render_footer,
    apply_plotly_theme,
    get_plotly_config,
    metric_card,
    badge,
    CHART_COLORS,
    UFES_COLORS
)

# ========================================
# CONFIGURAÇÃO DA PÁGINA
# ========================================
st.set_page_config(
    page_title="Exemplos - Tema UFES",
    page_icon="🎨",
    layout="wide"
)

# ========================================
# CARREGAR TEMA UFES
# ========================================
load_css()

# ========================================
# LOGO E HEADER
# ========================================
render_logo()

render_header(
    title="🎨 Exemplos do Tema UFES",
    subtitle="Galeria de componentes e visualizações com identidade visual da UFES"
)

# ========================================
# 1. MÉTRICAS
# ========================================
st.header("📊 Métricas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Pesquisadores", "1,234", "+12%")

with col2:
    st.metric("📚 Publicações", "5,678", "+8%")

with col3:
    st.metric("🔬 Projetos", "234", "-3%")

with col4:
    st.metric("🌍 Parcerias", "89", "+15%")

st.markdown("---")

# ========================================
# 2. BADGES
# ========================================
st.header("🏷️ Badges")

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("**Tipos disponíveis:**")
    
with col2:
    badge("Primary - Azul UFES", color='primary')
    badge("Sucesso", color='success')
    badge("Atenção", color='warning')
    badge("Erro", color='error')
    badge("Informação", color='info')

st.markdown("---")

# ========================================
# 3. GRÁFICO DE BARRAS
# ========================================
st.header("📊 Gráfico de Barras")

# Dados de exemplo
df_barras = pd.DataFrame({
    'Area': ['Ciências Exatas', 'Engenharias', 'Saúde', 'Humanas', 'Biológicas'],
    'Pesquisadores': [320, 450, 280, 190, 240]
})

fig_barras = px.bar(
    df_barras,
    x='Pesquisadores',
    y='Area',
    orientation='h',
    title='Pesquisadores por Área de Conhecimento',
    color='Pesquisadores',
    color_continuous_scale=[
        [0, UFES_COLORS['light_blue']],
        [0.5, UFES_COLORS['secondary_blue']],
        [1, UFES_COLORS['primary_blue']]
    ],
    text='Pesquisadores'
)

fig_barras = apply_plotly_theme(fig_barras)
fig_barras.update_traces(texttemplate='%{text}', textposition='outside')
fig_barras.update_layout(height=400, showlegend=False)

st.plotly_chart(fig_barras, use_container_width=True, config=get_plotly_config())

# Código de exemplo
with st.expander("💻 Ver código"):
    st.code("""
import plotly.express as px
from ufes_theme import apply_plotly_theme, get_plotly_config, UFES_COLORS

fig = px.bar(df, x='Pesquisadores', y='Area', orientation='h',
             color='Pesquisadores',
             color_continuous_scale=[
                 [0, UFES_COLORS['light_blue']],
                 [0.5, UFES_COLORS['secondary_blue']],
                 [1, UFES_COLORS['primary_blue']]
             ])

fig = apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())
""", language='python')

st.markdown("---")

# ========================================
# 4. GRÁFICO DE PIZZA
# ========================================
st.header("🥧 Gráfico de Pizza")

# Dados de exemplo
df_pizza = pd.DataFrame({
    'Categoria': ['Artigos', 'Livros', 'Capítulos', 'Eventos', 'Outros'],
    'Quantidade': [450, 120, 200, 180, 90]
})

fig_pizza = px.pie(
    df_pizza,
    values='Quantidade',
    names='Categoria',
    title='Distribuição de Produções Científicas',
    color_discrete_sequence=CHART_COLORS
)

fig_pizza = apply_plotly_theme(fig_pizza)
fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
fig_pizza.update_layout(height=500)

st.plotly_chart(fig_pizza, use_container_width=True, config=get_plotly_config())

with st.expander("💻 Ver código"):
    st.code("""
import plotly.express as px
from ufes_theme import apply_plotly_theme, get_plotly_config, CHART_COLORS

fig = px.pie(df, values='Quantidade', names='Categoria',
             color_discrete_sequence=CHART_COLORS)

fig = apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())
""", language='python')

st.markdown("---")

# ========================================
# 5. GRÁFICO DE LINHAS
# ========================================
st.header("📈 Gráfico de Linhas")

# Dados de exemplo
anos = list(range(2015, 2026))
df_linhas = pd.DataFrame({
    'Ano': anos * 3,
    'Tipo': ['Artigos'] * len(anos) + ['Livros'] * len(anos) + ['Capítulos'] * len(anos),
    'Quantidade': [45, 52, 58, 65, 72, 78, 85, 92, 98, 105, 110] +
                  [12, 15, 18, 20, 22, 25, 28, 30, 33, 35, 38] +
                  [20, 25, 28, 32, 35, 38, 42, 45, 48, 50, 52]
})

fig_linhas = px.line(
    df_linhas,
    x='Ano',
    y='Quantidade',
    color='Tipo',
    title='Evolução Temporal de Produções Científicas',
    markers=True,
    color_discrete_sequence=CHART_COLORS
)

fig_linhas = apply_plotly_theme(fig_linhas)
fig_linhas.update_layout(height=500, hovermode='x unified')

st.plotly_chart(fig_linhas, use_container_width=True, config=get_plotly_config())

with st.expander("💻 Ver código"):
    st.code("""
import plotly.express as px
from ufes_theme import apply_plotly_theme, get_plotly_config, CHART_COLORS

fig = px.line(df, x='Ano', y='Quantidade', color='Tipo',
              markers=True, color_discrete_sequence=CHART_COLORS)

fig = apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())
""", language='python')

st.markdown("---")

# ========================================
# 6. TABELAS ESTILIZADAS
# ========================================
st.header("📋 Tabelas Estilizadas")

df_tabela = pd.DataFrame({
    'Pesquisador': ['Ana Silva', 'João Santos', 'Maria Oliveira', 'Pedro Costa'],
    'Área': ['Engenharia', 'Saúde', 'Humanas', 'Exatas'],
    'Publicações': [45, 38, 52, 41],
    'H-Index': [12, 10, 15, 11]
})

st.dataframe(
    df_tabela.style.format({'Publicações': '{:.0f}', 'H-Index': '{:.0f}'}),
    use_container_width=True,
    height=200
)

st.markdown("---")

# ========================================
# 7. ALERTAS E MENSAGENS
# ========================================
st.header("💬 Alertas e Mensagens")

col1, col2 = st.columns(2)

with col1:
    st.success("✅ Operação concluída com sucesso!")
    st.info("ℹ️ Informação importante sobre os dados")

with col2:
    st.warning("⚠️ Atenção: Alguns dados estão pendentes")
    st.error("❌ Erro ao conectar com o banco de dados")

st.markdown("---")

# ========================================
# 8. BOTÕES
# ========================================
st.header("🔘 Botões")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button("Botão Principal", type="primary")

with col2:
    st.button("Botão Secundário")

with col3:
    st.download_button("Download", data="exemplo", file_name="dados.csv")

with col4:
    st.button("🔄 Atualizar")

st.markdown("---")

# ========================================
# 9. PALETA DE CORES
# ========================================
st.header("🎨 Paleta de Cores UFES")

st.markdown("### Cores Principais")

cores_principais = [
    ("Azul Principal", UFES_COLORS['primary_blue']),
    ("Azul Secundário", UFES_COLORS['secondary_blue']),
    ("Azul Claro", UFES_COLORS['light_blue']),
    ("Azul Céu", UFES_COLORS['sky_blue'])
]

cols = st.columns(4)
for i, (nome, cor) in enumerate(cores_principais):
    with cols[i]:
        st.markdown(f"""
        <div style="background: {cor}; padding: 40px; border-radius: 10px; text-align: center;">
            <p style="color: white; font-weight: bold; margin: 0;">{nome}</p>
            <p style="color: white; margin: 5px 0 0 0; font-size: 0.9rem;">{cor}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("### Cores para Gráficos")

cols = st.columns(5)
for i, cor in enumerate(CHART_COLORS[:5]):
    with cols[i]:
        st.markdown(f"""
        <div style="background: {cor}; padding: 30px; border-radius: 8px; text-align: center;">
            <p style="color: white; font-weight: bold; margin: 0; font-size: 0.9rem;">{cor}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ========================================
# FOOTER
# ========================================
render_footer()

