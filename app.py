"""
AdaptFin - Assistente Financeiro Adaptativo
Versão 2.0.0
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
from utils.theme_utils import aplicar_tema_global

# ====================== CONFIGURAÇÃO ======================
st.set_page_config(
    page_title="AdaptFin - Dashboard",
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

# Aplicar tema
aplicar_tema_global()

# ====================== FUNÇÕES ======================
def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def formatar_data_br(data):
    if pd.isna(data):
        return "N/A"
    try:
        if isinstance(data, str):
            data = pd.to_datetime(data, errors='coerce')
        if pd.isna(data):
            return "N/A"
        return data.strftime("%d/%m/%Y")
    except:
        return "N/A"

def carregar_todas():
    todas = []
    if not st.session_state.receitas.empty:
        todas.append(st.session_state.receitas)
    if not st.session_state.despesas_fixas.empty:
        todas.append(st.session_state.despesas_fixas)
    if not st.session_state.gastos_variaveis.empty:
        todas.append(st.session_state.gastos_variaveis)
    
    if todas:
        df = pd.concat(todas, ignore_index=True)
        if 'Valor' in df.columns:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df = df.dropna(subset=['Valor'])
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df
    return pd.DataFrame()

def obter_nome_descricao(df):
    if df is None or df.empty:
        return None
    colunas = df.columns.tolist()
    for nome in ['Descricao', 'Descrição', 'descricao', 'descrição']:
        if nome in colunas:
            return nome
    return None

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 🧠 AdaptFin")
    st.caption("Seu assistente financeiro")
    st.markdown("---")
    
    # Menu - NÃO inclui app.py (já é a página inicial)
    st.page_link("pages/2_💰_Transacoes.py", label="💰 Transações")
    st.page_link("pages/3_📊_Relatorios.py", label="📈 Relatórios")
    st.page_link("pages/4_🤖_Insights_ML.py", label="🤖 Insights ML")
    st.page_link("pages/5_🎯_Metas.py", label="🎯 Metas")
    st.page_link("pages/6_💬_Chat_Financeiro.py", label="💬 Chat")
    st.page_link("pages/7_⚙️_Configuracoes.py", label="⚙️ Configurações")
    
    st.markdown("---")
    
    df_total = carregar_todas()
    if not df_total.empty:
        entradas = df_total[df_total["Valor"] > 0]["Valor"].sum()
        saidas = abs(df_total[df_total["Valor"] < 0]["Valor"].sum())
        st.metric("💰 Entradas", formatar_moeda(entradas))
        st.metric("📤 Saídas", formatar_moeda(saidas))
        st.metric("💵 Saldo", formatar_moeda(entradas - saidas))
    
    st.markdown("---")
    st.caption("AdaptFin v2.0")

# ====================== DASHBOARD ======================
st.title("🏠 Dashboard Financeiro")
st.markdown("---")

dados = carregar_todas()

if not dados.empty:
    # Métricas
    entradas = dados[dados["Valor"] > 0]["Valor"].sum()
    saidas = abs(dados[dados["Valor"] < 0]["Valor"].sum())
    saldo = entradas - saidas
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total de Entradas", formatar_moeda(entradas))
    with col2:
        st.metric("📤 Total de Saídas", formatar_moeda(saidas))
    with col3:
        delta_cor = "normal" if saldo >= 0 else "inverse"
        st.metric("💵 Saldo Total", formatar_moeda(saldo), delta_color=delta_cor)
    
    # Alertas
    if saldo < 0:
        st.error(f"🚨 ATENÇÃO: Você está gastando R$ {abs(saldo):,.2f} a mais do que ganha!")
    elif entradas > 0 and saldo < entradas * 0.1:
        st.warning(f"⚠️ Seu saldo é de apenas {formatar_moeda(saldo)}. Tente economizar mais!")
    elif entradas > 0:
        st.success(f"✅ Parabéns! Você está no azul com {formatar_moeda(saldo)} de saldo!")
    
    st.markdown("---")
    
    # Gráficos
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("🥧 Gastos por Categoria")
        despesas = dados[dados["Valor"] < 0].copy()
        if not despesas.empty:
            gastos = despesas.groupby("Categoria")["Valor"].sum().abs()
            if not gastos.empty:
                fig = px.pie(values=gastos.values, names=gastos.index, title="Distribuição de Gastos")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum gasto registrado")
    
    with col_graf2:
        st.subheader("📈 Evolução do Saldo")
        if 'Data' in dados.columns and not dados.empty:
            df_daily = dados.groupby('Data')['Valor'].sum().reset_index()
            df_daily = df_daily.sort_values('Data')
            df_daily['Saldo_Acumulado'] = df_daily['Valor'].cumsum()
            
            fig = px.line(df_daily, x='Data', y='Saldo_Acumulado', 
                         title="Saldo Acumulado ao Longo do Tempo",
                         markers=True,
                         color_discrete_sequence=['#2ecc71'])
            fig.update_layout(xaxis_title="Data", yaxis_title="Saldo (R$)")
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Adicione transações com datas para ver a evolução do saldo")
    
    st.markdown("---")
    
    # Resumo do período
    st.subheader("📅 Resumo do Período")
    
    if 'Data' in dados.columns and not dados.empty:
        data_inicio = dados['Data'].min()
        data_fim = dados['Data'].max()
        st.caption(f"Período analisado: {formatar_data_br(data_inicio)} a {formatar_data_br(data_fim)}")
        
        dados['Mes'] = dados['Data'].dt.to_period('M')
        
        entradas_mensais = dados[dados['Valor'] > 0].groupby('Mes')['Valor'].sum().reset_index()
        entradas_mensais.columns = ['Mes', 'Entradas']
        
        saidas_mensais = dados[dados['Valor'] < 0].groupby('Mes')['Valor'].sum().abs().reset_index()
        saidas_mensais.columns = ['Mes', 'Saídas']
        
        resumo_mensal = pd.merge(entradas_mensais, saidas_mensais, on='Mes', how='outer').fillna(0)
        resumo_mensal['Saldo'] = resumo_mensal['Entradas'] - resumo_mensal['Saídas']
        resumo_mensal['Mes'] = resumo_mensal['Mes'].astype(str)
        
        fig = px.bar(resumo_mensal, x='Mes', y=['Entradas', 'Saídas'], 
                     title="Entradas vs Saídas por Mês",
                     barmode='group',
                     color_discrete_sequence=['#2ecc71', '#e74c3c'])
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(resumo_mensal, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Últimas transações
    st.subheader("📋 Últimas Transações")
    if 'Data' in dados.columns:
        ultimas = dados.sort_values('Data', ascending=False).head(10).copy()
        ultimas["Valor"] = ultimas["Valor"].apply(formatar_moeda)
        ultimas["Data"] = ultimas["Data"].apply(formatar_data_br)
        
        col_desc = obter_nome_descricao(ultimas)
        colunas = ['Data']
        if col_desc:
            colunas.append(col_desc)
        colunas.append('Valor')
        colunas.append('Categoria')
        
        st.dataframe(ultimas[colunas], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma transação registrada")
    
    # Top 5 gastos
    st.subheader("🔝 Top 5 Maiores Gastos")
    gastos_df = dados[dados["Valor"] < 0].copy()
    if not gastos_df.empty:
        gastos_df["Valor"] = pd.to_numeric(gastos_df["Valor"], errors='coerce')
        gastos_df = gastos_df.dropna(subset=['Valor'])
        
        if not gastos_df.empty:
            top5 = gastos_df.sort_values("Valor", ascending=True).head(5)
            top5["Valor"] = top5["Valor"].abs().apply(formatar_moeda)
            
            col_desc = obter_nome_descricao(top5)
            colunas = []
            if col_desc:
                colunas.append(col_desc)
            colunas.append('Valor')
            colunas.append('Categoria')
            
            st.dataframe(top5[colunas], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum gasto registrado")
    else:
        st.info("Nenhum gasto registrado")

else:
    st.info("📊 Nenhum dado disponível. Adicione transações na página de Transações!")
    
    with st.expander("💡 Como começar"):
        st.markdown("""
        **Para começar a usar o AdaptFin:**
        
        1. Vá para a página **💰 Transações**
        2. Adicione suas receitas (salário, freelas)
        3. Adicione suas despesas (aluguel, contas)
        4. Volte aqui para ver seus dados!
        """)

st.markdown("---")
st.caption("📊 Dashboard atualizado em tempo real")