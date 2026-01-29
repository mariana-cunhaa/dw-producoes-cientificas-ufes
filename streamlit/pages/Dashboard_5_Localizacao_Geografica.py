"""
Dashboard 5: Localização Geográfica
Análises consolidadas sobre localização geográfica das produções (UFES, Brasil e Internacional)
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
    page_title="Localização Geográfica - UFES",
    page_icon="🌎",
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
        st.title("Localização Geográfica")
        st.markdown("**Análises sobre localização geográfica das produções científicas**")
except Exception as e:
    st.title("Localização Geográfica")
    st.markdown("**Análises sobre localização geográfica das produções científicas**")

st.markdown("---")

# PERGUNTA 14: Apresentações de Trabalho na UFES
st.header("14. Apresentações de Trabalho na UFES")
st.markdown("*Quantas apresentações de trabalho ocorreram na UFES ao longo dos anos?*")

query_anos = """
SELECT DISTINCT dt.ano
FROM dw.fato_pesquisador_producao_localizacao f
JOIN dw.dim_tempo dt
  ON dt.id_tempo = f.id_tempo
JOIN dw.dim_tipo_producao dtp
  ON dtp.id_tipo_producao = f.id_tipo_producao
WHERE dtp.tipo_producao = 'Apresentação de Trabalho'
ORDER BY dt.ano;
"""

try:
    df_anos = run_query(query_anos)
    anos_disponiveis = [int(x) for x in df_anos["ano"].tolist()] if not df_anos.empty else []
    
    if anos_disponiveis:
        col_f1, col_f2 = st.columns([1, 2])
        
        with col_f1:
            termo_busca = st.text_input("Termo de busca para instituição", value="UFES", help="Busca por UFES ou Universidade Federal do Espírito Santo")
        
        with col_f2:
            ano_ini, ano_fim = st.slider(
                "Selecione o intervalo de anos",
                min_value=min(anos_disponiveis),
                max_value=max(anos_disponiveis),
                value=(min(anos_disponiveis), max(anos_disponiveis)),
                step=1,
            )
        
        query_ufes = f"""
        SELECT
          dt.ano,
          SUM(f.qtd_producoes) AS total_apresentacoes
        FROM dw.fato_pesquisador_producao_localizacao f
        JOIN dw.dim_tempo dt
          ON dt.id_tempo = f.id_tempo
        JOIN dw.dim_tipo_producao dtp
          ON dtp.id_tipo_producao = f.id_tipo_producao
        JOIN dw.dim_localizacao_trabalhos dlt
          ON dlt.id_localizacao_trabalhos = f.id_localizacao_trabalhos
        WHERE dtp.tipo_producao = 'Apresentação de Trabalho'
          AND (
            dlt.instituicao ILIKE '%{termo_busca}%' OR
            dlt.instituicao ILIKE '%Universidade Federal do Espírito Santo%'
          )
          AND dt.ano BETWEEN {int(ano_ini)} AND {int(ano_fim)}
        GROUP BY dt.ano
        ORDER BY dt.ano;
        """
        
        df_ufes = run_query(query_ufes)
        
        if not df_ufes.empty:
            total_geral = int(df_ufes["total_apresentacoes"].sum())
            anos_qtd = int(df_ufes["ano"].nunique())
            media_anual = (total_geral / anos_qtd) if anos_qtd else 0
            
            melhor = df_ufes.loc[df_ufes["total_apresentacoes"].idxmax()]
            melhor_ano = int(melhor["ano"])
            melhor_total = int(melhor["total_apresentacoes"])
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total de Apresentações", f"{total_geral:,}")
            k2.metric("Anos Analisados", f"{anos_qtd}")
            k3.metric("Média por ano", f"{media_anual:,.0f}")
            k4.metric("Melhor ano", f"{melhor_ano} ({melhor_total:,})")
            
            st.markdown("---")
            
            fig1 = px.line(
                df_ufes,
                x='ano',
                y='total_apresentacoes',
                title='Evolução Anual de Apresentações na UFES',
                labels={
                    'ano': 'Ano',
                    'total_apresentacoes': 'Total de Apresentações'
                },
                markers=True
            )
            
            fig1 = apply_plotly_theme(fig1)
            fig1.update_traces(line=dict(width=3, color='#2ca02c'), marker=dict(size=8))
            fig1.update_layout(height=450)
            
            st.plotly_chart(fig1, use_container_width=True, config=get_plotly_config())
            
        else:
            st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    else:
        st.error("❌ Não foram encontrados anos disponíveis para 'Apresentação de Trabalho'.")
        
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# PERGUNTA 15: Pesquisadores com Produções Internacionais
st.header("15. Pesquisadores com Mais Produções Internacionais")
st.markdown("*Ranking de pesquisadores por volume de trabalhos em eventos e apresentações fora do Brasil*")

query_internacional = """
SELECT
  dp.nome,
  SUM(f.qtd_producoes) AS total_internacional
FROM dw.fato_pesquisador_producao_localizacao f
JOIN dw.dim_pesquisador dp ON dp.id_pesquisador = f.id_pesquisador
JOIN dw.dim_localizacao_trabalhos dlt ON dlt.id_localizacao_trabalhos = f.id_localizacao_trabalhos
WHERE dlt.pais IS NOT NULL
  AND dlt.pais <> 'Brasil'
