"""
Data Warehouse - Produções Científicas UFES
Página inicial (Home) com visão geral do sistema
Tema personalizado: Universidade Federal do Espírito Santo
"""

import streamlit as st
from pathlib import Path
from PIL import Image
from db_utils import test_connection, get_metric_value
from ufes_theme import (
    load_css, 
    render_header, 
    render_logo, 
    render_footer,
    UFES_COLORS
)


st.set_page_config(
    page_title="DW Produções Científicas - UFES",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()


try:
    logo_path = Path(__file__).parent / "logo_ufes_app.png"
    logo = Image.open(logo_path)
    col_logo_center = st.columns([1, 2, 1])
    with col_logo_center[1]:
        st.image(logo, use_container_width=True)
except Exception as e:
    render_logo()


render_header(
    title="Data Warehouse - Produções Científicas",
    subtitle="Dashboard interativo para análise de produções científicas de pesquisadores da UFES"
)

st.markdown("") 

col_status1, col_status2 = st.columns([1, 3])

with col_status1:
    if test_connection():
        st.success("Banco conectado")
    else:
        st.error("Banco offline")

with col_status2:
    st.info("💡 Use o menu lateral para navegar entre as análises")

st.markdown("---")

st.header("📈 Visão Geral do Sistema")

col1, col2, col3, col4 = st.columns(4)

try:
    with col1:
        total_pesquisadores = get_metric_value("""
            SELECT COUNT(DISTINCT id_pesquisador) 
            FROM dw.dim_pesquisador;
        """)
        st.metric(
            label="Total de Pesquisadores",
            value=f"{total_pesquisadores:,}"
        )
    
    with col2:
        total_producoes = get_metric_value("""
            SELECT SUM(qtd_producoes) 
            FROM dw.fato_pesquisador_producoes;
        """)
        st.metric(
            label="Total de Produções",
            value=f"{total_producoes:,}"
        )
    
    with col3:
        total_areas = get_metric_value("""
            SELECT COUNT(DISTINCT grande_area) 
            FROM dw.dim_area;
        """)
        st.metric(
            label="Grandes Áreas",
            value=f"{total_areas}"
        )
    
    with col4:
        total_linhas = get_metric_value("""
            SELECT COUNT(*) 
            FROM dw.dim_linha_pesquisa;
        """)
        st.metric(
            label="Linhas de Pesquisa",
            value=f"{total_linhas:,}"
        )

except Exception as e:
    st.error(f"Erro ao carregar métricas gerais: {e}")

st.markdown("---")


st.header("🧭 Navegação Rápida")

col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns(5)

with col_nav1:
    st.page_link("pages/Dashboard_1_Areas_Atuacao.py", label="📊 Áreas de Atuação", use_container_width=True)
    st.markdown("""
    - Pesquisadores por área
    - Distribuição multi-área
    - Rankings
    """)

with col_nav2:
    st.page_link("pages/Dashboard_2_Linhas_Pesquisa.py", label="🔬 Linhas de Pesquisa", use_container_width=True)
    st.markdown("""
    - Top linhas
    - Distribuição
    - Concentração por área
    """)

with col_nav3:
    st.page_link("pages/Dashboard_3_Evolucao_Temporal.py", label="📈 Produções no Tempo", use_container_width=True)
    st.markdown("""
    - Evolução anual
    - Por tipo de produção
    - Tendências
    """)

with col_nav4:
    st.page_link("pages/Dashboard_4_Produtividade_Rankings.py", label="🏆 Produtividade e Rankings", use_container_width=True)
    st.markdown("""
    - Pesquisadores mais produtivos
    - Pesquisadores ativos
    - Análises consolidadas
    """)

with col_nav5:
    st.page_link("pages/Dashboard_5_Localizacao_Geografica.py", label="🌍 Localização", use_container_width=True)
    st.markdown("""
    - Produções por país
    - Instituições
    - Internacional vs Brasil
    """)

st.markdown("---")


render_footer()
