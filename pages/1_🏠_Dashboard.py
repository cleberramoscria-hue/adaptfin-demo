import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os
from utils.theme_utils import aplicar_tema_global

# Aplicar tema
aplicar_tema_global()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_manager import DataManager
from utils.format_utils import format_currency
from utils.date_utils import format_date_br

st.set_page_config(page_title="Dashboard - AdaptFin", page_icon="🏠", layout="wide")

def formatar_moeda(valor):
    return format_currency(valor)

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

st.title("🏠 Dashboard Financeiro")
st.markdown("---")

# Carregar dados do session_state
if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame()
if "despesas_fixas" not in st.session_state:
    st.session_state.despesas_fixas = pd.DataFrame()
if "gastos_variaveis" not in st.session_state:
    st.session_state.gastos_variaveis = pd.DataFrame()

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
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df
    return pd.DataFrame()

dados = carregar_todas()

if not dados.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        entradas = dados[dados["Valor"] > 0]["Valor"].sum()
        st.metric("💰 Total de Entradas", formatar_moeda(entradas))
    with col2:
        saidas = dados[dados["Valor"] < 0]["Valor"].sum()
        st.metric("📤 Total de Saídas", formatar_moeda(saidas))
    with col3:
        saldo = dados["Valor"].sum()
        st.metric("💸 Saldo Final", formatar_moeda(saldo))
    with col4:
        st.metric("💾 Economia", formatar_moeda(entradas - saidas))
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("🥧 Gastos por Categoria")
        despesas = dados[dados["Valor"] < 0].copy()
        if not despesas.empty:
            gastos = despesas.groupby("Categoria")["Valor"].sum().abs()
            if not gastos.empty:
                fig = px.pie(values=gastos.values, names=gastos.index, title="Distribuição")
                st.plotly_chart(fig, use_container_width=True)
    
    with col_graf2:
        st.subheader("📈 Evolução do Saldo")
        if 'Data' in dados.columns:
            df_daily = dados.groupby('Data')['Valor'].sum().cumsum().reset_index()
            fig = px.line(df_daily, x='Data', y='Valor', title="Saldo Acumulado", markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Últimas Transações")
    ultimas = dados.sort_values('Data', ascending=False).head(10).copy()
    ultimas["Valor"] = ultimas["Valor"].apply(formatar_moeda)
    ultimas["Data"] = ultimas["Data"].apply(formatar_data_br)
    st.dataframe(ultimas[["Data", "Descrição", "Valor", "Categoria"]], use_container_width=True, hide_index=True)

else:
    st.info("📊 Nenhum dado disponível. Adicione transações!")

st.markdown("---")
st.caption("📊 Dashboard atualizado em tempo real")