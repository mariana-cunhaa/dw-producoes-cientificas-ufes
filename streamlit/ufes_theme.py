"""
Módulo de tema UFES para aplicações Streamlit
Cores oficiais da Universidade Federal do Espírito Santo
"""

import streamlit as st
import pandas as pd
import re
from pathlib import Path

# ========================================
# FUNÇÕES AUXILIARES DE LIMPEZA DE DADOS
# ========================================
def limpar_capitalizacao(texto):
    """
    Corrige problemas de capitalização incorreta nos dados provenientes do banco.
    
    Exemplos de correção:
    - 'EducaçãO' -> 'Educação'
    - 'InteligêNcia' -> 'Inteligência'
    - 'ProduçãO' -> 'Produção'
    - 'FísIca' -> 'Física'
    
    Args:
        texto (str): Texto a ser corrigido
        
    Returns:
        str: Texto com capitalização corrigida
    """
    if pd.isna(texto) or not isinstance(texto, str):
        return texto
    
    # Mapeamento de correções específicas conhecidas
    correcoes = {
        # Educação e variantes
        'EducaçãO': 'Educação',
        'educaçãO': 'educação',
        
        # Produção e variantes
        'ProduçãO': 'Produção',
        'produçãO': 'produção',
        
        # Inteligência e variantes
        'InteligêNcia': 'Inteligência',
        'inteligêNcia': 'inteligência',
        
        # Eficiência e variantes
        'EficiêNcia': 'Eficiência',
        'eficiêNcia': 'eficiência',
        
        # Ciência
        'CiêNcia': 'Ciência',
        'ciêNcia': 'ciência',
        
        # Outras palavras comuns
        'TecnolOgia': 'Tecnologia',
        'GestaO': 'Gestão',
        'AvaliaçãO': 'Avaliação',
        'InformaçãO': 'Informação',
        'ComunicaçãO': 'Comunicação',
        'FísIca': 'Física',
        'QuímIca': 'Química',
        'BiologIa': 'Biologia',
        'MatemáTica': 'Matemática',
        'HistóRia': 'História',
        'GeografIa': 'Geografia',
    }
    
    # Aplicar correções específicas primeiro
    for errado, correto in correcoes.items():
        texto = texto.replace(errado, correto)
    
    # Correções genéricas via regex
    # Corrige padrões como "çãO" -> "ção"
    texto = re.sub(r'çãO\b', 'ção', texto)
    texto = re.sub(r'çãO([^a-zA-Z])', r'ção\1', texto)
    
    # Corrige padrões como "êNcia" -> "ência"
    texto = re.sub(r'êNcia\b', 'ência', texto)
    texto = re.sub(r'êNcia([^a-zA-Z])', r'ência\1', texto)
    
    # Corrige padrões como "Ologia" -> "ologia"
    texto = re.sub(r'OlogIa\b', 'ologia', texto)
    texto = re.sub(r'TecnolOgia', 'Tecnologia', texto)
    
    # Corrige padrões como "Ica" no final
    texto = re.sub(r'([a-zà-ú])Ica\b', r'\1ica', texto)
    
    return texto

# ========================================
# CORES OFICIAIS DA UFES
# ========================================
UFES_COLORS = {
    'primary_blue': '#004B87',      # Azul UFES principal
    'secondary_blue': '#0066A1',    # Azul UFES secundário
    'light_blue': '#0099CC',        # Azul claro
    'sky_blue': '#00BFFF',          # Azul céu (accent)
    'white': '#FFFFFF',             # Branco
    'light_gray': '#F8F9FA',        # Cinza claro
    'medium_gray': '#E9ECEF',       # Cinza médio
    'dark_gray': '#262730',         # Cinza escuro (texto)
    'success': '#28A745',           # Verde (sucesso)
    'warning': '#FFC107',           # Amarelo (aviso)
    'error': '#DC3545',             # Vermelho (erro)
    'info': '#17A2B8',              # Azul info
}

# ========================================
# PALETA DE CORES PARA GRÁFICOS
# ========================================
CHART_COLORS = [
    '#004B87',  # Azul UFES principal
    '#0099CC',  # Azul claro
    '#00BFFF',  # Azul céu
    '#0066A1',  # Azul UFES secundário
    '#17A2B8',  # Azul info
    '#28A745',  # Verde
    '#FFC107',  # Amarelo
    '#FF6B35',  # Laranja
    '#6C757D',  # Cinza
    '#9B59B6',  # Roxo
]

