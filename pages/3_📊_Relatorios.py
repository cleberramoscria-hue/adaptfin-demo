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

from utils.format_utils import format_currency

st.set_page_config(page_title="Relatórios - AdaptFin", page_icon="📊", layout="wide")

def formatar_moeda(valor):
    return format_currency(valor)

st.title("📊 Relatórios Financeiros")
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
    # Criar coluna de mês
    dados['Mes'] = dados['Data'].dt.to_period('M')
    
    # Relatório por Mês
    st.subheader("📊 Resumo Mensal")
    
    # Calcular totais mensais
    resumo_mensal = []
    for mes in dados['Mes'].unique():
        df_mes = dados[dados['Mes'] == mes]
        entradas = df_mes[df_mes['Valor'] > 0]['Valor'].sum()
        saidas = abs(df_mes[df_mes['Valor'] < 0]['Valor'].sum())
        saldo = entradas - saidas
        
        resumo_mensal.append({
            'Mês': str(mes),
            'Entradas': entradas,
            'Saídas': saidas,
            'Saldo': saldo
        })
    
    df_resumo = pd.DataFrame(resumo_mensal)
    
    # Gráfico de barras
    fig = px.bar(df_resumo, x='Mês', y=['Entradas', 'Saídas'], 
                 title="Entradas vs Saídas por Mês",
                 barmode='group',
                 color_discrete_sequence=['#2ecc71', '#e74c3c'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela resumo
    st.subheader("📋 Tabela Resumo Mensal")
    df_display = df_resumo.copy()
    df_display['Entradas'] = df_display['Entradas'].apply(formatar_moeda)
    df_display['Saídas'] = df_display['Saídas'].apply(formatar_moeda)
    df_display['Saldo'] = df_display['Saldo'].apply(formatar_moeda)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Relatório Anual
    st.subheader("📅 Relatório Anual")
    
    ano_atual = datetime.now().year
    dados_ano = dados[dados['Data'].dt.year == ano_atual]
    
    if not dados_ano.empty:
        total_entradas = dados_ano[dados_ano['Valor'] > 0]['Valor'].sum()
        total_saidas = abs(dados_ano[dados_ano['Valor'] < 0]['Valor'].sum())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total de Entradas", formatar_moeda(total_entradas))
        with col2:
            st.metric("📤 Total de Saídas", formatar_moeda(total_saidas))
        with col3:
            st.metric("💵 Saldo Anual", formatar_moeda(total_entradas - total_saidas))
        
        # Gráfico de pizza anual
        fig = px.pie(values=[total_entradas, total_saidas], 
                     names=['Entradas', 'Saídas'], 
                     title=f"Proporção {ano_atual}")
        st.plotly_chart(fig, use_container_width=True)
    
    # Relatório por Categoria
    st.subheader("🏷️ Gastos por Categoria")
    
    # Selecionar período
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data inicial", value=datetime.now().replace(month=1, day=1))
    with col2:
        data_fim = st.date_input("Data final", value=datetime.now())
    
    df_filtrado = dados[(dados['Data'] >= pd.to_datetime(data_inicio)) & 
                        (dados['Data'] <= pd.to_datetime(data_fim))]
    
    gastos_cat = df_filtrado[df_filtrado['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
    
    if not gastos_cat.empty:
        fig = px.pie(values=gastos_cat.values, names=gastos_cat.index, 
                     title=f"Gastos por Categoria")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de categorias
        df_cat = pd.DataFrame({
            'Categoria': gastos_cat.index,
            'Valor': gastos_cat.values,
            'Percentual': (gastos_cat.values / gastos_cat.sum() * 100).round(1)
        })
        df_cat['Valor'] = df_cat['Valor'].apply(formatar_moeda)
        df_cat['Percentual'] = df_cat['Percentual'].astype(str) + '%'
        st.dataframe(df_cat, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum gasto no período selecionado")

else:
    st.info("📊 Nenhum dado disponível. Adicione transações na página de Transações!")

st.markdown("---")
st.caption("📊 Relatórios gerados com base nos seus dados")