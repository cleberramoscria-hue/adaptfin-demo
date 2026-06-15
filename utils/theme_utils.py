"""
Utilitários de Tema - Aplicação global
"""
import streamlit as st

def aplicar_tema_global():
    """Aplica o tema selecionado em todas as páginas"""
    tema = st.session_state.configuracoes.get("tema", "Claro")
    
    temas_css = {
        "Claro": """
        <style>
        .stApp { background-color: #ffffff !important; }
        .stMarkdown, .stText, .stTitle, .stSubheader, p, label { color: #000000 !important; }
        [data-testid="stSidebar"] { background-color: #f0f2f6 !important; }
        [data-testid="stMetric"] { background-color: #f0f2f6 !important; padding: 10px !important; border-radius: 10px !important; }
        .stButton > button { background-color: #4CAF50 !important; color: white !important; }
        .stDataFrame { background-color: #ffffff !important; }
        </style>
        """,
        
        "Escuro": """
        <style>
        .stApp { background-color: #0a0a0a !important; }
        .stMarkdown, .stText, .stTitle, .stSubheader, p, label { color: #e0e0e0 !important; }
        h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
        [data-testid="stSidebar"] { background-color: #1a1a1a !important; border-right: 1px solid #333 !important; }
        [data-testid="stMetric"] { background-color: #1a1a1a !important; border: 1px solid #333 !important; border-radius: 10px !important; }
        .stButton > button { background-color: #4CAF50 !important; color: white !important; }
        .stDataFrame { background-color: #1a1a1a !important; color: #e0e0e0 !important; }
        .stTextInput > div > div > input { background-color: #2a2a2a !important; color: #ffffff !important; }
        .stSelectbox > div > div { background-color: #2a2a2a !important; color: #ffffff !important; }
        </style>
        """,
        
        "Azul": """
        <style>
        .stApp { background-color: #e8f4f8 !important; }
        .stMarkdown, .stText, .stTitle, .stSubheader, p, label { color: #1a3a5c !important; }
        [data-testid="stSidebar"] { background-color: #d4eaf0 !important; }
        [data-testid="stMetric"] { background-color: #c5e3ed !important; padding: 10px !important; border-radius: 10px !important; }
        .stButton > button { background-color: #2e86c1 !important; color: white !important; }
        </style>
        """,
        
        "Verde": """
        <style>
        .stApp { background-color: #e8f5e9 !important; }
        .stMarkdown, .stText, .stTitle, .stSubheader, p, label { color: #1b5e20 !important; }
        [data-testid="stSidebar"] { background-color: #c8e6c9 !important; }
        [data-testid="stMetric"] { background-color: #a5d6a7 !important; padding: 10px !important; border-radius: 10px !important; }
        .stButton > button { background-color: #43a047 !important; color: white !important; }
        </style>
        """,
        
        "Rosa": """
        <style>
        .stApp { background-color: #fce4ec !important; }
        .stMarkdown, .stText, .stTitle, .stSubheader, p, label { color: #880e4f !important; }
        [data-testid="stSidebar"] { background-color: #f8bbd0 !important; }
        [data-testid="stMetric"] { background-color: #f48fb1 !important; padding: 10px !important; border-radius: 10px !important; }
        .stButton > button { background-color: #e91e63 !important; color: white !important; }
        </style>
        """,
        
        "Roxo": """
        <style>
        .stApp { background-color: #f3e5f5 !important; }
        .stMarkdown, .stText, .stTitle, .stSubheader, p, label { color: #4a148c !important; }
        [data-testid="stSidebar"] { background-color: #e1bee7 !important; }
        [data-testid="stMetric"] { background-color: #ce93d8 !important; padding: 10px !important; border-radius: 10px !important; }
        .stButton > button { background-color: #9c27b0 !important; color: white !important; }
        </style>
        """,
        
        "Âmbar": """
        <style>
        .stApp { background-color: #fff8e1 !important; }
        .stMarkdown, .stText, .stTitle, .stSubheader, p, label { color: #bf360c !important; }
        [data-testid="stSidebar"] { background-color: #ffecb3 !important; }
        [data-testid="stMetric"] { background-color: #ffe082 !important; padding: 10px !important; border-radius: 10px !important; }
        .stButton > button { background-color: #ff9800 !important; color: white !important; }
        </style>
        """
    }
    
    css = temas_css.get(tema, temas_css["Claro"])
    st.markdown(css, unsafe_allow_html=True)

def get_temas_disponiveis():
    return ["Claro", "Escuro", "Azul", "Verde", "Rosa", "Roxo", "Âmbar"]

def get_icone_tema(tema):
    icones = {
        "Claro": "☀️",
        "Escuro": "🌙",
        "Azul": "💙",
        "Verde": "💚",
        "Rosa": "💗",
        "Roxo": "💜",
        "Âmbar": "🧡"
    }
    return icones.get(tema, "🎨")