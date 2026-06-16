import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.theme_utils import aplicar_tema_global
from utils.format_utils import format_currency

# Aplicar tema
aplicar_tema_global()

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

# Carregar dados do session state
if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame()
if "despesas_fixas" not in st.session_state:
    st.session_state.despesas_fixas = pd.DataFrame()
if "gastos_variaveis" not in st.session_state:
    st.session_state.gastos_variaveis = pd.DataFrame()

def carregar_todas():
    """Carrega todas as transações do session state"""
    todas = []
    if not st.session_state.receitas.empty:
        todas.append(st.session_state.receitas)
    if not st.session_state.despesas_fixas.empty:
        todas.append(st.session_state.despesas_fixas)
    if not st.session_state.gastos_variaveis.empty:
        todas.append(st.session_state.gastos_variaveis)
    
    if todas:
        df = pd.concat(todas, ignore_index=True)
        
        # Garantir que Valor seja numérico
        if 'Valor' in df.columns:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df = df.dropna(subset=['Valor'])
        
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        
        return df
    return pd.DataFrame()

dados = carregar_todas()

if not dados.empty:
    # Calcular totais
    entradas = dados[dados["Valor"] > 0]["Valor"].sum()
    saidas = abs(dados[dados["Valor"] < 0]["Valor"].sum())
    saldo = entradas - saidas
    
    # Métricas
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
        
        # Total por mês
        dados['Mes'] = dados['Data'].dt.to_period('M')
        resumo_mensal = dados.groupby('Mes').agg({
            'Valor': lambda x: x[x > 0].sum(),
            'Valor_despesa': lambda x: abs(x[x < 0].sum())
        }).reset_index()
        resumo_mensal.columns = ['Mês', 'Entradas', 'Saídas']
        resumo_mensal['Saldo'] = resumo_mensal['Entradas'] - resumo_mensal['Saídas']
        
        fig = px.bar(resumo_mensal, x='Mês', y=['Entradas', 'Saídas'], 
                     title="Entradas vs Saídas por Mês",
                     barmode='group',
                     color_discrete_sequence=['#2ecc71', '#e74c3c'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Últimas transações - CORRIGIDO
    st.subheader("📋 Últimas Transações")
    if 'Data' in dados.columns:
        ultimas = dados.sort_values('Data', ascending=False).head(10).copy()
        
        # Verificar quais colunas existem
        colunas_disponiveis = []
        if 'Data' in ultimas.columns:
            colunas_disponiveis.append('Data')
        if 'Descrição' in ultimas.columns:
            colunas_disponiveis.append('Descrição')
        elif 'descricao' in ultimas.columns:
            ultimas = ultimas.rename(columns={'descricao': 'Descrição'})
            colunas_disponiveis.append('Descrição')
        if 'Valor' in ultimas.columns:
            colunas_disponiveis.append('Valor')
        if 'Categoria' in ultimas.columns:
            colunas_disponiveis.append('Categoria')
        
        if colunas_disponiveis:
            ultimas["Valor"] = ultimas["Valor"].apply(formatar_moeda)
            ultimas["Data"] = ultimas["Data"].apply(formatar_data_br)
            st.dataframe(ultimas[colunas_disponiveis], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma transação para exibir")
    else:
        st.info("Nenhuma transação registrada")
    
    # Top 5 gastos - CORRIGIDO
    st.subheader("🔝 Top 5 Maiores Gastos")
    gastos_df = dados[dados["Valor"] < 0].copy()
    if not gastos_df.empty:
        gastos_df["Valor"] = pd.to_numeric(gastos_df["Valor"], errors='coerce')
        gastos_df = gastos_df.dropna(subset=['Valor'])
        
        if not gastos_df.empty:
            top5 = gastos_df.sort_values("Valor", ascending=True).head(5)
            colunas_top = []
            if 'Descrição' in top5.columns:
                colunas_top.append('Descrição')
            elif 'descricao' in top5.columns:
                top5 = top5.rename(columns={'descricao': 'Descrição'})
                colunas_top.append('Descrição')
            if 'Valor' in top5.columns:
                colunas_top.append('Valor')
            if 'Categoria' in top5.columns:
                colunas_top.append('Categoria')
            
            if colunas_top:
                top5["Valor"] = top5["Valor"].abs().apply(formatar_moeda)
                st.dataframe(top5[colunas_top], use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum gasto registrado")
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
        
        Ou clique em "Carregar Dados de Exemplo" na página de Transações.
        """)

st.markdown("---")
st.caption("📊 Dashboard atualizado em tempo real")