"""
Componentes padronizados para dashboards
Estrutura padrão: Cabeçalho → Filtros → Cartões → Gráficos
"""

import streamlit as st
from pathlib import Path
from PIL import Image
from ufes_theme import render_footer, UFES_COLORS

def render_dashboard_header(title, subtitle=None):
    """
    Renderiza cabeçalho padrão com logo UFES, título e navegação
    
    Args:
        title: Título da página
        subtitle: Subtítulo opcional
    """
    col_logo, col_title, col_nav = st.columns([1, 3, 1])
    
    with col_logo:
        try:
            logo_path = Path(__file__).parent / "logo_ufes.png"
            logo = Image.open(logo_path)
            st.image(logo, width=100)
        except:
            st.markdown("**UFES**")
    
    with col_title:
        st.markdown(f"# {title}")
        if subtitle:
            st.markdown(f"*{subtitle}*")
    
    with col_nav:
        st.markdown("**Navegação**")
        pages = {
            "🏠 Home": "/",
            "📊 Áreas": "Dashboard_1_Areas_Atuacao",
            "🔬 Linhas": "Dashboard_2_Linhas_Pesquisa",
            "📈 Temporal": "Dashboard_3_Evolucao_Temporal",
            "🏆 Rankings": "Dashboard_4_Produtividade_Rankings",
            "🌎 Localização": "Dashboard_5_Localizacao_Geografica"
        }
    
    st.markdown("---")


def render_filters_section(filters_config):
    """
    Renderiza seção de filtros padronizada
    
    Args:
        filters_config: Dicionário com configuração dos filtros
        
    Returns:
        dict: Valores selecionados nos filtros
    """
    st.markdown("### 🔍 Filtros")
    st.markdown("*Ajuste os filtros abaixo para personalizar a visualização dos dados*")
    
    selected_filters = {}
    
    cols = st.columns(len(filters_config))
    
    for idx, (filter_name, filter_data) in enumerate(filters_config.items()):
        with cols[idx]:
            if filter_data['type'] == 'selectbox':
                selected_filters[filter_name] = st.selectbox(
                    filter_data['label'],
                    options=filter_data['options'],
                    index=filter_data.get('default_index', 0),
                    key=f"filter_{filter_name}"
                )
            elif filter_data['type'] == 'multiselect':
                selected_filters[filter_name] = st.multiselect(
                    filter_data['label'],
                    options=filter_data['options'],
                    default=filter_data.get('default', []),
                    key=f"filter_{filter_name}"
                )
            elif filter_data['type'] == 'slider':
                selected_filters[filter_name] = st.slider(
                    filter_data['label'],
                    min_value=filter_data['min'],
                    max_value=filter_data['max'],
                    value=filter_data.get('default', (filter_data['min'], filter_data['max'])),
                    key=f"filter_{filter_name}"
                )
            elif filter_data['type'] == 'date_range':
                col1, col2 = st.columns(2)
                with col1:
                    date_start = st.date_input(
                        filter_data['label_start'],
                        value=filter_data.get('default_start'),
                        key=f"filter_{filter_name}_start"
                    )
                with col2:
                    date_end = st.date_input(
                        filter_data['label_end'],
                        value=filter_data.get('default_end'),
                        key=f"filter_{filter_name}_end"
                    )
                selected_filters[filter_name] = (date_start, date_end)
    
    st.markdown("---")
    return selected_filters


def render_metric_cards(metrics, cols_per_row=4):
    """
    Renderiza cartões de métricas em grid
    
    Args:
        metrics: Lista de dicionários com {label, value, delta, help}
        cols_per_row: Número de colunas por linha
    """
    st.markdown("### 📊 Indicadores Principais")
    
    rows = [metrics[i:i + cols_per_row] for i in range(0, len(metrics), cols_per_row)]
    
    for row in rows:
        cols = st.columns(len(row))
        for idx, metric in enumerate(row):
            with cols[idx]:
                st.metric(
                    label=metric['label'],
                    value=metric['value'],
                    delta=metric.get('delta'),
                    help=metric.get('help')
                )
    
    st.markdown("---")


def render_chart_section(title, chart_func, chart_data, description=None):
    """
    Renderiza uma seção de gráfico padronizada
    
    Args:
        title: Título do gráfico
        chart_func: Função que renderiza o gráfico
        chart_data: Dados para o gráfico
        description: Descrição opcional
    """
    st.markdown(f"### {title}")
    
    if description:
        st.markdown(f"*{description}*")
    
    chart_func(chart_data)
    
    st.markdown("")


def render_dashboard_footer():
    """
    Renderiza rodapé padrão dos dashboards
    """
    st.markdown("---")
    render_footer()


def create_download_button(df, filename="dados.csv", button_label="📥 Baixar dados"):
    """
    Cria botão para download de dados
    
    Args:
        df: DataFrame com os dados
        filename: Nome do arquivo
        button_label: Texto do botão
    """
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=button_label,
        data=csv,
        file_name=filename,
        mime='text/csv',
    )


def render_info_box(title, content, box_type="info"):
    """
    Renderiza caixa de informação/destaque
    
    Args:
        title: Título da caixa
        content: Conteúdo (pode ser markdown)
        box_type: Tipo da caixa (info, success, warning, error)
    """
    icons = {
        'info': '💡',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    icon = icons.get(box_type, '💡')
    
    if box_type == 'info':
        st.info(f"{icon} **{title}**\n\n{content}")
    elif box_type == 'success':
        st.success(f"{icon} **{title}**\n\n{content}")
    elif box_type == 'warning':
        st.warning(f"{icon} **{title}**\n\n{content}")
    elif box_type == 'error':
        st.error(f"{icon} **{title}**\n\n{content}")


def apply_filters_to_query(base_query, filters):
    """
    Aplica filtros a uma query SQL
    
    Args:
        base_query: Query SQL base
        filters: Dicionário com filtros selecionados
        
    Returns:
        str: Query modificada com filtros
    """
    query = base_query
    where_clauses = []
    
    for filter_name, filter_value in filters.items():
        if filter_value and filter_value != "Todos":
            if isinstance(filter_value, list) and len(filter_value) > 0:
                values_str = "', '".join(filter_value)
                where_clauses.append(f"{filter_name} IN ('{values_str}')")
            elif isinstance(filter_value, tuple):
                where_clauses.append(f"{filter_name} BETWEEN '{filter_value[0]}' AND '{filter_value[1]}'")
            elif not isinstance(filter_value, list):
                where_clauses.append(f"{filter_name} = '{filter_value}'")
    
    if where_clauses:
        if "WHERE" in query.upper():
            query += " AND " + " AND ".join(where_clauses)
        else:
            query += " WHERE " + " AND ".join(where_clauses)
    
    return query

