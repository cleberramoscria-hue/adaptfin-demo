"""
AdaptFin - Assistente Financeiro Adaptativo
Versão 2.0.0
"""
import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
from src.shared import formatar_moeda, carregar_todas_transacoes
from utils.theme_utils import aplicar_tema_global

# ====================== CONFIGURAÇÃO ======================
st.set_page_config(
    page_title="AdaptFin",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== INICIALIZAÇÃO ======================
db = DatabaseManager()

if "despesas_fixas" not in st.session_state:
    st.session_state.despesas_fixas = pd.DataFrame()
if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame()
if "gastos_variaveis" not in st.session_state:
    st.session_state.gastos_variaveis = pd.DataFrame()
if "configuracoes" not in st.session_state:
    st.session_state.configuracoes = {
        "salario_mensal": 0.0,
        "limite_gastos": 0.0,
        "alertas_ativos": True,
        "ml_ativado": True,
        "tema": "Claro"
    }

# Aplicar tema GLOBALMENTE (em todas as páginas)
aplicar_tema_global()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 🧠 AdaptFin")
    st.caption("Seu assistente financeiro")
    st.markdown("---")
    
    # Menu
    st.page_link("pages/1_🏠_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_💰_Transacoes.py", label="💰 Transações")
    st.page_link("pages/3_📊_Relatorios.py", label="📈 Relatórios")
    st.page_link("pages/4_🤖_Insights_ML.py", label="🤖 Insights ML")
    st.page_link("pages/5_🎯_Metas.py", label="🎯 Metas")
    st.page_link("pages/6_💬_Chat_Financeiro.py", label="💬 Chat")
    st.page_link("pages/7_⚙️_Configuracoes.py", label="⚙️ Configurações")

# ====================== CORPO ======================
st.title("🧠 AdaptFin")
st.subheader("Assistente Financeiro Adaptativo")

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰", "R$ 0,00")
with col2:
    st.metric("📤", "R$ 0,00")
with col3:
    st.metric("💵", "R$ 0,00")

st.info("👈 Selecione uma opção no menu lateral para começar!")

st.markdown("---")
st.caption("AdaptFin v2.0")