GROUP BY dp.nome
ORDER BY total_internacional DESC;
"""

try:
    df_int = run_query(query_internacional)
    
    if len(df_int) > 0:
        max_pesquisadores = len(df_int)
        top_n = st.slider(
            "Top pesquisadores (ranking)",
            min_value=5,
            max_value=min(50, max_pesquisadores),
            value=20,
            step=5
        )
        
        df_top = df_int.head(top_n)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_producoes = df_int['total_internacional'].sum()
            st.metric("Total de Produções Internacionais", f"{total_producoes:,}")
        
        with col2:
            st.metric("Pesquisadores com Prod. Internacional", f"{len(df_int):,}")
        
        with col3:
            media_top = df_top['total_internacional'].mean()
            st.metric(f"Média (Top {top_n})", f"{media_top:,.1f}")
        
        st.markdown("---")
        
        fig2 = px.bar(
            df_top,
            x='total_internacional',
            y='nome',
            orientation='h',
            title=f'Top {top_n} Pesquisadores com Produções Internacionais',
            labels={
                'total_internacional': 'Total de Produções Internacionais',
                'nome': 'Pesquisador'
            },
            color='total_internacional',
            color_continuous_scale='Oranges',
            text='total_internacional'
        )
        
        fig2 = apply_plotly_theme(fig2)
        fig2.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig2.update_layout(
            showlegend=False,
            height=max(400, top_n * 25),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig2, use_container_width=True, config=get_plotly_config())
        
        with st.expander("📋 Ver tabela completa"):
            df_display = df_top.copy()
            df_display.insert(0, 'Posição', range(1, len(df_display) + 1))
            df_display.columns = ['Posição', 'Nome do Pesquisador', 'Produções Internacionais']
            df_display['% do Total'] = (100 * df_display['Produções Internacionais'] / total_producoes).round(2)
            
            st.dataframe(
                df_display.style.format({
                    'Produções Internacionais': '{:,.0f}',
                    '% do Total': '{:.2f}%'
                }),
                use_container_width=True,
                height=400
            )
    else:
        st.warning("⚠️ Nenhum dado encontrado")
        
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# PERGUNTA 16: Brasil vs Internacional (Anual)
st.header("16. Brasil vs Internacional (Anual)")
st.markdown("*Comparação do total anual de produções no Brasil vs fora do Brasil*")

query_anos_geral = """
SELECT DISTINCT dt.ano
FROM dw.fato_pesquisador_producao_localizacao f
JOIN dw.dim_tempo dt
  ON dt.id_tempo = f.id_tempo
ORDER BY dt.ano;
"""

try:
    df_anos_geral = run_query(query_anos_geral)
    anos = [int(x) for x in df_anos_geral["ano"].tolist()] if not df_anos_geral.empty else []
    
    if anos:
        ano_min, ano_max = min(anos), max(anos)
        
        ano_ini, ano_fim = st.slider(
            "Filtro de anos",
            min_value=ano_min,
            max_value=ano_max,
            value=(max(ano_min, 2010), ano_max) if ano_max >= 2010 else (ano_min, ano_max),
            step=1,
        )
        
        query_brasil_int = f"""
        SELECT
          dt.ano,
          CASE WHEN dlt.pais = 'Brasil' THEN 'Brasil' ELSE 'Internacional' END AS origem,
          SUM(f.qtd_producoes) AS total
        FROM dw.fato_pesquisador_producao_localizacao f
        JOIN dw.dim_tempo dt ON dt.id_tempo = f.id_tempo
        JOIN dw.dim_localizacao_trabalhos dlt ON dlt.id_localizacao_trabalhos = f.id_localizacao_trabalhos
        WHERE dt.ano BETWEEN {int(ano_ini)} AND {int(ano_fim)}
        GROUP BY dt.ano, origem
        ORDER BY dt.ano, origem;
        """
        
        df_brasil_int = run_query(query_brasil_int)
        
        if not df_brasil_int.empty:
            total_geral = int(df_brasil_int["total"].sum())
            total_brasil = int(df_brasil_int.loc[df_brasil_int["origem"] == "Brasil", "total"].sum())
            total_int = int(df_brasil_int.loc[df_brasil_int["origem"] == "Internacional", "total"].sum())
            pct_int = (100.0 * total_int / total_geral) if total_geral else 0.0
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total (período)", f"{total_geral:,}")
            k2.metric("Brasil", f"{total_brasil:,}")
            k3.metric("Internacional", f"{total_int:,}")
            k4.metric("% Internacional", f"{pct_int:.1f}%")
            
            st.markdown("---")
            
            fig3 = px.line(
                df_brasil_int,
                x='ano',
                y='total',
                color='origem',
                title='Evolução Anual: Brasil vs Internacional',
                labels={
                    'ano': 'Ano',
                    'total': 'Total de Produções',
                    'origem': 'Origem'
                },
                markers=True,
                color_discrete_map={'Brasil': '#2ca02c', 'Internacional': '#ff7f0e'}
            )
            
            fig3 = apply_plotly_theme(fig3)
            fig3.update_traces(line=dict(width=3), marker=dict(size=8))
            fig3.update_layout(height=450)
            
            st.plotly_chart(fig3, use_container_width=True, config=get_plotly_config())
            
            st.markdown("---")
            
            st.subheader("Visualização Alternativa: Área Empilhada")
            
            fig4 = px.area(
                df_brasil_int,
                x='ano',
                y='total',
                color='origem',
                title='Distribuição Brasil vs Internacional (Área Empilhada)',
                labels={
                    'ano': 'Ano',
                    'total': 'Total de Produções',
                    'origem': 'Origem'
                },
                color_discrete_map={'Brasil': '#2ca02c', 'Internacional': '#ff7f0e'}
            )
            
            fig4 = apply_plotly_theme(fig4)
            fig4.update_layout(height=400)
            
            st.plotly_chart(fig4, use_container_width=True, config=get_plotly_config())
            
        else:
            st.warning("⚠️ Nenhum dado encontrado para o intervalo selecionado.")
    else:
        st.error("❌ Não foram encontrados anos disponíveis.")
        
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")

st.markdown("---")

# FOOTER UFES
render_footer()

