"""
Funções compartilhadas entre todas as páginas
"""
import streamlit as st
import pandas as pd
from datetime import datetime

def carregar_todas_transacoes():
    """Carrega todas as transações do session state"""
    todas = []
    if not st.session_state.get('receitas', pd.DataFrame()).empty:
        todas.append(st.session_state.receitas)
    if not st.session_state.get('despesas_fixas', pd.DataFrame()).empty:
        todas.append(st.session_state.despesas_fixas)
    if not st.session_state.get('gastos_variaveis', pd.DataFrame()).empty:
        todas.append(st.session_state.gastos_variaveis)
    
    if todas:
        df_total = pd.concat(todas, ignore_index=True)
        if 'Valor' in df_total.columns:
            df_total['Valor'] = pd.to_numeric(df_total['Valor'], errors='coerce')
            df_total = df_total.dropna(subset=['Valor'])
        
        if 'Data' in df_total.columns:
            df_total['Data'] = pd.to_datetime(df_total['Data'], errors='coerce')
            df_total['Data'] = df_total['Data'].fillna(pd.Timestamp.now())
        
        return df_total
    return pd.DataFrame()

def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def formatar_data_br(data):
    """Formata data para padrão brasileiro DD/MM/YYYY"""
    if data is None or pd.isna(data):
        return "N/A"
    try:
        if isinstance(data, str):
            data = pd.to_datetime(data, errors='coerce')
        if pd.isna(data):
            return "N/A"
        return data.strftime("%d/%m/%Y")
    except:
        return "N/A"