# ========================================
# CONFIGURAÇÃO PLOTLY PARA UFES
# ========================================
PLOTLY_TEMPLATE = {
    'layout': {
        'colorway': CHART_COLORS,
        'font': {
            'family': 'sans-serif',
            'color': UFES_COLORS['dark_gray']
        },
        'title': {
            'font': {
                'size': 22,
                'color': UFES_COLORS['primary_blue'],
                'family': 'sans-serif'
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        'plot_bgcolor': UFES_COLORS['white'],
        'paper_bgcolor': UFES_COLORS['white'],
        'xaxis': {
            'gridcolor': UFES_COLORS['medium_gray'],
            'linecolor': UFES_COLORS['medium_gray'],
            'title': {
                'font': {
                    'color': UFES_COLORS['primary_blue'],
                    'size': 14
                }
            }
        },
        'yaxis': {
            'gridcolor': UFES_COLORS['medium_gray'],
            'linecolor': UFES_COLORS['medium_gray'],
            'title': {
                'font': {
                    'color': UFES_COLORS['primary_blue'],
                    'size': 14
                }
            }
        }
    }
}

# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def load_css():
    """Carrega o CSS personalizado do tema UFES"""
    try:
        # Usa caminho relativo ao arquivo atual
        css_path = Path(__file__).parent / "style.css"
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Arquivo CSS não encontrado. Usando tema padrão.")

def render_header(title, subtitle=None):
    """
    Renderiza o cabeçalho com o tema UFES
    
    Args:
        title (str): Título principal
        subtitle (str, optional): Subtítulo/descrição
    """
    header_html = f"""
    <div class="ufes-header">
        <h1>{title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_logo():
    """Renderiza o logo da UFES no topo da página"""
    logo_html = """
    <div style="text-align: center; padding: 20px 0; background: white; border-radius: 10px; margin-bottom: 20px;">
        <div style="display: inline-block;">
            <svg width="200" height="60" viewBox="0 0 200 60">
                <rect x="0" y="0" width="80" height="60" fill="#004B87"/>
                <rect x="80" y="40" width="20" height="20" fill="#00BFFF"/>
                <text x="110" y="35" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#004B87">UFES</text>
                <text x="110" y="50" font-family="Arial, sans-serif" font-size="8" fill="#666">Universidade Federal do Espírito Santo</text>
            </svg>
        </div>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

def render_footer():
    """Renderiza o rodapé com informações da UFES"""
    footer_html = """
    <div class="ufes-footer">
        <svg width="150" height="45" viewBox="0 0 200 60" style="margin-bottom: 10px;">
            <rect x="0" y="0" width="80" height="60" fill="#004B87"/>
            <rect x="80" y="40" width="20" height="20" fill="#00BFFF"/>
            <text x="110" y="35" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#004B87">UFES</text>
            <text x="110" y="50" font-family="Arial, sans-serif" font-size="8" fill="#666">Universidade Federal do Espírito Santo</text>
        </svg>
        <p style="color: #666; margin: 10px 0 5px 0; font-size: 0.9rem;">
            Data Warehouse - Produções Científicas
        </p>
        <p style="color: #999; margin: 0; font-size: 0.8rem;">
            Desenvolvido com Streamlit | © 2026 UFES
        </p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def metric_card(label, value, icon="📊"):
    """
    Cria um card de métrica estilizado
    
    Args:
        label (str): Rótulo da métrica
        value: Valor da métrica
        icon (str): Emoji ou ícone
    """
    card_html = f"""
    <div class="metric-card">
        <div style="font-size: 1.5rem; margin-bottom: 5px;">{icon}</div>
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">{label}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #004B87;">{value}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def badge(text, color='primary'):
    """
    Cria um badge estilizado
    
    Args:
        text (str): Texto do badge
        color (str): 'primary', 'success', 'warning', 'error', 'info'
    """
    color_map = {
        'primary': '#004B87',
        'success': '#28A745',
        'warning': '#FFC107',
        'error': '#DC3545',
        'info': '#17A2B8'
    }
    bg_color = color_map.get(color, UFES_COLORS['primary_blue'])
    
    badge_html = f"""
    <span style="
        display: inline-block;
        background: {bg_color};
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 5px;
    ">{text}</span>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

def get_plotly_config():
    """Retorna a configuração Plotly com tema UFES"""
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'grafico_ufes',
            'height': 600,
            'width': 1000,
            'scale': 2
        }
    }

def apply_plotly_theme(fig):
    """
    Aplica o tema UFES a um gráfico Plotly
    
    Args:
        fig: Figura Plotly
    
    Returns:
        Figura com tema aplicado
    """
    fig.update_layout(
        font=dict(family='sans-serif', color=UFES_COLORS['dark_gray']),
        title_font=dict(size=22, color=UFES_COLORS['primary_blue'], family='sans-serif'),
        plot_bgcolor=UFES_COLORS['white'],
        paper_bgcolor=UFES_COLORS['white'],
        xaxis=dict(
            gridcolor=UFES_COLORS['medium_gray'],
            linecolor=UFES_COLORS['medium_gray'],
            title_font=dict(color=UFES_COLORS['primary_blue'], size=14)
        ),
        yaxis=dict(
            gridcolor=UFES_COLORS['medium_gray'],
            linecolor=UFES_COLORS['medium_gray'],
            title_font=dict(color=UFES_COLORS['primary_blue'], size=14)
        ),
        colorway=CHART_COLORS,
        margin=dict(t=80, b=60, l=60, r=40)
    )
    return fig

